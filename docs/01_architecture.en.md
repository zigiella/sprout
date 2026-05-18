# Sprout architecture

> Local-first AI for water decisions under absence, with bounded, expiring authority, auditable receipts and a physical veto.

This document is the canonical architectural reference for Sprout. It describes the system as it actually exists in [`main`](https://github.com/zigiella/sprout/tree/main) at v1.0 (Gemma 4 Good Hackathon submission), not as it was originally specced. The earlier Spanish working draft is preserved at [`01_architecture.md`](01_architecture.md) as evidence of process.

---

## 1. Definition

Sprout is a local-first AI architecture for water decisions in plots where the field, the human and the network do not coincide in time. Its promise is not to automate a pump. Its promise is to **reduce the latency between local evidence and local action** while preserving auditability and a physical safety floor.

The MVP runs on living pots as proxies for small farms, community gardens, rural school greenhouses and cooperative plots where connectivity and human presence arrive in fragments. The pattern generalises beyond pots: the unit of value is a decision with bounded authority, not a particular crop or hardware bundle.

---

## 2. Operating invariant

```
Physical layer prevails → Rhizome arbitrates → Pollen mediates → Meristem refines.
```

Three corollaries follow from this single invariant:

1. **Physical authority increases near the water.** The ESP32 owns the actuator path (relay + pump). No model, agent or human override can move water without an ESP32 ACK.
2. **Symbolic authority decreases near the water.** Meristem can write durable policy, but cannot execute in the field. Pollen can compile a `MissionPatch`, but only Rhizome can apply it under safety gates.
3. **Every criterion expires.** A `MissionPatch` carries a short TTL (visit-scope). A `PolicyPacket` carries a validity window (policy-scope). A `WeatherDigest` carries a freshness window. Late objects are rejected and logged with a legible reason.

> Every intelligence has jurisdiction. Every authority expires. The physical layer can say no.

---

## 3. Three jurisdictions and one safety floor

### 3.1 Field — Rhizome and ESP32

The field carries **two distinct intelligences** with explicit jurisdictions:

**Rhizome** runs on Jetson Orin Nano Super with **Gemma 4 E2B** via `llama.cpp`. It:

- reads local telemetry from the ESP32 over USB-CDC serial (soil moisture, heartbeat, pump state, plus tank level and flow when those sensors are wired);
- builds a `RhizomeSnapshot` — missing tank or flow readings become explicit `tank_level_unavailable` / `flow_sensor_unavailable` contradictions, not silent zeros;
- applies a deterministic gate (telemetry, active policy, TTL, cooldown, tank state, safety state, execution mode);
- chooses among `WATER`, `DEFER`, `SKIP`, `BLOCK` and `ALERT`;
- emits a candidate action plus a versioned `DecisionReceipt` — the schema reserves a `signature` field; cryptographic signing is wired as a placeholder (`signature=None`) and reserved for a follow-up milestone;
- when configured, asks Gemma 4 E2B to write a short human-readable rationale over the already-closed decision.

**Rhizome does not authorize water.** The decision is closed before Gemma writes anything; Gemma improves the *explanation*, not the *action*. This isolates LLM drift risk from the safety hierarchy.

Two runtime profiles are documented:

- `safe-cpu` — `-ngl 0 --device none --no-op-offload --reasoning off`. The contractual demo path. The Rhizome v0.5 prompt battery reaches 18/18 on this profile. Later sensitivity in the strict-helper RH02 path is documented separately and does not affect the physical action chain. Slow but reliable.
- `gpu-experimental` — `-ngl 99 --fit off --no-op-offload --reasoning off`. Loads 36/36 layers to GPU. Faster but not contractual (RD04 shows safe semantic drift `need_clarification` instead of `ok`). Not promoted to demo.

**ESP32-S3** runs custom **ESP-IDF firmware** and owns the physical layer. Its state machine is `SAFE_IDLE → READY → EXECUTING → DEGRADED → ALERT_LATCHED`. It validates every irrigation command against five canonical hard rules and rejects with a legible reason code if any fails:

- `JETSON_HEARTBEAT_LOST` — validated on real hardware.
- `TANK_LOW` — contract path. The tank level sensor is not wired in the pot MVP; the firmware accepts simulated values via `SET_SENSOR_STUB TANK_LEVEL_PCT` and the rule exercises correctly with stubs.
- `EVENT_DURATION_OUT_OF_RANGE` — validated on real hardware.
- `NO_FLOW_DETECTED` — contract path. The flow sensor is not wired in the pot MVP; same stub mechanism as `TANK_LOW`.
- `ALERT_LATCHED` — validated on real hardware.

The physical bench includes a 12V pump with active-low relay on `GPIO16`, a capacitive soil moisture sensor on `GPIO4 (ADC)` and a `BME280` ambient sensor over I²C on `GPIO8/GPIO9`. Tank level and flow remain stubbed inputs in the MVP — see `30_safety_rules.en.md` and `hardware/firmware_esp32/README.md` for the stub commands.

**Submission boundary:** the autonomous `WATER` command remains conservative in `DRY_RUN`; supervised physical actuation is demonstrated through `PUMP_PULSE <ms>` returning `execution=TEST_ONLY`. Day 27 validated 12 supervised pulses on a real pot with measurable soil moisture drop (raw 2278 → 1289 after pulse). The full hard-rules contract is documented in [`30_safety_rules.en.md`](30_safety_rules.en.md).

### 3.2 Mobile — Pollen

Pollen runs on Android (Pixel 10 Pro) with **Gemma 4 E4B** via Google AI Edge **LiteRT-LM**, with **native multimodal audio**. The app records `.wav` at 16 kHz from the microphone and feeds it directly to the model — there is no separate STT pipeline.

Pollen has two build flavors:

- **`demo` flavor** — deterministic contract evaluator, no model bundled, "D" watermark on the launcher icon, permanent red "DEMO APP — NO LLM" banner, dependency-injected mock clients (`RhizomeMockClient` + `MeristemMockClient`) so the app works offline-first with no Jetson or ESP32 powered on. Voice/chat buttons are blocked with a clear notice pointing to the device flavor.
- **`device` flavor** — real LiteRT-LM pipeline with side-loaded `gemma-4-E4B-it.litertlm` (3.6 GB) in `/data/local/tmp/`. Runs Gemma 4 E4B fully offline on the phone. Requires Android 12+ / API 31+, 12 GB RAM recommended.

Pollen has four responsibilities:

1. **Compile human intent** into a structured `MissionPatch` with a short TTL (the patch belongs to the visit, not to the system forever).
2. **Cross-validate** Rhizome's recent state against direct operator observation, emitting a `ValidationStamp`.
3. **Ferry context** between disconnected Rhizomes, carrying `WeatherDigest`, `FieldVisit`, receipts, validations and mission patches. A phone reaches many places before stable connectivity does.
4. **Translate receipts** into language the operator can act on, when they ask what happened since the last visit.

Pollen's `MiniEvaluator.kt` applies four deterministic checks before any `MissionPatch` is applied:

1. **Schema validation** — the emitted JSON must match the `MissionPatch` contract.
2. **No conflict with hard limits** — the proposed policy cannot violate the firmware safety envelope.
3. **Syntactic-semantic match** — at least one keyword or number from the transcript must appear in the rationale or the patch fields.
4. **Explicit model confidence** — if LiteRT-LM exposes `logprobs`, the threshold is 0.7.

If any check fails, Pollen responds with `REFUSE_RETRY` or `REFUSE_HARD`. **Refusal is a product feature, not a failure.**

### 3.3 Home — Meristem

Meristem runs on a home laptop (FastAPI + SQLite) with **Gemma 4 E4B** via `llama.cpp`. It is the slow brain.

Meristem ingests bundles that Pollen carries from each Rhizome visit (snapshot + `DecisionReceipt` set + `WeatherDigest` + `ValidationStamp`), evaluates them with a deterministic four-rule evaluator (`CONFIRM`, `CONSERVATIVE`, `ALERT`, `REFUSE`), and emits a durable `PolicyPacket` for the next window.

Two critical separations:

- **The evaluator never depends on the model.** The four rules close on facts. Gemma 4 E4B only writes the `rationale` (technical + operator-friendly prose). This isolates model drift from the policy hierarchy.
- **Tool calling can enrich the rationale** of both the operator-facing chat and the `/visit` response (recent-history lookup, cross-target comparison, previous-policy diff). The four-rule evaluator itself never depends on tool output; tool calls are descriptive, not authoritative.

Pollen talks to Meristem either over WebSocket or a parallel HTTP fallback (added after a real field test on day 27). Meristem listens on port 13000. **In v1.0 Pollen exposes a Settings screen** (gear icon on Home) where the user enters Meristem and Rhizome URLs at runtime, persisted via `SharedPreferences`. The Visitar screens read those URLs each time the user opens a node. mDNS / NSD auto-discovery (no manual entry at all) is roadmap for v1.1. **Nothing leaves the home network** — no cloud, no accounts, no telemetry.

A `PolicyPacket` carries a validity window. Its authority belongs to days, not seconds. Rhizome validates it before use. The ESP32 remains above it in the safety hierarchy. Policies emitted by Meristem carry `policy_origin="meristem-batch"` and `policy_scope="durable"`; transient policies generated by Pollen during a visit carry `policy_origin="pollen-visit"` and `policy_scope="transient"` with a maximum TTL of 12 h.

### 3.4 Why not a single controller

Sprout could have been a single Jetson with one model. We chose three jurisdictions because each one solves a problem the others cannot:

| Problem | Solved by | Cannot be solved by |
|---|---|---|
| Decide while the network is absent | Rhizome (field-local) | Pollen (intermittent) · Meristem (eventual) |
| Carry context across disconnected plots | Pollen (mobile ferry) | Rhizome (fixed) · Meristem (home-bound) |
| Refine policy over days with hindsight | Meristem (slow, batch) | Rhizome (real-time) · Pollen (visit-scope) |
| Refuse unsafe commands at the actuator | ESP32 (deterministic firmware) | any LLM, any home laptop |

Three intelligences, four jurisdictions, no cloud roundtrip at any layer.

---

## 4. Data contracts

The MVP runs on **ten JSON contracts**, all documented in [`20_data_contracts.md`](20_data_contracts.md) and exercised by tests in [`code/shared/`](../code/shared/):

| Contract | Origin | Validity | Purpose |
|---|---|---|---|
| `RhizomeSnapshot` | Rhizome | snapshot timestamp + sensor freshness | Current local state of the plot |
| `DecisionReceipt` | Rhizome | permanent (audit trail) | Versioned record of one decision: evidence, candidate, ESP32 outcome, final action, rationale. Schema reserves a `signature` field (currently `None`, signing wired as placeholder for follow-up milestone). |
| `AlertEvent` | Rhizome / ESP32 | until acknowledged | Operator-visible safety event |
| `MissionPatch` | Pollen | short TTL (hours) | Human intent compiled from voice, scoped to the visit |
| `ValidationStamp` | Pollen | snapshot moment | Operator confirmation or dispute of Rhizome state |
| `WeatherDigest` | Pollen (ferried) | freshness window | Weather context from another node or station |
| `VisitAmendment` | Pollen | until consumed | One-shot override during a visit |
| `FieldVisit` | Pollen | snapshot moment | Structured record of a human visit |
| `PolicyPacket` | Meristem | validity window (days) | Durable policy for the next operational window |
| `SyncBundle` | Pollen (transport) | until delivered | Container carrying the above across legs of a visit |

Every contract carries explicit authority and explicit expiry. **No old criterion silently governs water.**

---

## 5. Authority model

### 5.1 Priority order

When sources conflict, authority flows in this order (highest first):

1. Physical stop / `ALERT_LATCHED`
2. ESP32 hard limits (the five rules)
3. Rhizome's active policy
4. Pollen `VisitAmendment` (in-visit override)
5. `MissionPatch` (visit-scope policy)
6. Non-binding suggestions (e.g. `ShadowSkeptic` objections)

Documented in [`30_safety_rules.en.md`](30_safety_rules.en.md) §4.

### 5.2 The dual-agent pattern

Inside Rhizome, two local agents run in parallel over the same `RhizomeSnapshot`:

- The **Operational Steward** closes the decision through deterministic gates and emits the `DecisionReceipt`. It is authoritative.
- **`ShadowSkeptic`** audits the decision and writes objections with `affects_decision=false`. It is observational only — it never irrigates, vetoes, rewrites the final action or touches the ESP32 path.

The boundary is intentional. The second agent gives Sprout a precise local jurisdiction: observe, question, record. Each disagreement becomes a measurable event. Proven recurring objections can later be promoted into deterministic gates. **Even skepticism has jurisdiction.**

Both the Operational Steward and the `ShadowSkeptic` class live in `code/rhizome/src/rhizome_steward.py`. Skeptic observations are stored under `~/.local/share/sprout/rhizome_steward/shadow_skeptic/YYYY-MM-DD.jsonl`.

### 5.3 Why no model touches the valve

The cleanest one-line statement of the safety architecture:

> Gemma proposes — the deterministic gate decides — the ESP32 executes — the receipt records.

If any of those four pieces is bypassed, the system is no longer Sprout.

---

## 6. Decision flow (end-to-end)

A typical irrigation decision moves through this chain:

```
1. ESP32 emits TELEMETRY  (sensors + heartbeat)
2. Rhizome reads telemetry  → RhizomeSnapshot
3. Rhizome applies deterministic gates  (policy, TTL, cooldown, tank, safety)
4. Optional: ShadowSkeptic logs objection  (affects_decision=false)
5. Rhizome chooses candidate action  → DRY_RUN, WATER_A (single physical plot in MVP), DEFER, SKIP, BLOCK or ALERT
6. Optional: Gemma 4 E2B writes rationale  (over already-closed decision)
7. Rhizome emits command to ESP32  → over serial
8. ESP32 validates against five hard rules
9. ESP32 ACK / REJECT  → with reason code
10. Rhizome persists versioned DecisionReceipt  (signature reserved, `None` in MVP)
11. Pollen visits Rhizome (next time the human walks by)
12. Pollen pulls /summary/since · /receipts · /snapshot/latest
13. Pollen optionally compiles voice → MissionPatch (with TTL)
14. Mini Evaluator validates MissionPatch (four deterministic checks)
15. Pollen POSTs MissionPatch to Rhizome /policy (TTL ≤ 12h, scope=transient)
16. Rhizome activates transient policy for next decision window
17. Pollen carries SyncBundle home to Meristem (eventual)
18. Meristem evaluates bundle (four-rule evaluator) → PolicyPacket
19. Optional: Gemma 4 E4B enriches PolicyPacket rationale via tool calling (over already-closed evaluation)
20. PolicyPacket returns to Rhizome via Pollen on the next visit
```

Steps 1–10 are real-time, local, and never require the network. Steps 11–16 are visit-scoped. Steps 17–20 are eventual.

---

## 7. Runtime profiles

| Node | Hardware | Model | Runtime | Notes |
|---|---|---|---|---|
| Rhizome | Jetson Orin Nano Super | Gemma 4 E2B (Q4_K_S) | `llama.cpp` | `safe-cpu` contractual; `gpu-experimental` for iteration only |
| Pollen | Pixel 10 Pro (Android 12+) | Gemma 4 E4B (Q4_K_M) | LiteRT-LM (Google AI Edge) | Native multimodal audio; demo flavor uses mock; device flavor side-loads model |
| Meristem | Home laptop | Gemma 4 E4B (Q4_K_M, ~5 GB) | `llama.cpp` (`llama-server`) | Adapter tool-calling capability validated day 14; end-to-end with E4B + `tool_calls_recovered_from_text=1` validated day 26 (smoke v6) |
| ESP32 | ESP32-S3 N16R8 | n/a (no model) | ESP-IDF | Five hard rules; state machine; physical veto |

`llama.cpp` is the shared runtime for Rhizome and Meristem — two distinct resource-constrained deployments serviced by the same binary family. LiteRT-LM is the only path for native audio multimodal Gemma 4 on Android in 2026.

A model-configuration result shaped the demo path: in the Meristem path, output length drove latency more strongly than input context. Shorter structured outputs preserved the contract and improved usability. Each node has a different model profile because each jurisdiction has different output requirements:

- Rhizome: short, stable, bounded outputs over deterministic decisions.
- Pollen: audio understanding, refusal, schema fidelity, low latency.
- Meristem: policy review, tool calling, longer rationale, batched.

---

## 8. What is real vs what is contract

We are explicit about the boundary between **validated execution** and **contract demonstration**:

### Validated on physical hardware

- Rhizome on Jetson Orin Nano Super running Gemma 4 E2B (Q4_K_S) via `llama.cpp` — Rhizome v0.5 `safe-cpu` battery reached 18/18 envelope-valid + status-match. Later strict-helper RH02 sensitivity is documented separately and does not affect the physical action path.
- ESP32-S3 firmware on real hardware — state machine `SAFE_IDLE / READY / EXECUTING / DEGRADED / ALERT_LATCHED`. Three of the five hard rules are exercised against real sensors (`JETSON_HEARTBEAT_LOST`, `EVENT_DURATION_OUT_OF_RANGE`, `ALERT_LATCHED`); `TANK_LOW` and `NO_FLOW_DETECTED` are contract paths exercised via `SET_SENSOR_STUB` (tank/flow sensors are not wired in the pot MVP).
- End-to-end Pollen ↔ Rhizome ↔ ESP32 — HTTP polling from Android to Jetson; Rhizome decides locally; commands flow to ESP32; ESP32 validates and (in supervised mode) actuates a 12V pump on a real pot.
- 12 supervised water pulses observed and recorded on day 27 pilot run, with `ACCEPT_ESP32_TEST_ONLY_PULSE_AS_EXECUTED=1` enabled after operator-validated supervision. Soil moisture raw reading dropped from 2278 to 1289 after the pulse series, consistent with water reaching the substrate.
- Meristem deterministic four-rule evaluator — 5/5 mini-battery PASS on day 24 (evaluator only, no model required).
- Meristem end-to-end with Gemma 4 E4B + tool calling — day 26 smoke v6 ran successfully with `tool_calls_recovered_from_text=1` on the `chat_alert` path.

### Contract demonstrated in repo + browser

- The browser landing demo at `landing-demo/` runs deterministic mocks (code in `landing-demo/js/api.js`) so a judge can inspect contracts without downloading models. The mocks are intentionally deterministic, not "fake".
- All ten JSON contracts of the MVP are documented in [`20_data_contracts.md`](20_data_contracts.md). The core subset (`RhizomeSnapshot`, `DecisionReceipt`, `MissionPatch`, `ValidationStamp`, `WeatherDigest`, `PolicyPacket`) is exercised by tests in `code/shared/`; the remaining contracts (`AlertEvent`, `VisitAmendment`, `FieldVisit`, `SyncBundle`) are documented and instantiated in code but not yet covered by dedicated tests.

### Natural extensions noted

- `SAFETY_DOWNGRADE` (capping a valid command to a safer envelope instead of rejecting it) — defined in the contract; the firmware currently rejects with `EVENT_DURATION_OUT_OF_RANGE` when out of bounds. Modulation ("AI asked 30s → final 12s") is the natural next step once the flow sensor closes the operational loop.
- GPU offload on Jetson — 36/36 layers load successfully, but quality is not contractual under one test case (`RD04` derives semantically). The contractual path of the demo is `safe-cpu`.
- Full-duplex audio in Pollen (the phone also speaks back) — only input audio is implemented. Output audio is roadmap.

---

## 9. Out of scope (honest)

- **Production `WATER` semantics with flow-loop closure.** The MVP keeps autonomous `WATER` in `DRY_RUN`; supervised actuation runs via `PUMP_PULSE` `TEST_ONLY`. Closing the loop with a real flowmeter is the next milestone.
- **Multi-zone simultaneous irrigation.** The architecture supports it (multiple plots, multiple Rhizomes). The physical MVP runs on one Rhizome with one ESP32 and a single physical sensing path on one pot; `rhizome_02` is a host-side simulation for the multi-Rhizome interoperability demo, not a second physical node.
- **Solar power.** Currently mains-powered; the bench includes no solar harvest.
- **Vision evidence as authoritative.** Camera input is planned to add visible plant evidence; in the MVP it is non-authoritative.
- **Fine-tuned Gemma 4 for local agricultural vocabularies.** Scaffolded in `code/finetune/` (Unsloth path) but not in the MVP.
- **Production deployment automation.** No CI/CD pipeline for APK distribution; binaries are built locally and attached to the GitHub Release manually.
- **mDNS / NSD auto-discovery in the Pollen Android client.** v1.0 ships a Settings screen for manual URL entry; automatic discovery via Android `NsdManager` of services announced as `_sprout-meristem._tcp` and `_sprout-rhizome._tcp` is roadmap for v1.1.

---

## 10. Where to read next

| Topic | Document |
|---|---|
| Safety rules (the five hard limits + priority order) | [`30_safety_rules.en.md`](30_safety_rules.en.md) |
| JSON contracts (the ten objects, fields, validity) | [`20_data_contracts.md`](20_data_contracts.md) |
| Rhizome node spec | [`10_rhizome_spec.md`](10_rhizome_spec.md) |
| Pollen node spec | [`11_pollen_spec.md`](11_pollen_spec.md) |
| Meristem node spec | [`12_meristem_spec.md`](12_meristem_spec.md) |
| ESP32 firmware spec | [`13_esp32_spec.md`](13_esp32_spec.md) |
| Gemma 4 naming compliance | external Google guidelines summary in [`external/README.md`](external/README.md) (canonical Sprout compliance audit) |
| Rhizome runtime on Jetson | [`../code/rhizome/jetson/README.md`](../code/rhizome/jetson/README.md) |
| Pollen Android app | [`../code/pollen/README.md`](../code/pollen/README.md) |
| Meristem service | [`../code/meristem_node/README.md`](../code/meristem_node/README.md) |
| ESP32 firmware | [`../hardware/firmware_esp32/README.md`](../hardware/firmware_esp32/README.md) |
| Project writeup (EN) | [`../writeup/draft.md`](../writeup/draft.md) |
| Submission guide for reviewers | [`../SUBMISSION.md`](../SUBMISSION.md) |

---

## Note on language

This document is canonical English. The original Spanish working draft (day-15 era, pre-ShadowSkeptic, pre-Mini-Evaluator) is preserved at [`01_architecture.md`](01_architecture.md) as evidence of process. Internal bitácoras and decision trails continue in Spanish under [`../bitacora/`](../bitacora/). See the [Language note in the root README](../README.md#language-note) for the project-wide policy.

The canonical refusal codes (`TANK_LOW`, `JETSON_HEARTBEAT_LOST`, `EVENT_DURATION_OUT_OF_RANGE`, `NO_FLOW_DETECTED`, `ALERT_LATCHED`) are identifiers in code and are not translated.
