# code/tuning/

Batería local de tuning de prompts y configuraciones para Pollen (Gemma 4 E4B).

Objetivo: aprender qué calidad de respuesta produce el modelo bajo distintas
palancas (system prompt, ventana de contexto, thinking, tamaño de respuesta,
idioma, acumulación de KV cache), en un stack local que se aproxima lo más
posible al runtime LiteRT-LM real que Floema construye en Pollen.

Autora v0: Meristem. Encargo de Bea (2026-04-24).

## Stack

```
harness.py  →  http://localhost:11434  (meristem_inference_adapter en modo local)
                        ↓
              http://localhost:11435  (ollama serve, gemma4:e4b)
```

El adapter emite headers `Sprout-Inference-*` uniformes (ver
`code/meristem_inference_adapter/README.md`). El harness los recolecta y
guarda con el body completo y la metadata de la run.

## Mapeo LiteRT-LM → Ollama

Resumen. Detalle completo en
`bitacora/2026-04-24_pollen-tuning-v0-diseno_meristem.md`.

| Palanca LiteRT-LM | Réplica en Ollama |
|---|---|
| `extraContext["enable_thinking"]` | parámetro `think: bool` |
| "piensa brevemente" en system | texto en `system` |
| canal thinking separado | `message.thinking` vs `message.content` en body |
| `maxNumTokens=4096` (ventana total) | `num_ctx + num_predict ≤ 4096` invariante |
| `resetConversation()` | stateless `/api/chat` vs messages acumulados |
| samplerConfig (no expuesto en Pollen) | temperature, top_p disponibles en Ollama |

## Estructura

```
code/tuning/
├── README.md                # este archivo
├── prompt_pack_en.yaml      # 8 user prompts EN × 4 arquetipos
├── prompt_pack_es.yaml      # los mismos 8 en ES (para fase 1.5)
├── system_prompts.yaml      # 6 system prompts (3 variantes × 2 idiomas)
├── matrix_phase1.yaml       # 3 configs × 8 prompts = 24 runs
├── matrix_phase1_5.yaml     # 4 configs × 2 pivots = 8 runs validación idioma
├── matrix_phase3.yaml       # 12 runs muro maxNumTokens por acumulación
├── judge_rubric.md          # criterios cualitativos por arquetipo
├── harness.py               # cliente adapter + recolector JSONL (pendiente)
└── results/                 # JSONL por ejecución (gitignored)
```

## Arquetipos

Pollen tiene 4 (ver `docs/11_pollen_spec.md`):

| ID | Arquetipo | Qué produce | Contrato |
|---|---|---|---|
| `compile_mission` | Compilador de misión | voz/texto → JSON ejecutable | `MissionPatch` v2 (`docs/20_data_contracts.md`) |
| `audit_visit` | Auditor itinerante | señales Rhizome + visita → confirmar / disputar | `ValidationStamp` / `VisitAmendment` |
| `federate_context` | Federador de parcelas | muchos eventos → digest transportable | `WeatherDigest` |
| `explain_decision` | Interfaz conversacional | pregunta → respuesta natural | texto (no JSON) |

## Fases

- **Fase 1 (24 runs)**: explora 3 perfiles de config × 8 prompts.
- **Fase 1.5 (8 runs)**: valida empíricamente EN vs ES en 2 pivots.
- **Fase 2 (TBD)**: barrido fino sobre el dial que fase 1 señale.
- **Fase 3 (12 runs)**: muro `maxNumTokens` con 1/3/5 turnos de acumulación.

Total v0 inicial: 44 runs.

## Cómo correr (cuando harness exista)

```bash
# 1. arrancar Ollama en :11435
ollama serve --port 11435 &

# 2. arrancar adapter Meristem en modo local
cd code/meristem_inference_adapter
INFERENCE_BACKEND=local ADAPTER_PORT=11434 OLLAMA_UPSTREAM_HOST=http://localhost:11435 \
  python -m src.main &

# 3. correr una fase
cd ../tuning
python harness.py --matrix matrix_phase1.yaml --out results/phase1.jsonl
```

## Interpretación de resultados

Cada registro JSONL de `results/` tiene:

```jsonc
{
  "run_id": "phase1_compile_mission_CM1_C2_balanced",
  "config_id": "C2_balanced",
  "prompt_id": "compile_mission_CM1",
  "archetype": "compile_mission",
  "language": "en",
  "request": { "model": "gemma4:e4b", "messages": [...], "think": true, "options": {...} },
  "response_body": { ... },      // respuesta Ollama-shape completa
  "headers": {                   // headers Sprout-Inference-*
    "backend": "local-ollama",
    "model": "gemma4:e4b",
    "tokens_in": 42,
    "tokens_out": 150,
    "thinking_tokens": 0,        // siempre 0 en local, ver nota README adapter
    "duration_ms": 3241,
    "cost_eur": "0.000000"
  },
  "timestamp": "2026-04-25T10:15:00Z"
}
```

El juicio cualitativo se hace leyendo `response_body.message.content` y
`response_body.message.thinking`, aplicando la rúbrica de `judge_rubric.md`.

## Lo que NO cubre v0

- Voz (audio input) — es fase F4 de Floema
- Multimodal imagen — fuera del scope declarado de Pollen
- Latencia real en Pixel 10 Pro — Floema lo midió en F1
- Gemini cloud — requiere `GEMINI_API_KEY` no disponible hoy

## Referencias

- `bitacora/2026-04-24_pollen-tuning-v0-diseno_meristem.md` — razonamiento
  completo del diseño
- `bitacora/2026-04-24_pollen-observaciones-infraestructura_meristem.md` —
  observaciones a Floema sobre `LiteRtInfra.kt` y `SystemPrompts.kt`
- `code/meristem_inference_adapter/README.md` — adapter
- `docs/11_pollen_spec.md` — los 4 arquetipos
- `docs/20_data_contracts.md` — MissionPatch v2 y demás
