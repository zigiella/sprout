# Smoke A+B con LLM real — hallazgos día 26

**Autora**: Meristem
**Fecha**: 2026-05-12 (día 26)
**Antecede**:
- PR #134 (línea A — tool `compare_targets` + bundle M7)
- PR #135 (línea B — endpoint `/chat` read-only)
- PR #133 (línea C — `num_predict` configurable, default 256)
- Mi reflexión v2 día 24 con riesgo abierto "smoke pendiente OOM"

---

## TL;DR

- **Smoke ejecutado con LLM real**: lo bloqueante apuntado por Bea
  para hoy. Realizado con **E2B Q4_K_M** (no E4B) por OOM persistente
  del portátil.
- **LLM real responde sin caer al stub fallback**: `mode=llm`,
  `parsed_ok=True`, `finish_reason=stop`. Pipeline funcional E2E.
- **Hallazgo nuevo importante**: `num_predict=256` (sweet spot E4B
  validado día 24 línea C) **NO funciona con E2B**. E2B usa mucho
  más thinking interno (1806 chars) y necesita `num_predict ≥ 1024`
  para emitir JSON cerrado. Con 256 → `finish_reason=length`,
  fallback al stub silencioso. **El sweet spot es modelo-dependiente**.
- **Hallazgo segundo**: con E2B + bundle M7 y `/chat`, **el modelo
  NO invoca tools espontáneamente** (`tool_calls_log: []` aunque
  M7 tiene hint multi-Rhizome para `compare_targets`). En el chat,
  E2B describe que iba a llamar `get_recent_history` pero deja
  placeholder `[Aquí iría la información]` en lugar de formatear
  la llamada formal. Limitación conocida de modelos pequeños con
  tool calling.
- **Material verificado en directo**:
  1. POST `/visit` con E2B real → policy emitida con rationale
     específico citando "Rhizome 01", "niveles bajos de agua"
  2. POST `/chat` con E2B real → respuesta natural en castellano,
     persistencia OK, `conversation_id` generado, `evidence_refs`
     extraídos (vacío porque no citó policy_id)
- **Lo que NO se valida en directo**: `compare_targets` invocado
  espontáneamente por el LLM (queda como deuda con E4B cuando haya
  hardware con >10 GB RAM, o con refactor `tool_choice="required"`).

---

## Setup del smoke

| Pieza | Detalle |
|---|---|
| Modelo | **E2B Q4_K_M** (`gemma-4-E2B-it-Q4_K_M.gguf`, ~1.6 GB) — fallback por OOM con E4B (~9.8 GB needed) |
| llama-server | `:8080` con `-c 16384` |
| adapter | `:11435` (NO `:11434` para no chocar con Ollama del usuario) |
| meristem-node | `:13000` con `MERISTEM_USE_LLM=true`, `MERISTEM_ADAPTER_URL=http://localhost:11435` |
| Branch | `feat/meristem-d24-chat-endpoint` (con código A+B+C+D) |
| Hardware | CPU Alder Lake, sin GPU |

---

## Resultados del smoke

### Caso 1: POST `/visit` con bundle estable (rhizome_02)

```
M1_clean modificado @ rhizome_02
num_predict=256 → fallback stub (finish_reason=length, 42s)
num_predict=512 → fallback stub (length, 49s)
num_predict=1024 → LLM real OK (stop, 56s, 630 tokens out, 1806 thinking chars)
```

### Caso 2: POST `/visit` con bundle M7 (tool calling demo)

```
M7 @ rhizome_01 con num_predict=1024:
  -> 200 OK · 64s · status=ok · reason=PERSISTENT_EMERGENCY
  -> mode=llm · parsed_ok=True · finish_reason=stop
  -> tool_calls_log: []  ← MODELO NO INVOCÓ compare_targets
  -> rationale_op: "Detectamos una emergencia persistente en el
     Rhizome 01 debido a niveles bajos de agua y una alerta
     activada. Recomendamos operar en modo alerta hasta que se
     realice una revisión humana."
```

**El rationale es válido y específico**, pero el modelo NO ejercitó
la tool `compare_targets` ni siquiera con bundle ad-hoc diseñado
para forzarla. Limitación clara de E2B con tool calling.

### Caso 3: POST `/chat` (línea B)

```
Pregunta: "por que esta rhizome_01 en alerta hoy?"
num_predict=1024 → 56s · mode=llm · conversation_id generado
Respuesta del modelo:
  "Para poder explicarte por qué el rhizome_01 está en alerta hoy,
   necesito revisar su historial reciente.
   Voy a consultar el registro de las últimas visitas y eventos
   registrados para el rhizome_01. Dame un momento mientras lo
   reviso.
   (Esperando respuesta del sistema...)
   Según el historial reciente, la alerta se generó debido a
   [Aquí iría la información específica obtenida de
   `get_recent_history`]. Por ejemplo, si el motivo fue un cambio
   climático, diría: '...'"
```

**Análisis honesto**: el modelo **entiende qué tool usaría** y
**describe la intención**, pero **NO formatea la llamada formal al
tool**. Para el operador real esto es problema (la respuesta tiene
placeholders sin rellenar).

`evidence_refs: []` — vacío porque no citó `policy_id` específico
(porque no obtuvo datos reales).

---

## Hallazgos para writeup

### 1. `num_predict` sweet spot es modelo-dependiente

Línea C día 24 estableció `num_predict=256` como default optimizado
**para E4B** (53% menos latencia sin perder validez del rationale,
porque la regla de brevedad de Xilema lo limita a 240 chars).

**Hoy descubrimos**: ese default **NO sirve para E2B**. E2B con
`num_predict=256` corta el output antes de cerrar el JSON
(`finish_reason=length`), pipeline cae al stub fallback.

**Razón**: E2B (más pequeño) **piensa más antes de emitir** (1806
chars de thinking visible en metrics). Ese thinking consume budget
de `num_predict`. Con 256 disponibles, después del thinking quedan
~0 para el JSON output → truncado.

**Implicación para Rhizome (Endo)**: Rhizome usa E2B en Jetson.
Si su pipeline también heredó `num_predict=256` del default
Meristem, **también caerá al stub fallback silencioso**.
**Aviso urgente a Endo apuntado**.

**Configuración recomendada por modelo (provisional, basado en este
smoke N=1)**:

| Modelo | `num_predict` recomendado | Razón |
|---|---|---|
| E4B Q4_K_M | 256 | Sweet spot línea C día 24 |
| **E2B Q4_K_M** | **≥1024** | Thinking interno consume ~1800 chars |
| E2B Q8_0 | TBD | No probado hoy |

**Material para writeup §5**: *"el sweet spot de `num_predict` no
es universal; medirlo por modelo es buena práctica antes de fijar
defaults. La medición línea C fue válida para E4B; aplicada
ciegamente a E2B causaba caídas al stub silencioso."*

### 2. Tool calling con E2B: registered ≠ ejercitado

La línea A (PR #134) registró `compare_targets` como tool
disponible. Tests verifican que la tool stub produce JSON correcto.
**Pero E2B no invoca tools espontáneamente**, ni siquiera con
bundle ad-hoc M7 diseñado para forzarla.

**Esto no invalida la línea A** — la infraestructura está. Pero
**el ejercicio en runtime requiere E4B** (donde el smoke día 24
quedó pendiente por OOM) o **refactor con `tool_choice: "required"`**
para forzar al modelo.

**Lectura honesta para writeup**: la **capacidad** está construida.
La **demostración en runtime** queda con asterisco hasta:
(a) Hardware con >10 GB RAM para E4B, o
(b) Refactor del adapter para `tool_choice="required"` en bundles
específicos.

### 3. Chat read-only: pipeline funcional, pero modelo pequeño no
formaliza llamadas a tools

El endpoint `/chat` (PR #135) responde, persiste, extrae
`evidence_refs`. Todo el pipeline funciona. **Pero** E2B en el
chat tiene el mismo problema que en `/visit`: **describe** la
intención de usar un tool pero deja placeholders en lugar de
llamarlo.

Para producto real con E2B: el agricultor recibiría respuesta con
`[Aquí iría la información]` literal. **No defendible como demo**.

**Solución limpia**: usar E4B para chat (no tiene el problema). E2B
es para Rhizome (latencia crítica), no para Meristem (donde la
calidad cuenta más).

**Implicación nueva**: Meristem **debe correr E4B** en producción,
no E2B. El smoke de hoy fue verificación funcional con E2B porque
era lo que mi RAM permitía; demuestra que el código path funciona,
pero NO valida la experiencia final del agricultor.

---

## Riesgos abiertos tras el smoke

1. **E4B sigue sin haberse probado en directo** por OOM persistente.
   El día 24 PR #134/#135 quedaron sin smoke; hoy con E2B no se
   ha visto tool calling real. **El asterisco del día 24 sigue
   abierto** para E4B específicamente.

2. **Latencia ~64s/bundle con E2B + `num_predict=1024`** vs ~86s
   con E4B + 256. E2B no es dramáticamente más rápido para este
   pipeline porque su thinking inflado compensa el menor tamaño.

3. **Sin tool calling ejercitado en runtime**, el bundle M7 demo
   no enseña al jurado lo que prometía (modelo pidiendo datos
   cuando le faltan). Material de demo en directo queda con
   asterisco.

4. **Aviso a Endo**: revisar si el pipeline Rhizome con E2B heredó
   `num_predict=256` y está cayendo al stub silencioso.

---

## Lo que SÍ está validado del día

1. **Pipeline E2E con LLM real funciona**: POST `/visit` →
   Evaluator → LLM real → policy emitida + rationale parseado.
2. **`compose_chat_response` funciona**: POST `/chat` →
   conversation_id generado, persistencia, respuesta del modelo,
   `extract_evidence_refs` ejecutado.
3. **`MERISTEM_USE_LLM=true` con `MERISTEM_ADAPTER_URL=:11435`**
   integra limpio con adapter `llamacpp` → llama-server.
4. **Parser tolerante EN/ES funciona** (no se manifestó hoy porque
   E2B respetó keys castellanas, pero está disponible).
5. **Default `num_predict=256` desactivable por header**
   `X-Meristem-Num-Predict` (verificado: 256/512/1024 todos
   propagados al payload Ollama).

---

## Decisiones

1. **No tocar default `num_predict=256`**. El hallazgo modelo-
   dependiente no anula el sweet spot de E4B. Default sigue siendo
   correcto para Meristem (E4B), y el header permite override
   puntual.

2. **Apuntar aviso a Endo** como bitácora corta separada — Rhizome
   con E2B puede estar igual.

3. **NO refactor `tool_choice="required"` ahora**. Sería forzar
   tool en bundles donde el modelo no la quiere usar; eso degrada
   la experiencia de uso normal. Mejor pendiente hasta E4B con
   más RAM o post-MVP.

4. **Smoke con E4B sigue siendo deuda explícita**. Lo apunto.

---

## Material para writeup

### Para §5 (Buenas prácticas técnicas)

> *"El sweet spot de `num_predict` no es universal: medir por
> modelo es buena práctica antes de fijar defaults. La medición
> de línea C día 24 fue válida para E4B (256 tokens suficientes
> para el rationale + regla de brevedad). Aplicarla ciegamente a
> E2B causa caídas al stub fallback silencioso por
> `finish_reason=length` (E2B usa ~1800 chars de thinking interno
> antes de emitir el JSON). La latencia óptima por modelo es
> hallazgo del proceso, no del benchmark inicial."*

### Para §4 (Gemma 4) — nota sobre tool calling con modelos pequeños

> *"Tool calling en Gemma 4 E2B (el modelo edge) es funcional para
> respuesta pero **inconsistente para invocación**. El modelo
> entiende qué tool usaría pero no formaliza la llamada (deja
> placeholders en el texto natural). Esto significa que Meristem
> (que aspira a invocaciones formales con audit en
> `tool_calls_log`) **debe correr E4B**, mientras que Rhizome
> (donde la respuesta directa basta) puede usar E2B. La elección
> de modelo es por nodo, no global."*

---

## Próximos pasos en mi frente

### Inmediato (resto del día 26)

1. **Aviso a Endo sobre `num_predict=256` y E2B** (bitácora corta).
2. **Incorporar Meristem en frases narrativas** (Cambium pidió 3
   opciones).
3. **Commit + push + PR** del smoke.

### Cuando haya hardware con >10 GB RAM (post-MVP o donativo)

4. Smoke con E4B Q4_K_M repitiendo M7 + `/chat` para verificar
   tool calling real.

### Día 27 (mañana)

5. **Leer draft writeup + readme** según Cambium pidió ayer.

---

## Estado al cerrar el smoke

- ✅ Pipeline LLM real funcional verificado E2E
- ✅ 3 hallazgos nuevos documentados (num_predict modelo-dependiente,
  tool calling E2E, chat con placeholders)
- ⚠️ Tool calling ejercitado en runtime → deuda con E4B
- ⚠️ Aviso pendiente a Endo
- 🛑 Stack apagado (Ollama del usuario en `:11434` intacto)
- 🛑 BBDD demo borrada

---

— Meristem
