"""Smoke A+B automatizado del Meristem-node con LLM real.

Diseñado para que Bea lo lance con Claude cerrado y vuelva a ver los
resultados. Hace todo end-to-end sin intervención:

1. Verifica prerequisitos (binario llama-server, modelo, deps Python)
2. Limpia procesos anteriores si los hay (puertos 8080, 11435, 13000)
3. Arranca stack: llama-server + adapter + meristem-node
4. Hace 3 POSTs concretos:
   - Seed rhizome_02 estable (para que compare_targets tenga 2 targets)
   - Bundle M7 (debería disparar compare_targets si el modelo lo decide)
   - POST /chat (debería responder con citas o pedir tools)
5. Lee llm_metrics de cada decisión
6. Apaga stack limpio
7. Imprime resumen + guarda results_d26_smoke.json

USO:
    cd code/meristem_node
    python scripts/smoke_a_b_auto.py --model e4b
    # o si OOM: python scripts/smoke_a_b_auto.py --model e2b

    # Con log file:
    python scripts/smoke_a_b_auto.py --model e4b > smoke_d26.log 2>&1

ARGS:
    --model {e4b,e2b}    Modelo a usar. Default e4b.
                         E4B necesita ~10 GB RAM disponible.
                         E2B funciona con ~3-4 GB pero NO ejercita
                         tool calling correctamente.
    --num-predict N      Override num_predict. Default: 256 para e4b,
                         1024 para e2b (modelo-dependiente, ver
                         hallazgo dia 26).
    --output FILE        Path JSON resultado. Default: results_d26_smoke.json
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

try:
    import httpx
except ImportError:
    print("ERROR: instala httpx (pip install httpx)", file=sys.stderr)
    sys.exit(2)


# Paths relativos a la raíz del repo
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
LLAMA_SERVER_BIN = REPO_ROOT / "tools" / "llama.cpp" / "llama-server.exe"
MODELS_DIR = REPO_ROOT / "models"
ADAPTER_DIR = REPO_ROOT / "code" / "meristem_inference_adapter"
MERISTEM_DIR = REPO_ROOT / "code" / "meristem_node"
EXAMPLES_DIR = MERISTEM_DIR / "examples"
DB_PATH = MERISTEM_DIR / "meristem_node.db"

# Puertos del stack
PORT_LLAMA = 8080
PORT_ADAPTER = 11435  # NO 11434 para no chocar con Ollama del usuario
PORT_MERISTEM = 13000

# Timeouts
LLAMA_READY_TIMEOUT_S = 120
ADAPTER_READY_TIMEOUT_S = 30
MERISTEM_READY_TIMEOUT_S = 30
VISIT_TIMEOUT_S = 600


def log(msg: str, level: str = "INFO") -> None:
    """Log con timestamp + nivel."""
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)


def kill_port(port: int) -> None:
    """Mata cualquier proceso escuchando en el puerto. Best-effort."""
    try:
        out = subprocess.run(
            ["netstat", "-ano"], capture_output=True, text=True, timeout=10,
        ).stdout
        pids = set()
        for line in out.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                if parts:
                    pids.add(parts[-1])
        for pid in pids:
            log(f"Matando PID {pid} en puerto {port}", "WARN")
            subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True, timeout=5)
    except Exception as e:
        log(f"kill_port({port}) excepción: {e}", "WARN")


def wait_for_url(url: str, timeout_s: int, name: str) -> bool:
    """Polling al URL hasta que responda HTTP <500 o timeout.

    Aceptamos cualquier respuesta no-5xx (incluyendo 404) porque
    indica que el servidor está vivo. Antes esperabamos 200 estricto,
    pero el adapter Ollama-compatible devuelve 404 a `/` (sus rutas
    son `/api/chat`, `/api/generate`, no raíz).
    """
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            r = httpx.get(url, timeout=2.0)
            if r.status_code < 500:
                log(f"{name} READY ({url}) [HTTP {r.status_code}]")
                return True
        except httpx.HTTPError:
            pass
        time.sleep(2)
    log(f"{name} timeout {timeout_s}s ({url})", "ERROR")
    return False


@contextmanager
def background_process(
    cmd: list[str], cwd: Path, env: dict, name: str, log_path: Path,
):
    """Levanta un proceso en background y lo cierra al salir del context."""
    log(f"Lanzando {name}: {' '.join(cmd[:3])}...")
    log_file = open(log_path, "w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        env={**os.environ, **env},
        stdout=log_file,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    log(f"{name} arrancando, PID {proc.pid}, log en {log_path.name}")
    try:
        yield proc
    finally:
        log(f"Cerrando {name} (PID {proc.pid})")
        try:
            if sys.platform == "win32":
                proc.send_signal(signal.CTRL_BREAK_EVENT)
                proc.wait(timeout=5)
            else:
                proc.terminate()
                proc.wait(timeout=5)
        except (subprocess.TimeoutExpired, Exception):
            try:
                proc.kill()
            except Exception:
                pass
        try:
            log_file.close()
        except Exception:
            pass


def post_visit(bundle: dict, num_predict: int) -> dict[str, Any]:
    """POST /visit con header de num_predict. Devuelve metrics + response."""
    t0 = time.perf_counter()
    try:
        r = httpx.post(
            f"http://localhost:{PORT_MERISTEM}/visit",
            json=bundle,
            headers={"X-Meristem-Num-Predict": str(num_predict)},
            timeout=VISIT_TIMEOUT_S,
        )
        latency_ms = int((time.perf_counter() - t0) * 1000)
        body = r.json()
    except Exception as e:
        return {
            "latency_ms": int((time.perf_counter() - t0) * 1000),
            "error": f"{type(e).__name__}: {e}",
        }
    # Lee llm_metrics de la BBDD
    metrics = read_last_decision_metrics()
    return {
        "latency_ms": latency_ms,
        "http_status": r.status_code,
        "envelope_status": body.get("status"),
        "reason_code": body.get("reason_code"),
        "rationale_for_operator": (
            (body.get("payload") or {}).get("rationale_for_operator", "")
        ),
        "llm_metrics": metrics,
    }


def post_chat(message: str, num_predict: int) -> dict[str, Any]:
    """POST /chat. Devuelve answer + metrics."""
    t0 = time.perf_counter()
    try:
        r = httpx.post(
            f"http://localhost:{PORT_MERISTEM}/chat",
            json={"operator_id": "bea_smoke_d26", "message_es": message},
            headers={"X-Meristem-Num-Predict": str(num_predict)},
            timeout=VISIT_TIMEOUT_S,
        )
        latency_ms = int((time.perf_counter() - t0) * 1000)
        body = r.json()
        return {
            "latency_ms": latency_ms,
            "http_status": r.status_code,
            "conversation_id": body.get("conversation_id"),
            "answer_es": body.get("answer_es"),
            "evidence_refs": body.get("evidence_refs"),
            "llm_metrics": body.get("llm_metrics"),
        }
    except Exception as e:
        return {
            "latency_ms": int((time.perf_counter() - t0) * 1000),
            "error": f"{type(e).__name__}: {e}",
        }


def read_last_decision_metrics() -> dict[str, Any] | None:
    """Lee llm_metrics de la última decisión persistida."""
    if not DB_PATH.exists():
        return None
    try:
        con = sqlite3.connect(str(DB_PATH))
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT llm_metrics FROM decisions ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        con.close()
        if not row:
            return None
        return json.loads(row["llm_metrics"])
    except Exception:
        return None


def print_summary(results: dict[str, Any]) -> None:
    """Resumen legible al final."""
    print()
    print("=" * 78)
    print("SMOKE A+B DIA 26 — RESUMEN")
    print("=" * 78)
    print(f"Modelo:       {results['config']['model']}")
    print(f"num_predict:  {results['config']['num_predict']}")
    print(f"Branch:       {results['config']['branch']}")
    print()
    for case_name, case in results["cases"].items():
        print(f"--- {case_name} ---")
        if "error" in case:
            print(f"  ERROR: {case['error']}")
            continue
        print(f"  latency: {case.get('latency_ms', '?')} ms")
        print(f"  http:    {case.get('http_status', '?')}")
        env_st = case.get("envelope_status") or "n/a"
        reason = case.get("reason_code") or ""
        print(f"  status:  {env_st}  reason: {reason}")
        metrics = case.get("llm_metrics") or {}
        mode = metrics.get("mode", "?")
        parsed_ok = metrics.get("parsed_ok")
        finish = metrics.get("finish_reasons") or ["?"]
        tool_calls = metrics.get("tool_calls_log", [])
        tokens_out = metrics.get("tokens_out_iter_0")
        print(f"  mode:    {mode}  parsed_ok: {parsed_ok}  finish: {finish[-1] if finish else '?'}")
        print(f"  tokens_out: {tokens_out}")
        if tool_calls:
            print(f"  TOOLS INVOKED ({len(tool_calls)}):")
            for tc in tool_calls:
                print(f"    - {tc.get('name')}({tc.get('args')})")
        else:
            if mode == "llm":
                print(f"  tools:   ninguna invocada en runtime")
        if "answer_es" in case:
            answer = case.get("answer_es") or ""
            print(f"  answer (300):  {answer[:300]}")
        else:
            rationale = case.get("rationale_for_operator") or ""
            print(f"  rationale (240): {rationale[:240]}")
        print()

    print("=" * 78)
    veredict = compute_verdict(results)
    print(f"VEREDICTO: {veredict}")
    print("=" * 78)
    output_path = results["config"]["output_path"]
    print(f"\nResultados completos en: {output_path}")


def compute_verdict(results: dict[str, Any]) -> str:
    cases = results["cases"]
    visit_seed = cases.get("seed_rhizome_02", {})
    visit_m7 = cases.get("bundle_M7", {})
    chat = cases.get("chat_alert", {})

    issues = []
    if "error" in visit_seed:
        issues.append("seed FAILED")
    elif (visit_seed.get("llm_metrics") or {}).get("mode") != "llm":
        issues.append(f"seed cae a {(visit_seed.get('llm_metrics') or {}).get('mode')}")

    if "error" in visit_m7:
        issues.append("M7 FAILED")
    elif (visit_m7.get("llm_metrics") or {}).get("mode") != "llm":
        issues.append(f"M7 cae a {(visit_m7.get('llm_metrics') or {}).get('mode')}")
    else:
        tc = (visit_m7.get("llm_metrics") or {}).get("tool_calls_log", [])
        if tc:
            issues.append(f"M7 OK + invoca {len(tc)} tools (compare_targets esperado)")
        else:
            issues.append("M7 OK pero NO invoca compare_targets")

    if "error" in chat:
        issues.append("chat FAILED")
    elif (chat.get("llm_metrics") or {}).get("mode") != "llm":
        issues.append(f"chat cae a {(chat.get('llm_metrics') or {}).get('mode')}")

    return "; ".join(issues) if issues else "TODO OK"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model", choices=["e4b", "e2b"], default="e4b",
        help="Modelo: e4b necesita ~10 GB RAM, e2b funciona con ~3-4 GB",
    )
    parser.add_argument(
        "--num-predict", type=int, default=None,
        help="Override num_predict. Default: 256 para e4b, 1024 para e2b",
    )
    parser.add_argument(
        "--output", type=Path, default=MERISTEM_DIR / "results_d26_smoke.json",
    )
    args = parser.parse_args()

    # 0) Verificar prerequisitos
    log(f"Repo root: {REPO_ROOT}")
    if not LLAMA_SERVER_BIN.exists():
        log(f"FALTA: {LLAMA_SERVER_BIN}", "ERROR")
        return 2

    model_filename = (
        "gemma-4-E4B-it-Q4_K_M.gguf" if args.model == "e4b"
        else "gemma-4-E2B-it-Q4_K_M.gguf"
    )
    model_path = MODELS_DIR / model_filename
    if not model_path.exists():
        log(f"FALTA modelo: {model_path}", "ERROR")
        return 2

    num_predict = args.num_predict
    if num_predict is None:
        num_predict = 256 if args.model == "e4b" else 1024

    log(f"Modelo: {model_filename}  num_predict: {num_predict}")
    log(f"Output JSON: {args.output}")

    # 1) Limpiar puertos
    for port in (PORT_LLAMA, PORT_ADAPTER, PORT_MERISTEM):
        kill_port(port)

    # 2) Limpiar BBDD anterior
    if DB_PATH.exists():
        try:
            DB_PATH.unlink()
            log(f"BBDD anterior borrada: {DB_PATH.name}")
        except Exception as e:
            log(f"No pude borrar BBDD: {e}", "WARN")

    results: dict[str, Any] = {
        "config": {
            "model": args.model,
            "model_filename": model_filename,
            "num_predict": num_predict,
            "branch": subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, cwd=str(REPO_ROOT),
            ).stdout.strip(),
            "output_path": str(args.output),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "cases": {},
    }

    # 3) Stack: llama-server -> adapter -> meristem
    log_dir = MERISTEM_DIR / "scripts" / "_smoke_logs"
    log_dir.mkdir(exist_ok=True)

    llama_cmd = [
        str(LLAMA_SERVER_BIN),
        "-m", str(model_path),
        "--port", str(PORT_LLAMA),
        "-c", "16384",
    ]
    adapter_cmd = [sys.executable, "-m", "src.main"]
    meristem_cmd = [sys.executable, "-m", "src.main"]

    with background_process(
        llama_cmd, REPO_ROOT, {}, "llama-server",
        log_dir / "llama-server.log",
    ) as proc_llama:
        if not wait_for_url(
            f"http://localhost:{PORT_LLAMA}/health",
            LLAMA_READY_TIMEOUT_S, "llama-server",
        ):
            results["error"] = "llama-server no arrancó (posible OOM)"
            print_summary(results)
            args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
            return 3

        adapter_env = {
            "ADAPTER_PORT": str(PORT_ADAPTER),
            "INFERENCE_BACKEND": "llamacpp",
            "LLAMACPP_SERVER_URL": f"http://localhost:{PORT_LLAMA}",
        }
        with background_process(
            adapter_cmd, ADAPTER_DIR, adapter_env, "adapter",
            log_dir / "adapter.log",
        ) as proc_adapter:
            if not wait_for_url(
                f"http://localhost:{PORT_ADAPTER}/",
                ADAPTER_READY_TIMEOUT_S, "adapter",
            ):
                results["error"] = "adapter no arrancó"
                print_summary(results)
                args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
                return 4

            meristem_env = {
                "MERISTEM_USE_LLM": "true",
                "MERISTEM_ADAPTER_URL": f"http://localhost:{PORT_ADAPTER}",
                "MERISTEM_MDNS_ENABLED": "false",
            }
            with background_process(
                meristem_cmd, MERISTEM_DIR, meristem_env, "meristem",
                log_dir / "meristem.log",
            ) as proc_meristem:
                if not wait_for_url(
                    f"http://localhost:{PORT_MERISTEM}/health",
                    MERISTEM_READY_TIMEOUT_S, "meristem",
                ):
                    results["error"] = "meristem no arrancó"
                    print_summary(results)
                    args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
                    return 5

                # 4) Hacer smoke
                log("Stack arriba. Empieza smoke (3 casos).")

                # Caso 1: seed rhizome_02 con bundle limpio
                log("CASO 1: seed rhizome_02 (bundle limpio)")
                bundle_seed = json.loads(
                    (EXAMPLES_DIR / "bundle_M1_clean.json").read_text(encoding="utf-8")
                )
                bundle_seed["target_rhizome_id"] = "rhizome_02"
                bundle_seed["active_policy_id"] = "pkt_rhizome_02_baseline"
                results["cases"]["seed_rhizome_02"] = post_visit(bundle_seed, num_predict)
                log(f"  latency: {results['cases']['seed_rhizome_02'].get('latency_ms')} ms")

                # Caso 2: bundle M7 (debe disparar compare_targets)
                log("CASO 2: bundle M7 (compare_targets demo)")
                bundle_m7 = json.loads(
                    (EXAMPLES_DIR / "bundle_M7_compare_targets_demo.json").read_text(encoding="utf-8")
                )
                results["cases"]["bundle_M7"] = post_visit(bundle_m7, num_predict)
                log(f"  latency: {results['cases']['bundle_M7'].get('latency_ms')} ms")

                # Caso 3: POST /chat con pregunta sobre alerta
                log("CASO 3: POST /chat sobre alerta de rhizome_01")
                results["cases"]["chat_alert"] = post_chat(
                    "¿Por qué está rhizome_01 en alerta hoy?",
                    num_predict,
                )
                log(f"  latency: {results['cases']['chat_alert'].get('latency_ms')} ms")

                # 5) Lectura final del /health para audit
                try:
                    h = httpx.get(
                        f"http://localhost:{PORT_MERISTEM}/health", timeout=5
                    ).json()
                    results["final_health"] = h
                except Exception as e:
                    results["final_health"] = {"error": str(e)}

    # 6) Guardar JSON + resumen
    args.output.write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print_summary(results)

    # 7) Limpieza
    if DB_PATH.exists():
        try:
            DB_PATH.unlink()
            log("BBDD borrada")
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
