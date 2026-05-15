# Sprout — Kaggle Gemma 4 Good Hackathon submission

> **Sprout is a safety-bounded decision network for water under absence.**
> When the field, the human and the network do not coincide in time, Sprout brings local Gemma 4 reasoning to the plot, the visit, and the farmer's home — each with strict jurisdiction and expiry.

---

## Quick links

| Asset | Where |
|-------|-------|
| **Video (≤ 3 min)** | https://www.youtube.com/watch?v=D9ETS4EPnxI |
| **Landing demo** | https://sprout.zigiella.com |
| **Repository** | https://github.com/zigiella/sprout |
| **Writeup** | [`writeup/draft.md`](writeup/draft.md) (1467 words, also submitted as Kaggle draft) |
| **Pollen demo build** | `cd code/pollen && ./gradlew assembleDemoDebug` — mock LiteRT inference, no 3 GB model needed |
| **Pollen device build** | `cd code/pollen && ./gradlew assembleDeviceRelease` — real Gemma 4 E4B via LiteRT-LM, model side-loaded with `adb push` |
| **License** | Apache 2.0 |
| **Gemma 4 attribution** | *Sprout uses Gemma 4 models by Google. Gemma is a trademark of Google LLC. This project is not affiliated with or endorsed by Google.* |

---

## What you'll see, in 30 seconds

Sprout distributes irrigation decisions across **three Gemma 4 nodes with different jurisdictions**, with an **ESP32 safety coprocessor** that owns the physical layer:

- **Rhizome** — Jetson Orin Nano Super + Gemma 4 E2B via `llama.cpp`. Decides offline whether to irrigate. Never moves water directly.
- **Pollen** — Android + Gemma 4 E4B via LiteRT-LM (native audio multimodal). Turns each human visit into a structured `MissionPatch`.
- **Meristem** — Farmer's home laptop + Gemma 4 E4B via `llama.cpp` with tool calling. Refines durable policy when things are calm.
- **ESP32-S3** — Custom ESP-IDF firmware. The only piece that can authorize physical actuation. Vetoes commands that violate hard limits.

Three invariants govern the system:

1. **Physical safety prevails.** No LLM can bypass the ESP32.
2. **Every intelligence has jurisdiction.** Rhizome acts in minutes, Pollen in visit TTL, Meristem in days.
3. **Every criterion expires.** A `MissionPatch`, `WeatherDigest` or `PolicyPacket` is never silently valid forever.

---

## What is real vs what is contract

We want to be very explicit about this distinction. A hackathon project that overclaims loses more than one that underdelivers — so this section is the contract between us and the judge.

### Validated on physical hardware

- **Rhizome on Jetson Orin Nano Super** running Gemma 4 E2B (Q4_K_S) via `llama.cpp`. Battery of 18 prompts, 18/18 envelope-valid + status-match.
- **ESP32-S3 firmware** in real hardware. State machine `SAFE_IDLE / READY / EXECUTING / DEGRADED / ALERT_LATCHED`. Rejects out-of-range duration, lost heartbeat, low tank, latched alert.
- **End-to-end Pollen ↔ Rhizome ↔ ESP32**: HTTP polling from the Android app to the Jetson; Rhizome decides locally; commands flow to the ESP32 which validates and (in supervised mode) actuates a 12V pump on a real pot.
- **12 real water pulses** observed and recorded during day 27 pilot run, with `ACCEPT_ESP32_TEST_ONLY_PULSE_AS_EXECUTED=1` enabled after operator-validated supervision.
- **Meristem deterministic evaluator + Gemma 4 E4B tool calling** with 5/5 mini-battery PASS and end-to-end runtime with `tool_calls_recovered_from_text=1`.

### Contract demonstrated in repo + browser

- The **browser landing demo** at `landing-demo/` runs **deterministic mocks** (code in `landing-demo/js/api.js`, read it) so a judge can inspect the contracts without downloading models or using cloud APIs. The mocks are intentionally deterministic, not "fake" — they let you scrutinize the shape of every JSON object the real system produces.
- **All ten JSON contracts** of the MVP (`RhizomeSnapshot`, `DecisionReceipt`, `AlertEvent`, `MissionPatch`, `ValidationStamp`, `WeatherDigest`, `VisitAmendment`, `FieldVisit`, `PolicyPacket`, `SyncBundle`) are documented in `docs/20_data_contracts.md` and exercised by tests in `code/shared/`.

### Apuntado para extensión natural

- **`SAFETY_DOWNGRADE` rule** (capping a valid command to a safer envelope instead of rejecting it): defined in the contract; the firmware currently rejects with `EVENT_DURATION_OUT_OF_RANGE` when out of bounds. Modulation (e.g. *"AI asked 30s → final 12s"*) is the natural next step once the flow sensor closes the operational loop.
- **GPU offload** on Jetson: 36/36 layers loaded successfully, but quality is not contractual under one test case (`RD04` derives semantically). The contractual path of the demo is `safe-cpu`.
- **Full-duplex audio** in Pollen (the phone also speaks back): only input audio is implemented. Output audio is roadmap.

---

## How to reproduce the system

### Browser landing demo

```bash
git clone https://github.com/zigiella/sprout
cd sprout/landing-demo
# serve as static site, e.g.
python -m http.server 8000
# open http://localhost:8000
```

### Meristem (no hardware needed)

```bash
cd code/meristem_node
make run    # serves on :8000
make test   # runs deterministic tests + LLM smoke
```

### Pollen on Android — demo flavor (no model needed)

Build the demo flavor and install it on any Android 12+ device or emulator:

```bash
cd code/pollen
./gradlew assembleDemoDebug
adb install app/build/outputs/apk/demo/debug/app-demo-debug.apk
```

Mock LiteRT inference — walks through the UI without needing a 3 GB model on disk.

### Pollen on Android — device flavor (real Gemma 4 E4B via LiteRT-LM)

The device flavor uses the official Google AI Edge dependency `com.google.ai.edge.litertlm:litertlm-android` and consumes raw `.wav` audio directly through `LiteRtInfra.kt::sendAudioFile()`.

1. Build the `deviceRelease` variant from `code/pollen/`.
2. Download the LiteRT-LM-compatible Gemma 4 E4B model (e.g. `gemma-4-E4B-it.litertlm`) from Kaggle/HuggingFace.
3. Push the model to the device:
   ```bash
   adb push gemma-4-E4B-it.litertlm /data/local/tmp/gemma-4-E4B-it.litertlm
   ```
4. Launch the app. On first run, choose **"Skip (Model already on device)"** and confirm the path `/data/local/tmp/gemma-4-E4B-it.litertlm`.
5. Grant microphone permission. Speak in Spanish or English; the app compiles the utterance into a `MissionPatch` with expiry.

Requirements: Android 12 / API 31+, 12 GB RAM recommended (16 GB ideal), at least 6 GB free.

### Rhizome on Jetson Orin Nano Super

See [`code/rhizome/jetson/README.md`](code/rhizome/jetson/README.md) for `run_runtime.sh`, `start_adapter.sh`, `smoke_adapter.sh`. The `safe-cpu` profile is the contractual one.

### ESP32 firmware

See [`hardware/firmware_esp32/README.md`](hardware/firmware_esp32/README.md). Built with ESP-IDF for ESP32-S3.

---

## Repository map for a judge with limited time

If you only have **5 minutes**:

1. Watch the 3-minute video (link above).
2. Read [`writeup/draft.md`](writeup/draft.md).
3. Open the landing demo and try one Rhizome decision + one Pollen voice compile.

If you have **30 minutes**:

4. Read [`docs/01_architecture.md`](docs/01_architecture.md) for the three-node design.
5. Read [`docs/30_safety_rules.md`](docs/30_safety_rules.md) for the ESP32 hard limits.
6. Run `make test` in `code/meristem_node/` to see the deterministic evaluator + LLM smoke pass.
7. Build and install the Pollen demo flavor: `cd code/pollen && ./gradlew assembleDemoDebug && adb install app/build/outputs/apk/demo/debug/app-demo-debug.apk`.

If you have **2 hours and want to scrutinize**:

8. Build the Pollen device flavor and side-load Gemma 4 E4B as described above.
9. Read `code/rhizome/src/rhizome_steward.py` for the deterministic gate that runs before the LLM ever writes a rationale.
10. Read `hardware/firmware_esp32/main/app_main.c` for the safety state machine.

---

## Why Gemma 4

Each node receives a model sized for its environment:

- **E2B on Jetson** for Rhizome — small enough to leave headroom, instructed enough to produce useful rationales.
- **E4B on Android via LiteRT-LM** for Pollen — the only path for native audio multimodal in a pocket device.
- **E4B on a home laptop via `llama.cpp`** for Meristem — large enough for tool calling and policy reasoning, slow enough for the calm of evening review.

Three Gemma 4 instances, three jurisdictions, **no cloud roundtrip at any layer**. The deterministic logic decides; Gemma writes the rationale. This separation is what makes the system both refusable and auditable.

---

## Tracks

We submit primarily to **Main Track** for vision + execution. The architecture is also a natural fit for:

- **Global Resilience** — drought + dispersed agriculture + intermittent connectivity, with a working pattern that brings the decision to where the water lives.
- **Safety & Trust** — auditable decisions, signed receipts, expiring contracts, physical veto. Every refusal is a product feature, not a failure.

---

## License and winner grant

The Sprout repository is licensed under **Apache 2.0** (see [`LICENSE`](LICENSE)) — an OSI-approved permissive license. All third-party dependencies used to generate this Submission are OSI-approved open source (`llama.cpp`, LiteRT-LM, FastAPI, Pydantic, SQLite, ESP-IDF, Bosch `BME280_SensorAPI`).

If the Submission is selected as a Prize winner, the team agrees to grant the Competition Sponsor the **CC-BY 4.0** license on the winning Submission and source code, in accordance with §1.6 and §2.5 of the Competition Rules. The repository will continue to be available to the public under Apache 2.0; the CC-BY 4.0 grant is in addition, not in replacement.

Sprout uses Gemma 4 models by Google. **Gemma is a trademark of Google LLC.** This project is not affiliated with or endorsed by Google. The Gemma 4 model naming and attribution guidelines (Google) are followed throughout the public surfaces (README, writeup, landing demo, video, node READMEs).

---

## Team

Sprout was built by **zigiella + a coordinated set of role-specialized agents** (Cambium, Floema, Xilema, Endodermis, Meristem, Corola, Bract, Venation) during the 30-day window of the Gemma 4 Good Hackathon. The bitácora (`bitacora/`) documents every architectural decision, course correction and dependency between frentes.

---

*Built on Gemma 4 by Google. Gemma is a trademark of Google LLC. Apache 2.0.*
