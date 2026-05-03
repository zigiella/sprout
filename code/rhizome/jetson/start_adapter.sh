#!/usr/bin/env bash
set -euo pipefail

ADAPTER_CONTAINER="${ADAPTER_CONTAINER:-sprout-adapter-12000}"
ADAPTER_IMAGE="${ADAPTER_IMAGE:-python:3.10-slim}"
ADAPTER_PORT="${ADAPTER_PORT:-12000}"
LLAMACPP_SERVER_URL="${LLAMACPP_SERVER_URL:-http://127.0.0.1:8080}"
REPO_DIR="${REPO_DIR:-$HOME/sprout}"

if [ ! -d "$REPO_DIR/code/meristem_inference_adapter" ]; then
  echo "adapter source not found under $REPO_DIR" >&2
  exit 1
fi

echo "Starting Sprout inference adapter on :$ADAPTER_PORT"
echo "Upstream llama.cpp: $LLAMACPP_SERVER_URL"
echo "Repo: $REPO_DIR"

docker rm -f "$ADAPTER_CONTAINER" >/dev/null 2>&1 || true

docker run -d \
  --name "$ADAPTER_CONTAINER" \
  --network host \
  -v "$REPO_DIR:/app" \
  -w /app/code/meristem_inference_adapter \
  -e INFERENCE_BACKEND=llamacpp \
  -e ADAPTER_PORT="$ADAPTER_PORT" \
  -e LLAMACPP_SERVER_URL="$LLAMACPP_SERVER_URL" \
  "$ADAPTER_IMAGE" \
  sh -lc 'python -m pip install --no-cache-dir -r requirements.txt >/tmp/adapter_pip.log 2>&1 && python -m src.main' \
  >/tmp/sprout_adapter_container_id.txt

container_id="$(cat /tmp/sprout_adapter_container_id.txt)"
echo "Container: $container_id"

for _ in $(seq 1 90); do
  if curl -fsS "http://127.0.0.1:$ADAPTER_PORT/health" >/tmp/sprout_adapter_health.json 2>/tmp/sprout_adapter_health.err; then
    cat /tmp/sprout_adapter_health.json
    echo
    docker ps --filter "name=$ADAPTER_CONTAINER" --format 'table {{.Names}}\t{{.Status}}'
    exit 0
  fi
  if ! docker ps --filter "name=$ADAPTER_CONTAINER" --format '{{.Names}}' | grep -q "^$ADAPTER_CONTAINER$"; then
    echo "adapter container stopped before health OK" >&2
    docker logs "$ADAPTER_CONTAINER" --tail 160 >&2 || true
    exit 1
  fi
  sleep 5
done

echo "adapter health timeout" >&2
docker logs "$ADAPTER_CONTAINER" --tail 160 >&2 || true
exit 1
