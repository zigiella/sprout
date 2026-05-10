#!/usr/bin/env bash
set -euo pipefail

# Minimal ESP32 profile for the first physical smoke:
# - serial ESP32
# - pump-toggle command mode
# - missing tank sensor allowed but traceable
# - missing flow sensor allowed for MVP observe mode
# - no water execution

export ESP32_MODE="${ESP32_MODE:-serial}"
export ESP32_PORT="${ESP32_PORT:-/dev/ttyACM0}"
export SERIAL_WATER_COMMAND_MODE="${SERIAL_WATER_COMMAND_MODE:-pump-toggle}"
export ALLOW_MISSING_TANK_SENSOR="${ALLOW_MISSING_TANK_SENSOR:-1}"
export REQUIRE_FLOW_SENSOR_FOR_WATER="${REQUIRE_FLOW_SENSOR_FOR_WATER:-0}"
export EXECUTE_WATER=0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/run_steward_once.sh"
