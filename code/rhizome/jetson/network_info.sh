#!/usr/bin/env bash
set -euo pipefail

HOSTNAME_SHORT="$(hostname)"
MDNS_HOST="${MDNS_HOST:-${HOSTNAME_SHORT}.local}"
PRIMARY_IP="${PRIMARY_IP:-}"

if [ -z "$PRIMARY_IP" ]; then
  PRIMARY_IP="$(hostname -I | tr ' ' '\n' | grep -E '^192\.168\.' | head -n 1 || true)"
fi

if [ -z "$PRIMARY_IP" ]; then
  PRIMARY_IP="$(hostname -I | tr ' ' '\n' | grep -Ev '^(127\.|172\.17\.|$)' | head -n 1 || true)"
fi

if [ -z "$PRIMARY_IP" ]; then
  PRIMARY_IP="<jetson-ip>"
fi

active_wifi="$(
  nmcli -t -f NAME,DEVICE,TYPE connection show --active 2>/dev/null \
    | awk -F: '$3 == "802-11-wireless" {print $1 " (" $2 ")"; exit}'
)"

echo "Rhizome Jetson network"
echo "Hostname: ${HOSTNAME_SHORT}"
echo "mDNS: ${MDNS_HOST}"
echo "Active WiFi: ${active_wifi:-unknown}"
echo "IPs: $(hostname -I | xargs)"
echo
echo "Preferred stable URLs (try these first):"
echo "  rhizome_01 -> http://${MDNS_HOST}:13010/"
echo "  rhizome_02 -> http://${MDNS_HOST}:13020/"
echo
echo "Current IP fallback:"
echo "  rhizome_01 -> http://${PRIMARY_IP}:13010/"
echo "  rhizome_02 -> http://${PRIMARY_IP}:13020/"
echo
echo "Health checks from the Jetson:"
for port in 13010 13020; do
  if curl -fsS "http://127.0.0.1:${port}/status" >/tmp/sprout_network_info_${port}.json 2>/dev/null; then
    echo "  :${port} OK $(cat /tmp/sprout_network_info_${port}.json)"
  else
    echo "  :${port} not responding locally"
  fi
done

cat <<'TXT'

If Pollen cannot reach the .local URLs on a new WiFi, use the current IP
fallback. Some guest/mobile networks block multicast DNS even when normal HTTP
works.
TXT
