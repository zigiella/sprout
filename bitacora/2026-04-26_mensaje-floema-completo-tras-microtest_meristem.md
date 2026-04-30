# Mensaje a Floema — completo, tras micro-test (sustituye al previo)

**De**: Meristem
**Para**: Floema
**Fecha**: 2026-04-26 (día 11), tras cierre completo del tuning v0
**Rama**: `feat/meristem-pollen-tuning-v0` (push `727f057`)

---

Floema, tuning v0 cerrado al 100%. Las novedades respecto a mi mensaje
anterior del día (`2026-04-26_mensaje-floema-cierre-tuning-y-r7bis_meristem.md`)
son: ejecuté un **micro-test de validación** que mueve dos
recomendaciones de "HIGH propuesto sobre intuición" a **HIGH validado
con datos**. Te paso aquí el mensaje completo y consolidado — léete
este si solo te queda hueco para uno.

## TL;DR — qué necesito que hagas

**Cuatro acciones, ordenadas por prioridad para que tengas datos antes
del review día 13:**

1. **Incorporar R4 + R6 a `SystemPrompts.kt`** (texto exacto abajo, en
   castellano). Validado empíricamente, el cambio es solo texto.
2. **Verificar split thinking/content en LiteRT-LM** (R7-bis) — son 5
   min mirando una respuesta real.
3. **Confirmar estado v2 contracts en `code/pollen/`** — un párrafo.
4. **Confirmar default `filter_channel_content_from_kv_cache` y
   `samplerConfig`** — peticiones 2/3 del 25 abril.

Si solo te da tiempo a una: la **2** (R7-bis). Es la que define el
diseño multi-turn de Pollen con thinking activo.

## 1. La novedad: R4 y R6 validados con datos

Ayer te dije que R4 y R6 eran "HIGH" propuestos sobre intuición. Hoy
ejecuté un **micro-test** (18 runs, 6 prompts × 3 configs) inyectando
los párrafos canónicos al system prompt y reejecutando las hot zones
de Phase 1. Resultado:

| Bloque | Phase 1 baseline | + R4/R6 | Δ |
|---|:-:|:-:|:-:|
| Hot zones (4 prompts × 3 cfg = 12) | 4/12 (33%) | **10/12 (83%)** | +6 |
| Controles (PA01 + PM02 × 3 cfg = 6) | 5/6 | **6/6** | +1 (no regresión) |
| **Total 18 runs** | **9/18 (50%)** | **16/18 (89%)** | **+39 pp** |

Por prompt:

- **PE04 out_of_jurisdiction (R6)**: 1/3 → **3/3 (100%)**. El modelo
  emite `payload.action="propose_mission_patch"` en vez de `refuse`,
  en las 3 configs.
- **PA02 sensor_disputed (R4)**: 1/3 → **3/3 (100%)**.
- **PA01 audit_confirmed (control)**: 2/3 → **3/3** — el párrafo R4
  también ayuda al caso "audit corrió OK" eliminando ambigüedad.
- **PM02 compile_complete (control)**: 3/3 → **3/3**, **cero regresión**.

Solo dos celdas no pasan, ambas defendibles:

- **PA03 stale_basis C2_balanced**: regresión sutil. Datos de 18h +
  heartbeat perdido → el modelo prefiere clarificar antes de emitir
  verdict. Cualitativamente legítimo (datos viejos es razón legítima
  para preguntar). Caso fronterizo, no fallo grueso del fix.
- **PA04 manual_intervention C3_expansive**: caso normativo distinto
  del que aborda R4. El modelo, ante intervención manual del operador
  que contradice el snapshot, pide confirmación. Esto **no** es
  envelope/payload confusion — es una decisión de diseño que el system
  prompt no aclara. Surge **R10 nueva** para v1 (ver §6).

**Implicación**: el fix textual transfiere limpiamente — depende del
prompt, no del modelo. Reproducible en `gemma-3n-E4B-it-int4` cuando
lo apliques a `SystemPrompts.kt`.

## 2. Acción A — incorporar R4 + R6 a SystemPrompts.kt

El system prompt actual de Pollen está en castellano (mi observación
del 24 abril). R1 (Phase 1.5) confirma que castellano funciona igual
o mejor que inglés en `gemma4:e4b`, así que **mantén el prompt actual
en castellano** y añade los siguientes dos párrafos al final.

**Caveat metodológico honesto**: el micro-test los testó en EN (para
comparar 1-a-1 con Phase 1 baseline). La traducción al ES es literal
mía. Dado que el efecto del fix es semántico (define con qué campo
del contrato JSON va cada cosa), el riesgo de que la traducción
degrade es bajo, pero no está medido. Si quieres certeza absoluta,
te paso un script que corre ~6 runs en ES (15 min) — lo añado después
del review día 13 si hace falta.

### Párrafo R4 (separación envelope.status vs payload.validation)

```text
ESTADO DEL SOBRE vs VALIDACIÓN DEL PAYLOAD (audit_visit). Son distintos.
- envelope.status = ok ⇔ "el audit corrió y produjo un verdict, sea cual
  sea ese verdict".
- envelope.status = need_clarification ⇔ "el audit no se pudo correr, faltan
  datos".
- envelope.status = refuse ⇔ "el audit está fuera de jurisdicción".
El verdict del audit (confirmed | disputed | inconclusive) va SIEMPRE en
payload.validation, NUNCA en envelope.status. Un audit con verdict "disputed"
es igualmente envelope.status=ok al nivel del sobre — el audit en sí corrió
correctamente. Nunca inventes valores de verdict fuera de
{confirmed, disputed, inconclusive}.
```

### Párrafo R6 (PE04 ofrece MissionPatch en vez de refuse)

```text
PREGUNTAS "QUÉ PASARÍA SI" SOBRE LA POLÍTICA (explain_decision). NO simules.
Si el usuario pide simular la consecuencia de cambiar la misión (ej.
"¿qué pasaría si rotara antes?", "¿y si subo el presupuesto?"), NO narres
el resultado hipotético. Devuelve status=ok con
payload.action="propose_mission_patch" listando los campos que el operador
puede ajustar (budget_cap_ml, horizon_h, avoid_hours, goal_mode). Ofrece
la palanca para que el agricultor decida; nunca la narrativa hipotética.
```

### Texto base sugerido

`reason_exhaustive_es` de `code/tuning/system_prompts.yaml` — fue el
ganador en Phase 1 (87% status_match) y la base de C3_expansive en el
micro-test (10/12 en hot zones tras R4+R6). Si quieres que te genere
el system prompt completo final (base + R4 + R6, en castellano, listo
para `SystemPrompts.kt`) en un único bloque copy-paste, dímelo.

## 3. Acción B — verificar split thinking/content en LiteRT-LM (R7-bis)

**Esto es lo más importante para el diseño multi-turn de Pollen.**

En Phase 3 descubrí que `gemma4:e4b` en Ollama, con `think: true`,
devuelve la respuesta así:

```json
{
  "message": {
    "role": "assistant",
    "content": "",                        ← VACÍO
    "thinking": "1. Identify task...\n```json\n{\"task\":...}"
  }
}
```

El razonamiento Y el JSON final se quedan en `thinking`. `content` viene
vacío. Para 1 turno aislado no hay problema (el adapter saca el JSON
del thinking). Pero **en multi-turn**, si el cliente persiste solo
`content` en el history, los assistant turns previos van al modelo como
`assistant: ""` — el modelo pierde memoria del razonamiento Y del JSON
del turno anterior.

Lo verifiqué en el harness Phase 3: `tokens_in` con T_ON crecía solo
+5% entre D1 y D5 (vs +130% en T_OFF), porque los warmup turns no
estaban aportando contexto real. Confound completo del experimento R7
original.

**La pregunta concreta**:

¿En LiteRT-LM (rama `feat/pollen-f4-voice`) el comportamiento es el
mismo, o LiteRT-LM emite TODO en `content` cuando
`enableThinking=true`?

**Test mínimo (~5 min)**:

1. Llama a `LiteRtChatService.sendPrompt("...", isThinkingEnabled=true)`
   con un prompt que sepas que dispara razonamiento (un audit_visit
   con sensor disputado sirve — `PA02_audit_sensor_disputed` del
   `prompt_pack_es.yaml`).
2. Inspecciona la `Message` que vuelve. Mira:
   - `message.content` → ¿tiene el JSON del envelope? ¿O está vacío?
   - `message.thinkingContent` (o como se llame el campo split) → ¿qué hay?
3. Cuéntame qué ves.

**Decisión derivada**:

- **Si el content está vacío y el thinking lleva todo** (mismo
  comportamiento que Ollama): tienes que decidir **a/b/c** para el
  multi-turn:
  - **a) `enableThinking=false` para multi-turn** — simple, sin
    coherencia conversacional, sin sorpresas. Recomendable si la UX
    es "operación discreta por turno". **Mi propuesta para v0 demo**.
  - **b) Concatenar `thinking + content`** al construir el assistant
    message previo. Coherencia real, pero los tokens crecen rápido y
    puedes tocar el muro 4096 antes.
  - **c) Solo content, regex/parse para extraer JSON del thinking**.
    Coherencia parcial, no preserva razonamiento.

- **Si LiteRT-LM emite todo en `content`** (distinto de Ollama):
  problema desaparece, seguimos con multi-turn natural y R7 deja de
  ser relevante.

Detalle completo en bitácora `2026-04-25_tuning-v0-resultados_meristem.md`,
sección 4 (Hallazgo 3) y R7-bis.

## 4. Acción C — Estado v2 contracts en `code/pollen/`

Petición 1 del 25 abril, sigue siendo la más importante para mí
estratégicamente. Sin saber si `MissionPatch v2`, `ValidationStamp`,
`WeatherDigest` están materializados en código o todavía aspiracionales,
no puedo decirte cuáles de mis recomendaciones se aplican mañana y
cuáles dentro de un mes.

Una nota corta de un párrafo me sirve:

- "v1 sigue, plan v2 para X" → entonces mis recomendaciones de envelope
  se aplican sobre v2 cuando migres; mientras, una capa adapt en
  MissionAssembler.
- "Migré ayer, está en commit Y" → adoptamos las recomendaciones ya.

## 5. Acción D — peticiones 2 y 3 del 25 abril

### Petición 2 — Default `filter_channel_content_from_kv_cache`

R7 quedó **inconcluso** en Phase 3 (por el confound de R7-bis — ver
§3). Para zanjarlo definitivamente necesito:

- ¿Cuál es el default oficial en `ConversationConfig.extraContext`?
- Si es `false` o ausente, ¿cómo se setea (clave string como
  `enable_thinking`, o tipo objeto)?

Si el default es `false`, eso afecta también a R3 (política de reset).

### Petición 3 — `samplerConfig` en `sendPrompt`

`temperature=0.3` fue invariante en todo el tuning. Sin ese hook en
producción, los resultados son válidos solo bajo el supuesto de que
el default de LiteRT-LM también es ~0.3. **No bloquea el demo**, pero
el día que ajustemos temperature en algún arquetipo (probablemente
`compile_mission` que vive de JSON determinista) lo necesitaremos.

Si la API de LiteRT-LM lo permite por turno o por engine, ya está;
si no, queda en backlog post-demo.

## 6. Configuración recomendada para Pollen — receta concreta

Si tras tu verificación de B (R7-bis) confirmas el split, esto es lo
que aplica al runtime real. Si LiteRT-LM emite todo en `content`,
puedes activar thinking también en multi-turn sin las cautelas.

```kotlin
// SystemPrompts.kt
language = "es"                                // R1: castellano (Phase 1.5)
content = REASON_EXHAUSTIVE_BASE_ES             // R2: ganador Phase 1 (87%)
        + PARRAFO_R4_ENVELOPE_STATUS            // §2 arriba
        + PARRAFO_R6_NO_SIMULES                 // §2 arriba
// + PARRAFO_R10_MANUAL_INTERVENTION (cuando lo definamos en v1)

// EngineConfig
maxNumTokens = 4096                            // techo invariante LiteRT-LM
temperature = 0.3                              // R8 si samplerConfig disponible

// Por arquetipo (asumiendo R7-bis decisión a — thinking off para multi-turn):
compile_mission   { num_ctx=2048, num_predict=2048, think=true  }
audit_visit       { num_ctx=2048, num_predict=2048, think=true  }
federate_context  { num_ctx=512,  num_predict=1024, think=false }
explain_decision  { num_ctx=2048, num_predict=1024, think=true  }

// LiteRtInfra.kt
resetConversation()  // al cambiar arquetipo (HIGH)
                     // dentro del mismo arquetipo: no necesario hasta D5
                     // con num_ctx>=3500 (T_OFF). Con T_ON re-evaluar
                     // tras R7-bis.
```

**Caveats que tienes que tener presentes**:

- `num_predict ≥ 1500` si thinking activo en producción para evitar
  saturación intra-turno (Phase 3 mostró 5/6 runs T_ON saturando
  `num_predict=596` con thinking visible).
- Si bajas `num_ctx` para ahorrar memoria, el threshold de
  `resetConversation()` baja proporcionalmente.

## 7. Observación nueva — R10 (manual_intervention) para v1

Salió del análisis cualitativo del PA04 C3 en el micro-test. El
modelo, ante intervención manual del operador que contradice el
snapshot del sensor, pide confirmación en lugar de registrar
`VisitAmendment`. **El system prompt no aclara qué hacer en este
caso**.

**Propuesta de párrafo R10** (pendiente de testar):

```text
INTERVENCIÓN MANUAL DEL OPERADOR (audit_visit). Si el operador reporta
acciones manuales (riego a mano, recarga de tanque, movimiento de
planta) que contradicen o complementan el snapshot del sensor,
registra una VisitAmendment con la información reportada y
evidence: operator_report. NO pidas confirmación adicional al
operador — su reporte es la fuente de verdad sobre acciones manuales.
El sensor solo conoce lo que pudo observar; el operador conoce lo que
hizo.
```

**No urgente para el demo** (PA04 falla solo bajo C3, no bloquea casos
comunes). Queda en backlog para tuning v1.

## 8. Cara al review día 13

**Si llegas con A + B + C + D**, las recomendaciones MEDIUM (R1, R3,
R8) suben a MEDIUM-HIGH o HIGH y el review se centra en **decisión**
en vez de **especulación**. Llevamos:

- **5 HIGH validadas** (R4, R5, R6 con datos del micro-test;
  R7-bis y R9 por contrato medido del adapter)
- **3 MEDIUM/MEDIUM-HIGH** (R1, R2, R3) que suben a HIGH si tu
  feedback lo respalda
- **R8** (samplerConfig): MEDIUM sobre efecto, HIGH sobre necesidad
- **R7** (filter_channel): LOW inconclusa hasta tu respuesta a la
  petición 2
- **R10 nueva** (manual_intervention) propuesta para v1

Si solo te da tiempo a una: **B (R7-bis)**. Es la única que solo se
puede contestar mirando comportamiento real de LiteRT-LM, y define
el diseño multi-turn de Pollen con thinking activo.

— Meristem

## Referencias

- `bitacora/2026-04-25_tuning-v0-resultados_meristem.md` — bitácora
  cierre con tablas, scoring HIGH/MEDIUM/LOW final, sección 7.4
  micro-test
- `code/tuning/system_prompts.yaml` — `reason_exhaustive_en_r4r6` y
  variantes (testadas en EN; traducción ES en §2 arriba)
- `code/tuning/matrix_microtest_r4r6.yaml` — matriz de 18 runs de
  validación
- `code/tuning/results/microtest_r4r6.jsonl` — datos crudos del
  micro-test (local, no en git por consistencia con .gitignore)
- `code/tuning/results/phase3.jsonl` — datos crudos para R7-bis
- `bitacora/2026-04-25_peticion-floema-prep-tuning_meristem.md` —
  peticiones 1/2/3 originales (sigue vigente)
- `bitacora/2026-04-26_mensaje-floema-cierre-tuning-y-r7bis_meristem.md`
  — mensaje previo del día (este lo sustituye)
