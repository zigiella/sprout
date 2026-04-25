"""Run reproducible Ollama benchmarks for Rhizome prompt sets."""

from __future__ import annotations

import argparse
import base64
import json
import statistics
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .common import (
    BENCHMARKS_DIR,
    DEFAULT_PROMPT_SET_PATH,
    MemorySampler,
    bytes_to_gib,
    detect_host,
    percentile,
    slugify,
    utc_now_iso,
)

DEFAULT_ENDPOINT = "http://127.0.0.1:11434"


@dataclass(frozen=True)
class PhaseConfig:
    name: str
    repeat_count: int
    keep_alive: str
    reset_before_phase: bool = False
    warmup_before_phase: bool = False


def _post_json(url: str, payload: dict[str, Any], timeout_s: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_s) as response:
        return json.load(response)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        records.append(json.loads(stripped))
    return records


def _load_image_inputs(prompt_record: dict[str, Any], prompt_set_path: Path) -> list[str]:
    encoded: list[str] = []
    for relative_path in prompt_record.get("image_paths", []):
        image_path = (prompt_set_path.parent / relative_path).resolve()
        encoded.append(base64.b64encode(image_path.read_bytes()).decode("ascii"))
    return encoded


def _collect_ollama_version() -> str | None:
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except Exception:
        return None
    return result.stdout.strip() or None


def _collect_model_details(endpoint: str, model: str, timeout_s: int) -> dict[str, Any]:
    try:
        response = _post_json(f"{endpoint}/api/show", {"model": model}, timeout_s)
    except Exception as exc:  # pragma: no cover - depends on runtime availability
        return {"error": str(exc)}
    return {
        "details": response.get("details"),
        "capabilities": response.get("capabilities"),
        "parameters": response.get("parameters"),
    }


def _compute_tokens_per_second(eval_count: int | None, eval_duration_ns: int | None) -> float | None:
    if not eval_count or not eval_duration_ns:
        return None
    if eval_duration_ns <= 0:
        return None
    return round(eval_count / (eval_duration_ns / 1_000_000_000), 3)


def _ns_to_ms(value: int | None) -> float | None:
    if value is None:
        return None
    return round(value / 1_000_000, 3)


def _approx_first_token_latency_ms(payload: dict[str, Any]) -> float | None:
    load_duration = payload.get("load_duration")
    prompt_eval_duration = payload.get("prompt_eval_duration")
    if load_duration is None and prompt_eval_duration is None:
        return None
    total_ns = (load_duration or 0) + (prompt_eval_duration or 0)
    return _ns_to_ms(total_ns)


def _build_output_path(model: str, hardware_label: str | None) -> Path:
    date_prefix = time.strftime("%Y-%m-%d")
    model_slug = slugify(model.replace(":", "-"))
    hardware_slug = slugify(hardware_label or detect_host().get("model") or detect_host().get("hostname") or "unknown-host")
    return BENCHMARKS_DIR / f"{date_prefix}_{model_slug}_{hardware_slug}.json"


def build_phase_plan(phases: str | None, *, keep_alive: str, repeat_count: int) -> list[PhaseConfig]:
    if not phases:
        return []

    phase_defs: dict[str, PhaseConfig] = {
        "cold": PhaseConfig(name="cold", repeat_count=1, keep_alive="0", reset_before_phase=True),
        "warm": PhaseConfig(name="warm", repeat_count=1, keep_alive=keep_alive, reset_before_phase=True, warmup_before_phase=True),
        "repeat": PhaseConfig(name="repeat", repeat_count=max(1, repeat_count), keep_alive=keep_alive),
    }
    plan: list[PhaseConfig] = []
    seen: set[str] = set()
    for raw_name in phases.split(","):
        name = raw_name.strip().lower()
        if not name:
            continue
        if name not in phase_defs:
            raise ValueError(f"Unsupported phase: {name}")
        if name in seen:
            raise ValueError(f"Duplicated phase: {name}")
        seen.add(name)
        plan.append(phase_defs[name])
    return plan


def _reset_model(endpoint: str, model: str, timeout_s: int) -> dict[str, Any]:
    payload = {"model": model, "prompt": "", "stream": False, "keep_alive": 0}
    try:
        response = _post_json(f"{endpoint}/api/generate", payload, timeout_s)
    except Exception as exc:  # pragma: no cover - depends on runtime availability
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "done_reason": response.get("done_reason")}


def _warmup_model(endpoint: str, model: str, timeout_s: int, keep_alive: str) -> dict[str, Any]:
    payload = {
        "model": model,
        "prompt": "warmup",
        "stream": False,
        "keep_alive": keep_alive,
        "options": {"temperature": 0.0, "num_predict": 1},
    }
    started = time.perf_counter()
    try:
        response = _post_json(f"{endpoint}/api/generate", payload, timeout_s)
    except Exception as exc:  # pragma: no cover - depends on runtime availability
        return {"ok": False, "error": str(exc)}
    return {
        "ok": True,
        "wall_clock_ms": round((time.perf_counter() - started) * 1000, 3),
        "load_duration_ms": _ns_to_ms(response.get("load_duration")),
        "first_token_latency_ms": _approx_first_token_latency_ms(response),
    }


def benchmark_prompt(
    *,
    endpoint: str,
    model: str,
    prompt_record: dict[str, Any],
    prompt_set_path: Path,
    timeout_s: int,
    keep_alive: str,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "prompt": prompt_record["prompt"],
        "stream": False,
        "keep_alive": keep_alive,
        "options": {
            "temperature": prompt_record.get("temperature", 0.0),
            "num_predict": prompt_record.get("max_tokens", 64),
        },
    }
    images = _load_image_inputs(prompt_record, prompt_set_path)
    if images:
        payload["images"] = images

    sampler = MemorySampler()
    sampler.start()
    wall_start = time.perf_counter()
    try:
        response = _post_json(f"{endpoint}/api/generate", payload, timeout_s)
        wall_clock_ms = round((time.perf_counter() - wall_start) * 1000, 3)
    except urllib.error.HTTPError as exc:
        wall_clock_ms = round((time.perf_counter() - wall_start) * 1000, 3)
        sampler.stop()
        body = exc.read().decode("utf-8", errors="replace")
        return {
            "id": prompt_record["id"],
            "category": prompt_record["category"],
            "modality": prompt_record.get("modality", "text"),
            "ok": False,
            "wall_clock_ms": wall_clock_ms,
            "error": f"HTTP {exc.code}: {body}",
            "memory_peak_used_bytes": sampler.peak_used_bytes,
            "memory_peak_used_gib": bytes_to_gib(sampler.peak_used_bytes),
        }
    except Exception as exc:
        wall_clock_ms = round((time.perf_counter() - wall_start) * 1000, 3)
        sampler.stop()
        return {
            "id": prompt_record["id"],
            "category": prompt_record["category"],
            "modality": prompt_record.get("modality", "text"),
            "ok": False,
            "wall_clock_ms": wall_clock_ms,
            "error": str(exc),
            "memory_peak_used_bytes": sampler.peak_used_bytes,
            "memory_peak_used_gib": bytes_to_gib(sampler.peak_used_bytes),
        }

    sampler.stop()
    eval_count = response.get("eval_count")
    eval_duration = response.get("eval_duration")
    prompt_eval_count = response.get("prompt_eval_count")
    total_duration = response.get("total_duration")
    load_duration = response.get("load_duration")
    prompt_eval_duration = response.get("prompt_eval_duration")

    return {
        "id": prompt_record["id"],
        "category": prompt_record["category"],
        "modality": prompt_record.get("modality", "text"),
        "ok": True,
        "max_tokens": prompt_record.get("max_tokens"),
        "temperature": prompt_record.get("temperature", 0.0),
        "source_examples": prompt_record.get("source_examples", []),
        "image_count": len(prompt_record.get("image_paths", [])),
        "wall_clock_ms": wall_clock_ms,
        "total_duration_ms": _ns_to_ms(total_duration),
        "load_duration_ms": _ns_to_ms(load_duration),
        "prompt_eval_duration_ms": _ns_to_ms(prompt_eval_duration),
        "first_token_latency_ms": _approx_first_token_latency_ms(response),
        "prompt_eval_count": prompt_eval_count,
        "eval_count": eval_count,
        "eval_duration_ms": _ns_to_ms(eval_duration),
        "tokens_per_second": _compute_tokens_per_second(eval_count, eval_duration),
        "memory_peak_used_bytes": sampler.peak_used_bytes,
        "memory_peak_used_gib": bytes_to_gib(sampler.peak_used_bytes),
        "response_chars": len(response.get("response", "")),
        "response_preview": response.get("response", "")[:240],
        "done_reason": response.get("done_reason"),
    }


def _slice_result_class(*, failures: int, repeat_count: int) -> str:
    if failures:
        return "failed"
    if repeat_count > 1:
        return "engineering-pass"
    return "demo-pass"


def _summarize_slice(results: list[dict[str, Any]], *, repeat_count: int) -> dict[str, Any]:
    successes = [result for result in results if result.get("ok")]
    failures = [result for result in results if not result.get("ok")]
    latency_values = [result["wall_clock_ms"] for result in successes if result.get("wall_clock_ms") is not None]
    first_token_values = [result["first_token_latency_ms"] for result in successes if result.get("first_token_latency_ms") is not None]
    tok_s_values = [result["tokens_per_second"] for result in successes if result.get("tokens_per_second") is not None]
    memory_values = [result["memory_peak_used_bytes"] for result in successes if result.get("memory_peak_used_bytes") is not None]

    return {
        "requests_total": len(results),
        "requests_ok": len(successes),
        "requests_failed": len(failures),
        "wall_clock_ms_p50": round(percentile(latency_values, 0.50), 3) if latency_values else None,
        "wall_clock_ms_p95": round(percentile(latency_values, 0.95), 3) if latency_values else None,
        "first_token_latency_ms_p50": round(percentile(first_token_values, 0.50), 3) if first_token_values else None,
        "first_token_latency_ms_p95": round(percentile(first_token_values, 0.95), 3) if first_token_values else None,
        "tokens_per_second_avg": round(statistics.fmean(tok_s_values), 3) if tok_s_values else None,
        "tokens_per_second_p50": round(percentile(tok_s_values, 0.50), 3) if tok_s_values else None,
        "tokens_per_second_p95": round(percentile(tok_s_values, 0.95), 3) if tok_s_values else None,
        "memory_peak_used_bytes_max": max(memory_values) if memory_values else None,
        "memory_peak_used_gib_max": bytes_to_gib(max(memory_values) if memory_values else None),
        "power_watts_avg": None,
        "result_class": _slice_result_class(failures=len(failures), repeat_count=repeat_count),
    }


def summarize_results(
    results: list[dict[str, Any]],
    *,
    repeat_count: int,
    phase_repeat_counts: dict[str, int] | None = None,
) -> dict[str, Any]:
    summary = _summarize_slice(results, repeat_count=repeat_count)
    modalities = sorted({result.get("modality", "text") for result in results})
    summary["by_modality"] = {
        modality: _summarize_slice(
            [result for result in results if result.get("modality", "text") == modality],
            repeat_count=repeat_count,
        )
        for modality in modalities
    }

    phase_order = ["cold", "warm", "repeat"]
    phase_names = [name for name in phase_order if any(result.get("phase") == name for result in results)]
    phase_names.extend(
        sorted(
            {
                result["phase"]
                for result in results
                if result.get("phase") and result["phase"] not in phase_order
            }
        )
    )
    if phase_names:
        by_phase: dict[str, dict[str, Any]] = {}
        by_phase_and_modality: dict[str, dict[str, dict[str, Any]]] = {}
        for phase_name in phase_names:
            phase_results = [result for result in results if result.get("phase") == phase_name]
            phase_repeat = phase_repeat_counts.get(phase_name, 1) if phase_repeat_counts else 1
            by_phase[phase_name] = _summarize_slice(phase_results, repeat_count=phase_repeat)
            phase_modalities = sorted({result.get("modality", "text") for result in phase_results})
            by_phase_and_modality[phase_name] = {
                modality: _summarize_slice(
                    [result for result in phase_results if result.get("modality", "text") == modality],
                    repeat_count=phase_repeat,
                )
                for modality in phase_modalities
            }
        summary["by_phase"] = by_phase
        summary["by_phase_and_modality"] = by_phase_and_modality

    return summary


def _iter_prompt_records(prompt_set_path: Path, limit: int | None) -> list[dict[str, Any]]:
    prompt_records = _read_jsonl(prompt_set_path)
    if limit is not None:
        prompt_records = prompt_records[:limit]
    return prompt_records


def run_benchmark(
    *,
    endpoint: str,
    model: str,
    prompt_set_path: Path,
    timeout_s: int,
    keep_alive: str,
    repeat_count: int,
    limit: int | None,
    phase_plan: list[PhaseConfig] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    prompt_records = _iter_prompt_records(prompt_set_path, limit)
    results: list[dict[str, Any]] = []
    phase_events: list[dict[str, Any]] = []

    if phase_plan:
        phase_repeat_counts = {phase.name: phase.repeat_count for phase in phase_plan}
        for phase in phase_plan:
            phase_event: dict[str, Any] = {
                "name": phase.name,
                "repeat_count": phase.repeat_count,
                "keep_alive": phase.keep_alive,
                "reset_before_phase": phase.reset_before_phase,
                "warmup_before_phase": phase.warmup_before_phase,
            }
            if phase.reset_before_phase:
                phase_event["reset"] = _reset_model(endpoint, model, timeout_s)
            if phase.warmup_before_phase:
                phase_event["warmup"] = _warmup_model(endpoint, model, timeout_s, phase.keep_alive)
            phase_events.append(phase_event)

            for iteration in range(phase.repeat_count):
                for prompt_record in prompt_records:
                    result = benchmark_prompt(
                        endpoint=endpoint,
                        model=model,
                        prompt_record=prompt_record,
                        prompt_set_path=prompt_set_path,
                        timeout_s=timeout_s,
                        keep_alive=phase.keep_alive,
                    )
                    result["phase"] = phase.name
                    result["iteration"] = iteration + 1
                    result["phase_keep_alive"] = phase.keep_alive
                    results.append(result)
                    status = "OK" if result["ok"] else "FAIL"
                    print(
                        f"[{phase.name.upper()}][{status}] {result['id']} "
                        f"lat={result.get('wall_clock_ms')}ms "
                        f"tok/s={result.get('tokens_per_second')} "
                        f"mem_gib={result.get('memory_peak_used_gib')}"
                    )

        summary = summarize_results(results, repeat_count=max(1, repeat_count), phase_repeat_counts=phase_repeat_counts)
        return results, summary, phase_events

    for iteration in range(max(1, repeat_count)):
        for prompt_record in prompt_records:
            result = benchmark_prompt(
                endpoint=endpoint,
                model=model,
                prompt_record=prompt_record,
                prompt_set_path=prompt_set_path,
                timeout_s=timeout_s,
                keep_alive=keep_alive,
            )
            result["iteration"] = iteration + 1
            results.append(result)
            status = "OK" if result["ok"] else "FAIL"
            print(
                f"[{status}] {result['id']} "
                f"lat={result.get('wall_clock_ms')}ms "
                f"tok/s={result.get('tokens_per_second')} "
                f"mem_gib={result.get('memory_peak_used_gib')}"
            )

    summary = summarize_results(results, repeat_count=max(1, repeat_count))
    return results, summary, phase_events


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Ollama model tag, e.g. gemma4:e4b.")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="Base URL for the Ollama API.")
    parser.add_argument("--prompt-set", type=Path, default=DEFAULT_PROMPT_SET_PATH, help="Path to the benchmark JSONL prompt set.")
    parser.add_argument("--output", type=Path, default=None, help="Path to save the benchmark JSON report.")
    parser.add_argument("--timeout-sec", type=int, default=300, help="Per-request timeout in seconds.")
    parser.add_argument("--repeat", type=int, default=1, help="Classic mode: full prompt-set passes. Phased mode: repeat phase passes.")
    parser.add_argument("--limit", type=int, default=None, help="Limit the run to the first N prompts.")
    parser.add_argument("--hardware-label", default=None, help="Optional label used in the output filename.")
    parser.add_argument("--keep-alive", default="30m", help="Ollama keep_alive value.")
    parser.add_argument(
        "--phases",
        default=None,
        help="Comma-separated phase plan such as cold,warm,repeat. When omitted the runner uses classic mode.",
    )
    args = parser.parse_args()

    output_path = args.output or _build_output_path(args.model, args.hardware_label)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    phase_plan = build_phase_plan(args.phases, keep_alive=args.keep_alive, repeat_count=args.repeat)

    host_info = detect_host()
    report = {
        "captured_at": utc_now_iso(),
        "runtime": {
            "name": "ollama",
            "endpoint": args.endpoint,
            "version": _collect_ollama_version(),
        },
        "host": {
            **host_info,
            "label": args.hardware_label or slugify(host_info.get("model") or host_info.get("hostname") or "unknown-host"),
        },
        "model": {
            "name": args.model,
            "details": _collect_model_details(args.endpoint, args.model, args.timeout_sec),
        },
        "benchmark_config": {
            "prompt_set_path": str(args.prompt_set),
            "repeat": args.repeat,
            "limit": args.limit,
            "timeout_sec": args.timeout_sec,
            "keep_alive": args.keep_alive,
            "phases": [phase.name for phase in phase_plan] if phase_plan else None,
        },
    }

    results, summary, phase_events = run_benchmark(
        endpoint=args.endpoint,
        model=args.model,
        prompt_set_path=args.prompt_set,
        timeout_s=args.timeout_sec,
        keep_alive=args.keep_alive,
        repeat_count=args.repeat,
        limit=args.limit,
        phase_plan=phase_plan,
    )
    report["summary"] = summary
    report["results"] = results
    if phase_events:
        report["phase_runs"] = phase_events
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    print(f"Saved benchmark report to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
