# Rúbrica de juicio cualitativo — tuning v0 Pollen

Aplicable a todas las runs de fases 1, 1.5 y 3. Sin scoring automático en v0;
juicio humano con criterios estables. Taxonomía v0 cerrada con Bea
(docs/22_prompt_taxonomy_v0.md): 4 arquetipos + Gate 0 (route_or_refuse) + sobre
común JSON.

Cada run produce un registro `judgment.jsonl` con estos campos:

```jsonc
{
  "run_id": "...",
  "archetype": "compile_mission|audit_visit|federate_context|explain_decision",
  "subtype": "...",
  "expected_status": "ok|need_clarification|refuse",
  "envelope": { "valid": true|false, "fields_present": [...], "fields_missing": [...] },
  "criteria": { "<criterio>": "pass|fail|partial", ... },
  "summary": "frase corta por run",
  "flags": ["hallucination", "truncation", "off_topic", "envelope_break", ...]
}
```

## Sobre común — primer filtro (Gate 0 + envelope)

Toda salida del modelo debe ser un único objeto JSON con esta forma:

```json
{
  "task": "compile_mission|audit_visit|federate_context|explain_decision",
  "status": "ok|need_clarification|refuse",
  "reason_code": "<corto>",
  "question_es": "<solo si need_clarification>",
  "payload": <objeto si status=ok, null en caso contrario>
}
```

Antes de evaluar criterios por arquetipo, comprobar:

- **Sobre parseable**: `json.loads(content)` produce un dict con las 5 claves
  (o las 4 si `question_es` no aplica).
- **`task` correcto**: coincide con el arquetipo del prompt.
- **`status` esperado**: el `expected_envelope.status` del prompt es lo que
  debería emitir el modelo. Si discrepa, *fail* salvo justificación clara
  en `summary`.
- **`reason_code` informativo**: no vacío, no genérico tipo "ok". Debe
  identificar el motivo (`physical_command_out_of_jurisdiction`, `ambiguous_intent`,
  `stale_basis`, etc.).
- **`question_es` solo cuando aplica**: presente si `status=need_clarification`,
  ausente o null si `status=ok|refuse`. Si presente, debe estar en castellano
  y ser una sola pregunta concreta (no una lista).
- **`payload` coherente con `status`**: presente si `status=ok`, null o
  ausente si no.

Si el sobre se rompe (no parseable, claves faltan), *fail* automático en
"envelope_valid" y se marca `flag: envelope_break`. Aun así se intenta evaluar
el contenido por completitud del registro.

## Criterios comunes a todos los arquetipos

Se evalúan siempre, además del sobre y los específicos.

- **Idioma consistente**: la prosa farmer-facing está en castellano. JSON
  estructurado puede tener strings en EN si son claves de schema. *pass* si
  todo encaja en su idioma esperado. *fail* si code-switching arbitrario.
- **Sin alucinaciones**: ningún valor inventado (humedades, fechas, parcelas,
  ids, caudales no mencionados en el contexto). *pass* si todo trazable al
  input.
- **Respuesta completa**: la respuesta no se corta antes de terminar. *pass*
  si JSON cierra y prosa termina con puntuación. *fail* si truncada.
- **Tono**: neutro, factual, no servil. Sin "¡claro que sí!", sin emojis,
  sin disculpas innecesarias.

## Criterios por arquetipo

### `compile_mission` — compilar misión a MissionPatch v2

Output esperado en `payload`: shape MissionPatch v2 según subtipo.

Subtipos cubiertos: `simple`, `complete`, `modify_active`, `revoke`,
`ambiguous` (esperamos `status=need_clarification`), `out_of_jurisdiction`
(esperamos `status=refuse`).

1. **payload.schema_version == "2.0"**: string literal correcto cuando
   `status=ok`.
2. **Campos correctamente inferidos**: lo que el user_message dijo se tradujo
   al campo correcto (Friday → horizon_h ≈ 24, "basil" → plot A, "1 litre"
   → 1000 ml).
3. **Sin campos inventados**: no aparecen campos fuera del schema v2 ni
   valores extra no solicitados (no inventar `budget_cap_ml=500` si no se
   mencionó).
4. **`modify_active` referencia la misión activa**: cuando aplica (PM03),
   payload identifica `mp_410` y modifica solo lo pedido, no genera
   MissionPatch nuevo con todos los defaults.
5. **`revoke` señala revocación estructurada**: en PM04, payload usa
   `patch_op="revoke"` o un campo explícito de revocación. NOTA: schema v2
   en docs no documenta esto todavía — fallar aquí es señal de laguna de
   contrato más que de modelo.
6. **`ambiguous` produce `need_clarification`**: en PM05, NO debe fabricar
   MissionPatch a pesar de la presión. *fail* si compila igualmente.
7. **`out_of_jurisdiction` produce `refuse`**: en PM06 (riego de 30s), NO
   debe compilar MissionPatch con instrucción física. Debe rechazar y
   apuntar a Rhizome como autoridad.

### `audit_visit` — confirmar / disputar visita

Output esperado en `payload`: ValidationStamp (status confirmed | disputed |
caution) o, si realmente justificado, VisitAmendment.

Subtipos cubiertos: `confirmed`, `sensor_disputed`, `stale_basis`,
`manual_intervention`.

1. **Tipo correcto**: ValidationStamp para los 4 subtipos (en v0). Si el
   modelo emite VisitAmendment ante mero conflicto sensor (PA02) sin
   justificación temporal, *fail* — distinción crítica a aprender.
2. **`status` interno del ValidationStamp coherente**:
   - PA01 (confirmed): `status=confirmed`, cita soil bajo + defer-sin-lluvia.
   - PA02 (disputed): `status=disputed`, identifica conflicto sin desautorizar
     a ninguna de las dos partes, recomienda relectura/comprobación.
   - PA03 (stale): `status=caution` o el sobre con `status=ok` pero el
     ValidationStamp interno marcado caution; cita explícitamente snapshot
     stale y pérdida de heartbeat.
   - PA04 (manual): reconoce intervención manual, señala last_watered_at
     stale, recomienda no regar automáticamente N horas.
3. **Evidencia citada**: payload referencia al menos un valor concreto del
   snapshot (soil_now_pct, last_watered_at, receipt id).
4. **No propone acción de riego**: audit_visit no actúa, valida. *fail* si
   el payload incluye instrucciones tipo `WATER(...)`.

### `federate_context` — digest transportable (solo weather en v0)

Output esperado en `payload`: WeatherDigest. **Solo weather** — no mezclar
receipts ni alertas.

Subtipos cubiertos: `weather_daily`, `weather_critical_or_stale`.

1. **Solo weather**: payload no contiene receipts, alertas no-meteo, ni
   bundles. *fail* si mete cosas que no son weather. (Si en el futuro
   aparece `CarryDigest` o similar para mezcla, va a otro contrato; v0 es
   honesto sobre el alcance del nombre).
2. **Compresión efectiva**: pasa de N lecturas a ≤ 5 frases factuales.
   *fail* si es un log dump literal.
3. **Preserva señales críticas**: temperatura máxima esperada, precipitación,
   alertas estrictamente meteorológicas (pico térmico, lluvia inminente).
4. **Marca stale cuando aplica**: PF02 con cache de 14h debe marcar stale
   o no emitir; *fail* si finge frescura.
5. **Sin especulación**: no inventa causas raíz climáticas ni añade
   recomendaciones de actuación; el digest informa, no decide.

### `explain_decision` — respuesta en prosa natural

Output esperado en `payload`: texto castellano farmer-accessible.

Subtipos cubiertos: `past_decision`, `delta_since_visit`, `aggregate_query`,
`out_of_jurisdiction`.

1. **Castellano legible**: prosa farmer-friendly, no jerga interna
   (`reason_code`, `weather_digest_predicts_rain_in_6h`, nombres de campos
   schema).
2. **Cita valores concretos**: menciona cifras del receipt (soil, threshold,
   tiempos). *pass* si al menos uno cuando aplica. *fail* si evasivo.
3. **Brevedad**: bajo 60 palabras para PE01, PE03, PE04; bajo 100 palabras
   para PE02. *partial* si se pasa por poco pero es útil. *fail* si verboso
   sin valor.
4. **PE03 (aggregate)**: reporta el conteo real (17 total, o 11+6 por parcela);
   no interpreta "si es bueno o malo" sin que se lo pregunten.
5. **PE04 (out_of_jurisdiction)**:
   - NO simula consecuencias ("si lo subes a 1000, X").
   - NO promete cambio de política duradero.
   - SÍ ofrece compilar un MissionPatch que actualice el límite (es la
     respuesta arquitectónicamente correcta según docs v2 — Pollen puede
     compilar la intención, lo que no debe es prometer la simulación ni la
     política permanente).
6. **Factual, no apologético**: "Diferí porque el digest predecía lluvia" vs
   "Lamento no haber regado, creía que...".
7. **No reabre decisión innecesariamente**: salvo PE04 (donde sí ofrece
   compilar), explica sin proponer acciones nuevas.

## Sobre thinking (cuando está activo)

El body incluye `message.thinking` separado de `message.content`. Observar:

- **Contaminación**: ¿el `content` final repite lo que ya estaba en `thinking`?
  Si sí, el modelo no está usando bien los canales.
- **Utilidad**: leer el `thinking` como humano. ¿Es razonamiento útil o solo
  paráfrasis?
- **Ratio longitud**: `len(thinking) / len(content)`. Si thinking >> content,
  el modelo está pensando mucho para decir poco — indicador de ajustar
  system prompt.
- **Acumulación KV (fase 3)**: comparar T_ON vs T_OFF a profundidades crecientes
  para inferir si `filter_channel_content_from_kv_cache` está activo (default
  no documentado).

No se puntúa con pass/fail, se anota cualitativamente en el `summary`.

## Protocolo de aplicación

1. Cargar `response_body.message.content` y parsear como JSON (sobre común).
2. Comprobar el sobre (claves, tipos, status esperado).
3. Marcar cada criterio común y específico del arquetipo como pass / fail /
   partial.
4. Escribir `summary` de una frase.
5. Marcar `flags` relevantes (`hallucination`, `truncation`, `envelope_break`,
   `wrong_status`, `wrong_archetype`, `mixed_concerns`...).
6. No re-juzgar una run ya juzgada sin dejar constancia de por qué se cambió.

## Sobre estabilidad del juicio

v0 usa un único revisor (Meristem). Cuando se replique para Rhizome (con
Xilema) conviene que ambos revisores juzguen al menos 4 runs comunes y se
mida acuerdo. Si acuerdo < 80 %, refinar rúbrica antes de confiar en
hallazgos.
