#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/sprout}"

cd "$(dirname "$0")"

echo "Starting demo Rhizome facades on one Jetson."
echo "This is an explicit video/demo simulation, not two physical ESP32 nodes."

FACADE_NODE_ID=rhizome_01 \
FACADE_PORT=13010 \
REPO_DIR="$REPO_DIR" \
./start_sync_facade.sh

FACADE_NODE_ID=rhizome_02 \
FACADE_PORT=13020 \
FACADE_DATA_DIR="$REPO_DIR/code/rhizome/demo_data/rhizome_02" \
REPO_DIR="$REPO_DIR" \
./start_sync_facade.sh

echo "Smoke rhizome_01 (:13010)"
FACADE_URL=http://127.0.0.1:13010 ./smoke_sync_facade.sh

echo "Smoke rhizome_02 (:13020)"
FACADE_URL=http://127.0.0.1:13020 ./smoke_sync_facade.sh

cat <<'TXT'
Demo endpoints:
  rhizome_01 -> http://192.168.1.60:13010/
  rhizome_02 -> http://192.168.1.60:13020/

Document in video/writeup: rhizome_02 is simulated on the same Jetson to show
multi-Rhizome sync behavior. It does not represent a second physical ESP32.
TXT
