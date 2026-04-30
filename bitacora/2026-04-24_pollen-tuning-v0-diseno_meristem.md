# Diseño batería de tuning v0 para Pollen

**Autora**: Meristem
**Fecha**: 2026-04-24
**Rama de trabajo**: `feat/meristem-pollen-tuning-v0`
**Encargo**: Bea — "La idea es que te conviertas en la reina del tuning".
Probar y aprender calidades de respuesta de Gemma 4 E4B bajo distintas
configuraciones, en un entorno local que imite el runtime LiteRT-LM de
Pollen lo más posible. Replicar después para Rhizome (apoyo a Xilema).

## Principio operativo

> Lo que pruebe en Ollama debe ser extrapolable a LiteRT-LM. Cuando una
> palanca no exista en LiteRT-LM o exista de forma distinta, el diseño debe
> documentar la asimetría y fijar la restricción equivalente.

## Mapeo LiteRT-LM → Ollama

| Palanca LiteRT-LM | Réplica en Ollama | Asimetría a documentar |
|---|---|---|
| `extraContext["enable_thinking"]` on/off | parámetro `think: bool` | ninguna (comportamiento binario idéntico) |
| "piensa brevemente" en system prompt | texto en `system` | ninguna |
| separar canal de thinking | body viene con `message.thinking` vs `message.content` | Ollama no cuenta thinking en contadores, LiteRT-LM sí (via extraContext) |
| limitar `maxNumTokens` | `num_ctx + num_predict ≤ 4096` como invariante | LiteRT-LM tiene ventana única; Ollama separa input y output. Fijo la suma como techo en cada run |
| podar / limpiar KV cache | turnos explícitos vs reset entre arquetipos | Ollama /api/chat con `messages` controla acumulación; LiteRT-LM tiene `resetConversation()` pero el consumer decide cuándo |
| temperature / topP / topK | parámetros Ollama estándar | LiteRT-LM **no expone samplerConfig** hoy (punto 2 del doc de observaciones) |

## Asunciones (revertibles)

- **Schema MissionPatch**: opción (A) — `schema_version: "2.0"` de
  `docs/20_data_contracts.md`. Confirmada por Bea.
- **Idioma de system prompts**: hipótesis "inglés mejor para lógica interna".
  Se valida empíricamente en fase 1.5, no se asume.
- **Techo**: `num_ctx + num_predict ≤ 4096` invariante. No se viola en
  ninguna run de v0 para que la extrapolación a LiteRT-LM sea honesta.
- **Temperature base**: 0.3. Baja para favorecer JSON determinista en
  compilación. Si fase 2 muestra que importa, se barre.
- **Modelo**: `gemma4:e4b` cuantizado de Ollama (9.6 GB). Es el que más se
  aproxima al `gemma-4-E4B-it.litertlm` (3.65 GB) que documentó Floema en F0.
  Cuantización ≠ exactamente igual — lo dejo explícito.

## Fases

### Fase 1 — exploración de dials en turno único (24 runs)

**Objetivo**: ver qué perfil de config produce respuestas utilizables por
arquetipo. Tres perfiles que cruzan palancas para no barrer a ciegas.

| Config | system_prompt | think | num_ctx | num_predict | temperature |
|---|---|---|---|---|---|
| C1 austero | brief_direct_en | false | 2048 | 512 | 0.3 |
| C2 balanced | auditor_standard_en | true | 2048 | 2048 | 0.3 |
| C3 expansive | reason_exhaustive_en | true | 512 | 3584 | 0.3 |

**Prompts**: 4 arquetipos × 2 prompts cada uno = 8 prompts.
Ver `code/tuning/prompt_pack_en.yaml`.

**Runs**: 8 × 3 = 24.

**Output**: JSONL con un registro por run, que incluye headers
`Sprout-Inference-*` del adapter + body completo + metadata (config, prompt).

### Fase 1.5 — validación empírica de idioma (8 runs)

**Objetivo**: resolver si inglés es mejor que español para la lógica interna
de prompts en Gemma 4 E4B, o si da igual.

| Config | Language | system_prompt | think | num_ctx | num_predict |
|---|---|---|---|---|---|
| EN-balanced | en | auditor_standard_en | true | 2048 | 2048 |
| EN-expansive | en | reason_exhaustive_en | true | 512 | 3584 |
| ES-balanced | es | auditor_standard_es | true | 2048 | 2048 |
| ES-expansive | es | reason_exhaustive_es | true | 512 | 3584 |

**Prompts pivot**: 2 (uno de compilar misión, uno de explicar decisión).

**Runs**: 2 × 4 = 8.

**Criterio de decisión**:
- Si EN gana en ambos pivots por rúbrica → se fija EN en toda la batería y
  se propone a Floema migrar `SystemPrompts.kt`.
- Si no hay diferencia clara → se recomienda EN igualmente por alineación con
  la training data dominante de Gemma, pero sin evidencia de coste.
- Si ES gana → hallazgo importante, se documenta y se revisa hipótesis.

### Fase 2 — barrido fino sobre dial clave (TBD)

**Objetivo**: diseñar tras leer fases 1 y 1.5. No se especifica a ciegas.
Típicamente será algo como: "temperature movió la aguja en compilación, barrer
0.1/0.3/0.5/0.7 con los 2 prompts de compilación".

### Fase 3 — muro `maxNumTokens` con conversación acumulada (12 runs)

**Objetivo**: reproducir el escenario del feature request que Bea mencionó:
qué pasa cuando la conversación acumula turnos y se acerca a 4096. Responder
"¿dónde se rompe y qué estrategia de poda recomendar a Floema?".

| Dimensión | Valores |
|---|---|
| Arquetipos | explain_decision, validate_visit (los dos más stateful) |
| Profundidad | 1, 3, 5 turnos de calentamiento antes del turno medido |
| Configs | think=off con num_ctx=3500, think=on con num_ctx=3500 |

**Runs**: 2 × 3 × 2 = 12.

**Medidas clave**:
- Tokens del KV cache acumulado al inicio del turno medido
- ¿Se produce corte? ¿Alucinación? ¿Degradación de calidad subjetiva?
- ¿El thinking se acumula o se filtra del KV? (punto 5 del doc de
  observaciones — test empírico)

## Total v0

**44 runs** (24 + 8 + 12), más fase 2 diseñada en vivo. Factible en una sesión
de medio día con el adapter + Ollama locales.

## Rúbrica de juicio

Cualitativa por arquetipo. Vive en `code/tuning/judge_rubric.md`. No hay
scoring numérico automatizado en v0 — es lectura humana con criterios
estables. La automatización viene en una iteración posterior si se demuestra
que el juicio humano es estable entre revisores.

## Lo que v0 NO prueba (scope explícito)

- **Voz (audio input)**: es fase F4 de Floema, no compite con tuning de texto.
- **Multimodal imagen**: fuera del scope declarado de Pollen (la cámara no es
  ruta crítica según `docs/11_pollen_spec.md`).
- **Latencia real en Pixel 10 Pro**: requiere hardware que no tengo. Floema
  lo ejerció en F1 con resultados publicados. La batería produce latencias
  del adapter local, que son referencia de orden, no de producción.
- **Gemini cloud como alternativa**: requiere `GEMINI_API_KEY` que no tengo.
  Cuando Bea monte la infra compartida (conversación pendiente con Cambium,
  ver resumen del día), se incorpora como vector adicional.

## Stack

```
harness.py  →  http://localhost:11434  (meristem_inference_adapter en modo local)
                        ↓
              http://localhost:11435  (ollama serve --port 11435, gemma4:e4b)
```

El adapter aporta los headers `Sprout-Inference-*` uniformes (Tokens-In,
Tokens-Out, Thinking-Tokens, Duration-Ms) que la batería recolecta sin lógica
extra. Cost-EUR = 0 en modo local.

## Estructura de `code/tuning/`

```
code/tuning/
├── README.md                 # cómo correr + mapeo + interpretación
├── prompt_pack_en.yaml       # 8 prompts EN × 4 arquetipos
├── prompt_pack_es.yaml       # los mismos 8 en ES (para fase 1.5)
├── matrix_phase1.yaml        # 3 configs × 8 prompts = 24 runs
├── matrix_phase1_5.yaml      # 4 configs × 2 pivots = 8 runs
├── matrix_phase3.yaml        # 12 runs de muro por acumulación
├── judge_rubric.md           # criterios cualitativos por arquetipo
├── harness.py                # cliente adapter, recolector JSONL (próximo commit)
└── results/                  # salida de cada run (JSONL, gitignored)
```

## Siguientes pasos

1. Commit estructura `code/tuning/` + prompt packs + matrices + rúbrica
   (este commit y los siguientes dos, hoy).
2. Commit `harness.py` mañana.
3. Ejecutar fase 1 + 1.5 mañana, lectura cualitativa.
4. Diseñar y ejecutar fase 2 mañana.
5. Ejecutar fase 3 mañana.
6. Bitácora de cierre con recomendaciones concretas a Floema y a Bea.

## Referencias

- `docs/11_pollen_spec.md` — arquetipos de Pollen
- `docs/20_data_contracts.md` — MissionPatch v2 y demás contratos
- `docs/50_pollen_gemma4_e4b_guide.md` — guía LiteRT-LM
- `research/06_litertlm_thinking_digest.md` — plumbing de thinking (Peri)
- `bitacora/2026-04-24_pollen-observaciones-infraestructura_meristem.md` —
  gemela de este doc, observaciones al código de Floema
- `code/meristem_inference_adapter/README.md` — adapter que sirve como
  único punto de entrada
