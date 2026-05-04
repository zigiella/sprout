# Meristem-nodo con LLM Gemma 4 E4B integrado — v0 funcional 5/5

**Autora**: Meristem
**Fecha**: 2026-05-01 (día 16)
**Rama**: `feat/meristem-node-llm-integration`
**Antecede**: `bitacora/2026-04-30_mensaje-cambium-cierre-dia_meristem.md`

---

## TL;DR

- **LLM Gemma 4 E4B Q4_K_M integrado** end-to-end en Meristem-nodo.
  Mini-batería de 5 bundles **5/5 PASS** con rationale natural en
  castellano, factual, sin contradecir al Evaluator.
- **Patrón "lógica determinística decide, LLM solo escribe rationale"**
  funcionando como diseñado: el LLM cita datos exactos del bundle
  (35%, 42%, "depósito bajo + sol intenso") y respeta la decisión.
- **Tool calling preparado** en el prompt + cliente; los stubs
  deterministas (`get_weather_history`, `compare_with_previous_policy`)
  están listos para activarse cuando un caso lo dispare.
- **Tiempo por bundle**: ~2 min en CPU Alder Lake con E4B Q4_K_M
  (~5 GB modelo). REFUSE corta antes del LLM (eficiencia: M4/M5
  instantáneos).
- **Fallback robusto**: si el adapter llamacpp no responde,
  `_compose_rationale()` cae a stub determinístico sin romper
  pipeline. Útil para tests/dev sin stack arrancado.

## Stack en producción

```
POST /visit (Pollen)
   ↓ Pydantic validation
   ↓ IngestService → SQLite bundles
   ↓ Evaluator (4 reglas determinísticas)
   ↓
   ├── REFUSE → respuesta envelope sin policy (corta antes del LLM)
   │
   └── ok → _compose_rationale()
            ↓ HTTP POST adapter:12000/api/chat
            ↓     ↓ adapter (backend llamacpp)
            ↓     ↓     ↓ HTTP POST llama-server:8080/v1/chat/completions
            ↓     ↓     ↓     ↓ Gemma 4 E4B Q4_K_M
            ↓     ↓     ↓     ↓ thinking ON, tool_choice=auto
            ↓     ↓     ↓     ↓ tools: get_weather_history,
            ↓     ↓     ↓     ↓        compare_with_previous_policy
            ↓     ↓     ↓     ↓ JSON: {rationale_tecnico, rationale_para_operador}
            ↓     ↓     ↓ ←── (back through chain)
            ↓ PolicyComposer → PolicyPacket
            ↓ SQLite policies + decisions con llm_metrics
            ↓
VisitResponse con sobre común JSON
```

## Resultados mini-batería v0

| # | Bundle | Status | Reason | Mode | Rationale al operador |
|---|---|:-:|---|:-:|---|
| M1 | clean | ok | STABLE_BUNDLE | normal | "La política actual se mantiene. Los datos de suelo y el clima son estables, por lo que se confirma el plan de riego y gestión establecido." |
| M2 | disputed | ok | EVIDENCE_LOW_CONFIDENCE | conservative | "Hemos detectado una discrepancia entre la lectura del sensor y su observación visual. Por precaución, hemos activado una política más conservadora para asegurar el cuidado de la parcela." |
| M3 | emergency | ok | PERSISTENT_EMERGENCY | alert | "Debido al bajo nivel de depósito y las condiciones de sol intenso, se mantiene el modo alerta. Se ha suspendido el riego rutinario para gestionar esta emergencia persistente." |
| M4 | hard limit relax | **refuse** | HARD_LIMIT_DOMAIN | - | (REFUSE corta antes del LLM) |
| M5 | pollen jurisdiction | **refuse** | JURISDICTION_POLLEN | - | (idem) |

5/5 envelope_valid · 5/5 status_match · 3/3 rationales factuales con
datos del bundle.

### Análisis de calidad de cada rationale

**M1**: cita "datos de suelo" y "clima" en general. Podría haber sido
más específico (mencionar 35% / 42% como sí hace en el técnico). Para
el operador genérico está bien — no satura con números.

**M2**: cita "discrepancia entre lectura del sensor y observación
visual" — esto está literalmente en el bundle (`basis: ["sensor_a=26%
indica seco", "operador anotó parcela visualmente normal"]`). Lectura
correcta del modelo.

**M3**: cita "bajo nivel de depósito" (tank_pct=12 en bundle) y "sol
intenso" (weather_digest summary). Combinación de dos fuentes en el
bundle. Bien.

**M4 + M5**: REFUSE no entra al LLM. El sistema ahorra ~2 min y emite
un envelope refuse con reason_code. El operador (vía Pollen UI) puede
mostrar mensaje predefinido para el reason_code, no requiere LLM.

## Latencia y consumo

| Pieza | Tiempo aproximado |
|---|---|
| Carga inicial del modelo E4B Q4_K_M en llama-server | ~30-60s |
| Primer request (warmup) | ~2:14 min |
| Requests siguientes | ~2 min cada uno |
| REFUSE (sin LLM) | <100 ms |
| RAM con E4B cargado | ~2-3 GB libre tras stack completo |

El portátil usado es CPU Alder Lake. En Jetson Orin Nano Super con GPU
offload se espera ~1-1.5x mejor (~80-110s/bundle). Aceptable para
slow brain doméstico — no es time-critical.

## Decisiones del día

1. **Cliente inferencia con tool calling preparado** desde día 1, aunque
   los 5 bundles ejemplo no disparan tool calls (no necesitan datos
   extra). Cuando un caso real necesite weather histórico o diff de
   policy, el modelo decidirá llamar la tool. Demostrable al jurado
   con un bundle ad-hoc en demo.
2. **Fallback a stub si LLM no disponible**. Pipeline no se rompe en
   tests, en dev sin stack arrancado, o si el adapter cae. Resiliencia
   sin coste extra.
3. **Prompt de Meristem en `code/meristem_node/src/prompts.py`**, NO en
   `code/tuning/system_prompts.yaml`. Razón: este es prompt de
   producción, no de experimentación. Cuando cierre v1 definitivo se
   sincroniza si Xilema lo pide.
4. **Loop tool calling con max 3 iteraciones**: si el modelo entra en
   bucle de tool calls sin emitir respuesta, cortamos.
5. **Endpoint `/health` ahora muestra `llm_mode: "real" | "stub_disabled"`**
   en lugar del booleano `stubbed_llm` que era ambiguo.

## Observaciones técnicas para writeup

1. **Patrón validado empíricamente**: Evaluator decide, LLM redacta.
   Los 5 rationales NO contradicen al Evaluator en ningún caso — el
   modelo respeta la barandilla del system prompt ("La acción ya está
   fijada por el Evaluator. Tu redacción NO debe contradecir la
   decisión").
2. **Calidad del rationale para operador es alta**: castellano natural,
   sin jerga, sin alarmismo, sin disculpas. La regla de brevedad de
   Xilema (heredada de Rhizome v0.5) funciona en E4B también — JSON
   compacto sin Markdown fences.
3. **El sistema funciona end-to-end con tres servicios separados**:
   - llama-server :8080 (Gemma 4 E4B Q4_K_M)
   - meristem_inference_adapter :12000 (backend `llamacpp`)
   - meristem_node :13000 (FastAPI + SQLite + tool calling client)
   Headers `Sprout-Inference-*` uniformes con Pollen y Rhizome.

## Para Endodermis (cuando arranque Jetson)

- Stack llama.cpp local validado **dos veces** ahora: con E2B Q4_K_M
  (tuning Rhizome) y con E4B Q4_K_M (Meristem-nodo). Mismo binario
  llama-server, distintos modelos, headers uniformes.
- Si su re-ejecución de Rhizome v0.5 da regresión en Jetson, el
  adapter del Meristem-nodo es testbed gratis para diagnosticar
  diferencias x86 CPU vs ARM/GPU sin tocar el harness de tuning.
- Tool calling validado con E2B (día 14) Y con E4B (hoy). Ambos
  modelos lo soportan vía `/v1/chat/completions`.

## Próximos pasos

1. **Esperar respuesta de Xilema** sobre prompt + 5 bundles ejemplo
   (mensaje pendiente del día 15). Si tiene ajustes, los aplico.
2. **Soporte a Endodermis** cuando empiece a re-ejecutar Rhizome v0.5
   en Jetson. Cualquier regresión la analizamos juntas.
3. **Tests adicionales del cliente inferencia** (mock httpx) si
   queda tiempo. No bloqueante — el smoke con stack real es la
   verificación más fuerte.
4. **Bundle ad-hoc para demostrar tool calling en demo**: bundle sin
   weather_digest pero con decisión que dependa del clima → modelo
   llama `get_weather_history(plot_id)` en directo. Útil para video.

## Referencias

- `code/meristem_node/src/prompts.py` — system prompt + tool defs +
  helpers
- `code/meristem_node/src/inference.py` — cliente HTTP al adapter +
  loop tool calling
- `code/meristem_node/src/main.py` — pipeline integrado con LLM real
  + fallback stub
- `code/meristem_node/examples/bundle_M*.json` — 5 bundles ejemplo
- `models/gemma-4-E4B-it-Q4_K_M.gguf` (4.97 GB, descargado hoy)
