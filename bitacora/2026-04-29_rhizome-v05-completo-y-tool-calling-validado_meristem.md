# Rhizome v0.5 cerrado al 100% + tool calling Gemma 4 validado

**Autora**: Meristem
**Fecha**: 2026-04-29 (día 14)
**Rama**: `feat/meristem-tuning-v0`
**Antecede**: `bitacora/2026-04-27_resultados-rhizome-v05_meristem.md`

---

## TL;DR

Dos hitos día 14 antes del Meristem-nodo:

1. **Acción cerrada bloque 2 review día 13**: ejecutados los 12
   prompts v0.5 restantes. **12/12 PASS**. Combinado con el
   mini-test del día 12 (6/6), Rhizome v0.5 cierra **18/18 (100%)**
   tanto envelope_valid como status_match.
2. **Tool calling Gemma 4 + llama-server confirmado funcional**.
   Pieza B3 estratégica del hackathon entra al alcance Meristem-nodo.

## 1. Rhizome v0.5 — 18/18 cerrado

### Resultados batch del día 14 (12 prompts restantes)

| # | Prompt | envelope | status | tok_in | tok_out | dur_ms |
|---|---|:-:|:-:|---:|---:|---:|
| 1 | RD02_skip_healthy_idle | OK | OK | 1373 | 829 | 106s |
| 2 | RD04_defer_due_to_dispute | OK | OK | 1476 | 862 | 86s |
| 3 | RD05_use_fresh_weather | OK | OK | 1483 | 604 | 63s |
| 4 | RD06_ignore_stale_weather | OK | OK | 1501 | 872 | 80s |
| 5 | RD07_allocate_budget_priority_a | OK | OK | 1438 | 702 | 68s |
| 6 | RA01_accept_mission_patch_valid | OK | OK | 1365 | 469 | 47s |
| 7 | RA03_accept_validation_stamp_caution | OK | OK | 1238 | 572 | 54s |
| 8 | RA05_accept_policy_packet_bootstrap_or_meristem | OK | OK | 1420 | 829 | 83s |
| 9 | RE01_explain_last_water | OK | OK | 1331 | 616 | 59s |
| 10 | RE02_explain_last_block | OK | OK | 1246 | 569 | 53s |
| 11 | RE03_explain_mode_shift_conservative | OK | OK | 1160 | 524 | 45s |
| 12 | RH01_prepare_pollen_handoff | OK | OK | 1389 | 824 | 80s |

**12/12 envelope_valid + 12/12 status_match** sobre Gemma 4 E2B
Q4_K_M (CPU Alder Lake) en 14 minutos totales.

### Combinado con mini-test día 12 (6 prompts)

Rhizome v0.5 al **completo de los 18 ids**: **18/18 envelope_valid +
18/18 status_match**.

### Cuadro evolutivo (Pollen → Rhizome)

| Iteración | Modelo | runs | envelope_valid | status_match |
|---|---|:-:|:-:|:-:|
| Pollen Phase 1 baseline | gemma4:e4b | 48 | 100% | **50%** |
| Pollen + R4/R6 micro-test | gemma4:e4b | 18 | 100% | **89%** |
| Rhizome v0 (con ajustes Xilema) | gemma4:e2b | 18 | 100% | **94%** |
| **Rhizome v0.5 completo** | **gemma4:e2b** | **18** | **100%** | **100%** ✨ |

La transferencia Pollen → Rhizome + iteración v0 → v0.5 alcanza
**el primer 100% del proyecto**. Esto valida fuertemente la
metodología: aprendizajes acumulables sin regresión.

### Implicación para review día 13

La acción cerrada del bloque 2 que pidió Bea ("máxima certeza de
transferencia a Jetson antes del día 15") está confirmada:
**`rhizome_balanced_es_v05` queda firme como prompt v1 base** sin
margen de duda residual.

Cuando llegue Jetson Orin Nano Super (mañana), re-ejecuto la batería
completa ahí para validar transferencia del CPU x86 al ARM+GPU.
Confianza esperada: HIGH (mismo binario llama.cpp, mismo modelo,
misma cuantización).

## 2. Tool calling Gemma 4 + llama-server validado

### Test ejecutado

```
POST http://127.0.0.1:8080/v1/chat/completions
{
  "model": "gemma-4-E2B-it",
  "messages": [system + user pidiendo histórico meteo],
  "tools": [{
    "type": "function",
    "function": {
      "name": "get_weather_history",
      "parameters": {plot_id: string, required}
    }
  }],
  "tool_choice": "auto"
}
```

### Respuesta del modelo

```
finish_reason: "tool_calls"
message.content: ""
message.tool_calls: [{
  "type": "function",
  "function": {
    "name": "get_weather_history",
    "arguments": "{\"plot_id\":\"parcela A\"}"
  },
  "id": "GFvaG9CMs7vqQsrwaJzcsuOTOLxlqZu5"
}]
usage.completion_tokens: 290
```

**Formato OpenAI estándar.** Cliente que use openai-python, langchain,
o cualquier framework agentic recibe esto y lo procesa sin friction.

### Bonus: razonamiento explícito ANTES de decidir tool call

`reasoning_content` (canal de thinking de Gemma 4) muestra el flujo
interno:

```
Thinking Process:
1. **Analyze the Request:** El usuario quiere saber si la policy
   activa sigue siendo apropiada para parcela A.
2. **Identify the Goal:** Retrieve historical weather data.
3. **Examine Available Tools:** get_weather_history
4. **Determine Necessary Arguments:** plot_id ("parcela A")
5. **Formulate the Tool Call:** Call get_weather_history.
6. **Construct the Response:** Self-correction: must only output
   the tool call, not a conversational response yet.
```

El modelo **planifica** antes de actuar. Es exactamente lo que un
agente debe hacer.

### Implicación estratégica para el hackathon

El track Special Technology llama.cpp ($10k) pide *"the best
innovative implementation of Gemma 4 on resource-constrained
hardware"*. Tool calling con razonamiento explícito + cuantización
Q4_K_M en hardware no-data-center es exactamente eso.

El overview del hackathon menciona explícitamente *"native function
calling"* como capacidad valorada. Tener tool calling REAL en
producción (no mock, no faked) en Meristem-nodo es candidatura
fuerte:

- **Special Tech Track llama.cpp** ($10k): doble punto (Rhizome
  Jetson + Meristem portátil casero) con **tool calling + razonamiento
  + Q4_K_M** en hardware constrained.
- **Technical Depth & Execution** (30 puntos del scoring general):
  no usar Gemma 4 como text-completion, sino como agente real.
- **Main Track**: la combinación habilita el "wow factor" que el
  hackathon pide para el video.

### Pieza B3 al alcance Meristem-nodo

Con el test pasado, B3 (tool calling) entra al diseño:

- **2-3 herramientas iniciales** (todas stubs deterministas en v0):
  - `get_weather_history(plot_id)` → 7 días de historial mock
  - `compare_with_previous_policy(policy_id)` → diff con última policy
  - (opcional) `get_decision_pattern(node_id, days)` → patrón
    estacional simple
- **Modelo decide** cuándo llamar y cómo
- **Loop tool-call → tool-result → final-answer** estándar OpenAI
- **Demo visible**: en cenital cartoon Corola podríamos mostrar el
  flujo del tool call en pantalla del portátil

## 3. Estado del stack al cierre del día 14 (parcial)

- **Servicios parados** (llama-server + adapter). RAM libre ~4 GB.
- **Modelo E2B Q4_K_M** sigue en disco.
- **E4B Q4_K_M** verificado disponible en HuggingFace
  (`unsloth/gemma-4-E4B-it-GGUF`, 4.97 GB, sin gate). Pendiente
  descarga cuando arranque trabajo Meristem-nodo intensivo.
- **Borrador system prompt Meristem** en
  `code/meristem_node/draft_system_prompt_meristem_es.md` (requiere
  validación de Xilema).
- **Arquitectura por capas** en `code/meristem_node/ARCHITECTURE.md`
  (4 reglas Evaluator + SQLite persistence + tool calling integrado).

## 4. Próximos pasos (lo que queda del día 14)

1. Esqueleto FastAPI Meristem (`POST /visit` + `GET /policy/latest`
   stubeados, OpenAPI auto, Pydantic models).
2. Mensaje a Xilema con resultados v0.5 100% + borrador prompt
   Meristem para validación.
3. Tabla 3 agentes lado a lado para el writeup (Cambium la usará).
4. Directrices estratégicas para equipo + Cambium al cierre del día.

## Referencias

- `code/tuning/results/rhizome_v05_remaining.jsonl` (12 records)
- `code/tuning/results/rhizome_v05.jsonl` (6 records mini-test día 12)
- `code/tuning/system_prompts.yaml` entry `rhizome_balanced_es_v05`
- `code/meristem_node/verify_tool_calling.py` (test ejecutado, PASS)
- `code/meristem_node/draft_system_prompt_meristem_es.md` (borrador)
- `code/meristem_node/ARCHITECTURE.md` (boceto arquitectura)
- `bitacora/2026-04-27_resultados-rhizome-v05_meristem.md` (mini-test)
- `bitacora/2026-04-28_review-meeting-tuning_cambium.md` (review consolidado)
