# code/

Todo el software de Sprout. Cada subproyecto tiene su propio README con dependencias, como correr, como probar.

## Subproyectos

| Carpeta | Que es | Lenguaje | Target | Responsable |
|---------|--------|----------|--------|-------------|
| `rhizome/` | Nodo edge en parcela | Python 3.11 | Jetson Orin Nano Super | Dev Rhizome + especialista |
| `pollen/` | Nodo itinerante | Kotlin (Android) | Pixel 10 Pro | Dev Pollen |
| `meristem/` | Nodo estrategico local | Python 3.11 | Portatil (Mac mini en futuro) | Dev Meristem |
| `simulator/` | Visualizacion de red (2/4/8 nodos) | Python / web | navegador | flexible |
| `shared/` | Schemas JSON + protocolos comunes | JSON + pydantic + kotlinx | ambos | coordinado |
| `finetune/` | Fine-tuning Unsloth de Gemma 4 E2B | Python / notebooks | Colab | Dev Meristem |

## Flujos de datos entre subproyectos

```
Rhizome  <--BLE/WiFi Direct-->  Pollen  <--WiFi local / cloud opportunistic-->  Meristem
   |                                                                                |
   +------------------- todos consumen y producen schemas de shared/ ---------------+
```

## Pre-requisitos comunes

- Python 3.11+
- Ollama instalado y corriendo (`ollama pull gemma4:e4b` minimo para Meristem)
- Android Studio (solo para Pollen)
- JetPack 6.x en Jetson (solo para Rhizome)

## Variables de entorno

Ver `.env.example` en cada subproyecto. **Nunca** commitear `.env` real.

Variable relevante para todos:
- `SHADOW_ENABLED=false` por defecto (activa Meristem sombra solo en desarrollo)

Solo si `SHADOW_ENABLED=true`:
- `GEMINI_API_KEY=<tu-key-de-aistudio.google.com/apikey>`

## Como correr el sistema completo localmente (fase madura)

```bash
# Terminal 1: Meristem
cd code/meristem && python -m src.main

# Terminal 2: Rhizome (o en el Jetson)
cd code/rhizome && python -m src.main

# Movil: instalar APK de pollen/ en el Pixel 10 Pro
```

Detalle en los READMEs de cada subproyecto.
