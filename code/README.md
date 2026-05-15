# code/

All Sprout software. Each subproject has its own README with dependencies, how to run, and how to test.

## Subprojects

| Folder | What it is | Language | Target | Owner |
|--------|------------|----------|--------|-------|
| `rhizome/` | Plot edge node | Python 3.11 | Jetson Orin Nano Super | Dev Rhizome + specialist |
| `pollen/` | Roaming node | Kotlin (Android) | Pixel 10 Pro | Dev Pollen |
| `meristem/` | Local strategic node | Python 3.11 | Laptop (Mac mini in the future) | Dev Meristem |
| `simulator/` | Network visualization (2/4/8 nodes) | Python / web | browser | flexible |
| `shared/` | JSON schemas + common protocols | JSON + pydantic + kotlinx | both | coordinated |
| `finetune/` | Unsloth fine-tuning of Gemma 4 E2B | Python / notebooks | Colab | Dev Meristem |

## Data flow between subprojects

```
Rhizome  <--BLE/WiFi Direct-->  Pollen  <--local WiFi / opportunistic cloud-->  Meristem
   |                                                                                |
   +------------------ all consume and produce schemas from shared/ ----------------+
```

## Common prerequisites

- Python 3.11+
- Ollama installed and running (`ollama pull gemma4:e4b` minimum for Meristem)
- Android Studio (only for Pollen)
- JetPack 6.x on the Jetson (only for Rhizome)

## Environment variables

See `.env.example` in each subproject. **Never** commit a real `.env`.

Relevant variable across all subprojects:
- `SHADOW_ENABLED=false` by default (only enable shadow Meristem in development)

Only if `SHADOW_ENABLED=true`:
- `GEMINI_API_KEY=<your-key-from-aistudio.google.com/apikey>`

## How to run the full system locally (mature phase)

```bash
# Terminal 1: Meristem
cd code/meristem && python -m src.main

# Terminal 2: Rhizome (or on the Jetson)
cd code/rhizome && python -m src.main

# Mobile: install the Pollen APK on the Pixel 10 Pro
```

Detail in each subproject's README.
