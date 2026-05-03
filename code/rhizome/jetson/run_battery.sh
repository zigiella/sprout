#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-critical}"
DRY_RUN="${DRY_RUN:-false}"
ADAPTER_CONTAINER="${ADAPTER_CONTAINER:-sprout-adapter-12000}"
ADAPTER_URL="${ADAPTER_URL:-http://127.0.0.1:12000}"
LABEL="${LABEL:-jetson_$(date -u +%Y%m%dT%H%M%SZ)}"

if [ "${2:-}" = "--dry-run" ]; then
  DRY_RUN=true
fi

case "$MODE" in
  critical|remaining|full)
    ;;
  *)
    echo "unknown battery mode: $MODE" >&2
    echo "valid modes: critical | remaining | full" >&2
    exit 1
    ;;
esac

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found" >&2
  exit 1
fi

if ! docker ps --filter "name=$ADAPTER_CONTAINER" --format '{{.Names}}' | grep -q "^$ADAPTER_CONTAINER$"; then
  echo "adapter container not running: $ADAPTER_CONTAINER" >&2
  echo "Run ./start_adapter.sh first." >&2
  exit 1
fi

run_matrix() {
  matrix="$1"
  out="$2"
  dry_flag=""
  if [ "$DRY_RUN" = "true" ]; then
    dry_flag="--dry-run"
  fi

  echo "Running matrix=$matrix out=results/$out dry_run=$DRY_RUN"
  docker exec "$ADAPTER_CONTAINER" sh -lc \
    "cd /app/code/tuning && python harness.py --matrix $matrix --adapter-url $ADAPTER_URL --out results/$out $dry_flag"
}

case "$MODE" in
  critical)
    run_matrix "matrix_rhizome_v05.yaml" "rhizome_v05_${LABEL}_critical.jsonl"
    ;;
  remaining)
    run_matrix "matrix_rhizome_v05_remaining.yaml" "rhizome_v05_${LABEL}_remaining.jsonl"
    ;;
  full)
    run_matrix "matrix_rhizome_v05.yaml" "rhizome_v05_${LABEL}_critical.jsonl"
    run_matrix "matrix_rhizome_v05_remaining.yaml" "rhizome_v05_${LABEL}_remaining.jsonl"
    ;;
esac
