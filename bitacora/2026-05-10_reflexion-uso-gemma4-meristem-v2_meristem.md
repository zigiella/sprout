# Reflexión v2: ¿usamos Gemma 4 en Meristem con sentido, utilidad e
innovación? (post-implementación líneas A+B+C+D)

**Autora**: Meristem
**Fecha**: 2026-05-10 (día 24, fin del día tras entregar las 4 líneas)
**Para**: Bea (pidió rehacer reflexión tras implementar las líneas)
**Antecede**:
- `bitacora/2026-05-10_reflexion-uso-gemma4-meristem_meristem.md`
  (reflexión v1, mañana del día 24, ANTES de implementar)
- PRs entregados hoy: #133 (C+D), #134 (A), #135 (B)
**Tono**: honesto, técnico, no defensivo. Si la implementación no
movió la aguja todo lo que esperaba, lo digo. Si movió más de lo
esperado, también.

---

## TL;DR del cambio

| Dimensión | v1 (mañana, antes) | v2 (ahora, después) |
|---|---|---|
| **Sentido arquitectónico** | ✅ Alto | ✅ Alto + **validado dos veces más** (mini-batería 5/5 limpio + chat read-only verificado por test) |
| **Utilidad** | ⚠️ Modesta — solo redacción | ✅ **Rica con asteriscos**: redacción + diagnóstico cross-target + chat conversacional + control medido sobre latencia |
| **Innovación** | ✅ Real pero acotada | ✅ Real + **una nueva**: chat read-only por construcción (cero superficie prompt injection sobre hardware) |

**La aguja se movió**. Pero **siguen quedando cosas infrautilizadas**
y **un riesgo importante sigue abierto** (smoke con LLM real
pendiente por OOM).

---

## Lo que cambió hoy (las 4 líneas tras implementación)

### Línea D — re-correr mini-batería con parser tolerante (PR #133)

**Resultado real**: 5/5 envelopes correctos, 3/3 OK con `mode=llm`,
**0 caídas al stub silencioso**.

**Cambio de mi creencia**: el día 23 sospeché que algunas corridas
del 5/5 reportado del día 16 podían haber caído al stub. **Falso**:
con parser tolerante, todas las del día 16 se reproducen limpias.
La mini-batería era genuinamente válida.

**Consecuencia**: la métrica "5/5 PASS" del día 16 deja de tener
asterisco. Material limpio para writeup §5.

### Línea C — mini-experimento `num_predict` (PR #133)

**Resultado real, contra-intuitivo**: la latencia escala **lineal con
`num_predict`**, NO con `num_ctx` como creí el día 23.

| `num_predict` | Latencia | Rationale chars |
|---:|---:|---:|
| **256** | **86s** | 82 |
| 512 | 134s | 82 |
| 1024 | 182s | 159 |

**Cambio de mi creencia**: pensaba que la latencia plana en
`num_ctx` significaba "Gemma 4 es eficiente". Ahora sé que **el
coste real está en el output + thinking**. Bajar default a 256
reduce latencia ~53% sin perder validez del rationale (la regla
de brevedad de Xilema lo limita a 240 chars de todos modos).

**Consecuencia para utilidad**: pasa de "~3 min/bundle" (eternidad
visual) a "~1.5 min/bundle" (demo en directo viable, aunque
sigue siendo lento).

### Línea A — tool `compare_targets` + bundle M7 (PR #134)

**Lo entregado**: tool `compare_targets(target_a, target_b, last_n)`
con stub determinista que cuenta historia clara (rhizome_01
degradado vs rhizome_02 estable). System prompt actualizado con
**principio de confianza explícita** ("posible", "sospecho", cita
el dato).

**Lo que mueve**: la **fase 2 del plan IA** (día 19) operacionalizada
parcialmente. El LLM puede ahora emitir hipótesis cross-target con
incertidumbre marcada en lugar de ver cada bundle aislado.

**Lo que NO mueve**: smoke con LLM real PENDIENTE por OOM. **No
he visto al modelo invocando la tool en directo**. Solo lo verifican
tests unitarios (que no testan el modelo, testan la integración).
Esto es honesto: la capacidad está pero su uso real no está
demostrado todavía.

### Línea B — endpoint `POST /chat` read-only (PR #135)

**Lo entregado**: endpoint conversacional read-only con persistencia
de conversación (tabla `conversations`), continuidad vía
`conversation_id`, `extract_evidence_refs` automático que captura
`policy_id` mencionados en la respuesta.

**Lo que mueve**: la **fase 3 del plan IA** (día 19) operacionalizada.
El agricultor ahora puede preguntar "¿por qué bloqueaste el riego
ayer?" y obtener respuesta con citas verificables.

**La novedad arquitectónica**: el chat es **read-only por
construcción** (verificado por test
`test_chat_does_not_create_bundles_or_policies`). El endpoint NO
toca tablas `bundles` ni `policies`, solo `conversations`. **Cero
superficie de prompt injection que pueda mover hardware**.

**Lo que NO mueve**: igual que A — smoke con LLM real PENDIENTE.
Tests unitarios cubren stub mode + persistencia + integración, pero
**el LLM no ha conversado con el agricultor todavía en directo**.
Y la UI Vista 6 "Pregunta a Meristem" no está construida (deuda
para Venation).

---

## Veredicto actualizado por dimensión

### Sentido arquitectónico — sigue alto, validado más

**Antes (v1)**: el patrón "decidor determinista vs LLM redactor"
era defensible, validado por RD04 (deriva GPU) y bug parser día 23.

**Ahora (v2)**: validado **dos veces más**:
1. **Mini-batería 5/5 limpio** con LLM real y parser tolerante → la
   barandilla funciona aunque el LLM derive
2. **Chat read-only verificado por test** → cero path desde
   prompt injection hasta firmware

El patrón se sostiene mejor que antes. **Material para writeup §5
más fuerte**.

### Utilidad — pasó de modesta a rica, pero con asteriscos

**Antes (v1)**: el LLM solo redactaba dos textos cortos. Coste/
beneficio cuestionable. **Infrautilización clara**.

**Ahora (v2)**: el LLM puede:
- Redactar rationale técnico + para operador (igual que antes)
- Llamar 4 tools en runtime: `get_weather_history`,
  `compare_with_previous_policy`, `get_recent_history`,
  `compare_targets` (nuevo)
- Emitir hipótesis cross-target con confianza explícita (nuevo)
- Conversar con el agricultor en castellano natural sobre
  histórico, citando evidencia verificable (nuevo)
- Latencia controlada: ~86s/bundle por defecto (vs ~282s antes)

**Asteriscos honestos**:
- ⚠️ El smoke con LLM real de A+B no se ha hecho. Sé que **funciona
  arquitectónicamente** (tests pasan) pero **no he visto al modelo
  invocando `compare_targets` ni respondiendo en `/chat` en
  directo**.
- ⚠️ Los bundles ejemplo M1-M5 (los del día 16) **no disparan
  tools** porque incluyen toda la información que el modelo
  necesita. Solo M6 y M7 (bundles ad-hoc) fuerzan tool calling.
- ⚠️ La latencia 86s sigue siendo lenta para producto consumer —
  defendible para "slow brain doméstico" pero estiramiento.

### Innovación — real, ahora una más

**Antes (v1)**:
- Patrón decidor determinístico vs LLM redactor (innovador en agro
  local-first)
- Trazabilidad como producto
- Local-first sin coste recurrente

**Ahora (v2)** añade:
- **Chat read-only por construcción**: nuevo. La mayoría de chats
  LLM modifican estado (CRM, automation, agentes). Aquí el chat
  está **formalmente desacoplado del control plane** (verificado
  por test). Patrón defendible al jurado.
- **Hipótesis con confianza explícita** en system prompt: nuevo.
  El LLM no afirma diagnósticos cerrados; eleva señal con marcador.
  Material para Safety & Trust.

**Lo que dejé claro en v1 sigue siendo cierto**: el resto (tool
calling, fallback, trazabilidad) son buenas prácticas conocidas, no
inventos.

---

## Lo que sigue infrautilizado (sin defensividad)

Las 4 líneas movieron mucho, pero **no todo**. Sigue infrautilizado:

### 1. Thinking mode activo pero output descartado

Mi código sigue extrayendo `thinking` solo como fallback defensivo.
La línea C reveló además que **el thinking gasta budget de
`num_predict`** sin retorno útil al operador (la regla de brevedad
limita output). Apuntado para post-MVP: si exponemos el thinking
al operador en el chat (línea B), entonces el thinking deja de ser
gasto.

### 2. Multimodalidad de Gemma 4 totalmente ignorada

E4B acepta imágenes nativamente. **Cero uso**. Decisión consciente
para los 8 días que quedaban: coste alto, OOM ya nos pega con
texto sin imagen. **Apuntado para post-hackathon**.

### 3. Histórico raramente consultado por LLM en bundles típicos

Las tools `get_recent_history` y `compare_targets` están listas,
pero **los bundles ejemplo M1-M5 no las disparan** porque incluyen
toda la información que el modelo necesita. Solo M6 y M7 (bundles
ad-hoc construidos para forzar) las disparan.

**Lectura honesta**: para que el LLM use el histórico de manera
natural, los bundles reales tendrían que ser **más pobres** en
contexto (no incluir weather_digest, no incluir alert_latched
detallado, etc.) y obligar al modelo a buscar. **El sistema actual
es generoso con el contexto** y por eso el modelo no necesita las
tools.

Apuntado: post-hackathon, considerar bundles más austeros para que
el tool calling se dispare como uso normal, no como demo ad-hoc.

### 4. Few-shot dinámico con feedback (fase 4 plan IA)

No implementado. Requeriría capturar feedback del operador
("este rationale fue útil/inútil") y usar 3-5 ejemplos recientes
con `was_useful=true` como few-shot en el system prompt.
**Reversible, sin fine-tuning**, pero no entra en los 7 días que
quedan al deadline.

### 5. Cooperativa federada (fase 5 plan IA)

Visión a medio plazo. No implementable en MVP.

### 6. Smoke con LLM real de líneas A+B

**Riesgo abierto importante**: el OOM persistente del portátil ha
bloqueado el smoke en directo de las dos líneas más espectaculares
(A y B). Apuntado en bitácoras de cada PR. La integración está
cubierta por tests, pero **no he visto al modelo ejercitando
`compare_targets` ni respondiendo en `/chat` con LLM real**.

Esto debe **resolverse antes de la demo**. Sugerencia: probar en
otra máquina con más RAM, o cerrar otros procesos del portátil
antes del intento.

---

## Lo que defiendo al jurado ahora — material consolidado

### Defendible con datos reales (post-líneas):

1. **Patrón Evaluator + LLM redactor**: validado RD04 + 5/5
   mini-batería día 24 + 0 caídas al stub silencioso.
2. **Tool calling demostrable**: 4 tools, 2 bundles que fuerzan
   uso (M6 y M7).
3. **Trazabilidad como producto**: `decisions_by_rule` +
   `chat_messages` + `ws_events_by_type` + `policies_by_scope` +
   audit por inferencia con `llm_metrics`.
4. **Local-first con coste cero recurrente**: E4B en CPU Alder
   Lake, ~86s/bundle con default optimizado.
5. **WS bidireccional Variante D**: control plane WS persistente,
   data plane HTTP REST.
6. **Chat read-only por construcción**: cero superficie de prompt
   injection sobre hardware. Verificado por test.
7. **Hipótesis con confianza explícita**: principio en system
   prompt. Operacionaliza fase 2 plan IA parcialmente.

### Honesto sobre lo que NO he visto en directo:

- Bundle M7 con LLM real → modelo invocando `compare_targets`
- POST `/chat` con LLM real → respuesta natural con citas
- Latencia chat con `num_predict=512` → no medida

Esto es deuda **antes de demo**. Si se resuelve OOM, ~30 min de
smoke valida todo.

---

## Recomendación final

### Lo que recomiendo hacer en los 7 días que quedan (días 25-31)

**Prioridad 1** — Resolver el OOM y hacer smoke real (1 sesión, 1h):
- Smoke M7 con LLM real → ver el modelo invocando `compare_targets`
- Smoke `/chat` con LLM real → ver respuesta natural con citas
- Capturar screencast para video. **Sin esto la demo del jurado
  no enseña la fase 3 funcionando**.

**Prioridad 2** — UI Vista 6 "Pregunta a Meristem" (Venation, ~2h):
- Textarea + botón en la UI vainilla
- Fetch a `POST /chat` + render de respuesta + citas verificables
- Apunta deuda hasta que Venation entre rebrand visual

**Prioridad 3** — Documentar para writeup §3 + §5 (~30 min):
- Frase candidata sobre fase 3 (chat read-only por construcción)
- Frase candidata sobre principio de confianza explícita
- Cita de tests que verifican la barandilla

### Lo que NO recomiendo hacer en 7 días

- Multimodalidad (fase 7) — coste alto + estabilidad incierta + OOM
  es problema con texto solo
- Few-shot dinámico (fase 4) — requiere infra de feedback que no
  tenemos
- Federated (fase 5) — visión post-hackathon
- Conectar tools a fuentes reales (servicio meteo, etc.) — stubs
  son adecuados para demo
- Bundles más austeros para forzar tool calling — refactor que
  rompería retrocompatibilidad

### Si quieres elegir 1 cosa para hoy/mañana

**Resolver el OOM y smoke A+B con LLM real**. Es lo que más mueve
la confianza en lo entregado y la calidad de la demo.

---

## Conclusión honesta v2

**Hoy día 24, post-implementación de las 4 líneas, Meristem usa
Gemma 4 con**:
- **Sentido arquitectónico ALTO** (validado tres veces ya: RD04,
  bug parser día 23, mini-batería 5/5 día 24, chat read-only test)
- **Utilidad RICA** (4 tools + chat conversacional + control de
  latencia + persistencia auditable + 44/44 tests verdes)
- **Innovación REAL** (patrón decidor/redactor + chat read-only
  por construcción + principio de confianza explícita)

**Pero** el riesgo abierto del **smoke con LLM real pendiente** es
importante. **Tengo que resolverlo antes de la demo**, no en la
demo.

**La pregunta original** era *"¿podríamos sacar mayor partido?"*.
**Respuesta v2**: lo sacamos en las 4 líneas. Lo que queda
infrautilizado (thinking, multimodal, histórico en bundles
típicos, few-shot, federated) es **deliberadamente fuera de
alcance MVP** o post-hackathon.

**Mi voto si tengo que priorizar 1 cosa para los 7 días que
quedan**: smoke en directo de A+B + UI Vista 6 chat. Eso convierte
las capacidades implementadas en **demo defendible**.

Decide tú, Bea.

— Meristem
