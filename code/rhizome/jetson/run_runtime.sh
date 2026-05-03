#!/usr/bin/env bash
set -euo pipefail

PROFILE="${1:-safe-cpu}"

LLAMA_IMAGE="${LLAMA_IMAGE:-ghcr.io/nvidia-ai-iot/llama_cpp:latest-jetson-orin}"
LLAMA_CONTAINER="${LLAMA_CONTAINER:-sprout-llama-e2b}"
LLAMA_PORT="${LLAMA_PORT:-8080}"
MODEL_PATH="${MODEL_PATH:-$HOME/sprout_models/gemma-4-E2B-it-Q4_K_S.gguf}"
CTX_SIZE="${CTX_SIZE:-2048}"
BATCH_SIZE="${BATCH_SIZE:-128}"
UBATCH_SIZE="${UBATCH_SIZE:-128}"
N_GPU_LAYERS="${N_GPU_LAYERS:-99}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found" >&2
  exit 1
fi

if [ ! -f "$MODEL_PATH" ]; then
  echo "model not found: $MODEL_PATH" >&2
  echo "Expected Gemma 4 E2B Q4_K_S GGUF under \$HOME/sprout_models." >&2
  exit 1
fi

case "$PROFILE" in
  safe-cpu)
    LLAMA_ARGS=(
      llama-server
      -m /models/model.gguf
      -c "$CTX_SIZE"
      -ngl 0
      --device none
      --no-op-offload
      --reasoning off
      --host 0.0.0.0
      --port "$LLAMA_PORT"
    )
    ;;
  gpu-experimental)
    LLAMA_ARGS=(
      llama-server
      -m /models/model.gguf
      -c "$CTX_SIZE"
      -b "$BATCH_SIZE"
      -ub "$UBATCH_SIZE"
      -ngl "$N_GPU_LAYERS"
      --fit off
      --no-op-offload
      --reasoning off
      --host 0.0.0.0
      --port "$LLAMA_PORT"
    )
    ;;
  *)
    echo "unknown profile: $PROFILE" >&2
    echo "valid profiles: safe-cpu | gpu-experimental" >&2
    exit 1
    ;;
esac

echo "Starting Rhizome llama-server profile=$PROFILE port=$LLAMA_PORT"
echo "Image: $LLAMA_IMAGE"
echo "Model: $MODEL_PATH"

docker rm -f "$LLAMA_CONTAINER" >/dev/null 2>&1 || true

docker run -d \
  --name "$LLAMA_CONTAINER" \
  --runtime=nvidia \
  --network host \
  -v "$MODEL_PATH:/models/model.gguf:ro" \
  "$LLAMA_IMAGE" \
  "${LLAMA_ARGS[@]}" >/tmp/sprout_llama_container_id.txt

container_id="$(cat /tmp/sprout_llama_container_id.txt)"
echo "Container: $container_id"

for _ in $(seq 1 90); do
  if curl -fsS "http://127.0.0.1:$LLAMA_PORT/health" >/tmp/sprout_llama_health.json 2>/tmp/sprout_llama_health.err; then
    cat /tmp/sprout_llama_health.json
    echo
    docker ps --filter "name=$LLAMA_CONTAINER" --format 'table {{.Names}}\t{{.Status}}'
    exit 0
  fi
  if ! docker ps --filter "name=$LLAMA_CONTAINER" --format '{{.Names}}' | grep -q "^$LLAMA_CONTAINER$"; then
    echo "llama container stopped before health OK" >&2
    docker logs "$LLAMA_CONTAINER" --tail 160 >&2 || true
    exit 1
  fi
  sleep 5
done

echo "llama health timeout" >&2
docker logs "$LLAMA_CONTAINER" --tail 160 >&2 || true
exit 1
