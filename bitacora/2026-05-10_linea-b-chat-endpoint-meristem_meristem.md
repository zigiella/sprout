# Línea B día 24 — endpoint `POST /chat` minimal read-only

**Autora**: Meristem
**Fecha**: 2026-05-10 (día 24)
**Antecede**:
- `bitacora/2026-05-10_reflexion-uso-gemma4-meristem_meristem.md`
  (las 4 líneas)
- `bitacora/2026-05-10_lineas-cd-resultados-meristem_meristem.md`
  (C+D del mismo día, PR #133)
- `bitacora/2026-05-10_linea-a-compare-targets-meristem_meristem.md`
  (A del mismo día, PR #134)
**Material destino**: writeup §3 (caso de uso conversacional) +
§5 (Safety & Trust: read-only estricto)

---

## TL;DR

- **Endpoint `POST /chat` implementado** (fase 3 plan IA día 19
  operacionalizada). Read-only estricto: el LLM responde preguntas
  del agricultor sobre lo que ya pasó, sin modificar policies, sin
  emitir bundles, sin llamar a Pollen.
- **Continuidad de conversación** vía `conversation_id`. Si no se
  pasa, se crea uno nuevo. Mensajes persistidos en tabla
  `conversations` para audit + contexto.
- **44/44 tests PASS** (36 anteriores + 8 nuevos en `test_chat.py`)
  cubriendo: stub mode, conversation_id flow, persistencia, read-only
  (no crea bundles), `evidence_refs` extraction, validación
  pydantic, contadores en `/health`.
- **Construido encima de líneas A + C+D** (PR #134, #133): heredo
  default `num_predict=256` + tool `compare_targets` que el chat
  reusa.
- **Smoke con LLM real PENDIENTE** por OOM persistente del portátil
  (mismo problema día 23 + línea A). Apuntado en bitácora — la
  integración está cubierta por tests pero el smoke en directo
  hace falta cuando haya RAM.

---

## Lo que entrega

### 1. Endpoint `POST /chat`

Request:
```json
{
  "operator_id": "bea",
  "message_es": "¿por qué bloqueaste el riego ayer en rhizome_01?",
  "conversation_id": "conv_xxx"  // opcional
}
```

Response (envelope):
```json
{
  "task": "responder_operador",
  "status": "ok",
  "conversation_id": "conv_xxx",
  "answer_es": "Según la policy pkt_meristem_1779000_abc123, ...",
  "evidence_refs": ["pkt_meristem_1779000_abc123"],
  "llm_metrics": {
    "mode": "llm",
    "tool_iterations": 2,
    "tool_calls_log": [...],
    ...
  }
}
```

### 2. Endpoint `GET /chat/{conversation_id}/history`

Devuelve mensajes en orden ASC para auditar conversación o construir
UI futura. Útil para debug y para que el operador revise lo que
preguntó.

### 3. Read-only estricto verificado por test

`test_chat_does_not_create_bundles_or_policies` confirma:
- Antes del POST: `bundles_received_total=0`, `policies_emitted_total=0`
- Después: ambos siguen en 0
- Solo crece `chat_messages.{user, assistant}`

**El chat NO mueve hardware**. Esa es la garantía de seguridad.

### 4. Persistencia: tabla `conversations`

Schema:
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    operator_id TEXT NOT NULL,
    role TEXT NOT NULL,           -- 'user' | 'assistant'
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX idx_conversations_conv_id
    ON conversations(conversation_id, created_at ASC);
CREATE INDEX idx_conversations_operator
    ON conversations(operator_id, created_at DESC);
```

Funciones expuestas en `persistence.py`:
- `insert_conversation_message(conv_id, op_id, role, content)`
- `get_conversation_history(conv_id, limit=20)`
- `count_conversation_messages()` → para `/health`

### 5. System prompt `/chat` distinto del `/visit`

`MERISTEM_CHAT_SYSTEM_PROMPT_ES` (~80 líneas) deja explícito:
- Rol: asistente conversacional read-only
- Tools disponibles (mismas que `/visit`: `get_recent_history`,
  `compare_targets`, `compare_with_previous_policy`,
  `get_weather_history`)
- **Prohibiciones explícitas**: NO modifica policies, NO emite
  bundles, NO llama a Pollen, NO recomienda acciones que muevan
  hardware
- **Cita evidencia**: cuando hace referencia a una decisión, debe
  citar `policy_id` o `decision_id` específico
- **Confianza explícita**: cuando emite hipótesis, marca confianza
  ("posible", "sospecho")
- **Formato**: castellano natural, 1-3 párrafos cortos, sin JSON,
  sin Markdown fences

### 6. `compose_chat_response` en `inference.py`

Distinto de `compose_rationale_via_llm`:
- Acepta `conversation_history` (list of {role, content}) para
  continuidad
- Usa `MERISTEM_CHAT_SYSTEM_PROMPT_ES` no el de visit
- Output texto libre (no JSON estructurado)
- `num_predict=512` por defecto (más que rationale =256, porque
  respuestas chat son ligeramente más largas; ajustable via header)

### 7. `extract_evidence_refs(answer)` heurística

Regex simple busca patterns `pkt_meristem_xxx` y `dec_xxx` en el
texto del LLM. Dedup preservando orden. Si no encuentra, devuelve
lista vacía. El operador puede verificar haciendo `GET /policy/{id}`.

### 8. `/health` extendido

Ahora incluye `chat_messages: {user: N, assistant: M}` para
visibilidad de uso del chat. Material trazable para demo.

---

## Tests añadidos (8 nuevos, 44/44 total)

`tests/test_chat.py`:
1. `test_chat_creates_new_conversation_id_when_omitted` — sin id se
   genera uno nuevo (`conv_*`)
2. `test_chat_stub_mode_returns_deterministic_text` — stub mode
   devuelve respuesta determinista citando la pregunta
3. `test_chat_persists_user_and_assistant_messages` — cada POST
   persiste 2 filas
4. `test_chat_continues_conversation_with_id` — pasar conv_id
   continúa la conversación
5. `test_chat_does_not_create_bundles_or_policies` — read-only
   estricto (no afecta bundles/policies)
6. `test_chat_evidence_refs_extraction` — regex captura
   policy_ids y decision_ids del texto
7. `test_chat_validates_max_message_length` — Pydantic rechaza
   message > 1000 chars con 422
8. `test_chat_health_includes_chat_counters` — `/health` refleja
   contadores tras varios POSTs

---

## Lo que NO entrega (apuntado como deuda)

### Smoke con LLM real

OOM persistente del portátil bloquea el smoke en directo del chat
con LLM real. Apuntado para verificar cuando haya RAM. **Los tests
unitarios + integración cubren** todo el path desde POST hasta
persistencia + extract_evidence_refs.

### UI Vista 6 "Pregunta a Meristem"

La UI v1 actual no tiene textarea + botón para que el agricultor
pregunte. Apuntado para Venation cuando entre en rebrand visual:
sería **zona 6 nueva** debajo de las tablas, con:
- Textarea grande
- Botón "Preguntar"
- Lista de respuestas previas (paginada)
- Click en `evidence_refs.policy_id` → drill-down a esa policy

Mi spec UI v0 (PR #78 mergeado) ya tiene 5 zonas; añadir zona 6
es ~2h de Venation cuando ella decida arrancar rebrand. Mientras
tanto, el agricultor puede usar `/chat` directamente vía
`http://localhost:13000/docs` (Swagger) o curl — útil para demo
en directo.

### Tools que el LLM puede llamar en chat

Las 4 tools existentes (`get_recent_history`, `compare_targets`,
`compare_with_previous_policy`, `get_weather_history`) están
disponibles. Pero **no implementé `get_policy_by_id`** (lookup por
id directo) que sería natural en chat. Lo dejo para post-MVP — el
modelo puede consultar histórico vía `get_recent_history` y eso
basta para v0.

---

## Material para writeup

### Para §3 (Arquitectura) — caso de uso conversacional

> *"Meristem añade un endpoint `/chat` para que el agricultor
> pregunte en castellano sobre lo que ya pasó. El LLM responde
> con read-only estricto sobre histórico (vía tools) y cita
> `policy_id` específicas que el operador puede verificar. La
> conversación tiene continuidad vía `conversation_id` y queda
> persistida para audit. Esta es la fase 3 del plan IA: dialogar
> con el agricultor sobre lo que ya pasó, sin nunca cerrar el
> bucle de acción."*

### Para §5 (Safety & Trust) — read-only por construcción

> *"El chat es read-only por construcción: el endpoint `/chat`
> no toca tablas `bundles` ni `policies`, solo `conversations`.
> El test `test_chat_does_not_create_bundles_or_policies` lo
> verifica explícitamente. La superficie de prompt injection que
> pueda mover hardware es cero — el LLM puede 'decir' lo que
> quiera, no hay path desde el chat hasta el firmware ESP32."*

---

## Estado al cerrar línea B

- ✅ Endpoint `POST /chat` + `/chat/{id}/history` registrados
- ✅ Schemas `ChatRequest`, `ChatResponse`, `ConversationMessage`
  en `schemas.py`
- ✅ Persistencia tabla `conversations` + 3 funciones
- ✅ System prompt `/chat` distinto del `/visit`
- ✅ `compose_chat_response` + `extract_evidence_refs` en
  `inference.py`
- ✅ Tests **8 nuevos PASS** (44/44 total suite)
- ✅ Stub mode funciona (cuando `MERISTEM_USE_LLM=false`)
- ⏭️ Smoke con LLM real → pendiente OOM
- ⏭️ UI Vista 6 → deuda para Venation post-rebrand
- 🛑 Working tree limpio, todo pusheado

---

## Las 4 líneas del plan día 24 — estado consolidado

| Línea | PR | Estado |
|---|---|---|
| **D** — re-correr mini-batería con parser tolerante | #133 (con C) | 5/5 limpio, 0 stub. Hipótesis pesimista día 23 rectificada. |
| **C** — mini-exp `num_predict` | #133 | Hallazgo gigante: latencia escala lineal con `num_predict`, no con `num_ctx`. Default a 256 → 53% más rápido. |
| **A** — tool `compare_targets` + bundle M7 | #134 | Tool + stub + system prompt actualizado con principio de confianza. Default `num_predict=256` aplicado. |
| **B** — endpoint `POST /chat` read-only | #135 (este) | Endpoint + persistencia + tests 8/8 PASS. Fase 3 plan IA operacionalizada. |

**Total**: 4 PRs en un día, 4 líneas independientes pero
encadenadas (cada una construye encima de la anterior). Material
significativo para writeup §3 + §5.

Bea: si me dices que quieres priorizar algo distinto, replanteo.
Mientras tanto, las 4 entregadas sin romper arquitectura.

---

— Meristem
