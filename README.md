<!-- Project README · English first · Spanish version: README.es.md -->

🇬🇧 **English** · 🇪🇸 **[Español](README.es.md)**

---

# Sprout

> **AI Local-first water optimization for plots the network forgets.**
> *Safe · explainable · open-source.*

> *"When network is absent — and the human is far — local criteria still irrigate."*

📜 **Read the [technical writeup](writeup/draft.md)** — engineering proof behind the system
🏗️ **Reproduce locally** — see [setup section](#reproduce-locally) below

---

## In 30 seconds

Sprout is a **local-first AI architecture for water optimization in remote plots** — places where the field, the person and the network rarely coincide in time.

Each plot runs **Rhizome**, an autonomous node that decides offline using **Gemma 4 E2B** on a Jetson Orin Nano Super. Rhizome never moves water directly: an **ESP32-S3** with custom firmware enforces hard safety limits and can veto or modulate any action.

When a person visits the plots, **Pollen** runs on Android with **Gemma 4 E4B** (multimodal, audio native via LiteRT-LM). Pollen turns each visit into something more valuable than a sync: it talks with the person, asks Rhizome what happened, validates the local state, compiles human intent, and federates context between plots that have no direct network between them.

**Meristem** runs on the farmer's home laptop with **Gemma 4 E4B** via `llama.cpp`. When things are calm — at the end of the day, in the kitchen, not in the field — Meristem receives the bundles Pollen has carried back, evaluates with **deterministic logic**, and emits a new durable policy. **The LLM only writes the rationale; the decision is auditable down to a concrete rule.**

The result: **better irrigation criteria when the field, the person and the network don't coincide in time.**

---

## Why Sprout

In 2023, **48% of the world's land area suffered at least one month of extreme drought** — the second largest extent since 1951.<sup>[1]</sup> **1.8 billion people are affected by drought worldwide; the cost is $300 billion per year.**<sup>[1]</sup>

In Spain alone, drought cost the agricultural sector **€5.55 billion in 2023**.<sup>[2]</sup> 370,000 hectares of rain-fed cereal in the Mediterranean basin lost between 60% and 90% of their harvest. Two years in a row.<sup>[3]</sup>

But the field for which we design doesn't live in continuous connectivity. Globally, **only 58% of the rural population uses internet — in low-income countries, just 14%.**<sup>[4]</sup>

Sprout exists to bring **operational criteria to plots where you can't be every day, and where you can't always rely on the network.**

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Physical layer (ESP32 firmware) — VETO                         │
│       ↑                                                          │
│  Rhizome (Jetson + Gemma 4 E2B) — minutes                       │
│       ↑                                                          │
│  Pollen (Android + Gemma 4 E4B + audio multimodal) — visit TTL  │
│       ↑                                                          │
│  Meristem (home laptop + Gemma 4 E4B) — days                    │
└─────────────────────────────────────────────────────────────────┘
```

| Node | Question it answers | Hardware | Gemma 4 model | Runtime | Jurisdiction |
|------|---------------------|----------|---------------|---------|--------------|
| **Rhizome** | Should I irrigate now? | Jetson Orin Nano Super (or Raspberry Pi 5) + ESP32-S3 | E2B (it, Q4_K_S) | `llama.cpp` | Minutes |
| **Pollen** | What human criteria + context? | Android device | E4B | LiteRT-LM | Visit with short TTL |
| **Meristem** | What policy for the next window? | Farmer's home laptop (Linux/macOS/Windows) | E4B | `llama.cpp` | Days |
| **ESP32** | Is this command physically safe? | ESP32-S3 N16R8 (or any ESP32-S3 variant) | None — ESP-IDF firmware | — | Physical veto |

**Invariants:**

1. *"Physical layer prevails. Rhizome arbitrates. Pollen mediates. Meristem refines."*
2. No `PolicyPacket` from Meristem can reduce the firmware's hard limits. It can only recommend more conservative behavior.

**Key pattern (validated empirically)**: deterministic logic decides; the LLM only writes the rationale. When GPU offload caused semantic drift in test case RD04 (output: `need_clarification` instead of `ok`), the system did not break — the deterministic Evaluator held the contract while the LLM continued to author safe-but-off-contract prose. **This is the empirical proof of the Safety & Trust thesis.**

---

## How Gemma 4 is used

- **Multimodal audio native** — Pollen feeds raw 16kHz `.wav` directly to Gemma 4 E4B via LiteRT-LM, **without a separate STT pipeline**. Code: `code/pollen/.../PollenVoiceInfra.kt`.
- **Tool calling** — Meristem uses Gemma 4 E4B with native tool calling for `compose_policy(...)` and bundle validation. Mini-battery 5/5 PASS. Code: `code/meristem_node/...`.
- **Three-node routing** — three Gemma 4 instances (E2B + E4B + E4B), three jurisdictions, no cloud roundtrip. Each node holds the context type its layer is responsible for.
- **`safe-cpu` profile contractual** — Rhizome runs Gemma 4 E2B-it Q4_K_S on Jetson CPU (validated 18/18 in battery tests). GPU offload works (36/36 layers) but quality is not contractual yet.

---

## Reproduce locally

### Requirements

- **Laptop** for Meristem. 8GB RAM minimum, 16GB ideal. Linux, macOS or Windows.
- **Jetson Orin Nano Super 8GB** for Rhizome. **Alternative**: Raspberry Pi 5 (with adapted llama.cpp build).
- **ESP32-S3 N16R8 board** (or any ESP32-S3 variant) for the safety firmware. Required — the physical veto layer is part of the architecture, not optional.
- **Android device** for Pollen. Android 12 / API 31+ and 64-bit hardware. For Gemma 4 E4B to run smoothly: **12GB RAM recommended, 16GB ideal, at least 6GB free**. CPU is the stable runtime path; GPU/NPU performance depends heavily on the device.

### Quick start

```bash
git clone https://github.com/zigiella/sprout.git
cd sprout

# 1. Run Meristem locally (no hardware needed)
cd code/meristem_node
make run    # serves on :8000
make test   # runs 13 deterministic tests + LLM smoke

# 2. Run Pollen demo flavor (mock, runs in any emulator or Appetize)
# See code/pollen/README.md for Android Studio setup

# 3. (Optional) Run Rhizome on Jetson
# See code/rhizome/jetson/README.md and run_runtime.sh
```

### Detailed setup

- Meristem-node: [`code/meristem_node/README.md`](code/meristem_node/README.md)
- Pollen Android: [`code/pollen/README.md`](code/pollen/README.md)
- Rhizome Jetson: [`code/rhizome/jetson/`](code/rhizome/jetson/) (see scripts `run_runtime.sh`, `start_adapter.sh`, `smoke_adapter.sh`)
- ESP32 firmware: [`hardware/firmware_esp32/README.md`](hardware/firmware_esp32/README.md)
- Wiring schematics: [`hardware/wiring_diagrams/day19_mounting_schematics.md`](hardware/wiring_diagrams/day19_mounting_schematics.md)

### Installing the model on the phone

The user installs Pollen from the store — the app itself is light (**~15 MB**). On first launch with WiFi, an onboarding screen appears:

> *"Downloading agronomic brain (Gemma 4)..."*

The app uses Android's `DownloadManager` to fetch `gemma-4-E4B-it.litertlm` (3.6 GB) from a secure CDN directly into the app's private internal storage (`/data/data/net.sprout.pollen/files/`). Once the download completes, **the model lives on the device forever and Pollen runs 100% offline** — no further network round-trip.

> Requires: Android 12 / API 31+, 12 GB RAM recommended (16 GB ideal), at least 6 GB free for the model file plus runtime headroom. CPU is the stable runtime path; GPU/NPU varies by device.

> For developers and nightly testers, the `adb push` sideload flow is documented in [`code/pollen/README.md`](code/pollen/README.md).

---

## Project status

- **MVP**: all four nodes operational. Real Pollen ↔ Rhizome chain validated. ESP32 physical veto confirmed on real board. Meristem LLM integration with tool calling closed.
- **Architecture**: invariants stable. Three-node routing with deterministic logic + Gemma 4 LLMs as rationale authors.

---

## Team

**zigiella** — solo developer working with a coordinated team of specialized AI agents (Cambium, Floema, Meristem, Xilema, Corola, Endodermis, Bract, Venation), each with a defined role and identity. The methodology — repo-first, written bitácoras as contract, identity inline for git, day-start coordination messages with explicit `Interrelaciones` template — is documented in [`CONTRIBUTING.md`](CONTRIBUTING.md) and discussed in [writeup §5](writeup/draft.md).

---

## License

[Apache 2.0](LICENSE). Same as Gemma 4.

## Attribution

Sprout uses Gemma 4 models by Google. **Gemma is a trademark of Google LLC.** This project is not affiliated with or endorsed by Google.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Sources

[1] UNCCD — *Global Drought Hotspots Report 2023-2025* + OECD — *Global Drought Outlook 2025*.
[2] COAG / MAPA — Spain agricultural sector losses due to drought 2023.
[3] COAG Castilla y León — Mediterranean basin rain-fed cereal losses 2023-2024.
[4] ITU — *Facts and Figures 2025*: Internet use in urban and rural areas.

(Full references with URLs in [`research/metrics/impact_stats.md`](research/metrics/impact_stats.md).)
