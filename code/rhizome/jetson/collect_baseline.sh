#!/usr/bin/env bash
set -euo pipefail

LLAMA_CONTAINER="${LLAMA_CONTAINER:-sprout-llama-e2b}"
ADAPTER_CONTAINER="${ADAPTER_CONTAINER:-sprout-adapter-12000}"
LLAMA_PORT="${LLAMA_PORT:-8080}"
ADAPTER_PORT="${ADAPTER_PORT:-12000}"

section() {
  printf '\n=== %s ===\n' "$1"
}

run_or_note() {
  if "$@"; then
    return 0
  fi
  rc=$?
  echo "[unavailable rc=$rc] $*" >&2
  return 0
}

section "identity"
run_or_note hostname
run_or_note whoami
run_or_note date --iso-8601=seconds
run_or_note uname -a

section "jetson release"
if [ -f /etc/nv_tegra_release ]; then
  cat /etc/nv_tegra_release
else
  echo "/etc/nv_tegra_release not found"
fi

section "memory"
run_or_note free -h
if [ -r /proc/meminfo ]; then
  grep -E 'MemTotal|MemFree|MemAvailable|SwapTotal|SwapFree|CmaTotal|CmaFree|Huge|Vmalloc' /proc/meminfo || true
fi

section "storage"
run_or_note df -h /
run_or_note lsblk

section "power"
run_or_note nvpmodel -q
if command -v jetson_clocks >/dev/null 2>&1; then
  if [ "$(id -u)" -eq 0 ]; then
    run_or_note jetson_clocks --show
  else
    echo "jetson_clocks available but requires root; skipped"
  fi
else
  echo "jetson_clocks not found"
fi

section "docker"
run_or_note docker --version
if command -v docker >/dev/null 2>&1; then
  docker info 2>/dev/null | grep -E 'Runtimes|Default Runtime|Docker Root Dir|Server Version' || true
  docker ps --filter "name=sprout" --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}' || true
fi

section "sprout health"
run_or_note curl -fsS "http://127.0.0.1:$LLAMA_PORT/health"
echo
run_or_note curl -fsS "http://127.0.0.1:$ADAPTER_PORT/health"
echo

section "container logs tail"
if command -v docker >/dev/null 2>&1; then
  echo "--- $LLAMA_CONTAINER ---"
  docker logs "$LLAMA_CONTAINER" --tail 40 2>/dev/null || true
  echo "--- $ADAPTER_CONTAINER ---"
  docker logs "$ADAPTER_CONTAINER" --tail 40 2>/dev/null || true
fi

section "tegrastats"
if command -v tegrastats >/dev/null 2>&1; then
  timeout 3s tegrastats --interval 1000 || true
else
  echo "tegrastats not found"
fi
