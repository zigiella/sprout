#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/sprout}"
STEWARD_STATE_DIR="${STEWARD_STATE_DIR:-$HOME/.local/share/sprout/rhizome_steward}"
STEWARD_FACADE_DATA_DIR="${STEWARD_FACADE_DATA_DIR:-$STEWARD_STATE_DIR/facade_data}"
ESP32_MODE="${ESP32_MODE:-fake}"
ESP32_PORT="${ESP32_PORT:-/dev/ttyACM0}"
SERIAL_WATER_COMMAND_MODE="${SERIAL_WATER_COMMAND_MODE:-water-duration}"
EXECUTE_WATER="${EXECUTE_WATER:-0}"
ALLOW_MISSING_TANK_SENSOR="${ALLOW_MISSING_TANK_SENSOR:-0}"
REQUIRE_FLOW_SENSOR_FOR_WATER="${REQUIRE_FLOW_SENSOR_FOR_WATER:-0}"
NODE_ID="${NODE_ID:-rhizome_01}"
SYNC_FACADE_STATE_DIR="${SYNC_FACADE_STATE_DIR:-/tmp/sprout_rhizome_sync_facade/$NODE_ID}"
DECISION_INTERVAL_S="${DECISION_INTERVAL_S:-900}"
COOLDOWN_S="${COOLDOWN_S:-7200}"
WATER_SECONDS="${WATER_SECONDS:-8}"
MAX_AUTONOMOUS_WATERS_PER_DAY="${MAX_AUTONOMOUS_WATERS_PER_DAY:-2}"
MAX_TOTAL_BYTES="${MAX_TOTAL_BYTES:-67108864}"
RETENTION_DAYS="${RETENTION_DAYS:-120}"
SOIL_DRY_BELOW_PCT="${SOIL_DRY_BELOW_PCT:-35}"
SOIL_WET_ABOVE_PCT="${SOIL_WET_ABOVE_PCT:-55}"
SOIL_DRY_BELOW_RAW="${SOIL_DRY_BELOW_RAW:-}"
SOIL_WET_ABOVE_RAW="${SOIL_WET_ABOVE_RAW:-}"
SOIL_RAW_POLARITY="${SOIL_RAW_POLARITY:-low_is_dry}"
SOIL_WET_BELOW_RAW="${SOIL_WET_BELOW_RAW:-}"
SOIL_DRY_ABOVE_RAW="${SOIL_DRY_ABOVE_RAW:-}"
GEMMA_RATIONALE_URL="${GEMMA_RATIONALE_URL:-}"
STEWARD_COMMAND="${STEWARD_COMMAND:-run-once}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

ARGS=(
  "$STEWARD_COMMAND"
  --node-id "$NODE_ID"
  --state-dir "$STEWARD_STATE_DIR"
  --facade-data-dir "$STEWARD_FACADE_DATA_DIR"
  --sync-facade-state-dir "$SYNC_FACADE_STATE_DIR"
  --esp32 "$ESP32_MODE"
  --decision-interval-s "$DECISION_INTERVAL_S"
  --cooldown-s "$COOLDOWN_S"
  --water-seconds "$WATER_SECONDS"
  --max-autonomous-waters-per-day "$MAX_AUTONOMOUS_WATERS_PER_DAY"
  --max-total-bytes "$MAX_TOTAL_BYTES"
  --retention-days "$RETENTION_DAYS"
  --soil-dry-below-pct "$SOIL_DRY_BELOW_PCT"
  --soil-wet-above-pct "$SOIL_WET_ABOVE_PCT"
  --soil-raw-polarity "$SOIL_RAW_POLARITY"
)

if [ "$ESP32_MODE" = "serial" ]; then
  ARGS+=(--serial-port "$ESP32_PORT" --serial-water-command-mode "$SERIAL_WATER_COMMAND_MODE")
fi

if [ "$EXECUTE_WATER" = "1" ]; then
  ARGS+=(--execute-water)
fi

if [ "$ALLOW_MISSING_TANK_SENSOR" = "1" ]; then
  ARGS+=(--allow-missing-tank-sensor)
fi

if [ "$REQUIRE_FLOW_SENSOR_FOR_WATER" = "1" ]; then
  ARGS+=(--require-flow-sensor-for-water)
fi

if [ -n "$SOIL_DRY_BELOW_RAW" ]; then
  ARGS+=(--soil-dry-below-raw "$SOIL_DRY_BELOW_RAW")
fi

if [ -n "$SOIL_WET_ABOVE_RAW" ]; then
  ARGS+=(--soil-wet-above-raw "$SOIL_WET_ABOVE_RAW")
fi

if [ -n "$SOIL_WET_BELOW_RAW" ]; then
  ARGS+=(--soil-wet-below-raw "$SOIL_WET_BELOW_RAW")
fi

if [ -n "$SOIL_DRY_ABOVE_RAW" ]; then
  ARGS+=(--soil-dry-above-raw "$SOIL_DRY_ABOVE_RAW")
fi

if [ -n "$GEMMA_RATIONALE_URL" ]; then
  ARGS+=(--gemma-rationale-url "$GEMMA_RATIONALE_URL")
fi

cd "$REPO_DIR/code/rhizome"
"$PYTHON_BIN" -m src.rhizome_steward "${ARGS[@]}"
