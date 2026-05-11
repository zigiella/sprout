"""Mini-experimento num_predict: latencia + calidad rationale vs num_predict.

Linea C del plan dia 24: medir si reducir num_predict (budget de tokens
de salida) reduce latencia drasticamente. Si num_predict=256 logra
~100s/bundle sin perder calidad de rationale, hace la demo en directo
mas fluida.

USO (con stack levantado):
    cd code/meristem_node
    python scripts/mini_exp_num_predict.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
MERISTEM_URL = "http://localhost:13000"

# Bundle: M1 clean (mismo del experimento dia 23 para comparabilidad)
BUNDLE = "bundle_M1_clean.json"
NUM_PREDICT_VALUES = [256, 512, 1024]  # 1024 = default actual


def post_visit_with_num_predict(num_predict: int) -> tuple[int, dict]:
    bundle_path = EXAMPLES_DIR / BUNDLE
    bundle = json.load(bundle_path.open(encoding="utf-8"))
    headers = {
        "Content-Type": "application/json",
        "X-Meristem-Num-Predict": str(num_predict),
        "X-Meristem-Num-Ctx": "4096",  # fijar num_ctx default
    }
    t0 = time.perf_counter()
    try:
        with httpx.Client(timeout=600.0) as client:
            r = client.post(f"{MERISTEM_URL}/visit", json=bundle, headers=headers)
        return int((time.perf_counter() - t0) * 1000), r.json()
    except httpx.HTTPError as e:
        return int((time.perf_counter() - t0) * 1000), {"_error": str(e)}


def main() -> int:
    print("=" * 78)
    print(f"Linea C dia 24: mini-experimento num_predict")
    print(f"Bundle: M1 clean (default num_ctx=4096)")
    print(f"num_predict values: {NUM_PREDICT_VALUES}")
    print("=" * 78)
    print()

    results = []
    for npredict in NUM_PREDICT_VALUES:
        print(f"-> M1 @ num_predict={npredict}...", end=" ", flush=True)
        t_ms, resp = post_visit_with_num_predict(npredict)
        envelope_status = resp.get("status")
        reason = resp.get("reason_code")
        rationale = (resp.get("payload") or {}).get("rationale_for_operator", "")
        chars = len(rationale)
        print(
            f"{t_ms:>6}ms  status={envelope_status}  reason={reason}  "
            f"chars={chars}"
        )
        results.append({
            "bundle": "M1",
            "num_predict": npredict,
            "latency_ms": t_ms,
            "status": envelope_status,
            "reason_code": reason,
            "rationale_chars": chars,
            "rationale": rationale[:300],
        })

    print()
    print("=" * 78)
    print("Resumen")
    print("=" * 78)
    print(f"{'num_predict':>12} {'latency_ms':>12} {'chars':>6}")
    for r in results:
        print(f"{r['num_predict']:>12} {r['latency_ms']:>12} {r['rationale_chars']:>6}")

    out_path = Path("results_d24_num_predict.json")
    out_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n-> Detalle en {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
