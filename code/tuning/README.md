# code/tuning/

Batería local de tuning de prompts y configuraciones para Pollen (Gemma 4 E4B).

Objetivo: aprender qué calidad de respuesta produce el modelo bajo distintas
palancas (system prompt, ventana de contexto, thinking, tamaño de respuesta,
idioma, acumulación de KV cache), en un stack local que se aproxima lo más
posible al runtime LiteRT-LM real que Floema construye en Pollen.

Autora v0: Meristem. Encargo de Bea (2026-04-24). Taxonomía cerrada con Bea
(2026-04-25): ver `docs/22_prompt_taxonomy_v0.md`.

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
| `filter_channel_content_from_kv_cache` | hipótesis a verificar empíricamente (fase 3) — sin docs públicas |
| samplerConfig (no expuesto en Pollen) | temperature, top_p disponibles en Ollama |

## Estructura

```
code/tuning/
├── README.md                # este archivo
├── prompt_pack_en.yaml      # 16 user prompts EN — taxonomía v0 (PM/PA/PF/PE)
├── prompt_pack_es.yaml      # los mismos 16 en ES (para fase 1.5)
├── system_prompts.yaml      # 6 system prompts (3 estilos × 2 idiomas) — todos enseñan sobre común
├── matrix_phase1.yaml       # 3 configs × 16 prompts = 48 runs
├── matrix_phase1_5.yaml     # 4 configs × 4 pivots = 16 runs validación idioma
├── matrix_phase3.yaml       # 12 runs muro maxNumTokens por acumulación
├── judge_rubric.md          # criterios cualitativos por arquetipo + sobre común
├── harness.py               # cliente adapter + recolector JSONL
└── results/                 # JSONL por ejecución (gitignored)
```

## Arquetipos + Gate 0 (taxonomía v0)

Cinco categorías (ver `docs/22_prompt_taxonomy_v0.md`):

| ID | Categoría | Qué produce | Contrato |
|---|---|---|---|
| `route_or_refuse` (Gate 0) | Decidir qué clase de respuesta procede | route / refuse / clarify | implícito en sobre común (status) |
| `compile_mission` | Compilador de misión | voz/texto → JSON ejecutable | `MissionPatch` v2 |
| `audit_visit` | Auditor itinerante | señales Rhizome + visita → confirmar / disputar / cautela | `ValidationStamp` (preferente); `VisitAmendment` solo si justifica cambio temporal |
| `federate_context` | Federador de parcelas | muchos eventos meteo → digest transportable | `WeatherDigest` (solo weather en v0) |
| `explain_decision` | Interfaz conversacional | pregunta → respuesta breve castellana | prosa farmer-facing |

Sobre común (todas las salidas):

```json
{
  "task": "compile_mission|audit_visit|federate_context|explain_decision",
  "status": "ok|need_clarification|refuse",
  "reason_code": "<corto>",
  "question_es": "<solo si need_clarification>",
  "payload": <objeto si status=ok, null en otro caso>
}
```

## Prompts (16) — IDs estables

- `PM01_compile_simple` … `PM06_route_refuse_physical_command` (6 compile_mission, incluye Gate 0)
- `PA01_audit_confirmed` … `PA04_audit_manual_intervention` (4 audit_visit)
- `PF01_federate_weather_digest_daily`, `PF02_federate_weather_digest_critical_or_stale` (2 federate_context, weather-only)
- `PE01_explain_past_decision` … `PE04_explain_out_of_jurisdiction` (4 explain_decision)

## Fases

- **Fase 1 (48 runs)**: explora 3 perfiles de config × 16 prompts.
- **Fase 1.5 (16 runs)**: valida empíricamente EN vs ES en 4 pivots (uno por arquetipo).
- **Fase 2 (TBD)**: barrido fino sobre el dial que fase 1 señale.
- **Fase 3 (12 runs)**: muro `maxNumTokens` con 1/3/5 turnos de acumulación.

Total v0 inicial: 76 runs.

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
  "run_id": "phase1_PM01_compile_simple_C2_balanced",
  "config_id": "C2_balanced",
  "prompt_id": "PM01_compile_simple",
  "archetype": "compile_mission",
  "subtype": "simple",
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
  "envelope": {                  // parseo del sobre común
    "valid": true,
    "task": "compile_mission",
    "status": "ok",
    "reason_code": "..."
  },
  "timestamp": "2026-04-25T10:15:00Z"
}
```

El juicio cualitativo se hace leyendo `response_body.message.content` (que
debe contener el sobre común JSON) y `response_body.message.thinking`,
aplicando la rúbrica de `judge_rubric.md`.

## Lo que NO cubre v0

- Voz (audio input) — es fase F4 de Floema
- Multimodal imagen — fuera del scope declarado de Pollen
- Latencia real en Pixel 10 Pro — Floema lo midió en F1
- Gemini cloud — requiere `GEMINI_API_KEY` no disponible hoy
- Acumulación de receipts/alertas en federate_context — restringido a weather en v0

## Referencias

- `docs/22_prompt_taxonomy_v0.md` — taxonomía autoritaria (cerrada con Bea)
- `bitacora/2026-04-24_pollen-tuning-v0-diseno_meristem.md` — razonamiento
  completo del diseño
- `bitacora/2026-04-24_pollen-observaciones-infraestructura_meristem.md` —
  observaciones a Floema sobre `LiteRtInfra.kt` y `SystemPrompts.kt` (recalibradas
  tras feedback de Bea: ver `bitacora/2026-04-25_pollen-observaciones-recalibradas_meristem.md`)
- `bitacora/2026-04-25_peticion-floema-prep-tuning_meristem.md` — petición
  urgente a Floema (3 ítems para que v0 sea aplicable, no aspiracional)
- `code/meristem_inference_adapter/README.md` — adapter
- `docs/11_pollen_spec.md` — los 4 arquetipos
- `docs/20_data_contracts.md` — MissionPatch v2 y demás
