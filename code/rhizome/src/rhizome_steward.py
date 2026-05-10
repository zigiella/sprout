"""Minimal autonomous Rhizome steward loop.

This module closes the smallest real loop for a supervised plant pilot:

ESP32 telemetry -> deterministic decision -> optional Gemma rationale ->
optional ESP32 WATER command -> bounded local receipts.

It deliberately keeps physical authority outside the LLM. Gemma may explain a
decision, but hard gates and ESP32 ACK/REJECT decide what reaches water.
"""

from __future__ import annotations

import argparse
import json
import os
import select
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Protocol

VERSION = "0.1.0"
FIRMWARE_MAX_WATER_SECONDS_MVP = 30
FIRMWARE_TANK_MINIMUM_PCT = 20.0
DEFAULT_RETENTION_DAYS = 120
DEFAULT_MAX_TOTAL_BYTES = 64 * 1024 * 1024


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def zulu(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_zulu(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def default_state_dir() -> Path:
    return Path(os.environ.get("RHIZOME_STEWARD_STATE_DIR", "~/.local/share/sprout/rhizome_steward")).expanduser()


def parse_kv_line(line: str) -> tuple[str, dict[str, str]]:
    parts = line.strip().split()
    if not parts:
        return "", {}
    tag = parts[0]
    values: dict[str, str] = {}
    for token in parts[1:]:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        values[key] = value
    return tag, values


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@dataclass
class Telemetry:
    collected_at: str
    soil_a_raw: int | None = None
    soil_b_raw: int | None = None
    tank_level_pct: float | None = None
    flow_pulses: int | None = None
    host_link: str = "UNKNOWN"
    host_age_ms: int | None = None
    bme280: str | None = None
    bme280_temp_c: float | None = None
    raw_lines: list[str] = field(default_factory=list)

    @classmethod
    def from_esp32_lines(cls, lines: list[str], now: datetime | None = None) -> "Telemetry":
        now = now or utc_now()
        telemetry = cls(collected_at=zulu(now), raw_lines=lines)
        for line in lines:
            tag, values = parse_kv_line(line)
            if tag not in {"TELEMETRY_REPORT", "STATUS_REPORT"}:
                continue
            soil_a_raw = _int_or_none(values.get("soil_a_raw"))
            soil_b_raw = _int_or_none(values.get("soil_b_raw"))
            tank_level_pct = _float_or_none(values.get("tank_level_pct"))
            flow_pulses = _int_or_none(values.get("flow_pulses"))
            telemetry.soil_a_raw = soil_a_raw if soil_a_raw is not None and soil_a_raw >= 0 else telemetry.soil_a_raw
            telemetry.soil_b_raw = soil_b_raw if soil_b_raw is not None and soil_b_raw >= 0 else telemetry.soil_b_raw
            telemetry.tank_level_pct = tank_level_pct if tank_level_pct is not None and tank_level_pct >= 0 else telemetry.tank_level_pct
            telemetry.flow_pulses = flow_pulses if flow_pulses is not None and flow_pulses >= 0 else telemetry.flow_pulses
            telemetry.host_link = values.get("host_link", telemetry.host_link)
            host_age_ms = _int_or_none(values.get("host_age_ms"))
            telemetry.host_age_ms = host_age_ms if host_age_ms is not None and host_age_ms >= 0 else telemetry.host_age_ms
            telemetry.bme280 = values.get("bme280", telemetry.bme280)
            temp_x100 = _float_or_none(values.get("bme280_temp_c_x100"))
            if temp_x100 is not None and temp_x100 >= -10000:
                telemetry.bme280_temp_c = temp_x100 / 100.0
        return telemetry

    def soil_a_pct(self) -> float | None:
        if self.soil_a_raw is None:
            return None
        if 0 <= self.soil_a_raw <= 100:
            return float(self.soil_a_raw)
        return None


@dataclass
class ESP32CommandResult:
    ok: bool
    command: str
    sent_at: str
    received_at: str
    lines: list[str]
    ack_status: str
    reject_reason: str | None = None


class ESP32Client(Protocol):
    def heartbeat(self) -> ESP32CommandResult: ...

    def telemetry(self) -> Telemetry: ...

    def water(self, plot: str, seconds: int) -> ESP32CommandResult: ...

    def close(self) -> None: ...


class FakeESP32Client:
    def __init__(self, telemetry: Telemetry | None = None, reject_water_reason: str | None = None) -> None:
        self.current_telemetry = telemetry or Telemetry(
            collected_at=zulu(utc_now()),
            soil_a_raw=32,
            soil_b_raw=40,
            tank_level_pct=70.0,
            flow_pulses=0,
            host_link="FRESH",
            host_age_ms=0,
        )
        self.reject_water_reason = reject_water_reason

    def _result(self, command: str, lines: list[str], ok: bool = True, reason: str | None = None) -> ESP32CommandResult:
        now = zulu(utc_now())
        return ESP32CommandResult(ok=ok, command=command, sent_at=now, received_at=now, lines=lines, ack_status="OK" if ok else "REJECT", reject_reason=reason)

    def heartbeat(self) -> ESP32CommandResult:
        self.current_telemetry.host_link = "FRESH"
        self.current_telemetry.host_age_ms = 0
        return self._result("HOST_HEARTBEAT", ["ACK command=HOST_HEARTBEAT state=SAFE_IDLE host_link=FRESH host_age_ms=0"])

    def telemetry(self) -> Telemetry:
        line = (
            "TELEMETRY_REPORT "
            f"soil_a_raw={self.current_telemetry.soil_a_raw if self.current_telemetry.soil_a_raw is not None else -1} "
            f"soil_b_raw={self.current_telemetry.soil_b_raw if self.current_telemetry.soil_b_raw is not None else -1} "
            f"tank_level_pct={self.current_telemetry.tank_level_pct if self.current_telemetry.tank_level_pct is not None else -1} "
            f"flow_pulses={self.current_telemetry.flow_pulses if self.current_telemetry.flow_pulses is not None else -1} "
            f"host_link={self.current_telemetry.host_link} host_age_ms={self.current_telemetry.host_age_ms if self.current_telemetry.host_age_ms is not None else -1} "
            "source=fake"
        )
        return Telemetry.from_esp32_lines([line])

    def water(self, plot: str, seconds: int) -> ESP32CommandResult:
        command = f"WATER {plot} {seconds}"
        if self.reject_water_reason:
            return self._result(command, [f"REJECT reason={self.reject_water_reason} cmd={command}"], ok=False, reason=self.reject_water_reason)
        return self._result(command, [f"ACK command=WATER plot={plot} seconds={seconds} execution=DRY_RUN state=SAFE_IDLE host_link=FRESH tank_level_pct={self.current_telemetry.tank_level_pct}"])

    def close(self) -> None:
        return


class TermiosSerialPort:
    """Small Linux serial fallback for Jetson when pyserial is unavailable."""

    def __init__(self, port: str, baud: int, timeout_s: float) -> None:
        if baud != 115200:
            raise RuntimeError("TermiosSerialPort fallback solo soporta 115200 baud en MVP.")
        import termios

        self.termios = termios
        self.timeout = timeout_s
        self.fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        attrs = termios.tcgetattr(self.fd)
        attrs[0] = 0
        attrs[1] = 0
        attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
        attrs[3] = 0
        attrs[4] = termios.B115200
        attrs[5] = termios.B115200
        termios.tcsetattr(self.fd, termios.TCSANOW, attrs)

    def write(self, data: bytes) -> int:
        return os.write(self.fd, data)

    def readline(self) -> bytes:
        deadline = time.monotonic() + self.timeout
        chunks: list[bytes] = []
        while time.monotonic() < deadline:
            remaining = max(0.0, deadline - time.monotonic())
            ready, _, _ = select.select([self.fd], [], [], min(remaining, self.timeout))
            if not ready:
                break
            try:
                chunk = os.read(self.fd, 1)
            except BlockingIOError:
                continue
            if not chunk:
                break
            chunks.append(chunk)
            if chunk == b"\n":
                break
        return b"".join(chunks)

    def reset_input_buffer(self) -> None:
        self.termios.tcflush(self.fd, self.termios.TCIFLUSH)

    def reset_output_buffer(self) -> None:
        self.termios.tcflush(self.fd, self.termios.TCOFLUSH)

    def close(self) -> None:
        os.close(self.fd)


class SerialESP32Client:
    def __init__(self, port: str, baud: int = 115200, timeout_s: float = 0.1, quiet_s: float = 0.35, max_wait_s: float = 3.0, water_command_mode: str = "water-duration") -> None:
        try:
            import serial  # type: ignore
        except ModuleNotFoundError as exc:
            if os.name != "posix":
                raise RuntimeError("pyserial no esta instalado. Instala hardware/host_tools/requirements.txt") from exc
            self.serial = TermiosSerialPort(port=port, baud=baud, timeout_s=timeout_s)
        else:
            self.serial = serial.Serial(port=port, baudrate=baud, timeout=timeout_s)
        if water_command_mode not in {"water-duration", "pump-toggle"}:
            raise ValueError("water_command_mode debe ser water-duration o pump-toggle")
        self.quiet_s = quiet_s
        self.max_wait_s = max_wait_s
        self.water_command_mode = water_command_mode
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

    def _collect(self) -> list[str]:
        lines: list[str] = []
        started_at = time.monotonic()
        last_payload_at: float | None = None
        while True:
            raw = self.serial.readline()
            current = time.monotonic()
            if raw:
                decoded = raw.decode("utf-8", errors="replace").strip()
                if decoded:
                    lines.append(decoded)
                    last_payload_at = current
                continue
            if last_payload_at is not None and current - last_payload_at >= self.quiet_s:
                break
            if current - started_at >= self.max_wait_s:
                break
        return lines

    def command(self, command: str) -> ESP32CommandResult:
        sent_at = zulu(utc_now())
        self.serial.write(f"{command}\n".encode("utf-8"))
        lines = self._collect()
        received_at = zulu(utc_now())
        combined = "\n".join(lines)
        if "REJECT reason=" in combined:
            reason = None
            for line in lines:
                if line.startswith("REJECT "):
                    _, values = parse_kv_line(line)
                    reason = values.get("reason")
                    break
            return ESP32CommandResult(False, command, sent_at, received_at, lines, "REJECT", reason)
        ok = any(line.startswith("ACK ") for line in lines)
        return ESP32CommandResult(ok, command, sent_at, received_at, lines, "OK" if ok else "NO_ACK")

    def heartbeat(self) -> ESP32CommandResult:
        return self.command("HOST_HEARTBEAT")

    def telemetry(self) -> Telemetry:
        result = self.command("TELEMETRY")
        telemetry = Telemetry.from_esp32_lines(result.lines)
        if telemetry.host_link == "UNKNOWN":
            telemetry.host_link = "FRESH" if result.ok else "UNKNOWN"
        return telemetry

    def water(self, plot: str, seconds: int) -> ESP32CommandResult:
        if self.water_command_mode == "water-duration":
            return self.command(f"WATER {plot} {seconds}")
        started = self.command("PUMP_ON")
        if not started.ok:
            return started
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            time.sleep(min(0.25, max(0.0, deadline - time.monotonic())))
        stopped = self.command("PUMP_OFF")
        return ESP32CommandResult(
            ok=stopped.ok,
            command=f"PUMP_ON/PUMP_OFF {seconds}",
            sent_at=started.sent_at,
            received_at=stopped.received_at,
            lines=[*started.lines, *stopped.lines],
            ack_status=stopped.ack_status,
            reject_reason=stopped.reject_reason,
        )

    def close(self) -> None:
        self.serial.close()


@dataclass
class StewardConfig:
    node_id: str = "rhizome_01"
    state_dir: Path = field(default_factory=default_state_dir)
    facade_data_dir: Path | None = None
    sync_facade_state_dir: Path = Path("/tmp/sprout_rhizome_sync_facade/rhizome_01")
    decision_interval_s: int = 900
    heartbeat_interval_s: int = 2
    cooldown_s: int = 7200
    requested_water_seconds: int = 8
    soil_dry_below_pct: float = 35.0
    soil_wet_above_pct: float = 55.0
    soil_dry_below_raw: int | None = None
    soil_wet_above_raw: int | None = None
    soil_raw_polarity: str = "low_is_dry"
    soil_wet_below_raw: int | None = None
    soil_dry_above_raw: int | None = None
    tank_minimum_pct: float = FIRMWARE_TANK_MINIMUM_PCT
    max_water_seconds: int = FIRMWARE_MAX_WATER_SECONDS_MVP
    max_autonomous_waters_per_day: int = 2
    allow_missing_tank_sensor: bool = False
    allow_missing_flow_sensor: bool = True
    execute_water: bool = False
    shadow_skeptic_enabled: bool = True
    gemma_rationale_url: str | None = None
    gemma_model: str = "gemma4:e2b"
    retention_days: int = DEFAULT_RETENTION_DAYS
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES


class BoundedJsonlStore:
    def __init__(self, root: Path, *, retention_days: int, max_total_bytes: int) -> None:
        self.root = root
        self.retention_days = retention_days
        self.max_total_bytes = max_total_bytes
        self.root.mkdir(parents=True, exist_ok=True)

    def append(self, stream: str, payload: dict[str, Any], now: datetime | None = None) -> Path:
        now = now or utc_now()
        path = self.root / stream / f"{now.date().isoformat()}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        self.enforce_limits(now)
        return path

    def write_json(self, relative_path: str, payload: dict[str, Any]) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        tmp_path.replace(path)
        return path

    def load_json(self, relative_path: str) -> dict[str, Any] | None:
        path = self.root / relative_path
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def iter_jsonl(self, stream: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for path in sorted((self.root / stream).glob("*.jsonl")):
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
        return records

    def enforce_limits(self, now: datetime | None = None) -> None:
        now = now or utc_now()
        cutoff = now - timedelta(days=self.retention_days)
        jsonl_files = sorted(self.root.glob("*/*.jsonl"), key=lambda p: p.stat().st_mtime)
        for path in list(jsonl_files):
            try:
                if datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) < cutoff:
                    path.unlink(missing_ok=True)
            except FileNotFoundError:
                continue
        jsonl_files = sorted(self.root.glob("*/*.jsonl"), key=lambda p: p.stat().st_mtime)
        total = sum(path.stat().st_size for path in jsonl_files)
        for path in jsonl_files:
            if total <= self.max_total_bytes:
                break
            size = path.stat().st_size
            path.unlink(missing_ok=True)
            total -= size


def load_active_policy(config: StewardConfig) -> dict[str, Any] | None:
    path = config.sync_facade_state_dir / "active_policy.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        record = json.load(handle)
    policy = record.get("policy", record)
    valid_until = parse_zulu(policy.get("valid_until"))
    if valid_until is not None and valid_until <= utc_now():
        return None
    return policy


@dataclass
class Decision:
    action: str
    action_params: dict[str, Any]
    mode: str
    rationale_short: str
    rationale_full: str
    confidence: float
    blocked_reason: str | None = None
    policy_refs: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)


def _policy_threshold(policy: dict[str, Any] | None, key: str) -> float | None:
    if not policy:
        return None
    thresholds = policy.get("rules", {}).get("soil_moisture_thresholds", {})
    parcel_a = thresholds.get("parcel_a") or thresholds.get("single_zone") or {}
    return _float_or_none(parcel_a.get(key))


def _soil_metric(
    telemetry: Telemetry,
    config: StewardConfig,
) -> tuple[str, float | None, float | None, float | None, list[str]]:
    soil_pct = telemetry.soil_a_pct()
    if soil_pct is not None:
        return "pct", soil_pct, config.soil_dry_below_pct, config.soil_wet_above_pct, ["config.soil_pct_thresholds"]
    if telemetry.soil_a_raw is not None and config.soil_raw_polarity == "low_is_wet" and config.soil_wet_below_raw is not None:
        return (
            "raw_low_is_wet",
            float(telemetry.soil_a_raw),
            float(config.soil_dry_above_raw) if config.soil_dry_above_raw is not None else None,
            float(config.soil_wet_below_raw),
            ["config.soil_raw_thresholds", "config.soil_raw_polarity"],
        )
    if telemetry.soil_a_raw is not None and config.soil_dry_below_raw is not None and config.soil_wet_above_raw is not None:
        return (
            "raw_low_is_dry",
            float(telemetry.soil_a_raw),
            float(config.soil_dry_below_raw),
            float(config.soil_wet_above_raw),
            ["config.soil_raw_thresholds", "config.soil_raw_polarity"],
        )
    return "unknown", None, None, None, []


def _has_full_raw_soil_calibration(config: StewardConfig) -> bool:
    if config.soil_raw_polarity == "low_is_wet":
        return config.soil_wet_below_raw is not None and config.soil_dry_above_raw is not None
    return config.soil_dry_below_raw is not None and config.soil_wet_above_raw is not None


def _soil_unit(metric_kind: str) -> str:
    return "%" if metric_kind == "pct" else "raw"


def _soil_is_wet_enough(metric_kind: str, soil_value: float, wet_threshold: float | None) -> bool:
    if wet_threshold is None:
        return False
    if metric_kind == "raw_low_is_wet":
        return soil_value <= wet_threshold
    return soil_value >= wet_threshold


def _soil_is_dry(metric_kind: str, soil_value: float, dry_threshold: float | None) -> bool:
    if dry_threshold is None:
        return False
    if metric_kind == "raw_low_is_wet":
        return soil_value >= dry_threshold
    return soil_value <= dry_threshold


def _wet_threshold_text(metric_kind: str, wet_threshold: float | None) -> str:
    if wet_threshold is None:
        return "umbral de suelo suficiente"
    unit = _soil_unit(metric_kind)
    relation = "igual o por debajo de" if metric_kind == "raw_low_is_wet" else "igual o por encima de"
    return f"{relation} {wet_threshold:.0f}{unit}"


def _dry_threshold_text(metric_kind: str, dry_threshold: float | None) -> str:
    if dry_threshold is None:
        return "umbral de suelo seco"
    unit = _soil_unit(metric_kind)
    relation = "por encima de" if metric_kind == "raw_low_is_wet" else "por debajo de"
    return f"{relation} {dry_threshold:.0f}{unit}"


def _todays_water_count(store: BoundedJsonlStore, now: datetime) -> int:
    today = now.date().isoformat()
    count = 0
    for receipt in store.iter_jsonl("decision_receipts"):
        if not str(receipt.get("created_at", "")).startswith(today):
            continue
        if receipt.get("action") == "WATER_A" and receipt.get("executed") is True:
            count += 1
    return count


def _last_executed_water_at(store: BoundedJsonlStore) -> datetime | None:
    latest: datetime | None = None
    for receipt in store.iter_jsonl("decision_receipts"):
        if receipt.get("action") != "WATER_A" or receipt.get("executed") is not True:
            continue
        created_at = parse_zulu(receipt.get("created_at"))
        if created_at and (latest is None or created_at > latest):
            latest = created_at
    return latest


class DeterministicDecisionEngine:
    def decide(self, telemetry: Telemetry, config: StewardConfig, store: BoundedJsonlStore, policy: dict[str, Any] | None, now: datetime | None = None) -> Decision:
        now = now or utc_now()
        active_policy_id = policy.get("policy_id") if policy else "local_default_policy"
        tank = telemetry.tank_level_pct
        if tank is not None and tank < config.tank_minimum_pct:
            return Decision(
                action="ALERT",
                action_params={"alert_id": f"alert_{config.node_id}_{now.strftime('%Y%m%dT%H%M%SZ')}"},
                mode="safety_block",
                rationale_short=f"Deposito al {tank:.0f}%, por debajo del minimo {config.tank_minimum_pct:.0f}%. No se riega.",
                rationale_full="Gate determinista: deposito bajo tiene prioridad sobre cualquier politica o propuesta del modelo.",
                confidence=0.99,
                blocked_reason="TANK_LOW",
                policy_refs=[str(active_policy_id), "firmware.tank_minimum_pct"],
            )
        if tank is None and not config.allow_missing_tank_sensor:
            return Decision(
                action="DEFER",
                action_params={"defer_until": zulu(now + timedelta(seconds=config.decision_interval_s)), "reason": "TANK_SENSOR_UNAVAILABLE"},
                mode="safety_block",
                rationale_short="No hay lectura de deposito. Se aplaza hasta sensor o verificacion manual explicita.",
                rationale_full="Gate determinista: por defecto Rhizome no riega si falta el sensor de deposito previsto por la arquitectura.",
                confidence=0.90,
                blocked_reason="TANK_SENSOR_UNAVAILABLE",
                policy_refs=[str(active_policy_id), "config.allow_missing_tank_sensor"],
                contradictions=["tank_level_unavailable"],
            )

        if telemetry.host_link not in {"FRESH", "UNKNOWN"}:
            return Decision(
                action="BLOCK",
                action_params={"blocked_action": "WATER_A", "reason": "JETSON_HEARTBEAT_NOT_FRESH"},
                mode="safety_block",
                rationale_short="El enlace con ESP32 no esta fresco. No se riega.",
                rationale_full="Gate determinista: Rhizome exige host_link fresco antes de proponer riego.",
                confidence=0.95,
                blocked_reason="JETSON_HEARTBEAT_NOT_FRESH",
                policy_refs=[str(active_policy_id), "firmware.host_heartbeat_timeout_ms"],
            )

        metric_kind, soil_value, dry_below, wet_above, refs = _soil_metric(telemetry, config)
        if soil_value is None:
            return Decision(
                action="DEFER",
                action_params={"defer_until": zulu(now + timedelta(seconds=config.decision_interval_s)), "reason": "SOIL_UNKNOWN"},
                mode="fast_path",
                rationale_short="No hay lectura calibrada de humedad de suelo. Se aplaza.",
                rationale_full="Rhizome no riega si no puede interpretar la humedad de suelo como porcentaje o raw calibrado.",
                confidence=0.80,
                blocked_reason="SOIL_UNKNOWN",
                policy_refs=[str(active_policy_id)],
            )

        last_water_at = _last_executed_water_at(store)
        if last_water_at and (now - last_water_at).total_seconds() < config.cooldown_s:
            remaining = int(config.cooldown_s - (now - last_water_at).total_seconds())
            return Decision(
                action="DEFER",
                action_params={"defer_until": zulu(now + timedelta(seconds=remaining)), "reason": "COOLDOWN_NOT_MET"},
                mode="fast_path",
                rationale_short=f"Cooldown activo tras el ultimo riego. Reintento en {remaining}s.",
                rationale_full="Gate determinista: el cooldown evita riegos repetidos ante ruido de sensor.",
                confidence=0.92,
                blocked_reason="COOLDOWN_NOT_MET",
                policy_refs=[str(active_policy_id), "config.cooldown_s"],
            )

        daily_count = _todays_water_count(store, now)
        if daily_count >= config.max_autonomous_waters_per_day:
            return Decision(
                action="DEFER",
                action_params={"defer_until": zulu(now + timedelta(days=1)), "reason": "DAILY_AUTONOMY_BUDGET_USED"},
                mode="fast_path",
                rationale_short="Presupuesto diario de riegos autonomos agotado. Se aplaza.",
                rationale_full="Gate determinista: limite de eventos autonomos por dia para piloto de maceta.",
                confidence=0.90,
                blocked_reason="DAILY_AUTONOMY_BUDGET_USED",
                policy_refs=[str(active_policy_id), "config.max_autonomous_waters_per_day"],
            )

        if _soil_is_wet_enough(metric_kind, soil_value, wet_above):
            unit = _soil_unit(metric_kind)
            return Decision(
                action="SKIP",
                action_params={"next_check_in_s": config.decision_interval_s},
                mode="fast_path",
                rationale_short=f"Humedad A {soil_value:.0f}{unit}; suficiente. No se riega.",
                rationale_full=f"Gate determinista: la lectura esta {_wet_threshold_text(metric_kind, wet_above)}.",
                confidence=0.88,
                policy_refs=[str(active_policy_id), *refs],
            )

        if _soil_is_dry(metric_kind, soil_value, dry_below):
            if telemetry.flow_pulses is None and not config.allow_missing_flow_sensor:
                return Decision(
                    action="DEFER",
                    action_params={"defer_until": zulu(now + timedelta(seconds=config.decision_interval_s)), "reason": "FLOW_SENSOR_UNAVAILABLE"},
                    mode="safety_block",
                    rationale_short="No hay caudalimetro disponible para verificar riego. Se aplaza.",
                    rationale_full="Gate determinista: en modo estricto, Rhizome no ejecuta WATER sin sensor de caudal previsto por la arquitectura.",
                    confidence=0.88,
                    blocked_reason="FLOW_SENSOR_UNAVAILABLE",
                    policy_refs=[str(active_policy_id), "config.allow_missing_flow_sensor"],
                    contradictions=["flow_sensor_unavailable"],
                )
            duration_s = max(1, min(config.requested_water_seconds, config.max_water_seconds, FIRMWARE_MAX_WATER_SECONDS_MVP))
            expected_liters = round(duration_s * 0.05, 3)
            unit = _soil_unit(metric_kind)
            contradictions: list[str] = []
            policy_refs = [str(active_policy_id), *refs, "firmware.max_water_seconds_mvp"]
            confidence = 0.84
            rationale_full = "Gate determinista: suelo seco, deposito aceptable, cooldown cumplido y duracion dentro del limite firmware MVP."
            if tank is None:
                contradictions.append("tank_level_unavailable")
                policy_refs.append("config.allow_missing_tank_sensor")
                confidence = min(confidence, 0.72)
                rationale_full = "Gate determinista: suelo seco y cooldown cumplido. En perfil minimo, deposito no sensorizado se permite solo por flag explicito."
            if telemetry.flow_pulses is None:
                contradictions.append("flow_sensor_unavailable")
                policy_refs.append("config.allow_missing_flow_sensor")
                confidence = min(confidence, 0.74)
            return Decision(
                action="WATER_A",
                action_params={"duration_s": duration_s, "expected_liters": expected_liters},
                mode="fast_path",
                rationale_short=f"Humedad A {soil_value:.0f}{unit}, {_dry_threshold_text(metric_kind, dry_below)}. Riego corto dentro de sobre seguro.",
                rationale_full=rationale_full,
                confidence=confidence,
                policy_refs=policy_refs,
                contradictions=contradictions,
            )

        return Decision(
            action="DEFER",
            action_params={"defer_until": zulu(now + timedelta(seconds=config.decision_interval_s)), "reason": "AMBIGUOUS_MOISTURE_BAND"},
            mode="fast_path",
            rationale_short="Humedad en banda intermedia. Se aplaza para evitar riego innecesario.",
            rationale_full="Gate determinista: la lectura no es claramente seca ni claramente suficiente.",
            confidence=0.76,
            blocked_reason="AMBIGUOUS_MOISTURE_BAND",
            policy_refs=[str(active_policy_id), *refs],
        )


class GemmaRationaleClient:
    def __init__(self, adapter_url: str, model: str) -> None:
        self.adapter_url = adapter_url.rstrip("/")
        self.model = model

    def refine(self, decision: Decision, telemetry: Telemetry) -> tuple[str | None, str | None]:
        prompt = {
            "task": "rhizome_rationale",
            "rules": [
                "Return only JSON.",
                "Do not change the action.",
                "Do not add facts absent from input.",
                "No chain-of-thought.",
                "Keep rationale_short <= 180 chars.",
            ],
            "decision": asdict(decision),
            "telemetry": asdict(telemetry),
            "output_schema": {"rationale_short": "string", "risk_note": "string"},
        }
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are Gemma 4 E2B inside Rhizome. Explain decisions briefly and contractually. You cannot authorize water."},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
            "stream": False,
            "think": False,
            "options": {"temperature": 0.1, "num_ctx": 2048, "num_predict": 160},
        }
        request = urllib.request.Request(
            f"{self.adapter_url}/api/chat",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                response_body = json.loads(response.read().decode("utf-8"))
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            return None, f"gemma_error:{exc.__class__.__name__}"
        content = response_body.get("message", {}).get("content", "")
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return None, "gemma_invalid_json"
        rationale = parsed.get("rationale_short")
        if isinstance(rationale, str) and 0 < len(rationale) <= 180:
            return rationale, None
        return None, "gemma_bad_rationale"


class ShadowSkeptic:
    def review(self, decision: Decision, telemetry: Telemetry, config: StewardConfig) -> dict[str, Any]:
        concerns: list[str] = []
        if decision.action == "WATER_A":
            duration = decision.action_params.get("duration_s")
            if not isinstance(duration, int) or duration <= 0 or duration > FIRMWARE_MAX_WATER_SECONDS_MVP:
                concerns.append("duration_outside_firmware_limit")
            if telemetry.tank_level_pct is None:
                concerns.append("tank_unknown")
            elif telemetry.tank_level_pct < config.tank_minimum_pct:
                concerns.append("tank_below_minimum")
            if telemetry.soil_a_pct() is None and not _has_full_raw_soil_calibration(config):
                concerns.append("soil_not_calibrated")
        return {
            "shadow_id": f"shadow_{utc_now().strftime('%Y%m%dT%H%M%SZ')}",
            "reviewed_action": decision.action,
            "would_object": bool(concerns),
            "concerns": concerns,
            "recommended_action": "DEFER" if concerns else decision.action,
            "affects_decision": False,
            "mode": "deterministic_shadow_skeptic_v0",
        }


def build_snapshot(config: StewardConfig, telemetry: Telemetry, policy: dict[str, Any] | None, now: datetime) -> dict[str, Any]:
    soil_a_pct = telemetry.soil_a_pct()
    soil_b_pct = float(telemetry.soil_b_raw) if telemetry.soil_b_raw is not None and 0 <= telemetry.soil_b_raw <= 100 else soil_a_pct
    pending_contradictions: list[str] = []
    if soil_a_pct is None:
        pending_contradictions.append("soil_a_unavailable_or_uncalibrated")
    if soil_b_pct is None:
        pending_contradictions.append("soil_b_unavailable_or_uncalibrated")
    if telemetry.tank_level_pct is None:
        pending_contradictions.append("tank_level_unavailable")
    if telemetry.flow_pulses is None:
        pending_contradictions.append("flow_sensor_unavailable")
    sensors = {
        "soil_moisture_a_pct": soil_a_pct if soil_a_pct is not None else 0.0,
        "soil_moisture_b_pct": soil_b_pct if soil_b_pct is not None else (soil_a_pct if soil_a_pct is not None else 0.0),
        "tank_level_pct": telemetry.tank_level_pct if telemetry.tank_level_pct is not None else 0.0,
        "flow_rate_lpm": 0.0,
        "last_reading_at": telemetry.collected_at,
    }
    return {
        "schema_version": "1.0",
        "created_at": zulu(now),
        "origin_node_id": config.node_id,
        "signature": None,
        "snapshot_id": f"snap_{config.node_id}_{now.strftime('%Y%m%dT%H%M%SZ')}",
        "mode": "normal",
        "active_policy_id": (policy or {}).get("policy_id", "local_default_policy"),
        "active_policy_expires_at": (policy or {}).get("valid_until", zulu(now + timedelta(hours=12))),
        "sensors": sensors,
        "vision": {
            "last_capture_at": None,
            "parcel_a_status": None,
            "parcel_b_status": None,
            "visual_notes": "Sensor value unavailable; snapshot keeps schema-safe 0 and decision gate must defer." if pending_contradictions else None,
        },
        "health": {"cpu_temp_c": 0.0, "cpu_load_pct": 0.0, "ram_used_gb": 0.0, "ram_total_gb": 1.0, "esp32_heartbeat_ok": telemetry.host_link in {"FRESH", "UNKNOWN"}, "last_esp32_ack_at": telemetry.collected_at},
        "last_decision_id": None,
        "pending_contradictions": pending_contradictions,
    }


class RhizomeSteward:
    def __init__(self, config: StewardConfig, client: ESP32Client) -> None:
        self.config = config
        self.client = client
        self.store = BoundedJsonlStore(config.state_dir, retention_days=config.retention_days, max_total_bytes=config.max_total_bytes)
        self.facade_data_dir = config.facade_data_dir or (config.state_dir / "facade_data")
        self.engine = DeterministicDecisionEngine()
        self.shadow = ShadowSkeptic()
        self.gemma = GemmaRationaleClient(config.gemma_rationale_url, config.gemma_model) if config.gemma_rationale_url else None

    def run_once(self) -> dict[str, Any]:
        now = utc_now()
        heartbeat = self.client.heartbeat()
        telemetry = self.client.telemetry()
        policy = load_active_policy(self.config)
        snapshot = build_snapshot(self.config, telemetry, policy, now)
        decision = self.engine.decide(telemetry, self.config, self.store, policy, now)
        gemma_error = None
        if self.gemma is not None:
            refined, gemma_error = self.gemma.refine(decision, telemetry)
            if refined:
                decision.rationale_short = refined
                decision.mode = f"{decision.mode}+gemma_rationale"

        execution: ESP32CommandResult | None = None
        executed = False
        blocked_reason = decision.blocked_reason
        if decision.action == "WATER_A":
            if self.config.execute_water:
                self.client.heartbeat()
                execution = self.client.water("A", int(decision.action_params["duration_s"]))
                executed = execution.ok
                blocked_reason = None if execution.ok else execution.reject_reason or "ESP32_REJECTED"
            else:
                blocked_reason = "OBSERVE_MODE_EXECUTE_WATER_FALSE"

        receipt = self._receipt(now, snapshot, decision, executed, blocked_reason, execution, policy, gemma_error)
        shadow_record = self.shadow.review(decision, telemetry, self.config) if self.config.shadow_skeptic_enabled else None
        self.store.append("telemetry_samples", asdict(telemetry), now)
        self.store.write_json("current_snapshot.json", snapshot)
        self.store.append("decision_receipts", receipt, now)
        self.store.write_json("last_decision_receipt.json", receipt)
        self._write_facade_data(snapshot, receipt)
        if shadow_record:
            shadow_record["decision_id"] = receipt["decision_id"]
            shadow_record["created_at"] = receipt["created_at"]
            self.store.append("shadow_skeptic", shadow_record, now)
        return {
            "status": "ok",
            "node_id": self.config.node_id,
            "snapshot_id": snapshot["snapshot_id"],
            "decision_id": receipt["decision_id"],
            "action": receipt["action"],
            "executed": receipt["executed"],
            "blocked_reason": receipt["blocked_reason"],
            "rationale_short": receipt["rationale_short"],
            "heartbeat_ok": heartbeat.ok,
            "shadow_skeptic": shadow_record,
            "state_dir": str(self.config.state_dir),
            "facade_data_dir": str(self.facade_data_dir),
        }

    def _write_facade_data(self, snapshot: dict[str, Any], receipt: dict[str, Any]) -> None:
        self.facade_data_dir.mkdir(parents=True, exist_ok=True)
        self._write_json_to(self.facade_data_dir / "rhizome_snapshot.json", snapshot)
        self._write_json_to(self.facade_data_dir / "decision_receipt.json", receipt)
        if (
            receipt["action"] in {"ALERT", "BLOCK"} or receipt["executed"] is not True
        ):
            self._write_json_to(self.facade_data_dir / "decision_receipt_blocked.json", receipt)

    @staticmethod
    def _write_json_to(path: Path, payload: dict[str, Any]) -> None:
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        tmp_path.replace(path)

    def _receipt(self, now: datetime, snapshot: dict[str, Any], decision: Decision, executed: bool, blocked_reason: str | None, execution: ESP32CommandResult | None, policy: dict[str, Any] | None, gemma_error: str | None) -> dict[str, Any]:
        decision_id = f"rec_{self.config.node_id}_{now.strftime('%Y%m%dT%H%M%SZ')}"
        action_params = dict(decision.action_params)
        if decision.action == "WATER_A" and not executed and blocked_reason:
            # The shared schema permits WATER_* with executed=false when there is a blocked reason.
            pass
        if not executed and not blocked_reason:
            if decision.action == "SKIP":
                blocked_reason = "NO_ACTION_NEEDED"
            elif decision.action == "DEFER":
                blocked_reason = action_params.get("reason") or "DEFERRED"
            elif decision.action == "ALERT":
                blocked_reason = "ALERT_NOT_EXECUTED"
            elif decision.action == "BLOCK":
                blocked_reason = action_params.get("reason") or "BLOCKED"
            else:
                blocked_reason = "NOT_EXECUTED"
        receipt = {
            "schema_version": "1.0",
            "created_at": zulu(now),
            "origin_node_id": self.config.node_id,
            "signature": None,
            "decision_id": decision_id,
            "snapshot_id": snapshot["snapshot_id"],
            "active_policy_id": (policy or {}).get("policy_id", "local_default_policy"),
            "action": decision.action,
            "action_params": action_params,
            "rationale_short": decision.rationale_short[:180],
            "rationale_full": decision.rationale_full,
            "policy_refs": decision.policy_refs or ["local_default_policy"],
            "contradictions": decision.contradictions,
            "confidence": decision.confidence,
            "executed": executed,
            "execution_details": None,
            "blocked_reason": None if executed else blocked_reason,
            "backend_used": "deterministic+gemma_rationale" if self.gemma and not gemma_error else "deterministic",
            "gemma_error": gemma_error,
            "mode": decision.mode,
        }
        if executed and execution is not None:
            duration = float(action_params.get("duration_s", 0))
            flow_sensor_present = "flow_sensor_unavailable" not in receipt["contradictions"]
            receipt["execution_details"] = {
                "sent_to_esp32_at": execution.sent_at,
                "esp32_ack_at": execution.received_at,
                "esp32_ack_status": execution.ack_status,
                "actual_duration_s": duration,
                "flow_observed_lpm": 0.0,
                "estimated_liters_actual": action_params.get("expected_liters", 0.0),
                "flow_sensor_present": flow_sensor_present,
                "esp32_lines": execution.lines,
            }
        return receipt

    def run_loop(self) -> None:
        while True:
            result = self.run_once()
            print(json.dumps(result, ensure_ascii=False, separators=(",", ":")), flush=True)
            self._sleep_with_heartbeat(self.config.decision_interval_s)

    def _sleep_with_heartbeat(self, seconds: int) -> None:
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            self.client.heartbeat()
            time.sleep(min(self.config.heartbeat_interval_s, max(0.0, deadline - time.monotonic())))

    def close(self) -> None:
        self.client.close()


def build_client(args: argparse.Namespace) -> ESP32Client:
    if args.esp32 == "fake":
        telemetry = Telemetry(
            collected_at=zulu(utc_now()),
            soil_a_raw=args.fake_soil_a,
            soil_b_raw=args.fake_soil_b,
            tank_level_pct=args.fake_tank_pct,
            flow_pulses=0,
            host_link="FRESH",
            host_age_ms=0,
        )
        return FakeESP32Client(telemetry=telemetry, reject_water_reason=args.fake_reject_water)
    if not args.serial_port:
        raise SystemExit("--serial-port es obligatorio con --esp32 serial")
    return SerialESP32Client(args.serial_port, baud=args.baud, water_command_mode=args.serial_water_command_mode)


def build_config(args: argparse.Namespace) -> StewardConfig:
    return StewardConfig(
        node_id=args.node_id,
        state_dir=Path(args.state_dir).expanduser(),
        facade_data_dir=Path(args.facade_data_dir).expanduser() if args.facade_data_dir else None,
        sync_facade_state_dir=Path(args.sync_facade_state_dir).expanduser(),
        decision_interval_s=args.decision_interval_s,
        heartbeat_interval_s=args.heartbeat_interval_s,
        cooldown_s=args.cooldown_s,
        requested_water_seconds=args.water_seconds,
        soil_dry_below_pct=args.soil_dry_below_pct,
        soil_wet_above_pct=args.soil_wet_above_pct,
        soil_dry_below_raw=args.soil_dry_below_raw,
        soil_wet_above_raw=args.soil_wet_above_raw,
        soil_raw_polarity=args.soil_raw_polarity,
        soil_wet_below_raw=args.soil_wet_below_raw,
        soil_dry_above_raw=args.soil_dry_above_raw,
        tank_minimum_pct=args.tank_minimum_pct,
        max_water_seconds=args.max_water_seconds,
        max_autonomous_waters_per_day=args.max_autonomous_waters_per_day,
        allow_missing_tank_sensor=args.allow_missing_tank_sensor,
        allow_missing_flow_sensor=not args.require_flow_sensor_for_water,
        execute_water=args.execute_water,
        shadow_skeptic_enabled=not args.disable_shadow_skeptic,
        gemma_rationale_url=args.gemma_rationale_url,
        gemma_model=args.gemma_model,
        retention_days=args.retention_days,
        max_total_bytes=args.max_total_bytes,
    )


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--node-id", default="rhizome_01")
    parser.add_argument("--state-dir", default=str(default_state_dir()))
    parser.add_argument("--facade-data-dir", help="Directorio JSON compatible con rhizome_sync_facade. Por defecto: <state-dir>/facade_data")
    parser.add_argument("--sync-facade-state-dir", default="/tmp/sprout_rhizome_sync_facade/rhizome_01")
    parser.add_argument("--esp32", choices=["fake", "serial"], default="fake")
    parser.add_argument("--serial-port")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--serial-water-command-mode", choices=["water-duration", "pump-toggle"], default="water-duration")
    parser.add_argument("--execute-water", action="store_true", help="Permite enviar WATER al ESP32. Sin esto, WATER queda bloqueado como observe mode.")
    parser.add_argument("--decision-interval-s", type=int, default=900)
    parser.add_argument("--heartbeat-interval-s", type=int, default=2)
    parser.add_argument("--cooldown-s", type=int, default=7200)
    parser.add_argument("--water-seconds", type=int, default=8)
    parser.add_argument("--soil-dry-below-pct", type=float, default=35.0)
    parser.add_argument("--soil-wet-above-pct", type=float, default=55.0)
    parser.add_argument("--soil-dry-below-raw", type=int)
    parser.add_argument("--soil-wet-above-raw", type=int)
    parser.add_argument("--soil-raw-polarity", choices=["low_is_dry", "low_is_wet"], default="low_is_dry")
    parser.add_argument("--soil-wet-below-raw", type=int)
    parser.add_argument("--soil-dry-above-raw", type=int)
    parser.add_argument("--tank-minimum-pct", type=float, default=FIRMWARE_TANK_MINIMUM_PCT)
    parser.add_argument("--max-water-seconds", type=int, default=FIRMWARE_MAX_WATER_SECONDS_MVP)
    parser.add_argument("--max-autonomous-waters-per-day", type=int, default=2)
    parser.add_argument("--allow-missing-tank-sensor", action="store_true", help="Perfil minimo: permite WATER con deposito no sensorizado, registrando tank_level_unavailable.")
    parser.add_argument("--require-flow-sensor-for-water", action="store_true", help="Bloquea/promociona futuro modo estricto cuando caudalimetro exista.")
    parser.add_argument("--retention-days", type=int, default=DEFAULT_RETENTION_DAYS)
    parser.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES)
    parser.add_argument("--disable-shadow-skeptic", action="store_true")
    parser.add_argument("--gemma-rationale-url", help="Adapter /api/chat base URL, e.g. http://127.0.0.1:12000")
    parser.add_argument("--gemma-model", default="gemma4:e2b")
    parser.add_argument("--fake-soil-a", type=int, default=32)
    parser.add_argument("--fake-soil-b", type=int, default=40)
    parser.add_argument("--fake-tank-pct", type=float, default=70.0)
    parser.add_argument("--fake-reject-water")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rhizome Steward v0 autonomous loop.")
    sub = parser.add_subparsers(dest="command", required=True)
    once = sub.add_parser("run-once", help="Ejecuta un ciclo medir -> decidir -> receipt.")
    add_common_args(once)
    loop = sub.add_parser("run-loop", help="Ejecuta el ciclo en bucle con heartbeat entre decisiones.")
    add_common_args(loop)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = build_config(args)
    client = build_client(args)
    steward = RhizomeSteward(config, client)
    try:
        if args.command == "run-once":
            print(json.dumps(steward.run_once(), ensure_ascii=False, separators=(",", ":")))
            return 0
        steward.run_loop()
    except KeyboardInterrupt:
        return 130
    finally:
        steward.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
