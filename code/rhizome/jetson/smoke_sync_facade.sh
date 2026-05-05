#!/usr/bin/env bash
set -euo pipefail

FACADE_URL="${FACADE_URL:-http://127.0.0.1:13010}"

python - "$FACADE_URL" <<'PY'
import json
import sys
import urllib.request

base_url = sys.argv[1].rstrip("/")


def get_json(path: str):
    with urllib.request.urlopen(base_url + path, timeout=5) as response:
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("application/json"):
            raise SystemExit(f"unexpected content type for {path}: {content_type}")
        return json.loads(response.read().decode("utf-8"))


status = get_json("/status")
snapshot = get_json("/snapshot/latest")
receipts = get_json("/receipts")
summary = get_json("/summary/since?locale=es")

if status.get("status") != "ready":
    raise SystemExit(f"bad status payload: {status}")
if not snapshot.get("snapshot_id"):
    raise SystemExit(f"missing snapshot_id: {snapshot}")
if not receipts or not receipts[0].get("decision_id"):
    raise SystemExit(f"bad receipts payload: {receipts}")
if not summary.get("summary") or not summary.get("headline"):
    raise SystemExit(f"bad summary payload: {summary}")

explanation = get_json(f"/explain/decision/{receipts[0]['decision_id']}?locale=en")
if not explanation.get("explanation"):
    raise SystemExit(f"bad explanation payload: {explanation}")

print(
    json.dumps(
        {
            "status": "ok",
            "facade_url": base_url,
            "node_id": status.get("node_id"),
            "snapshot_id": snapshot["snapshot_id"],
            "receipts": len(receipts),
            "explained_decision_id": receipts[0]["decision_id"],
            "summary_severity": summary.get("severity"),
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
)
PY
