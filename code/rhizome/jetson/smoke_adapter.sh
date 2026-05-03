#!/usr/bin/env bash
set -euo pipefail

ADAPTER_URL="${ADAPTER_URL:-http://127.0.0.1:12000}"
MODEL="${MODEL:-gemma4:e2b}"

python3 - "$ADAPTER_URL" "$MODEL" <<'PY'
import json
import sys
import time
import urllib.request

adapter_url = sys.argv[1].rstrip("/")
model = sys.argv[2]

payload = {
    "model": model,
    "messages": [
        {
            "role": "system",
            "content": "Responde solo JSON valido, sin Markdown fences.",
        },
        {
            "role": "user",
            "content": "Devuelve exactamente un objeto con status ok.",
        },
    ],
    "think": False,
    "options": {"temperature": 0, "num_ctx": 512, "num_predict": 64},
    "stream": False,
}

request = urllib.request.Request(
    f"{adapter_url}/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)

t0 = time.time()
with urllib.request.urlopen(request, timeout=120) as response:
    body = response.read().decode("utf-8")
    elapsed_ms = int((time.time() - t0) * 1000)
    headers = {
        key: value
        for key, value in response.headers.items()
        if key.lower().startswith("sprout-inference-")
    }

print(f"status={response.status}")
print(f"elapsed_ms={elapsed_ms}")
print("sprout_headers=" + json.dumps(headers, ensure_ascii=False, sort_keys=True))
print("body=" + body[:1000])

data = json.loads(body)
content = data.get("message", {}).get("content", "")
json.loads(content)
print("smoke=OK")
PY
