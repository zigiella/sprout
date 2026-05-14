<!-- Main public README · English first · Spanish version: README.es.md -->

🇬🇧 **English** · 🇪🇸 **[Español](README.es.md)**

---

# Sprout

> **Local-first AI water optimization for plots the network forgets.**
> *Open · local · safe · explainable.*

> **Sprout is a safety-bounded decision network for water under absence.**

[Watch the 3-minute video](https://www.youtube.com/watch?v=D9ETS4EPnxI) · [Try the live contract demo](https://sprout.zigiella.com) · [Read the Kaggle writeup](writeup/draft.md) · [Submission guide](SUBMISSION.md)

---

## In 30 seconds

Sprout is a local-first AI architecture for irrigation in remote or weakly connected plots — places where the field, the person and the network rarely coincide in time.

The demo uses pots, a Jetson, an ESP32, an Android phone, a laptop, a 12V pump and real soil readings. The pattern represents something larger: small farms, community gardens, rural plots and peripheral land where water decisions cannot wait for the cloud or for the next human visit.

Sprout distributes intelligence across three Gemma 4 nodes and one physical veto layer:

- **Rhizome** lives in the plot. It runs **Gemma 4 E2B** on Jetson via `llama.cpp`, reads local state and decides whether to irrigate, defer, skip or block.
- **Pollen** lives on the farmer’s Android phone. It runs **Gemma 4 E4B** through **LiteRT-LM**, turns visits and voice into expiring `MissionPatch` objects, and carries context between disconnected plots.
- **Meristem** lives on the farmer’s home laptop. It runs **Gemma 4 E4B** via `llama.cpp`, evaluates bundles and refines durable `PolicyPacket` objects for the next window.
- **ESP32-S3** owns physical safety. It runs custom ESP-IDF firmware and can veto commands before anything touches water.

**The LLM can propose. The physical layer can say no.**

---

## Why Sprout

Irrigation is a timing problem as much as a water problem. A plot can become dry while the farmer is away. A local forecast can change while the network is absent. A human observation can matter more than a sensor, but only when a person actually visits.

Sprout reduces the latency between local evidence and local action.

Instead of assuming permanent connectivity, Sprout uses three time scales:

| Layer | Time scale | Question |
|---|---:|---|
| **Rhizome** | minutes | What should this plot do now? |
| **Pollen** | visit TTL | What human intent and context should enter the plot? |
| **Meristem** | days | What policy should govern the next window? |
| **ESP32** | physical instant | Is this command safe enough to execute? |

---

## Architecture

```text
             Pollen · Android · Gemma 4 E4B · LiteRT-LM
          visit voice → MissionPatch · WeatherDigest · FieldVisit
                                │
                                ▼
        Rhizome · Jetson · Gemma 4 E2B · llama.cpp
           local telemetry → candidate action → DecisionReceipt
                                │
                                ▼
              ESP32-S3 · ESP-IDF firmware · physical veto
                    pump · relay · soil sensor · tank/flow
                                ▲
                                │
        Meristem · home laptop · Gemma 4 E4B · llama.cpp
               bundles → evaluator/tools → PolicyPacket
```

### Invariants

1. **Physical layer prevails.** No LLM can bypass the ESP32.
2. **Every intelligence has jurisdiction.** Rhizome arbitrates, Pollen mediates, Meristem refines.
3. **Every criterion expires.** `MissionPatch`, `WeatherDigest` and `PolicyPacket` objects carry TTL or validity windows.
4. **Deterministic logic decides; Gemma 4 writes rationale and helps formulate criteria.**
5. **Refusal is a feature.** When the system is uncertain, stale or unsafe, it refuses with a legible reason.

---

## What is real vs simulated

Sprout is a hackathon MVP with explicit boundaries.

### Validated paths

- Rhizome local decision loop on Jetson with Gemma 4 E2B via `llama.cpp`.
- Pollen Android app with `demo` and `device` flavors; device path uses LiteRT-LM and Gemma 4 E4B.
- Pollen voice path records `.wav` audio and feeds audio content to the LiteRT-LM device backend.
- Meristem local evaluator and Gemma 4 E4B tool-calling path.
- ESP32-S3 firmware with serial protocol, heartbeat, safety checks, `WATER` `DRY_RUN`, and supervised `PUMP_PULSE` `TEST_ONLY` hardware proof.
- Physical bench path with relay, 12V pump, soil moisture readings and supervised pulses.

### Deliberately conservative boundaries

- Autonomous `WATER` remains conservative in `DRY_RUN` while production semantics are closed.
- Physical actuation is demonstrated through supervised `PUMP_PULSE <ms>` as `TEST_ONLY`.
- The browser demo is a deterministic contract simulator. Real Gemma 4 execution happens in the Android, Jetson and laptop paths documented in this repo.

This distinction is intentional. Sprout values honest safety boundaries over demo theatre.

---

## How Gemma 4 is used

Sprout uses Gemma 4 in concrete, node-specific ways:

### Rhizome — Gemma 4 E2B on Jetson

- Runtime: `llama.cpp`.
- Role: local rationale and arbitration support for a decision already bounded by deterministic gates.
- Constraint: Gemma 4 does not authorize water.

### Pollen — Gemma 4 E4B on Android

- Runtime: Google AI Edge LiteRT-LM.
- Role: multimodal audio input, natural-language mission compilation, refusal/retry for unclear instructions.
- Output: expiring `MissionPatch` objects validated before application.

### Meristem — Gemma 4 E4B on home laptop

- Runtime: `llama.cpp`.
- Role: tool-calling-assisted policy review and explanation.
- Output: durable `PolicyPacket` objects for the next window.

### Configuration work

We tested prompt and runtime configurations before freezing the demo path: context window, output budget, thinking behavior and structured-output stability. One useful finding was that latency often followed what the model wrote, not only what it read. Shorter output budgets improved usability when the contract stayed stable.

---

## Live demo

The public web demo is a **deterministic contract simulator**:

- inspect Rhizome decisions;
- compile Pollen-style mission patches;
- evaluate Meristem-style policy changes;
- see TTLs, receipts and refusal paths.

It does not pretend to run Gemma 4 in the browser. It exists so anyone can experience the architecture without hardware, model downloads, cloud APIs or login.

The real local Gemma 4 paths are documented in:

- `code/pollen/` — Android + LiteRT-LM;
- `code/rhizome/` — Jetson + `llama.cpp`;
- `code/meristem_node/` — laptop + `llama.cpp`;
- `hardware/firmware_esp32/` — physical safety coprocessor.

---

## Reproduce locally

### Meristem, no hardware needed

```bash
cd code/meristem_node
make run
make test
```

### Pollen Android demo flavor

```bash
cd code/pollen
./gradlew assembleDemoDebug
./gradlew testDemoDebugUnitTest
```

Install the demo APK from `demo/` or build locally. The demo flavor uses deterministic inference so it runs without a 3GB model file.

### Pollen device flavor with Gemma 4 E4B

```bash
cd code/pollen
./gradlew assembleDeviceRelease
adb push gemma-4-E4B-it.litertlm /data/local/tmp/gemma-4-E4B-it.litertlm
```

Then open Pollen on Android and select the local model path.

### Rhizome on Jetson

```bash
cd code/rhizome/jetson
./run_runtime.sh safe-cpu
./start_adapter.sh
./smoke_adapter.sh
```

### ESP32 firmware

```bash
cd hardware/firmware_esp32
idf.py set-target esp32s3
idf.py build
idf.py -p /dev/ttyACM0 flash monitor
```

See each component README for full setup.

---

## Repository map

| Path | Purpose |
|---|---|
| `SUBMISSION.md` | Fast path for evaluation: links, proof, what is real vs contract |
| `writeup/` | Kaggle writeup and supporting notes |
| `landing-demo/` | Public deterministic contract demo |
| `code/rhizome/` | Jetson plot node, local decision loop, sync facade |
| `code/pollen/` | Android mobile node, LiteRT-LM path, voice → MissionPatch |
| `code/meristem_node/` | Home laptop slow brain, evaluator, policy composer |
| `hardware/firmware_esp32/` | ESP32 safety coprocessor firmware |
| `docs/` | Architecture, specs, data contracts and safety rules |
| `bitacora/` | Spanish development journal and decision trail |
| `research/` | Evaluation notes, model configuration work and sources |
| `video/` | Video scripts and production notes |

---

## Language note

Sprout was built by a Spanish-speaking team. Public entry points are English-first or bilingual; internal bitácoras and fast-moving specs remain in Spanish by design. This mirrors the product thesis: local intelligence should meet people in the language and context where work actually happens.

---

## Status

Sprout is an MVP, not a production irrigation controller. It demonstrates the core architecture:

- local Gemma 4 reasoning by jurisdiction;
- Android mobile node with LiteRT-LM path;
- edge node with `llama.cpp`;
- laptop slow brain with policy refinement;
- physical ESP32 safety veto;
- signed receipts, TTLs and refusal paths.

Future work includes production `WATER` semantics with flow metering, multi-zone irrigation, solar power, local weather stations, vision evidence and language tuning for local agricultural vocabularies.

---

## License and attribution

Apache 2.0. See [`LICENSE`](LICENSE).

Sprout uses Gemma 4 models by Google. Gemma is a trademark of Google LLC. This project is not affiliated with or endorsed by Google.
