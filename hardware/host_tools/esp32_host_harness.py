from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


SCENARIOS_DIR = Path(__file__).resolve().parent / "scenarios"
REPORTS_DIR = Path(__file__).resolve().parent / "reports"
DEFAULT_BAUD = 115200


class SerialPort(Protocol):
    timeout: float

    def write(self, data: bytes) -> int: ...

    def readline(self) -> bytes: ...

    def reset_input_buffer(self) -> None: ...

    def reset_output_buffer(self) -> None: ...

    def close(self) -> None: ...


@dataclass
class TranscriptEvent:
    offset_ms: int
    direction: str
    payload: str


@dataclass
class StepResult:
    index: int
    name: str
    step_type: str
    ok: bool
    sent: str | None
    received: list[str]
    missing_expectations: list[str]


class HarnessError(RuntimeError):
    """Error controlado del harness."""


def load_scenario(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def bundled_scenarios() -> dict[str, Path]:
    return {path.stem: path for path in sorted(SCENARIOS_DIR.glob("*.json"))}


def resolve_scenario_path(name: str | None, path: str | None) -> Path:
    if path:
        scenario_path = Path(path).expanduser().resolve()
        if not scenario_path.exists():
            raise HarnessError(f"No existe el scenario file: {scenario_path}")
        return scenario_path

    if not name:
        raise HarnessError("Debes pasar --scenario o --scenario-file")

    candidates = bundled_scenarios()
    if name not in candidates:
        available = ", ".join(candidates) or "<ninguno>"
        raise HarnessError(
            f"Escenario desconocido '{name}'. Disponibles: {available}"
        )
    return candidates[name]


def open_serial_port(port: str, baud: int, timeout_s: float) -> SerialPort:
    try:
        import serial  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - depende del entorno
        raise HarnessError(
            "Falta pyserial. Instala dependencias con "
            "`python -m pip install -r hardware/host_tools/requirements.txt`."
        ) from exc

    return serial.Serial(port=port, baudrate=baud, timeout=timeout_s)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sanitize_label(value: str) -> str:
    return "".join(char if char.isalnum() or char in "-_" else "_" for char in value)


def collect_lines(
    serial_port: SerialPort,
    transcript: list[TranscriptEvent],
    start_monotonic: float,
    *,
    quiet_s: float,
    max_wait_s: float,
) -> list[str]:
    lines: list[str] = []
    started_at = time.monotonic()
    last_payload_at: float | None = None

    while True:
        raw = serial_port.readline()
        current = time.monotonic()
        if raw:
            decoded = raw.decode("utf-8", errors="replace").strip()
            if decoded:
                lines.append(decoded)
                transcript.append(
                    TranscriptEvent(
                        offset_ms=int((current - start_monotonic) * 1000),
                        direction="RX",
                        payload=decoded,
                    )
                )
                last_payload_at = current
            continue

        elapsed = current - started_at
        idle = None if last_payload_at is None else current - last_payload_at
        if last_payload_at is not None and idle is not None and idle >= quiet_s:
            break
        if elapsed >= max_wait_s:
            break

    return lines


def evaluate_expectations(received: list[str], expected: list[str]) -> list[str]:
    combined = "\n".join(received)
    return [needle for needle in expected if needle not in combined]


def run_scenario(
    serial_port: SerialPort,
    scenario: dict[str, Any],
    *,
    quiet_s: float,
    max_wait_s: float,
    sleep_fn=time.sleep,
) -> tuple[list[TranscriptEvent], list[StepResult], bool]:
    transcript: list[TranscriptEvent] = []
    results: list[StepResult] = []
    start_monotonic = time.monotonic()

    startup_capture_s = float(scenario.get("startup_capture_s", 0.0))
    if startup_capture_s > 0:
        collect_lines(
            serial_port,
            transcript,
            start_monotonic,
            quiet_s=quiet_s,
            max_wait_s=startup_capture_s,
        )

    for index, step in enumerate(scenario.get("steps", []), start=1):
        step_type = step["type"]
        name = step.get("name", f"step_{index}")
        if step_type == "sleep":
            seconds = float(step["seconds"])
            sleep_fn(seconds)
            results.append(
                StepResult(
                    index=index,
                    name=name,
                    step_type=step_type,
                    ok=True,
                    sent=None,
                    received=[],
                    missing_expectations=[],
                )
            )
            continue

        if step_type != "command":
            raise HarnessError(f"Tipo de paso no soportado: {step_type}")

        command = step["send"]
        serial_port.write(f"{command}\n".encode("utf-8"))
        transcript.append(
            TranscriptEvent(
                offset_ms=int((time.monotonic() - start_monotonic) * 1000),
                direction="TX",
                payload=command,
            )
        )
        response = collect_lines(
            serial_port,
            transcript,
            start_monotonic,
            quiet_s=float(step.get("quiet_s", quiet_s)),
            max_wait_s=float(step.get("timeout_s", max_wait_s)),
        )
        missing = evaluate_expectations(response, step.get("expect_all", []))
        ok = not missing
        results.append(
            StepResult(
                index=index,
                name=name,
                step_type=step_type,
                ok=ok,
                sent=command,
                received=response,
                missing_expectations=missing,
            )
        )
        if not ok:
            return transcript, results, False

    return transcript, results, True


def make_artifact_stem(
    *,
    scenario_id: str,
    label: str | None,
) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{sanitize_label(label)}" if label else ""
    return f"{timestamp}_{scenario_id}{suffix}"


def save_artifacts(
    output_dir: Path,
    stem: str,
    *,
    port: str,
    baud: int,
    scenario_path: Path,
    scenario: dict[str, Any],
    transcript: list[TranscriptEvent],
    results: list[StepResult],
    success: bool,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / f"{stem}.log"
    json_path = output_dir / f"{stem}.json"

    with log_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# scenario={scenario['id']} port={port} baud={baud}\n")
        for event in transcript:
            handle.write(
                f"[{event.offset_ms:06d} ms] {event.direction:<2} {event.payload}\n"
            )

    summary = {
        "scenario_id": scenario["id"],
        "scenario_path": str(scenario_path),
        "description": scenario.get("description", ""),
        "captured_at_utc": now_iso(),
        "port": port,
        "baud": baud,
        "success": success,
        "steps": [asdict(result) for result in results],
        "transcript_event_count": len(transcript),
    }

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    return log_path, json_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Harness host-side para automatizar secuencias serie del ESP32."
    )
    parser.add_argument("--port", help="Puerto serie, por ejemplo COM5 o /dev/ttyACM0")
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD)
    parser.add_argument("--scenario", help="Nombre de escenario bundled")
    parser.add_argument("--scenario-file", help="Ruta a un escenario JSON externo")
    parser.add_argument(
        "--output-dir",
        default=str(REPORTS_DIR),
        help="Directorio para transcript y resumen JSON",
    )
    parser.add_argument("--label", help="Etiqueta opcional para el nombre del artefacto")
    parser.add_argument(
        "--list-scenarios",
        action="store_true",
        help="Lista escenarios bundled y termina",
    )
    parser.add_argument("--quiet-s", type=float, default=0.35)
    parser.add_argument("--max-wait-s", type=float, default=3.0)
    parser.add_argument("--serial-timeout-s", type=float, default=0.10)
    return parser


def print_scenarios() -> int:
    for name, path in bundled_scenarios().items():
        scenario = load_scenario(path)
        print(f"- {name}: {scenario.get('description', '')}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_scenarios:
        return print_scenarios()

    if not args.port:
        parser.error("--port es obligatorio salvo con --list-scenarios")

    scenario_path = resolve_scenario_path(args.scenario, args.scenario_file)
    scenario = load_scenario(scenario_path)

    serial_port = open_serial_port(args.port, args.baud, args.serial_timeout_s)
    try:
        serial_port.reset_input_buffer()
        serial_port.reset_output_buffer()
        transcript, results, success = run_scenario(
            serial_port,
            scenario,
            quiet_s=args.quiet_s,
            max_wait_s=args.max_wait_s,
        )
    finally:
        serial_port.close()

    stem = make_artifact_stem(scenario_id=scenario["id"], label=args.label)
    log_path, json_path = save_artifacts(
        Path(args.output_dir),
        stem,
        port=args.port,
        baud=args.baud,
        scenario_path=scenario_path,
        scenario=scenario,
        transcript=transcript,
        results=results,
        success=success,
    )

    print(f"scenario={scenario['id']} success={success}")
    print(f"log={log_path}")
    print(f"json={json_path}")

    if not success:
        first_failure = next(result for result in results if not result.ok)
        print(
            "Paso fallido: "
            f"{first_failure.name} missing={first_failure.missing_expectations}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
