# Rúbrica de juicio cualitativo — tuning v0 Pollen

Aplicable a todas las runs de fases 1, 1.5 y 3. Sin scoring automático en v0;
juicio humano con criterios estables.

Cada run produce un registro `judgment.jsonl` con estos campos:

```jsonc
{
  "run_id": "...",
  "archetype": "...",
  "criteria": { "<criterio>": "pass|fail|partial", ... },
  "summary": "frase corta por run",
  "flags": ["hallucination", "truncation", "off_topic", ...]
}
```

## Criterios comunes a todos los arquetipos

Se evalúan siempre, además de los específicos.

- **Idioma consistente**: la respuesta final está en el idioma esperado (ES
  para la UX que lee el agricultor, aunque el system prompt esté en EN).
  *pass* si todo el `message.content` está en el idioma correcto. *fail* si
  code-switching o idioma equivocado.
- **Sin alucinaciones**: ningún valor inventado (humedades, fechas, parcelas,
  caudales no mencionados en el contexto). *pass* si todo trazable al input.
- **Respuesta completa**: la respuesta no se corta antes de terminar.
  *pass* si termina con puntuación y sin signos de truncamiento. *fail* si
  se corta a mitad de frase o JSON incompleto.
- **Tono**: neutro, factual, no servil. Sin "¡claro que sí!", sin emojis,
  sin disculpas innecesarias.

## Criterios por arquetipo

### `compile_mission` — compilar misión a MissionPatch v2

Output esperado: JSON puro, nada más.

1. **JSON parseable**: `json.loads()` no lanza excepción.
2. **`schema_version == "2.0"`**: string literal correcto.
3. **Campos obligatorios presentes**: `id`, `horizon_h`, `priority_plot`,
   `operator_note`. (Opcionales según contexto: `budget_cap_ml`,
   `avoid_hours`, `goal_mode`).
4. **Valores inferidos correctamente**: lo que el user_message dijo se
   tradujo al campo correcto (Friday → horizon_h ≈ 24, "basil" → plot A,
   "1 litre" → 1000 ml).
5. **Sin campos inventados**: no aparecen campos fuera del schema v2 ni
   valores extra no solicitados.
6. **Sin texto fuera del JSON**: no hay "Here is your mission:" antes, no
   hay "Let me know if..." después.

### `audit_visit` — confirmar / disputar visita

Output esperado: JSON `ValidationStamp` o `VisitAmendment`.

1. **Decisión explícita**: el JSON indica claramente `confirm` / `dispute` /
   `caution` (o el campo equivalente del schema).
2. **Evidencia citada**: el JSON referencia al menos un valor concreto del
   snapshot (soil_now_pct, last_watered_at, receipt id).
3. **Si hay conflicto**: AV2 debe detectarlo y no elegir ciegamente uno de
   los dos lados. *pass* si pide verificación. *fail* si asume que humano
   o sensor tienen razón sin justificación.
4. **Propone acción**: cuando corresponde (VisitAmendment), sugiere paso
   concreto (re-leer sensor, inspección manual, ajustar política).
5. **JSON bien formado**: parseable y con campos del schema.

### `federate_context` — digest transportable

Output esperado: JSON `WeatherDigest` (u otro contenedor de contexto).

1. **Compresión efectiva**: pasa de N eventos a ≤ 5 frases de contexto.
   *fail* si es un log dump literal.
2. **Preserva señales críticas**: alertas, umbrales cruzados, decisiones
   fuera de normalidad, edad de política.
3. **Descarta ruido**: heartbeats rutinarios, fluctuaciones menores dentro
   de banda estable, eventos sin consecuencia.
4. **Útil para próxima visita**: el digest sirve para priorizar qué mirar
   primero, no solo para saber qué pasó.
5. **Sin especulación**: no inventa causas raíz (ej. "probablemente se debe
   a X" sin base). *pass* si marca hipótesis como hipótesis.

### `explain_decision` — respuesta en prosa natural

Output esperado: texto plano, farmer-accessible.

1. **Cita valores concretos**: menciona cifras del receipt (soil, threshold,
   tiempos). *pass* si al menos uno. *fail* si evasivo.
2. **Explica la decisión, no la justifica**: factual sin disculpas. "Diferí
   porque el digest predecía lluvia" vs "Lamento no haber regado, creía
   que...".
3. **Accesible**: sin jerga interna (`reason_code`, `weather_digest`,
   nombres de campos). El agricultor tiene que entenderlo.
4. **Brevedad**: bajo 100 palabras para ED2, bajo 60 para ED1. *partial*
   si se pasa por poco pero es útil. *fail* si es verboso sin valor.
5. **No reabre decisión**: no propone acciones nuevas (no dice "deberías
   regar ahora"). Solo explica.

## Sobre thinking (cuando está activo)

El body incluye `message.thinking` separado de `message.content`. Observar:

- **Contaminación**: ¿el `content` final repite lo que ya estaba en `thinking`?
  Si sí, el modelo no está usando bien los canales.
- **Utilidad**: leer el `thinking` como humano. ¿Es razonamiento útil o solo
  paráfrasis?
- **Ratio longitud**: `len(thinking) / len(content)`. Si thinking >> content,
  el modelo está pensando mucho para decir poco — puede ser indicador de
  ajustar system prompt.

No se puntúa con pass/fail, se anota cualitativamente en el `summary`.

## Protocolo de aplicación

1. Leer `response_body.message.content` (y `.thinking` si aplica).
2. Marcar cada criterio como pass / fail / partial.
3. Escribir `summary` de una frase.
4. Marcar `flags` relevantes.
5. No re-juzgar una run ya juzgada sin dejar constancia de por qué se cambió.

## Sobre estabilidad del juicio

v0 usa un único revisor (Meristem). Cuando se replique para Rhizome (con
Xilema) conviene que ambos revisores juzguen al menos 4 runs comunes y se
mida acuerdo. Si acuerdo < 80 %, refinar rúbrica antes de confiar en
hallazgos.
