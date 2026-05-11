#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/sprout}"
STEWARD_STATE_DIR="${STEWARD_STATE_DIR:-$HOME/.local/share/sprout/rhizome_steward}"
STEWARD_LOG_FILE="${STEWARD_LOG_FILE:-/tmp/sprout_rhizome_steward.log}"
STEWARD_PID_FILE="${STEWARD_PID_FILE:-/tmp/sprout_rhizome_steward.pid}"

if [ -f "$STEWARD_PID_FILE" ]; then
  old_pid="$(cat "$STEWARD_PID_FILE" 2>/dev/null || true)"
  if [ -n "$old_pid" ] && kill -0 "$old_pid" >/dev/null 2>&1; then
    echo "Stopping previous Rhizome steward pid=$old_pid"
    kill "$old_pid" >/dev/null 2>&1 || true
    sleep 1
  fi
fi

mkdir -p "$(dirname "$STEWARD_LOG_FILE")" "$STEWARD_STATE_DIR"

echo "Starting Rhizome Steward v0"
echo "Repo: $REPO_DIR"
echo "State: $STEWARD_STATE_DIR"
echo "Log: $STEWARD_LOG_FILE"
echo "ESP32_MODE=${ESP32_MODE:-fake}"
echo "EXECUTE_WATER=${EXECUTE_WATER:-0}"

(
  cd "$REPO_DIR/code/rhizome/jetson"
  nohup env STEWARD_COMMAND=run-loop ./run_steward_once.sh >"$STEWARD_LOG_FILE" 2>&1 &
  echo $! >"$STEWARD_PID_FILE"
)

pid="$(cat "$STEWARD_PID_FILE")"
echo "PID: $pid"
sleep 1
tail -20 "$STEWARD_LOG_FILE" || true
