"""Analisis cualitativo de los resultados del tuning v0.

Lee los tres JSONL de `code/tuning/results/` y produce un resumen en stdout
con metricas por fase y por arquetipo, mas los outliers (envelope invalido,
status mismatch, errores HTTP).

No emite juicio final — eso vive en la bitacora de cierre. Este script da
la base numerica.

Uso:
    python code/tuning/analyze.py
    python code/tuning/analyze.py --results-dir code/tuning/results/
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_RESULTS = HERE / "results"


def load_jsonl(path: Path) -> list[dict]:
    """Carga JSONL y dedupe por run_id, prefiriendo el ultimo record OK (sin
    error y http_status==200). Si hay duplicados, el ultimo OK gana sobre
    cualquier fallo previo (caso tipico tras --resume).
    """
    if not path.exists():
        return []
    by_run_id: dict[str, dict] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            rid = rec.get("run_id") or f"_anon_{len(by_run_id)}"
            existing = by_run_id.get(rid)
            if existing is None:
                by_run_id[rid] = rec
                continue
            # Si el existente fallo y el nuevo es OK, sustituye.
            existing_ok = (
                not existing.get("error") and existing.get("http_status") == 200
            )
            new_ok = not rec.get("error") and rec.get("http_status") == 200
            if new_ok and not existing_ok:
                by_run_id[rid] = rec
            elif new_ok and existing_ok:
                # Ambos OK -> queda el ultimo (mas reciente en el JSONL).
                by_run_id[rid] = rec
    return list(by_run_id.values())


def fmt_pct(n: int, total: int) -> str:
    if total == 0:
        return "0/0"
    return f"{n}/{total} ({n * 100 // total}%)"


def summarize_phase_1(records: list[dict]) -> None:
    print("=" * 72)
    print(f"PHASE 1 — {len(records)} runs (3 configs × 16 prompts EN)")
    print("=" * 72)

    by_config = defaultdict(list)
    by_archetype = defaultdict(list)
    by_subtype = defaultdict(list)
    errors = []

    for r in records:
        cfg = r.get("config_id", "?")
        arch = r.get("archetype", "?")
        sub = r.get("subtype", "?")
        by_config[cfg].append(r)
        by_archetype[arch].append(r)
        by_subtype[f"{arch}/{sub}"].append(r)
        if r.get("error") or r.get("http_status") != 200:
            errors.append(r)

    print("\n-- por configuracion --")
    for cfg, runs in sorted(by_config.items()):
        env_ok = sum(1 for r in runs if r["envelope"].get("valid"))
        status_ok = sum(
            1
            for r in runs
            if r["envelope"].get("valid")
            and r["envelope"].get("status") == r.get("expected_status")
        )
        avg_ms = sum(r.get("client_elapsed_ms", 0) for r in runs) / max(len(runs), 1)
        avg_tokens_out = sum(
            int(r["headers"].get("tokens-out", 0) or 0) for r in runs
        ) / max(len(runs), 1)
        print(
            f"  {cfg:20s} envelope={fmt_pct(env_ok, len(runs))} "
            f"status_match={fmt_pct(status_ok, len(runs))} "
            f"avg_ms={avg_ms:.0f} avg_tok_out={avg_tokens_out:.0f}"
        )

    print("\n-- por arquetipo --")
    for arch, runs in sorted(by_archetype.items()):
        env_ok = sum(1 for r in runs if r["envelope"].get("valid"))
        status_ok = sum(
            1
            for r in runs
            if r["envelope"].get("valid")
            and r["envelope"].get("status") == r.get("expected_status")
        )
        print(
            f"  {arch:20s} envelope={fmt_pct(env_ok, len(runs))} "
            f"status_match={fmt_pct(status_ok, len(runs))}"
        )

    print("\n-- por subtipo (ordenado por status_match) --")
    rows = []
    for key, runs in by_subtype.items():
        env_ok = sum(1 for r in runs if r["envelope"].get("valid"))
        status_ok = sum(
            1
            for r in runs
            if r["envelope"].get("valid")
            and r["envelope"].get("status") == r.get("expected_status")
        )
        rows.append((key, env_ok, status_ok, len(runs)))
    rows.sort(key=lambda x: (x[2] / max(x[3], 1), x[0]))
    for key, env_ok, status_ok, total in rows:
        print(
            f"  {key:50s} envelope={fmt_pct(env_ok, total)} "
            f"status_match={fmt_pct(status_ok, total)}"
        )

    if errors:
        print(f"\n-- {len(errors)} errores --")
        for r in errors[:10]:
            print(f"  {r.get('run_id')}: status={r.get('http_status')} err={r.get('error')}")


def summarize_phase_1_5(records: list[dict]) -> None:
    print("\n" + "=" * 72)
    print(f"PHASE 1.5 — {len(records)} runs (4 configs EN/ES × 4 pivots)")
    print("=" * 72)

    by_lang = defaultdict(list)
    for r in records:
        by_lang[r.get("language", "?")].append(r)

    print("\n-- por idioma --")
    for lang, runs in sorted(by_lang.items()):
        env_ok = sum(1 for r in runs if r["envelope"].get("valid"))
        status_ok = sum(
            1
            for r in runs
            if r["envelope"].get("valid")
            and r["envelope"].get("status") == r.get("expected_status")
        )
        avg_ms = sum(r.get("client_elapsed_ms", 0) for r in runs) / max(len(runs), 1)
        print(
            f"  {lang:6s} envelope={fmt_pct(env_ok, len(runs))} "
            f"status_match={fmt_pct(status_ok, len(runs))} "
            f"avg_ms={avg_ms:.0f}"
        )

    print("\n-- pivote × idioma (envelope_valid Y status_match) --")
    by_pair = defaultdict(list)
    for r in records:
        by_pair[(r.get("prompt_id"), r.get("language"))].append(r)

    pivots_seen = sorted({k[0] for k in by_pair.keys()})
    print(f"  {'pivote':45s}  EN              ES")
    for piv in pivots_seen:
        en_runs = by_pair.get((piv, "en"), [])
        es_runs = by_pair.get((piv, "es"), [])
        en_ok = sum(
            1
            for r in en_runs
            if r["envelope"].get("valid")
            and r["envelope"].get("status") == r.get("expected_status")
        )
        es_ok = sum(
            1
            for r in es_runs
            if r["envelope"].get("valid")
            and r["envelope"].get("status") == r.get("expected_status")
        )
        print(
            f"  {piv:45s}  {fmt_pct(en_ok, len(en_runs)):14s}  {fmt_pct(es_ok, len(es_runs))}"
        )

    en_total = sum(
        1
        for r in records
        if r.get("language") == "en"
        and r["envelope"].get("valid")
        and r["envelope"].get("status") == r.get("expected_status")
    )
    es_total = sum(
        1
        for r in records
        if r.get("language") == "es"
        and r["envelope"].get("valid")
        and r["envelope"].get("status") == r.get("expected_status")
    )
    en_count = sum(1 for r in records if r.get("language") == "en")
    es_count = sum(1 for r in records if r.get("language") == "es")

    print(
        f"\n  decision rule: EN={en_total}/{en_count} vs ES={es_total}/{es_count} -> "
        f"{'EN wins' if en_total > es_total else 'ES wins' if es_total > en_total else 'TIE'}"
    )


def summarize_phase_3(records: list[dict]) -> None:
    print("\n" + "=" * 72)
    print(f"PHASE 3 — {len(records)} runs (2 archetypes × 3 depths × T_OFF/T_ON)")
    print("=" * 72)

    # Phase 3 schema: measured_headers (no headers), depth_id, config_think (bool),
    # warmup_failed (bool). Cada record es 1 turno medido + N warmup turns previos.
    rows = []
    for r in records:
        arch = r.get("archetype", "?")
        depth = r.get("depth_id", "?")
        think = "ON" if r.get("config_think") else "OFF"
        mh = r.get("measured_headers") or {}
        env = r.get("envelope") or {}
        rows.append({
            "arch": arch,
            "depth": depth,
            "think": think,
            "warmup_failed": bool(r.get("warmup_failed")),
            "tokens_in": int(mh.get("tokens-in", 0) or 0),
            "tokens_out": int(mh.get("tokens-out", 0) or 0),
            "thinking_tok": int(mh.get("thinking-tokens", 0) or 0),
            "duration_ms": int(mh.get("duration-ms", 0) or 0),
            "client_ms": r.get("client_elapsed_ms", 0),
            "env_valid": bool(env.get("valid")),
            "warmup_turns": r.get("warmup_turns", 0),
        })

    # Tabla detalle por (arch, depth, think) — N=1 por celda en Phase 3
    print(
        f"\n  {'archetype':18s} {'depth':5s} {'think':5s} "
        f"{'tok_in':>7s} {'tok_out':>7s} {'env_ok':>6s} {'wm_fail':>7s} {'dur_ms':>8s}"
    )
    rows.sort(key=lambda x: (x["arch"], x["depth"], x["think"]))
    for r in rows:
        print(
            f"  {r['arch']:18s} {r['depth']:5s} {r['think']:5s} "
            f"{r['tokens_in']:>7d} {r['tokens_out']:>7d} "
            f"{('OK' if r['env_valid'] else 'NO'):>6s} "
            f"{('YES' if r['warmup_failed'] else 'no'):>7s} "
            f"{r['duration_ms']:>8d}"
        )

    # Resumen R7 (filter_channel hypothesis): T_OFF vs T_ON a depth creciente
    print("\n  -- R7 (filter_channel KV hypothesis) --")
    print("  Si T_ON degrada >> T_OFF a D5 vs D1: indicio de acumulacion KV.")
    print("  Si curvas similares: hipotesis NO respaldada por estos datos.")

    by_pair = defaultdict(dict)
    for r in rows:
        by_pair[(r["arch"], r["depth"])][r["think"]] = r

    for arch in sorted({r["arch"] for r in rows}):
        print(f"\n  [{arch}]")
        for depth in ["D1", "D3", "D5"]:
            pair = by_pair.get((arch, depth), {})
            t_off = pair.get("OFF")
            t_on = pair.get("ON")
            if t_off and t_on:
                d_in = t_on["tokens_in"] - t_off["tokens_in"]
                d_out = t_on["tokens_out"] - t_off["tokens_out"]
                d_ms = t_on["duration_ms"] - t_off["duration_ms"]
                print(
                    f"    {depth}: tok_in OFF={t_off['tokens_in']:>5d} ON={t_on['tokens_in']:>5d} (d={d_in:+d})  "
                    f"tok_out OFF={t_off['tokens_out']:>5d} ON={t_on['tokens_out']:>5d} (d={d_out:+d})  "
                    f"dur OFF={t_off['duration_ms']:>6d}ms ON={t_on['duration_ms']:>6d}ms (d={d_ms:+d}ms)  "
                    f"env OFF={'OK' if t_off['env_valid'] else 'NO'} ON={'OK' if t_on['env_valid'] else 'NO'}"
                )

    # Resumen R3 (resetConversation): crecimiento tokens_in D1 -> D5 por arquetipo
    print("\n  -- R3 (acumulacion KV, decisión resetConversation()) --")
    for arch in sorted({r["arch"] for r in rows}):
        for think in ["OFF", "ON"]:
            d1 = by_pair.get((arch, "D1"), {}).get(think)
            d5 = by_pair.get((arch, "D5"), {}).get(think)
            if d1 and d5:
                growth = d5["tokens_in"] - d1["tokens_in"]
                pct = (d5["tokens_in"] / max(d1["tokens_in"], 1) - 1) * 100
                print(
                    f"    {arch:18s} T_{think}: D1 tok_in={d1['tokens_in']:>4d} -> D5 tok_in={d5['tokens_in']:>4d} "
                    f"(+{growth} = +{pct:.0f}%)"
                )

    n_warmup_failed = sum(1 for r in rows if r["warmup_failed"])
    n_env_invalid = sum(1 for r in rows if not r["env_valid"])
    print(f"\n  Outliers: warmup_failed={n_warmup_failed}/{len(rows)}  envelope_invalid={n_env_invalid}/{len(rows)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    args = ap.parse_args()

    p1 = load_jsonl(args.results_dir / "phase1.jsonl")
    p15 = load_jsonl(args.results_dir / "phase1_5.jsonl")
    p3 = load_jsonl(args.results_dir / "phase3.jsonl")

    if p1:
        summarize_phase_1(p1)
    if p15:
        summarize_phase_1_5(p15)
    if p3:
        summarize_phase_3(p3)

    if not (p1 or p15 or p3):
        print(f"No results found in {args.results_dir}")


if __name__ == "__main__":
    main()
