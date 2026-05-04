#!/usr/bin/env bash
set -euo pipefail

FACADE_PORT="${FACADE_PORT:-13010}"
FACADE_HOST="${FACADE_HOST:-0.0.0.0}"
FACADE_PID_FILE="${FACADE_PID_FILE:-/tmp/sprout_rhizome_sync_facade.pid}"
FACADE_LOG_FILE="${FACADE_LOG_FILE:-/tmp/sprout_rhizome_sync_facade.log}"
REPO_DIR="${REPO_DIR:-$HOME/sprout}"

if [ ! -f "$REPO_DIR/code/rhizome/src/rhizome_sync_facade.py" ]; then
  echo "rhizome sync facade source not found under $REPO_DIR" >&2
  exit 1
fi

if [ -f "$FACADE_PID_FILE" ]; then
  old_pid="$(cat "$FACADE_PID_FILE" 2>/dev/null || true)"
  if [ -n "$old_pid" ] && kill -0 "$old_pid" >/dev/null 2>&1; then
    echo "Stopping previous rhizome sync facade pid=$old_pid"
    kill "$old_pid" >/dev/null 2>&1 || true
    sleep 1
  fi
fi

echo "Starting Rhizome sync facade on ${FACADE_HOST}:${FACADE_PORT}"
echo "Repo: $REPO_DIR"
echo "Log: $FACADE_LOG_FILE"

(
  cd "$REPO_DIR/code/rhizome"
  nohup python -m src.rhizome_sync_facade \
    --host "$FACADE_HOST" \
    --port "$FACADE_PORT" \
    >"$FACADE_LOG_FILE" 2>&1 &
  echo $! >"$FACADE_PID_FILE"
)

pid="$(cat "$FACADE_PID_FILE")"
echo "PID: $pid"

for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:$FACADE_PORT/status" >/tmp/sprout_rhizome_sync_facade_status.json; then
    cat /tmp/sprout_rhizome_sync_facade_status.json
    echo
    exit 0
  fi
  if ! kill -0 "$pid" >/dev/null 2>&1; then
    echo "rhizome sync facade stopped before health OK" >&2
    tail -80 "$FACADE_LOG_FILE" >&2 || true
    exit 1
  fi
  sleep 1
done

echo "rhizome sync facade health timeout" >&2
tail -80 "$FACADE_LOG_FILE" >&2 || true
exit 1
