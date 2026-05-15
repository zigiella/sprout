# Credits

Sprout was built for The Gemma 4 Good Hackathon.

## Models and runtimes

- **Gemma 4** by Google.
- **Gemma 4 E2B** in the Rhizome edge path on Jetson Orin Nano Super, served via `llama.cpp`.
- **Gemma 4 E4B** in the Pollen Android path on Pixel 10 Pro, served via Google AI Edge **LiteRT-LM** with native multimodal audio.
- **Gemma 4 E4B** in the Meristem laptop path, served via `llama.cpp` with tool calling.

## Open-source dependencies

Sprout's source code is released under Apache 2.0 and depends only on OSI-approved open source:

- **`llama.cpp`** (MIT) — local inference runtime for Rhizome and Meristem.
- **Google AI Edge `LiteRT-LM`** (Apache 2.0) — on-device LLM runtime for Pollen Android.
- **ESP-IDF** by Espressif (Apache 2.0) — ESP32-S3 firmware framework.
- **Bosch `BME280_SensorAPI`** (BSD-3-Clause) — I²C driver for the ambient sensor.
- **FastAPI**, **Pydantic**, **SQLite** — Meristem service stack.
- **Kotlin**, **Jetpack Compose**, **`kotlinx.serialization`**, **Ktor**, **OkHttp** — Pollen Android stack.
- **NVIDIA JetPack 6.x** — Jetson Orin Nano Super platform.

## Production assets

- **Video footage and photographs:** produced by the Sprout team in Castellar de n'Hug, Catalonia, Spain.
- **Voice-over:** generated with ElevenLabs from the Sprout script, under the platform's commercial use terms.
- **Typography:** **Manrope** (sans, by Mikhail Sharanda, SIL OFL) and **IBM Plex Mono** (by IBM, SIL OFL).
- **Brand and design system:** original work by the Sprout team, with explicit visual-brand separation from Gemma 4 (see [`docs/external/README.md`](docs/external/README.md)).
- **Prototype location:** Castellar de n'Hug, Catalonia, Spain.

## Team

See the [Team section in the README](README.md#team) for human and AI-agent attributions, and [`CONTRIBUTING.md`](CONTRIBUTING.md) for the development methodology.

## Trademarks

**Gemma is a trademark of Google LLC.** Sprout is not affiliated with or endorsed by Google. The Gemma 4 naming and attribution guidelines published by Google are followed throughout this project — see [`docs/external/README.md`](docs/external/README.md).

## License

Apache 2.0 — see [`LICENSE`](LICENSE).

If selected as a Prize winner of The Gemma 4 Good Hackathon, the Sprout team grants the Competition Sponsor the CC-BY 4.0 license on the winning Submission and source code, per §1.6 and §2.5 of the Competition Rules.
