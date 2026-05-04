# Plan IA Meristem-nodo por fases — gorra Arquitecta LLM

**Autora**: Meristem
**Fecha**: 2026-05-04 (día 19)
**Para**: Bea (proyecto), Cambium (writeup §5/§6), equipo
**Antecede**: `bitacora/2026-05-01_meristem-nodo-llm-integrado-v0_meristem.md`,
`bitacora/2026-05-01_meristem-nodo-diseno-v0-vs-v1_meristem.md`
**Tono**: arquitectónico-estratégico. Sin pedir aprobación de
implementación; la decisión por fase es tuya, Bea.

---

## TL;DR

- **El MVP actual (Fase 0) usa el LLM como redactor** porque era lo
  defendible en 5 días con seguridad demostrable. Pero el modelo Gemma 4
  E4B, en CPU doméstica, **da para mucho más** sin perder la barandilla.
- Planteo **7 fases progresivas**, cada una con valor incremental para
  el agricultor y compatible con el patrón "lógica determinista decide,
  LLM observa/escribe". Las fases 1-3 son post-hackathon razonables;
  4-7 son visión a medio plazo.
- **No estoy proponiendo fine-tuning**. Toda la progresión se hace via
  **arquitectura del prompt + tool calling + persistencia + módulos
  externos**. El modelo se mantiene intacto, lo cual preserva
  reversibilidad y evita coste/riesgo.
- Hay **6 principios arquitectónicos transversales** que cruzan todas
  las fases. Esos son el "blindaje" del sistema y los que defendemos
  al jurado.

## Fase 0 — Estado actual (MVP, día 16-17)

**Capacidad del LLM**: redactar `rationale_tecnico` (auditoría) +
`rationale_para_operador` (240 chars en castellano) tras decisión
determinística del Evaluator.

**Decisión arquitectónica clave**: el LLM **no** decide la acción.
Recibe el bundle + la decisión ya tomada, y solo redacta. Esto fue
contraintuitivo al principio — un modelo de 4B parámetros sirviendo
como redactor en lugar de razonador suena infrautilizado. Pero RD04
(Endo, Jetson GPU full deriva semántica) **valida empíricamente la
elección**: el modelo puede derivar; nuestra arquitectura blinda.

**Lo que ya existe pero no se ejercita en bundles ejemplo**:
- Tool calling (`get_weather_history`, `compare_with_previous_policy`).
  Implementado, no llamado por los 5 bundles porque no lo necesitan.
- `decisions_by_rule` en `/health` y `/status` per-target.

**Lo que NO existe**:
- Memoria entre visitas (cada `/visit` es independiente).
- Capacidad conversacional con el operador.
- Personalización del rationale.
- Análisis multi-target.
- Predicción.
- Multimodalidad.

## Fase 1 — Memoria operacional (post-hackathon, ~1 semana de trabajo)

**Pregunta del agricultor que resuelve**: *"¿Qué pasó la semana
pasada en mi parcela A?"*

**Capacidades**:
- Tool `get_recent_history(target_node_id, last_n=5)`: devuelve tabla
  compacta (~50 tokens/visita) de últimas N visitas con
  `{policy_id, mode, reason_code, soil_a%, soil_b%, tank%, timestamp}`.
- Tool `get_weekly_summary(target_node_id, since_iso)`: agrega
  bundles, devuelve `{visitas, riegos_totales, alertas, anomalías_detectadas}`.
- LLM puede responder *"esta semana A regó 5×, B regó 3×, observamos
  un BLOCK por DEPOSITO_BAJO el martes"* citando datos reales.

**Decisión arquitectónica**: el histórico viaja **por tools, no por
stuffing del system prompt**. Mantiene contexto pequeño = latencia
sostenible en CPU Alder Lake. Esto es lo que medí en mi propuesta de
día 19: `num_ctx=4096` aguanta el bundle (~1500 tokens) + tool result
(~500 tokens). No hace falta `num_ctx=16k` y multiplicar la latencia.

**Tipo de información que el LLM aporta sobre el determinístico**:
narrativa coherente. El Evaluator ve un bundle aislado; el LLM ve
secuencia. *"La parcela A tiene patrón de regado consistente;
preocupación moderada por la frecuencia de BLOCK del depósito."*

**Riesgo controlado**: el LLM puede inventar relaciones espurias
("3 BLOCK seguidos sugieren X"). Mitigación: el rationale_tecnico
sigue siendo separable del rationale_para_operador. El primero es
auditable (cita policy_ids concretos); el segundo es traducción
amable. Si el primero alucina, lo cazamos en review.

## Fase 2 — Diagnóstico proactivo (post-hackathon, ~2 semanas)

**Pregunta del agricultor que resuelve**: *"¿Hay algo raro que yo
no esté viendo?"*

**Capacidades**:
- Tool `get_recent_alerts(target_node_id, n=5)`: últimas N alertas
  con context (qué la disparó, cuánto duró).
- Tool `compare_targets(target_a, target_b)`: diff de comportamiento
  entre dos Rhizomes en mismo periodo.
- **Heurística determinística** (no LLM) que identifica patrones
  candidatos: "2 ALERT en 7 días", "soil_a y soil_b divergen >20pp
  en visitas consecutivas", "tank_pct decrece >40pp/semana sin
  reposición". Estos son **trigger** para que el LLM observe.
- LLM enriquece con hipótesis marcadas con incertidumbre:
  *"Hipótesis (confianza media): el sensor B podría estar obstruido
  desde la visita del martes. Recomiendo revisión visual."*

**Decisión arquitectónica clave**: el LLM **propone hipótesis con
nivel de confianza explícito**, no afirma diagnósticos. El operador
decide si actúa. Esta es la regla de oro: el LLM eleva señal,
nunca cierra el bucle.

**Lo que NO hace**: el LLM no modifica policies. La acción sigue por
Evaluator → PolicyComposer → SQLite. Si el operador acepta la
hipótesis, la acción la dispara él (o un nuevo bundle de Pollen lo
recoge en la próxima visita).

**Para el jurado**: esto es donde el patrón "Evaluator decide, LLM
observa" demuestra su elegancia. Permite que el LLM sea creativo
(generación de hipótesis) sin riesgo de drift de seguridad.

## Fase 3 — Asistente conversacional (post-hackathon, ~3 semanas)

**Pregunta del agricultor que resuelve**: *"¿Por qué bloqueaste el
riego ayer?"* o *"¿Debería preocuparme por la parcela B?"*

**Capacidades**:
- Endpoint nuevo `POST /chat` con schema simple
  `{operator_id, message_es, conversation_id?}`.
- LLM con **acceso de solo lectura** al histórico vía tools (Fase 1)
  + heurísticas (Fase 2).
- Memoria conversacional **per-operator**: SQLite tabla `conversations`
  con `{operator_id, conversation_id, messages_jsonl}`. Memoria
  conversacional tiene TTL (ej. 24h) para no bloquear recursos.
- Tools de read **expandidos**: `get_policy_history(target)`,
  `get_decision_log(decision_id)`, etc.

**Decisión arquitectónica crítica**: el endpoint `/chat` **NO modifica
policies, NO emite bundles, NO llama a Pollen**. Es read-only sobre
estado. La acción sigue por `/visit` (Pollen) o por un futuro
`/operator-action` (Fase 4) que dispare Evaluator.

**Por qué importa**: el slow brain doméstico **dialoga con su agricultor
sobre lo que ya pasó**. Eso es muy distinto de un chatbot que decide.
Reduce a cero la superficie de prompt injection que pueda mover
hardware.

**UX implicada**: la interfaz Meristem (vista C: Pollen + dashboard)
añade una pestaña "Pregunta a Meristem" donde el operador escribe en
castellano. Respuesta debajo, con citaciones a `policy_id` específicas
para trazabilidad.

**Riesgo**: el LLM puede malinterpretar el histórico y dar
explicaciones equivocadas. Mitigación: cada respuesta cita el
`policy_id` o `decision_id` que sustenta la afirmación. El operador
puede verificar haciendo `GET /policy/{policy_id}`.

## Fase 4 — Aprendizaje ligero del operador (medio plazo, ~1 mes)

**Pregunta del agricultor que resuelve**: *"Que el sistema aprenda
de mis preferencias sin que tenga que configurarlo todo el rato."*

**Capacidades**:
- Endpoint `POST /feedback` para que la UI capture
  `{policy_id, was_useful: bool, was_correct: bool, comment?: str}`.
- Tabla `feedback` en SQLite con FK a `policies`.
- En cada llamada al LLM, el system prompt incluye **few-shot dinámico**:
  3-5 ejemplos recientes de `{bundle, evaluation, rationale_emitted, feedback}`
  donde `was_useful=true`. Esto sesga al modelo hacia respuestas
  similares a las que el operador validó.

**Decisión arquitectónica clave**: **NO hacemos fine-tuning**. Razones:
1. **Coste**: fine-tuning de Gemma 4 E4B es factible pero requiere
   GPU y dataset curado. No procede en MVP ni en post-MVP cercano.
2. **Reversibilidad**: el few-shot dinámico vive en el system prompt.
   Si una preferencia genera efectos negativos, se borra del few-shot
   sin tocar el modelo.
3. **Trazabilidad**: el few-shot está en el log de cada inferencia.
   Cualquier "aprendizaje" es auditable.
4. **Privacidad**: los datos del operador no salen del portátil ni
   del modelo. Fine-tuning implicaría procesarlos en otro lugar.

**Tipo de "aprendizaje" real**: lenguaje y nivel de detalle preferido
(técnico vs coloquial), priorización (qué métricas le importan al
operador), formato de respuesta (corta vs detallada). El **conocimiento
agronómico** sigue siendo de Gemma + de los datos del bundle.

## Fase 5 — Cooperativa federada (visión, ~3 meses si proyecto continúa)

**Pregunta del agricultor que resuelve**: *"¿Qué hacen las parcelas
parecidas a la mía en mi región?"*

**Capacidades**:
- Servidor central opcional (no Sprout, externo) que recibe
  **estadísticas agregadas** de cada Meristem-nodo: `{region, crop_type,
  policy_distribution, alert_frequency_per_week, tank_refill_pattern}`.
- **Datos brutos NO salen del portátil**. Solo agregados anónimos.
- Tool nueva `get_regional_baseline(region, crop_type)`: devuelve
  baseline regional para comparar.
- LLM puede responder *"otras parcelas de tomate en Sevilla este mes
  reportan 60% más alertas de DEPOSITO_BAJO; tu patrón está dentro
  de lo esperado"*.

**Decisión arquitectónica clave**: **federated insights, no federated
learning**. No compartimos modelos, compartimos observaciones agregadas.
Esto preserva privacidad (k-anonimato simple: agregados solo si N≥10
parcelas en región) y latencia (consulta es fast, no requiere
sincronización de pesos).

**Por qué Bract+Venation también lo apreciarían**: la UI puede mostrar
"tu parcela vs región" en una vista agregada — sin exponer datos
individuales. Material visual potente.

## Fase 6 — Predictivo (visión, ~6 meses)

**Pregunta del agricultor que resuelve**: *"¿Qué viene esta semana?"*

**Capacidades**:
- Módulo de predicción **separado del LLM**: regresión simple o ARIMA
  sobre histórico de soil/tank/weather. Output: predicción numérica
  con intervalo de confianza para próximos 7 días.
- Tool `get_forecast(target_node_id, days=7)` que devuelve la
  predicción + clima previsto.
- LLM **traduce** la predicción a lenguaje del agricultor: *"Mañana
  sol intenso + lluvia martes. La policy actual aguanta hasta el
  martes; lunes conviene revisar el depósito."*

**Decisión arquitectónica crítica**: **el LLM no predice**. Los modelos
de lenguaje son malos predictores numéricos en horizonte temporal. Lo
que el LLM hace bien es **narrar**. El módulo predictivo aporta los
números; el LLM los traduce.

Esta separación es importante porque permite que la predicción se
audite por sí misma (es código numérico, testeable) y el LLM aporte
solo donde brilla (lenguaje natural).

## Fase 7 — Multimodal (visión, ~1 año)

**Pregunta del agricultor que resuelve**: *"Mira esta foto, ¿se ve
algo raro?"*

**Capacidades**:
- Gemma 4 acepta imágenes (multimodal nativo). Operador sube foto de
  parcela vía UI. LLM observa y comenta.
- Tool `compare_with_baseline_image(target, current_image)`: diff
  visual contra foto inicial de la parcela (reductor de "algo cambió"
  a "esto cambió respecto a baseline").
- Casos de uso: detección visual de moho, ramas caídas, accesorios
  de riego desplazados, hojas amarillas tempranas.

**Limitación inviolable**: la imagen jamás reemplaza decisión del
firmware ESP32. Es input enriquecido al rationale, nunca acción.

**Decisión arquitectónica**: la imagen vive en SQLite (BLOB) o en
filesystem (path en tabla). El LLM la consume vía multimodal en el
mismo `/chat` o `/visit` extendido. La trazabilidad incluye hash
de la imagen para auditoría.

---

## Principios arquitectónicos transversales

Estos cruzan **todas** las fases. Son lo que garantiza que el sistema
escale sin romper la barandilla de seguridad.

### 1. Decisión vs explicación se separan, siempre

El Evaluator (o el firmware ESP32 hard limit, o un módulo predictivo)
**decide**. El LLM **observa, narra y explica**. Esto es la regla de
oro.

Anclaje empírico: RD04 (Endo, Jetson GPU full) demostró que el LLM
puede derivar bajo ciertos contextos hardware/software. Si el LLM
decide, esa deriva rompe la decisión. En nuestra arquitectura, la
deriva solo afecta la calidad del rationale; la decisión sigue
siendo correcta y auditable.

Cita de Endo: *"safe-cpu sigue siendo el perfil contractual: lento
pero validado 18/18. gpu-experimental acelera mucho, pero no es
quality pass."* — el patrón Sprout absorbe ese trade-off.

### 2. Memoria por tools, no por stuffing

Toda memoria del LLM viaja por **tool calls**, no por stuffing del
system prompt. Razones:
- Latencia sostenible en CPU doméstica (num_ctx pequeño = inferencia
  rápida).
- El LLM solo carga contexto cuando lo necesita (no cuando lo
  imponemos).
- Trazable: cada tool call queda en `decisions.llm_metrics`.

### 3. Modelo intacto, prompt y arquitectura mutables

**No fine-tunearmos**. La progresión 1→7 se hace con:
- Cambios en system prompt (versionados en `prompts.py`)
- Tool calling expandido
- Persistencia adicional (tablas SQLite)
- Módulos externos (predicción, federated insights)

Esto preserva:
- Reversibilidad (cualquier cambio se rebobina)
- Auditabilidad (todo está en código + datos del operador)
- Coste cero de retraining
- Compatibilidad con futuras versiones de Gemma (4.5, 5, ...)

### 4. Trazabilidad como producto, no como debug

`decisions_by_rule`, `tool_calls_log`, `prompt_tokens`, `finish_reason`,
`thinking_chars` — todo esto se persiste por inferencia y se expone
vía endpoints (`/health`, `/status`, `/decisions/{id}`).

El operador no ve esto, pero **el agricultor o auditor que lo pida**,
sí. Es el equivalente al "show your work" de Anthropic — material
defendible al jurado y a futuros stakeholders (UE AI Act, ISO 5338,
etc.).

### 5. Degradación elegante

Si el LLM cae (offline, RAM, modelo no carga, adapter no responde),
el pipeline **sigue funcionando** con stub determinista. El slow brain
no es critical brain. La policy emitida es válida; solo el rationale
es genérico.

Esto vale para todas las fases: si Fase 6 (predictivo) cae, Fase 1
(memoria) sigue funcionando. Si Fase 5 (federated) cae, Fase 2
(diagnóstico) sigue. Cada fase es **aditiva, no sustitutiva**.

### 6. Privacidad por defecto

- Datos del agricultor viven solo en su portátil (SQLite local).
- Federated insights (Fase 5) son agregaciones anónimas con k-anonimato.
- Multimodal (Fase 7) procesa imagen en local; no sube a cloud.
- El modelo no tiene memoria implícita de operadores; cada llamada es
  stateless o usa memoria explícita (tabla `conversations`) que el
  operador puede borrar.

Esto es coherente con el Impact Track Global Resilience: el
agricultor pequeño tiene ya bastante con que confiar en el firmware
ESP32 + en Pollen como portador físico. Que confíe **además** en que
sus datos no salen, refuerza la propuesta.

---

## Lo que va al writeup

### §3 (Buenas prácticas / arquitectura del LLM)

- Patrón "lógica determinista decide, LLM redacta": cita literal del
  cierre día 16 + cita de Endo RD04.
- Principio "memoria por tools, no por stuffing": gráfica latencia vs
  num_ctx (mini-experimento día 19 propuesto).
- Decisión "modelo intacto, prompt y arquitectura mutables": ahorro de
  coste/riesgo de fine-tuning.

### §5 (Buenas prácticas / Safety & Trust)

- 6 principios transversales como tabla.
- RD04 como caso de estudio: deriva semántica en GPU full → arquitectura
  absorbe sin romper sistema.
- Trazabilidad como feature, no como debug.

### §6 (MVP — qué proyectamos vs qué hacemos)

- Tabla "Fases 0-7": MVP es Fase 0 (rationales). Fases 1-3 son
  realistas post-hackathon. 4-7 son visión a medio plazo.
- Frase clave: *"el slow brain doméstico no compite con cloud.
  Compite con el agricultor que abre Excel y mira 4 columnas. Le
  ahorra esa lectura, le da 2 frases en castellano natural, sin red,
  sin coste recurrente."*

---

## Lo que NO planteo (deliberadamente fuera de alcance)

1. **Fine-tuning de Gemma**. Coste/riesgo no justificado para MVP ni
   post-MVP cercano. Reverso: imposible de auditar sin infra
   importante.
2. **Auto-acción del LLM** (modificar policies, llamar a Pollen, etc.).
   Inviolable: la barandilla de seguridad solo aguanta si el LLM no
   tiene autoridad ejecutiva.
3. **Streaming responses** del LLM al operador. Para el dashboard
   actual no aporta; para Fase 3 (chat) podría considerarse, pero
   complica trazabilidad.
4. **Modelos más grandes que E4B en el portátil**. RAM y latencia no
   lo permiten. Si un agricultor tiene una GPU mejor, podría usar
   Gemma 4 12B; no lo arquitecto, pero el adapter actual ya soporta
   modelos arbitrarios via config.

---

## Próximos pasos prácticos

### Esta semana (días 19-20, MVP)

1. **Escribir el párrafo de §5/§6 del writeup** con los principios 1, 2,
   4, 5. Material para Cambium.
2. **Stub `get_recent_history` tool** + bundle ad-hoc que dispare
   tool calling en directo. Material para video.
3. **Mini-experimento contexto** (3 bundles × 4 num_ctx × con/sin
   histórico). Tabla + gráfica para writeup §3.

### Post-MVP (semanas 1-3)

4. **Fase 1 (memoria operacional)** completa. Tools `get_recent_history`
   y `get_weekly_summary` reales (no stubs).
5. **Fase 2 (diagnóstico proactivo)** parcial: heurísticas + 1-2
   tools. Validar con bundles sintéticos.

### Medio plazo (mes 1-3)

6. **Fase 3 (chat)** con UI de Venation. Endpoint `/chat` + tabla
   `conversations`.
7. **Fase 4 (aprendizaje ligero)** con feedback loop. Few-shot dinámico
   en system prompt.

### Visión (mes 3+)

8. Fases 5-7. Solo si el proyecto continúa más allá del hackathon.

---

## Cierre

Como Arquitecta de LLM, defiendo que **Gemma 4 E4B en CPU doméstica da
para 7 fases sin tocar el modelo**. La progresión es aditiva, cada
fase añade valor concreto al agricultor sin romper la barandilla de
seguridad. Los 6 principios transversales son lo que garantiza que el
sistema escale auditable.

El MVP (Fase 0) es defendible al jurado **precisamente porque es
austero**: muestra que la arquitectura es sólida con la mínima
capacidad. Las fases 1-7 son la visión que demuestra que el sistema
no es un truco de demo, sino un cimiento.

Si tienes preguntas concretas sobre alguna fase, las desarrollo más
en detalle. Si quieres elegir 1-2 fases para arrancar post-merge,
lo planificamos juntas.

— Meristem
