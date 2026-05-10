"""Re-corre mini-bateria dia 16 con parser tolerante.

Linea D del plan dia 24: validar honestamente que las 5/5 corridas
reportadas como PASS dia 16 NO cayeron al stub fallback silencioso.

Para cada bundle M1-M5:
- POST /visit con LLM real
- Tras cada POST, leer llm_metrics de BBDD para ver mode=llm vs
  stub_fallback
- M4 y M5 son REFUSE: NO entran al LLM, no hay decision con
  llm_metrics. Lo apuntamos.

USO (con stack levantado):
    cd code/meristem_node
    python scripts/rerun_mini_bateria_d16.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path

import httpx

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
DB_PATH = Path(__file__).parent.parent / "meristem_node.db"
MERISTEM_URL = "http://localhost:13000"

BUNDLES = [
    ("M1", "bundle_M1_clean.json"),
    ("M2", "bundle_M2_disputed.json"),
    ("M3", "bundle_M3_emergency.json"),
    ("M4", "bundle_M4_hard_limit_relax.json"),
    ("M5", "bundle_M5_pollen_jurisdiction.json"),
]


def post_visit(bundle_path: Path) -> tuple[int, dict, int]:
    """POST /visit. Returns (latency_ms, response, http_status)."""
    bundle = json.load(bundle_path.open(encoding="utf-8"))
    t0 = time.perf_counter()
    with httpx.Client(timeout=600.0) as client:
        r = client.post(f"{MERISTEM_URL}/visit", json=bundle)
    return int((time.perf_counter() - t0) * 1000), r.json(), r.status_code


def read_last_decision_metrics() -> dict | None:
    """Lee llm_metrics de la decision mas reciente."""
    if not DB_PATH.exists():
        return None
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row
    row = con.execute(
        "SELECT llm_metrics FROM decisions ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    con.close()
    if not row:
        return None
    try:
        return json.loads(row["llm_metrics"])
    except json.JSONDecodeError:
        return None


def main() -> int:
    print("=" * 78)
    print("Linea D dia 24: re-correr mini-bateria dia 16 con parser tolerante")
    print("=" * 78)
    print()

    results = []
    for short_name, filename in BUNDLES:
        bundle_path = EXAMPLES_DIR / filename
        if not bundle_path.exists():
            print(f"  {short_name}: NOT FOUND {bundle_path}")
            continue
        print(f"-> POST {short_name} ({filename})...", end=" ", flush=True)
        t_ms, resp, status_http = post_visit(bundle_path)
        envelope_status = resp.get("status")
        reason = resp.get("reason_code")
        # Solo casos OK tienen decision con llm_metrics
        metrics = None
        if envelope_status == "ok":
            metrics = read_last_decision_metrics()
        mode = (metrics or {}).get("mode", "n/a")
        parsed_ok = (metrics or {}).get("parsed_ok", "n/a")
        rationale_ok = (resp.get("payload") or {}).get("rationale_for_operator", "")
        rationale_chars = len(rationale_ok)
        print(
            f"{t_ms:>6}ms  status={envelope_status:<6}  "
            f"reason={reason:<28}  mode={mode}  "
            f"parsed_ok={parsed_ok}  chars={rationale_chars}"
        )
        results.append({
            "bundle": short_name,
            "latency_ms": t_ms,
            "envelope_status": envelope_status,
            "reason_code": reason,
            "llm_mode": mode,
            "parsed_ok": parsed_ok,
            "rationale_chars": rationale_chars,
        })

    print()
    print("=" * 78)
    print("Resumen")
    print("=" * 78)
    n_total = len(results)
    n_ok = sum(1 for r in results if r["envelope_status"] == "ok")
    n_refuse = sum(1 for r in results if r["envelope_status"] == "refuse")
    n_llm = sum(1 for r in results if r["llm_mode"] == "llm")
    n_stub = sum(1 for r in results if r["llm_mode"] == "stub_fallback")
    print(f"  Total: {n_total}  OK: {n_ok}  REFUSE: {n_refuse}")
    print(f"  De los OK: LLM real: {n_llm}  Stub fallback: {n_stub}")
    print()

    # Volcar JSON para auditoria
    out_path = Path("results_d24_mini_bateria.json")
    out_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"-> Detalle en {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
