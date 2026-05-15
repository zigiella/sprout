# rhizome/

**Abstract.** Rhizome is the plot node. In the current MVP it runs on Jetson Orin Nano Super and operates offline-first: it reads local telemetry from the ESP32-S3 over serial, builds `RhizomeSnapshot` objects, applies deterministic safety and irrigation-need gates, and writes every outcome as a `DecisionReceipt`. When configured, Gemma 4 E2B via `llama.cpp` is used only to produce short human-readable rationales and visit summaries for Pollen; **it does not authorize water**. The deterministic gate decides whether an action is eligible, and the ESP32 owns the physical veto and pump execution boundary. Pollen consumes Rhizome through the local HTTP sync facade. Camera/vision, multi-zone control, and learning are outside the critical MVP path.

## Role

- Reads local telemetry from the ESP32-S3 over serial (soil moisture, tank level, heartbeat, pump state).
- Builds a `RhizomeSnapshot` and applies deterministic safety and need gates.
- Persists `DecisionReceipt` objects with evidence, active policy, candidate action, ESP32 outcome, final action and rationale.
- When configured, asks Gemma 4 E2B via `llama.cpp` for a short natural-language rationale (it does not authorize water).
- Serves the local HTTP facade for Pollen (`GET /summary/since?locale=es|en`, `GET /explain/decision/<id>`, `POST /visit`).
- `ShadowSkeptic` records objections from a second agent with `affects_decision=false`.

## Current stack (MVP)

- Python 3.11.
- **`llama.cpp`** with Gemma 4 E2B-it Q4_K_S (`safe-cpu` is the contractual profile; `gpu-experimental` offloads 36/36 layers to GPU for iteration).
- `pydantic` for schemas.
- Communication with ESP32-S3 over USB-CDC serial.
- Rotated persistence (`retention_days=120`, `max_total_bytes=64 MiB`).
- `decisions_by_rule` exposed on `/health` for exercised traceability.

## Actual structure (post-day-28)

```
rhizome/
├── README.md
├── Makefile
├── bench/                  # reproducible benchmark harness
├── benchmarks/             # versioned harness results
├── requirements.txt
├── src/
│   ├── main.py             # main loop
│   ├── sensors.py          # moisture / flow / level reading
│   ├── vision.py           # capture + preprocessing
│   ├── policy_engine.py    # applies the active policy with the LLM
│   ├── safety.py           # ESP32 handshake
│   ├── llm_client.py       # Ollama client
│   ├── sync_server.py      # BLE/WiFi endpoint for Pollen
│   └── persistence.py      # local SQLite
├── policies/               # active policies (JSON with schema)
│   └── examples/
└── tests/
```

## Pending

Full briefing in `docs/10_rhizome_spec.md` (to be written by Cambium + Jetson specialist).

## Local benchmark

While the Jetson is being delivered, the `#5` benchmark is prepared and validated on a laptop:

```bash
cd code/rhizome
make generate-prompts
make test
python -m bench.run_ollama_benchmark --model gemma4:e4b --hardware-label hp-probook-460-g11
```

The same harness is then reused on the Jetson, swapping only the model/runtime target.

## Local API for Pollen

The Rhizome spec defines a read-only API so Pollen can visit the plot without depending on Android mocks:

- `GET /status`
- `GET /snapshot/latest`
- `GET /receipts?since=...`
- `GET /explain/decision/{id}`
- `GET /summary/since?since=...&locale=es|en`
- `POST /policy`
- `GET /policy/active`

As an MVP step, `src/rhizome_sync_facade.py` serves those endpoints from local JSON files shaped like the shared contract (`code/shared/schemas/examples`). It is an interoperability facade: it does not touch the ESP32, does not open actuators, does not call the LLM and does not replace Rhizome's real persistence. Its value is letting Floema point `RhizomeNetworkClient` at a real Jetson IP while the definitive sensor/SQLite backend is being closed.

`/summary/since` is the endpoint behind Pollen's main button: "What has happened since I was away?". In the demo MVP it composes a deterministic summary with:

- counts of waterings, blocks and alerts;
- severity `ok | attention | alert`;
- current state of the tank and the A/B soil probes;
- a brief recommendation;
- locale `es` or `en`.

It does not use the LLM yet. This is intentional: it unblocks UX with a testable, safe piece. The natural evolution is for Gemma 4 E2B to help write that summary over already-aggregated data, without changing facts or decisions.

`POST /policy` receives the transient policy Pollen generates during a visit, for example from the voice → policy beta. The endpoint:

- only accepts `PolicyPacket` with `policy_origin="pollen-visit"`;
- normalizes `policy_scope` to `transient`;
- requires `target_node_id` equal to the facade's `node_id`;
- requires `valid_until` with a maximum TTL of 12 h;
- persists the policy as active for the next decision;
- does not validate physical hard limits.

That last line is intentional. The facade is only a schema gate and host-side persistence; hard limits live in Pollen's Mini-Evaluator before the policy is sent and in the ESP32 when Rhizome tries to execute an action.

Local / Jetson boot:

```bash
cd code/rhizome
python -m src.rhizome_sync_facade --host 0.0.0.0 --port 13010
```

Minimum check:

```bash
curl http://127.0.0.1:13010/status
curl http://127.0.0.1:13010/snapshot/latest
curl http://127.0.0.1:13010/receipts
curl "http://127.0.0.1:13010/summary/since?locale=es"
```

Policy smoke from the Jetson:

```bash
cd code/rhizome/jetson
./smoke_policy.sh
```

Base URL for Pollen on day-19 local network:

```text
http://192.168.1.60:13010/
```

For video / demo a second Rhizome can be simulated on the same Jetson:

```bash
cd code/rhizome/jetson
./start_demo_two_rhizomes.sh
```

This brings up:

```text
rhizome_01 -> http://192.168.1.60:13010/
rhizome_02 -> http://192.168.1.60:13020/
```

`rhizome_02` uses `code/rhizome/demo_data/rhizome_02`. It must be documented as a multi-Rhizome interoperability simulation, not as a second physical node.

## Rhizome Steward v0

`src/rhizome_steward.py` closes the minimal autonomous loop for a supervised pot pilot:

```text
ESP32 TELEMETRY -> snapshot -> safety/need gate -> optional Gemma rationale
-> optional WATER -> DecisionReceipt -> rotated logs -> facade_data
```

Safety properties:

- does not send `WATER` unless `--execute-water` is passed;
- never exceeds `30s` per event (`FIRMWARE_MAX_WATER_SECONDS_MVP`);
- applies local cooldown before watering again;
- limits autonomous events per day;
- if it does not understand the moisture reading, it defers;
- if the tank drops below the minimum, it emits `ALERT`;
- if there is no tank sensor, by default it defers unless the minimal-profile permission is explicit;
- if a reading is missing, the snapshot preserves a valid schema and marks `pending_contradictions`;
- `ShadowSkeptic` is experimental and does not affect the decision.

Run without hardware:

```bash
cd code/rhizome
python -m src.rhizome_steward run-once --esp32 fake
```

Run against real ESP32, single pass, still without opening water:

```bash
python -m src.rhizome_steward run-once \
  --esp32 serial \
  --serial-port /dev/ttyACM0
```

Run with explicit permission to send `WATER A <seconds>` to the ESP32:

```bash
python -m src.rhizome_steward run-once \
  --esp32 serial \
  --serial-port /dev/ttyACM0 \
  --execute-water \
  --water-seconds 8
```

If the moisture probe is not yet calibrated to a percentage, use raw thresholds:

```bash
python -m src.rhizome_steward run-once \
  --esp32 serial \
  --serial-port /dev/ttyACM0 \
  --soil-dry-below-raw 1500 \
  --soil-wet-above-raw 2600
```

Minimal pot hardware profile:

```bash
python -m src.rhizome_steward run-once \
  --esp32 serial \
  --serial-port /dev/ttyACM0 \
  --allow-missing-tank-sensor \
  --soil-dry-below-raw 1500 \
  --soil-wet-above-raw 2600
```

This profile exists for a minimal ESP32 with pump and moisture sensor while flowmeter and tank level are planned but not yet installed. If watering is allowed without tank sensing, the receipt keeps `tank_level_unavailable`; if the flowmeter is missing, it keeps `flow_sensor_unavailable`. Once those sensors exist, drop the flag and run in strict mode.

If moisture arrives as a raw value, polarity must be declared. The real probe from Xilema's handoff reports `soil_a_raw < 1300` as very moist soil, so first observe-mode uses `--soil-raw-polarity low_is_wet` and `--soil-wet-below-raw 1300`. Xilema fixes for the MVP:

```text
SOIL_RAW_POLARITY=low_is_wet
SOIL_WET_BELOW_RAW=1300
SOIL_DRY_ABOVE_RAW=2200
```

Interpretation:

- `<1300`: very moist, `SKIP`;
- `1300..2199`: ambiguous band, `DEFER`;
- `>=2200`: dry for the MVP, candidate for `WATER_A` if the other guardrails pass.

If the minimal firmware exposes the safe physical pulse `PUMP_PULSE <ms>`, use:

```bash
python -m src.rhizome_steward run-once \
  --esp32 serial \
  --serial-port /dev/ttyACM0 \
  --serial-water-command-mode pump-pulse
```

Do not use `pump-toggle` with the day-26 firmware: that build does not expose `PUMP_ON`, and Xilema authorizes the `PUMP_PULSE` path. `water-duration` is still valid for builds that execute `WATER A <seconds>` physically at the ESP32 boundary; in the current build `WATER A 1` replies `execution=DRY_RUN`.

If an ESP32 build physically moves the pump but keeps `execution=TEST_ONLY` in the `PUMP_PULSE` ACK, Rhizome does not count it as real watering by default. For the supervised profile validated on a pot by Bea, explicitly enable:

```bash
ACCEPT_ESP32_TEST_ONLY_PULSE_AS_EXECUTED=1
```

This keeps the ESP32 raw lines in `execution_details`, but prevents Pollen from showing the event as blocked by `ESP32_TEST_ONLY`.

Default persistence:

```text
~/.local/share/sprout/rhizome_steward/
├── telemetry_samples/YYYY-MM-DD.jsonl
├── decision_receipts/YYYY-MM-DD.jsonl
├── shadow_skeptic/YYYY-MM-DD.jsonl
├── current_snapshot.json
├── last_decision_receipt.json
└── facade_data/
```

The store applies per-day retention and a total byte budget (`--retention-days`, `--max-total-bytes`) so it can run for weeks / months without overflowing the microSD. So Pollen can see the real loop, start the facade with:

```bash
python -m src.rhizome_sync_facade \
  --host 0.0.0.0 \
  --port 13010 \
  --data-dir ~/.local/share/sprout/rhizome_steward/facade_data
```

Gemma 4 E2B can come in as the contractual rationale writer through the adapter:

```bash
python -m src.rhizome_steward run-once \
  --esp32 serial \
  --serial-port /dev/ttyACM0 \
  --gemma-rationale-url http://127.0.0.1:12000
```

Gemma does not change the action or authorize water; it only improves the explanation over already-decided facts.

### Data returned to Pollen

Rhizome always returns JSON. Pollen can choose language with `?locale=en` or `?locale=es`; if not specified, the fallback is `es`.

Language architecture decision:

- The system reasons in contracts, not in the UI language.
- Operational fields (`action`, `executed`, `blocked_reason`, amounts, timestamps, veto codes) are not translated.
- Rhizome can return localized narrative for the MVP, but the source of truth remains the `DecisionReceipt`.
- Pollen is the layer responsible for linguistic experience. Its local Gemma 4 can translate only the narrative that does not arrive already localized, based on the active UI language.
- This separation allows Pollen, in the future, to use fine-tuning or local adaptation for minority languages (for example Pular, Swahili or Wolof) without asking Rhizome to change its irrigation logic or its contracts.

Main endpoints:

```text
GET /snapshot/latest
GET /receipts?since=<UTC_ZULU>
GET /explain/decision/<decision_id>?locale=en|es
GET /summary/since?since=<UTC_ZULU>&locale=en|es
```

`/receipts` returns a near-canonical `DecisionReceipt`: `action`, `executed`, `blocked_reason`, `action_params`, `confidence`, `rationale_short`, `rationale_full`, `backend_used`, `contradictions`. Pollen must treat `executed=false` as a non-executed proposal, even when `action` is `WATER_A`.

`/explain/decision/<id>` returns a localized explanation built from the receipt. If Gemma 4 participated earlier in the steward, that explanation includes the `rationale_*` written by Gemma in the receipt. Otherwise it uses a deterministic rationale.

`/summary/since` returns the payload for the main "absence" button:

```json
{
  "headline": "...",
  "summary": "...",
  "highlights": ["..."],
  "recommendation": "...",
  "counts": {
    "total": 2,
    "water": 1,
    "water_proposed": 2,
    "water_not_executed": 1,
    "block": 0,
    "alert": 0,
    "executed": 1
  },
  "source": "deterministic_visit_summary",
  "simulation": false
}
```

Gemma 4 is not the source of truth for these fields. Its correct role is to write a better `rationale_short` / `rationale_full` and, as a next step, to synthesize an absence narrative from already-validated snapshots and receipts.

#### Optional Gemma 4 narrator

The facade can use a local Gemma 4 E2B as the narrator for the absence button:

```bash
GEMMA_VISIT_NARRATOR_URL=http://127.0.0.1:12000 \
GEMMA_VISIT_NARRATOR_MODEL=gemma4:e2b \
./start_sync_facade.sh
```

When enabled, Gemma can only rewrite `headline`, `summary`, `highlights` and `recommendation`. It cannot change `counts`, `severity`, `source`, `simulation`, receipts or snapshots. If Gemma fails, takes too long or returns invalid JSON, the response falls back to the deterministic summary.

E2B configuration: Rhizome's Gemma uses `num_predict=1024` to avoid silent fallbacks from truncated E2B responses.

Traceability fields:

```json
{
  "source": "deterministic_visit_summary",
  "narrative_source": "gemma_visit_narrator",
  "gemma_narrator": {
    "enabled": true,
    "used": true,
    "model": "gemma4:e2b"
  }
}
```

---

## Note on language

This README is English-first. Internal bitácoras (Spanish-language working journals) and the day-by-day development trace live under [`bitacora/`](../../bitacora/). See the [Language note in the root README](../../README.md#language-note) for the project-wide policy.
