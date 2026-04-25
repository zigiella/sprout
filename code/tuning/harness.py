#!/usr/bin/env python3
"""harness.py — corre matrices de tuning v0 contra meristem_inference_adapter.

Uso:

  # Smoke test (un round-trip; verifica adapter+Ollama up).
  python harness.py --smoke

  # Listado seco de la matriz (no llama al adapter).
  python harness.py --matrix matrix_phase1.yaml --dry-run

  # Ejecutar fase 1 (48 runs).
  python harness.py --matrix matrix_phase1.yaml

  # Cambiar URL del adapter.
  python harness.py --matrix matrix_phase1.yaml --adapter-url http://localhost:11434

Salida: JSONL en `results/<phase>.jsonl`. Un registro por run con request,
response_body, headers Sprout-Inference-*, parse del sobre común y metadata.

Cobertura por fase:
- phase=1   -> 3 configs × 16 prompts (prompt_pack_en.yaml) = 48 runs
- phase=1.5 -> 4 configs (EN/ES) × 4 pivots = 16 runs (selecciona pack según config.language)
- phase=3   -> 2 archetypes × 3 depths × 2 configs = 12 runs multi-turno (warmup + measured)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import yaml


HERE = Path(__file__).parent
DEFAULT_ADAPTER_URL = "http://localhost:11434"
SPROUT_HEADER_PREFIX = "sprout-inference-"


# ---------------------------------------------------------------------------
# Carga de YAML e indexado
# ---------------------------------------------------------------------------


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def index_by_id(items: list[dict]) -> dict[str, dict]:
    return {item["id"]: item for item in items}


# ---------------------------------------------------------------------------
# Sobre común — parseo del JSON que el modelo emite en message.content
# ---------------------------------------------------------------------------


def parse_envelope(content: str) -> dict:
    """Extrae el sobre común de message.content. Devuelve dict con `valid` y,
    si parsea, las claves del sobre. Tolera fences ```json ... ``` o texto
    alrededor del JSON (busca el primer { y el último } como heurística)."""
    text = content.strip()
    if not text:
        return {"valid": False, "parse_error": "empty_content"}

    # Heurística defensiva: si hay texto antes/después del JSON, intentar
    # recortar al bloque {...} más extenso.
    candidate = text
    if not candidate.startswith("{"):
        # buscar primer '{' y último '}'
        first = candidate.find("{")
        last = candidate.rfind("}")
        if first != -1 and last != -1 and last > first:
            candidate = candidate[first : last + 1]

    try:
        obj = json.loads(candidate)
    except (json.JSONDecodeError, ValueError) as e:
        return {"valid": False, "parse_error": f"json_error: {e}"}

    if not isinstance(obj, dict):
        return {"valid": False, "parse_error": "not_a_dict"}

    missing = [k for k in ("task", "status") if k not in obj]
    if missing:
        return {"valid": False, "parse_error": f"missing_keys: {missing}"}

    return {
        "valid": True,
        "task": obj.get("task"),
        "status": obj.get("status"),
        "reason_code": obj.get("reason_code"),
        "has_payload": obj.get("payload") is not None,
        "has_question_es": bool(obj.get("question_es")),
    }


# ---------------------------------------------------------------------------
# HTTP — adapter + recolección de headers Sprout-Inference-*
# ---------------------------------------------------------------------------


def collect_sprout_headers(response_headers) -> dict[str, str]:
    out = {}
    for k, v in response_headers.items():
        kl = k.lower()
        if kl.startswith(SPROUT_HEADER_PREFIX):
            out[kl[len(SPROUT_HEADER_PREFIX) :]] = v
    return out


def call_adapter(
    client: httpx.Client,
    adapter_url: str,
    payload: dict,
    timeout: float = 180.0,
) -> tuple[dict, dict, int, str | None]:
    """Devuelve (body, sprout_headers, status_code, error_or_None)."""
    try:
        r = client.post(f"{adapter_url}/api/chat", json=payload, timeout=timeout)
    except httpx.HTTPError as e:
        return ({}, {}, 0, f"http_error: {e!r}")
    headers = collect_sprout_headers(r.headers)
    if r.status_code != 200:
        return ({}, headers, r.status_code, f"status_{r.status_code}: {r.text[:200]}")
    try:
        body = r.json()
    except json.JSONDecodeError as e:
        return ({}, headers, r.status_code, f"body_not_json: {e!r}")
    return (body, headers, r.status_code, None)


# ---------------------------------------------------------------------------
# Construcción de requests
# ---------------------------------------------------------------------------


def build_request_payload(
    *,
    model: str,
    system_prompt_text: str,
    user_message: str,
    context: str | None,
    think: bool,
    num_ctx: int,
    num_predict: int,
    temperature: float,
    history: list[dict] | None = None,
) -> dict:
    """Construye payload /api/chat con un único turno de usuario o con historial.

    El `context` (snapshot, receipts, etc.) se concatena al user_message como
    bloque de datos antes de la pregunta del usuario, para dar al modelo un
    único bloque coherente.
    """
    user_content = (
        user_message if not context else f"{context.rstrip()}\n\n{user_message}"
    )
    messages: list[dict] = [{"role": "system", "content": system_prompt_text}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_content})
    return {
        "model": model,
        "messages": messages,
        "think": think,
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx,
            "num_predict": num_predict,
        },
        "stream": False,
    }


# ---------------------------------------------------------------------------
# Single-turn run (fases 1 y 1.5)
# ---------------------------------------------------------------------------


def run_single_turn(
    *,
    run_id: str,
    config: dict,
    prompt: dict,
    system_prompt: dict,
    invariants: dict,
    client: httpx.Client,
    adapter_url: str,
) -> dict:
    payload = build_request_payload(
        model=invariants["model"],
        system_prompt_text=system_prompt["text"],
        user_message=prompt["user_message"],
        context=prompt.get("context"),
        think=config.get("think", False),
        num_ctx=config["num_ctx"],
        num_predict=config["num_predict"],
        temperature=invariants["temperature"],
    )
    t0 = time.monotonic()
    body, headers, status, err = call_adapter(client, adapter_url, payload)
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    msg = (body.get("message") if body else None) or {}
    content = msg.get("content", "") or ""
    thinking = msg.get("thinking", "") or ""
    envelope = parse_envelope(content) if content else {
        "valid": False,
        "parse_error": "no_content",
    }

    expected_status = (prompt.get("expected_envelope") or {}).get("status")

    return {
        "run_id": run_id,
        "config_id": config["id"],
        "prompt_id": prompt["id"],
        "archetype": prompt.get("archetype"),
        "subtype": prompt.get("subtype"),
        "language": prompt.get("language"),
        "expected_status": expected_status,
        "request": payload,
        "response_body": body,
        "headers": headers,
        "envelope": envelope,
        "thinking_excerpt": thinking[:500] if thinking else None,
        "client_elapsed_ms": elapsed_ms,
        "http_status": status,
        "error": err,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Phase runners
# ---------------------------------------------------------------------------


def run_phase_1(matrix: dict, args) -> int:
    """Phase 1: 3 configs × 16 prompts = 48 runs (EN)."""
    invariants = matrix["invariants"]
    configs = matrix["configs"]
    prompt_ids = matrix["prompts"]

    pack = index_by_id(load_yaml(HERE / "prompt_pack_en.yaml"))
    sys_prompts = index_by_id(load_yaml(HERE / "system_prompts.yaml"))

    out_path = HERE / matrix["output"]["path"]
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n_total = len(configs) * len(prompt_ids)
    n_done = 0
    n_envelope_ok = 0
    n_status_match = 0

    with httpx.Client() as client, out_path.open("w", encoding="utf-8") as out_f:
        for config in configs:
            sys_prompt = sys_prompts[config["system_prompt_id"]]
            for prompt_id in prompt_ids:
                prompt = pack[prompt_id]
                run_id = f"phase1_{prompt_id}_{config['id']}"
                if args.dry_run:
                    print(f"[DRY] {run_id}", flush=True)
                    n_done += 1
                    continue
                print(f"[{n_done + 1}/{n_total}] {run_id}", flush=True)
                rec = run_single_turn(
                    run_id=run_id,
                    config=config,
                    prompt=prompt,
                    system_prompt=sys_prompt,
                    invariants=invariants,
                    client=client,
                    adapter_url=args.adapter_url,
                )
                out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out_f.flush()
                n_done += 1
                _print_run_summary(rec)
                if rec["envelope"].get("valid"):
                    n_envelope_ok += 1
                if (
                    rec["envelope"].get("status") == rec["expected_status"]
                    and rec["expected_status"] is not None
                ):
                    n_status_match += 1

    print(
        f"\nPhase 1 done. {n_done}/{n_total} runs. "
        f"envelope_ok={n_envelope_ok} status_match={n_status_match} -> {out_path}"
    )
    return 0


def run_phase_1_5(matrix: dict, args) -> int:
    """Phase 1.5: 4 configs (EN/ES) × 4 pivots = 16 runs."""
    invariants = matrix["invariants"]
    configs = matrix["configs"]
    pivots = matrix["pivot_prompts"]

    pack_en = index_by_id(load_yaml(HERE / "prompt_pack_en.yaml"))
    pack_es = index_by_id(load_yaml(HERE / "prompt_pack_es.yaml"))
    sys_prompts = index_by_id(load_yaml(HERE / "system_prompts.yaml"))

    out_path = HERE / matrix["output"]["path"]
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n_total = len(configs) * len(pivots)
    n_done = 0

    with httpx.Client() as client, out_path.open("w", encoding="utf-8") as out_f:
        for config in configs:
            lang = config["language"]
            pack = pack_en if lang == "en" else pack_es
            sys_prompt = sys_prompts[config["system_prompt_id"]]
            # phase 1.5 fija think=true como invariante de la fase
            run_config = {**config, "think": invariants.get("think", True)}
            for pivot in pivots:
                prompt = pack[pivot["id"]]
                run_id = f"phase1_5_{pivot['id']}_{config['id']}"
                if args.dry_run:
                    print(f"[DRY] {run_id} (lang={lang})", flush=True)
                    n_done += 1
                    continue
                print(f"[{n_done + 1}/{n_total}] {run_id} (lang={lang})", flush=True)
                rec = run_single_turn(
                    run_id=run_id,
                    config=run_config,
                    prompt=prompt,
                    system_prompt=sys_prompt,
                    invariants=invariants,
                    client=client,
                    adapter_url=args.adapter_url,
                )
                out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out_f.flush()
                n_done += 1
                _print_run_summary(rec)

    print(f"\nPhase 1.5 done. {n_done}/{n_total} runs -> {out_path}")
    return 0


def run_phase_3(matrix: dict, args) -> int:
    """Phase 3: 2 archetypes × 3 depths × 2 configs = 12 runs (multi-turn)."""
    invariants = matrix["invariants"]
    configs = matrix["configs"]
    depths = matrix["depths"]
    archetypes_tested = matrix["archetypes_tested"]
    prompts_per_arch = matrix["prompts_per_archetype"]

    pack = index_by_id(load_yaml(HERE / "prompt_pack_en.yaml"))
    sys_prompts = index_by_id(load_yaml(HERE / "system_prompts.yaml"))
    sys_prompt = sys_prompts[invariants["system_prompt_id"]]

    out_path = HERE / matrix["output"]["path"]
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n_total = len(archetypes_tested) * len(depths) * len(configs)
    n_done = 0

    with httpx.Client() as client, out_path.open("w", encoding="utf-8") as out_f:
        for archetype in archetypes_tested:
            warmup_prompt = pack[prompts_per_arch[archetype]["warmup"]]
            measured_prompt = pack[prompts_per_arch[archetype]["measured"]]
            for depth in depths:
                warmup_turns = depth["warmup_turns"]
                for config in configs:
                    run_id = f"phase3_{archetype}_{depth['id']}_{config['id']}"
                    if args.dry_run:
                        print(
                            f"[DRY] {run_id} (warmups={warmup_turns})", flush=True
                        )
                        n_done += 1
                        continue
                    print(
                        f"[{n_done + 1}/{n_total}] {run_id} (warmups={warmup_turns})",
                        flush=True,
                    )

                    # Warmup turns acumulan historia.
                    history: list[dict] = []
                    warmup_records: list[dict] = []
                    warmup_failed = False
                    for i in range(warmup_turns):
                        wp = build_request_payload(
                            model=invariants["model"],
                            system_prompt_text=sys_prompt["text"],
                            user_message=warmup_prompt["user_message"],
                            context=warmup_prompt.get("context"),
                            think=config["think"],
                            num_ctx=config["num_ctx"],
                            num_predict=config["num_predict"],
                            temperature=invariants["temperature"],
                            history=history,
                        )
                        body, headers, _, err = call_adapter(
                            client, args.adapter_url, wp
                        )
                        if err:
                            print(f"  ! warmup {i + 1} error: {err}", flush=True)
                            warmup_failed = True
                            break
                        msg = (body.get("message") if body else None) or {}
                        history.append(
                            {"role": "user", "content": warmup_prompt["user_message"]}
                        )
                        history.append(
                            {"role": "assistant", "content": msg.get("content", "")}
                        )
                        warmup_records.append(
                            {
                                "turn": i + 1,
                                "tokens_in": headers.get("tokens-in"),
                                "tokens_out": headers.get("tokens-out"),
                                "duration_ms": headers.get("duration-ms"),
                            }
                        )

                    # Turno medido — incluso si warmup falló, se registra.
                    t0 = time.monotonic()
                    measured_payload = build_request_payload(
                        model=invariants["model"],
                        system_prompt_text=sys_prompt["text"],
                        user_message=measured_prompt["user_message"],
                        context=measured_prompt.get("context"),
                        think=config["think"],
                        num_ctx=config["num_ctx"],
                        num_predict=config["num_predict"],
                        temperature=invariants["temperature"],
                        history=history,
                    )
                    body, headers, status, err = call_adapter(
                        client, args.adapter_url, measured_payload
                    )
                    elapsed_ms = int((time.monotonic() - t0) * 1000)

                    msg = (body.get("message") if body else None) or {}
                    content = msg.get("content", "") or ""
                    thinking = msg.get("thinking", "") or ""
                    envelope = (
                        parse_envelope(content)
                        if content
                        else {"valid": False, "parse_error": "no_content"}
                    )

                    rec = {
                        "run_id": run_id,
                        "phase": 3,
                        "archetype": archetype,
                        "subtype": measured_prompt.get("subtype"),
                        "depth_id": depth["id"],
                        "warmup_turns": warmup_turns,
                        "warmup_failed": warmup_failed,
                        "config_id": config["id"],
                        "config_think": config["think"],
                        "warmup_records": warmup_records,
                        "measured_request": measured_payload,
                        "measured_response_body": body,
                        "measured_headers": headers,
                        "envelope": envelope,
                        "thinking_excerpt": thinking[:500] if thinking else None,
                        "client_elapsed_ms": elapsed_ms,
                        "http_status": status,
                        "error": err,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    out_f.flush()
                    n_done += 1
                    _print_phase3_summary(rec)

    print(f"\nPhase 3 done. {n_done}/{n_total} runs -> {out_path}")
    return 0


# ---------------------------------------------------------------------------
# Helpers de print
# ---------------------------------------------------------------------------


def _print_run_summary(rec: dict) -> None:
    if rec.get("error"):
        print(f"  ! error: {rec['error']}", flush=True)
        return
    env = rec["envelope"]
    expected = rec.get("expected_status")
    actual = env.get("status") if env.get("valid") else None
    if expected is None:
        match_str = "(no expected_status)"
    elif actual == expected:
        match_str = "OK"
    else:
        match_str = f"MISMATCH (got={actual}, want={expected})"
    h = rec["headers"]
    print(
        f"  envelope_valid={env.get('valid')} status_match={match_str} "
        f"tokens_in={h.get('tokens-in')} tokens_out={h.get('tokens-out')} "
        f"duration_ms={h.get('duration-ms')}",
        flush=True,
    )


def _print_phase3_summary(rec: dict) -> None:
    if rec.get("error"):
        print(f"  ! error: {rec['error']}", flush=True)
        return
    env = rec["envelope"]
    h = rec["measured_headers"]
    print(
        f"  envelope_valid={env.get('valid')} status={env.get('status')} "
        f"tokens_in={h.get('tokens-in')} tokens_out={h.get('tokens-out')} "
        f"duration_ms={h.get('duration-ms')}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------


def smoke_test(args) -> int:
    """Un solo round-trip que verifica que adapter + Ollama responden."""
    payload = {
        "model": "gemma4:e4b",
        "messages": [
            {
                "role": "system",
                "content": "You are a brief assistant. Reply with one short sentence.",
            },
            {"role": "user", "content": "Say hello in Spanish."},
        ],
        "think": False,
        "options": {"temperature": 0.3, "num_ctx": 512, "num_predict": 64},
        "stream": False,
    }
    print(f"smoke: POST {args.adapter_url}/api/chat", flush=True)
    with httpx.Client() as client:
        body, headers, status, err = call_adapter(client, args.adapter_url, payload)
    if err:
        print(f"  FAIL: {err}", flush=True)
        return 1
    msg = body.get("message") or {}
    content = msg.get("content", "")
    print(f"  status={status}", flush=True)
    print(f"  content={content!r}", flush=True)
    print(
        f"  headers: backend={headers.get('backend')} "
        f"model={headers.get('model')} "
        f"tokens_in={headers.get('tokens-in')} "
        f"tokens_out={headers.get('tokens-out')} "
        f"thinking_tokens={headers.get('thinking-tokens')} "
        f"duration_ms={headers.get('duration-ms')} "
        f"cost_eur={headers.get('cost-eur')}",
        flush=True,
    )
    print("  smoke OK", flush=True)
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


PHASE_RUNNERS = {
    1: run_phase_1,
    1.5: run_phase_1_5,
    3: run_phase_3,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tuning v0 harness for Pollen.")
    parser.add_argument("--matrix", help="Path to matrix YAML.")
    parser.add_argument(
        "--out",
        help="Override output JSONL path (defaults to matrix.output.path).",
    )
    parser.add_argument(
        "--adapter-url",
        default=DEFAULT_ADAPTER_URL,
        help=f"Adapter URL (default {DEFAULT_ADAPTER_URL}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List runs without calling the adapter.",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Single round-trip smoke test, no matrix run.",
    )
    args = parser.parse_args(argv)

    if args.smoke:
        return smoke_test(args)

    if not args.matrix:
        parser.error("--matrix required (or use --smoke)")

    matrix_path = Path(args.matrix)
    if not matrix_path.exists():
        print(f"matrix not found: {matrix_path}", file=sys.stderr)
        return 1
    matrix = load_yaml(matrix_path)
    phase = matrix.get("phase")
    if args.out:
        matrix.setdefault("output", {})["path"] = args.out
    runner = PHASE_RUNNERS.get(phase)
    if runner is None:
        print(
            f"unknown phase: {phase}. supported: {sorted(PHASE_RUNNERS.keys())}",
            file=sys.stderr,
        )
        return 1
    return runner(matrix, args)


if __name__ == "__main__":
    sys.exit(main())
