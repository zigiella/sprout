#!/usr/bin/env bash
set -euo pipefail

FACADE_URL="${FACADE_URL:-http://127.0.0.1:13010}"

python3 - "$FACADE_URL" <<'PY'
import json
import sys
import urllib.request

base_url = sys.argv[1].rstrip("/")

with urllib.request.urlopen(f"{base_url}/summary/since?locale=en", timeout=180) as response:
    payload = json.loads(response.read().decode("utf-8"))

if payload.get("source") != "deterministic_visit_summary":
    raise SystemExit(f"unexpected source: {payload.get('source')}")
if payload.get("narrative_source") != "gemma_visit_narrator":
    raise SystemExit(f"Gemma narrator not used: {payload.get('gemma_narrator')}")
if not payload.get("gemma_narrator", {}).get("used"):
    raise SystemExit(f"Gemma narrator disabled or fallback: {payload.get('gemma_narrator')}")
if not isinstance(payload.get("counts"), dict):
    raise SystemExit(f"missing deterministic counts: {payload}")

print(
    json.dumps(
        {
            "status": "ok",
            "facade_url": base_url,
            "narrative_source": payload["narrative_source"],
            "counts": payload["counts"],
            "headline": payload.get("headline"),
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
)
PY
