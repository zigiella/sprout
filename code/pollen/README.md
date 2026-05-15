# pollen/

**Abstract.** Pollen is the mobile edge-node of the Sprout agricultural ecosystem, built as an Android application for the Pixel 10 Pro. It operates as the "roaming brain" of the farm, acting as an offline bridge between the home Meristem server and the field Rhizome plot nodes. Pollen handles synchronous data transport via local HTTP APIs and relies entirely on on-device LLM inference using Gemma 4 E4B. By integrating native 16 kHz `.wav` audio capture with Google's `LiteRT-LM` framework, Pollen enables multimodal, natural-language interactions with farm operators directly in the field with **zero reliance on cloud connectivity**. It validates agricultural policies, records field observations, and evaluates voice commands deterministically before syncing back to the base station.

**Build flavors:**
- **`demo` flavor** — Uses a deterministic mock evaluator to simulate model decisions instantly. Ideal for UI testing, fast iteration, and emulator deployments without requiring heavy model downloads or specific hardware.
- **`device` flavor** — The production-ready hardware path. Integrates the real `LiteRT-LM` pipeline bound to an on-device Gemma 4 E4B model. Requires Android 12+ (API 31+) and a device with NPU/GPU capabilities for interactive generation speeds.

---

Android application for the Pixel 10 Pro. Pollen is the **roaming node** of the Sprout system.

## Role

- Local sync with Rhizome via **HTTP polling** over WiFi (Rhizome exposes a read-only HTTP facade on the Jetson).
- On-device inference with **Gemma 4 E4B via LiteRT-LM** (Google AI Edge), with **native multimodal audio**: the app records `.wav` at 16 kHz from the microphone and feeds it directly to the model, bypassing a separate STT pipeline.
- Compilation of human intent into a structured `MissionPatch` with expiry.
- Cross-validation (`ValidationStamp`) of Rhizome state against direct operator observation.
- Physical transport of context (`WeatherDigest`, `MissionPatch`) to Meristem between visits.

Full detail in [`docs/11_pollen_spec.md`](../../docs/11_pollen_spec.md).

## Stack

- **Kotlin** + Jetpack Compose for the UI.
- **LiteRT-LM Android** (`com.google.ai.edge.litertlm:litertlm-android`) for Gemma 4 E4B inference with multimodal audio.
- **`kotlinx.serialization`** for JSON schemas (shared with `code/shared/schemas/`).
- **Ktor / OkHttp** for HTTP polling against Rhizome and Meristem.

## Build flavors

The app builds in two distinct flavors:

| Flavor | Use case | Inference | Model required | Build |
|--------|----------|-----------|----------------|-------|
| **`demo`** | Emulator, low-resource devices, UI walkthrough without a model | Deterministic mock LiteRT | None | `./gradlew assembleDemoDebug` |
| **`device`** | Pixel 10 Pro or any Android 12+ device with local Gemma 4 E4B | Real LiteRT-LM | `gemma-4-E4B-it.litertlm` (3.6 GB) side-loaded via ADB | Local build |

The split lives in `app/src/demo/.../llm/LiteRtInfra.kt` (mock) vs `app/src/device/.../llm/LiteRtInfra.kt` (real LiteRT-LM with `sendAudioFile()`).

## How to run the device build with real Gemma 4 E4B

1. **Build** the `deviceRelease` variant from `code/pollen/`:
   ```bash
   ./gradlew assembleDeviceRelease
   ```
2. **Download the model** compatible with LiteRT-LM (`gemma-4-E4B-it.litertlm`) from Kaggle or HuggingFace.
3. **Side-load the model** via ADB:
   ```bash
   adb push gemma-4-E4B-it.litertlm /data/local/tmp/gemma-4-E4B-it.litertlm
   ```
4. **Install the APK** and open the app. On first run, on the **"Download Manager"** screen:
   - Tap **"Skip (model already on device)"**.
   - Confirm the path `/data/local/tmp/gemma-4-E4B-it.litertlm` (or change it if you pushed elsewhere).
   - Tap **"Confirm"**.
5. **Permissions**: the app will request microphone access to process voice commands. Accept it to test the audio → `MissionPatch` flow.

Device requirements:
- Android 12 / API 31+
- 12 GB RAM recommended, 16 GB ideal
- At least 6 GB free storage
- CPU runtime is the stable path; GPU/NPU performance varies by device

## Structure (real, post-day-27)

```
pollen/
├── README.md
├── build.gradle.kts
├── settings.gradle.kts
├── gradlew + gradle/wrapper/   # Gradle 9.3.1 via wrapper
└── app/
    ├── build.gradle.kts        # demo + device flavors
    └── src/
        ├── main/kotlin/net/sprout/pollen/
        │   ├── MainActivity.kt
        │   ├── voice/          # PollenVoiceInfra.kt + AudioClipRecorder.kt
        │   ├── llm/            # SystemPrompts (real engines live in flavors)
        │   ├── inference/      # MiniEvaluator (deterministic guard rails)
        │   ├── schemas/        # MissionPatch, WeatherDigest, ValidationStamp, FieldVisit, etc.
        │   ├── sync/           # RhizomeMockClient + real HTTP clients
        │   └── ui/             # HomeScreen, VisitarRhizomeScreen, VisitarMeristemScreen, VoiceBetaPanel, ChatFeature
        ├── demo/kotlin/net/sprout/pollen/llm/LiteRtInfra.kt    # deterministic mock
        ├── device/kotlin/net/sprout/pollen/llm/LiteRtInfra.kt  # real LiteRT-LM
        └── test/kotlin/net/sprout/pollen/
            ├── inference/MiniEvaluatorTest.kt   # REFUSE_RETRY, REFUSE_HARD, APPLY_AS_IS, APPLY_CONSERVATIVE
            └── schemas/RoundTripTest.kt          # JSON ↔ Kotlin validation
```

## Local build

Requirements: **Android SDK 34**, **JDK 17**, **Gradle 9.3.1+** (included in the wrapper).

```bash
cd code/pollen
./gradlew assembleDebug            # debug APK (default demo flavor)
./gradlew assembleDeviceRelease    # device flavor APK (real LiteRT-LM)
./gradlew testDebugUnitTest        # JVM unit tests
```

If you don't have a local Android SDK: **use CI**. Every PR against `main` that touches `code/pollen/**` triggers [the workflow](../../.github/workflows/pollen-ci.yml), which builds and runs tests on an Ubuntu runner with the SDK.

## CI

Workflow: [`.github/workflows/pollen-ci.yml`](../../.github/workflows/pollen-ci.yml).

Triggers on:
- `push` to `feat/pollen-**` branches
- `pull_request` to `main` when it touches `code/pollen/**` or the workflow itself

Runs (using the local wrapper, guaranteeing Gradle 9.3.1):
- `./gradlew assembleDebug` — builds the debug APK
- `./gradlew testDebugUnitTest` — JVM unit tests

Test reports are uploaded as an artifact (`pollen-test-reports`) for post-failure inspection.

**Hard rule:** a PR with red CI does not get merged. Documented in CONTRIBUTING §9.

## Anti-nonsense logic (Mini Evaluator)

`MiniEvaluator.kt` applies four deterministic checks before applying any `MissionPatch` proposed by the LLM:

1. **Schema validation** — the emitted JSON must match the `MissionPatch` contract.
2. **No conflict with hard limits** — the proposed policy cannot violate the firmware safety envelope.
3. **Syntactic-semantic match** — at least one keyword or number from the transcript must appear in the rationale or the patch fields.
4. **Explicit model confidence** — if LiteRT-LM exposes `logprobs`, the threshold is 0.7.

If any check fails, Pollen responds with `REFUSE_RETRY` or `REFUSE_HARD` (four cases covered in `MiniEvaluatorTest.kt`). **Refusal is a product feature, not a failure.**

## Journal pointers

Relevant working journal entries:
- `bitacora/2026-04-27_draft-issue-litertlm-thinking_floema.md` — first LiteRT-LM attempt, initial issues.
- `bitacora/2026-05-01_litertlm-pixel10pro-compatibility_floema.md` — Pixel 10 Pro validation.
- `bitacora/2026-05-12_PR-voice-beta-final_floema.md` — consolidated description of the voice-beta-final PR.
- `research/04_litertlm_thinking_pt1.md`, `pt2`, `digest` — comparative LiteRT-LM vs MediaPipe research.

---

## Note on language

This README is English-first. Internal bitácoras (Spanish-language working journals) and the day-by-day development trace live under [`bitacora/`](../../bitacora/). See the [Language note in the root README](../../README.md#language-note) for the project-wide policy.
