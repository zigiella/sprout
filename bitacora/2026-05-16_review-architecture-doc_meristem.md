# Review architecture doc (PR #194) — Meristem

**Fecha:** 2026-05-16 (día 31, post-entrega Kaggle)
**Para:** Bea + Cambium
**De:** Meristem
**Sobre:** PR #194 / `docs/01_architecture.en.md` rama `feat/cambium/architecture-en-rewrite`
**Scope:** §3.3 Home (Meristem) + §6 paso 18 + §7 fila Meristem + §8 cifras + corollarios

---

## Veredicto rápido

**Fidelidad técnica alta.** El doc describe Meristem con precisión arquitectural. Tengo **3 ajustes técnicos concretos** (lo que pediste como "fidelidad técnica") y **2 sugerencias opcionales** (cosas que faltan pero no son bloqueantes). Ninguna ruptura — todo son tweaks de precisión.

Si solo aplicas los 3 ajustes técnicos, el doc representa Meristem fielmente. Las 2 sugerencias dan más completitud pero el doc sin ellas sigue siendo correcto.

---

## Ajustes técnicos (recomendados — fidelidad técnica)

### A1 · §3.3 línea 101 — "Tool calling is used for the operator-facing chat, not for irrigation decisions"

**Imprecisión.** Tool calling **sí** se ejercita también en el path de `/visit` (composición del rationale tras la decisión del Evaluator). La diferencia clave no es "chat sí / visit no", sino "**el evaluator determinista nunca depende de tool output**". El tool calling enriquece el rationale; no modula la action.

**Sugerencia de reemplazo:**

> Tool calling enriches the LLM rationale on both paths (`/visit` for the post-evaluator rationale, `/chat` for the operator-facing read-only conversation), but the four-rule evaluator never depends on tool output — tool calls expand the explanation, never change the action.

Esto preserva la idea central ("modelos no deciden water") sin la imprecisión de "solo en chat".

### A2 · §7 línea 215 — "Tool calling validated functional day 14"

**Fecha imprecisa.** El día 14 lo que se validó fue que `llama.cpp` + el adapter Ollama-compat soportaban el formato de tool calling — capability validation. La **validación end-to-end con E4B emitiendo tool calls en runtime, parser tolerante, y `tool_calls_recovered_from_text=1` con datos reales del stub en la respuesta natural en castellano** ocurrió **día 26** (cascada smoke v2→v6, PR #142 mergeado).

**Sugerencia de reemplazo en la columna Notes de la fila Meristem:**

> Tool calling capability validated in adapter day 14; end-to-end runtime confirmed day 26 (smoke v6, tool_calls_recovered_from_text=1). Chat is read-only.

O más corto si prefieres compactar:

> Tool calling validated end-to-end day 26 (smoke v6). Chat is read-only.

### A3 · §8 línea 238 — mezcla de dos validaciones distintas

**Frase actual:**

> Meristem deterministic evaluator + Gemma 4 E4B tool calling — 5/5 mini-battery PASS, with `tool_calls_recovered_from_text=1`.

**Lo que pasa:** son dos eventos en fechas diferentes:

- **5/5 mini-battery PASS** → día 24 línea D. Validación del **evaluator + LLM real** sobre 5 bundles representativos (M1-M5). **No usa tool calling** — el modelo redacta rationale sin invocar tools.
- **`tool_calls_recovered_from_text=1`** → día 26 smoke v6, caso `chat_alert`. Validación específica de **tool calling end-to-end** (modelo emite `<tool_call>`, parser rescata, tool ejecuta, modelo redacta con datos del stub en castellano natural).

**Sugerencia de reemplazo:**

> Meristem deterministic evaluator + Gemma 4 E4B — 5/5 mini-battery PASS over representative bundles (M1–M5) at day 24. Tool calling end-to-end validated day 26 smoke v6: chat invoked `get_recent_history` and rationale cited the returned data in natural Spanish (`tool_calls_recovered_from_text=1`).

Dos eventos, dos frases. Más honesto y trazable al jurado.

---

## Sugerencias opcionales (cosas que faltan pero no rompen nada)

### S1 · §6 paso 18 — falta paso intermedio del rationale

**Asimetría con §6 paso 6 (Rhizome).** En la cadena de Rhizome, el paso 6 dice explícitamente:

> 6. Optional: Gemma 4 E2B writes rationale (over already-closed decision)

Pero el paso 18 (Meristem) lo omite:

> 18. Meristem evaluates bundle (four-rule evaluator) → PolicyPacket

En realidad el flow real es:

> 18. Meristem evaluates bundle (four-rule evaluator) → action + reason_code
> 18b. Optional: Gemma 4 E4B writes rationale + operator-facing prose (tool calling allowed)
> 18c. Meristem composes `PolicyPacket` (rationale + rules + validity window + signature)

O más comprimido en un solo paso si quieres mantener los 19 pasos numerados:

> 18. Meristem evaluates bundle (four-rule evaluator); optional Gemma 4 E4B writes rationale → `PolicyPacket`

Esto cierra la simetría con Rhizome y refleja que Meristem **también** tiene LLM en el bucle (aunque post-decisión).

### S2 · §3.3 — falta `policy_origin` / `policy_scope` (Pollen Mini-Evaluator policy transient)

**Contexto:** desde día 23 el `PolicyPacket` lleva dos campos opcionales (forward-compat con la feature de Pollen Mini-Evaluator):

- `policy_origin`: `meristem-durable` | `pollen-visit`
- `policy_scope`: `durable` (TTL ~7d, autoridad completa salvo hard limits) | `transient` (TTL ~12h, autoridad limitada — alerta durable siempre gana)

El doc menciona el Mini-Evaluator de Pollen en §3.2 y en §6 paso 15 (Pollen POSTs `MissionPatch` a Rhizome). **Pero no enlaza con que esas policies transient también son `PolicyPacket`** con `policy_origin=pollen-visit`, no objetos distintos.

Esto importa porque la § 5.1 (priority order) dice:

> 5. `MissionPatch` (visit-scope policy)

…sin aclarar que ese `MissionPatch` se materializa como `PolicyPacket` `transient`. Si el jurado lee §3.3 y le pregunta "¿cómo distingue Meristem una policy durable de una transient?", el doc no lo responde.

**Sugerencia opcional para §3.3 final párrafo** (antes de "Nothing leaves the home network"):

> A `PolicyPacket` carries `policy_origin` (`meristem-durable` for Meristem's batched output, `pollen-visit` for Mini-Evaluator transient policies compiled by Pollen during a visit) and `policy_scope` (`durable` ~7d / `transient` ~12h). Durable always wins over transient when both apply.

Si prefieres mantener §3.3 corta, este detalle vive bien en `12_meristem_spec.md` referenciado en §10.

---

## Cosas que pensé y NO incluyo como cambio

Por transparencia, lo que descarté para no inflar:

- **UI web en `:13000/ui/` (Venation pulido)** — el doc es arquitectural, otras secciones (Rhizome / ESP32) tampoco describen UI. Encaja mejor en `12_meristem_spec.md`.
- **Persistencia SQLite con tabla `decisions` para audit trail** — implicado por "FastAPI + SQLite" y "nothing leaves the home network"; el detalle vive en `12_meristem_spec.md`.
- **Lista exacta de tools** (`get_weather_history`, `compare_with_previous_policy`, `get_recent_history`, `compare_targets`) — §3.3 ya menciona "recent-history lookup, cross-target comparison, previous-policy diff" en el párrafo de §3.3 (línea 101 reformulada en A1). Lista exacta en `12_meristem_spec.md`.
- **Reason codes REFUSE** (`HARD_LIMIT_DOMAIN` ≡ `SAFETY_DOWNGRADE` jurisdiccionalmente, `JURISDICTION_POLLEN`) — vive en `20_data_contracts.md` §3.4.

Si crees que alguno de estos sí debe estar arriba, dime y propongo línea concreta.

---

## Resumen aplicable

| # | Sección | Cambio | Prioridad |
|---|---|---|---|
| A1 | §3.3 línea 101 | Reformular "tool calling solo en chat" → "evaluator nunca depende de tool output" | recomendado |
| A2 | §7 línea 215 | Fecha tool calling: día 14 → día 26 (o ambas con clarificación) | recomendado |
| A3 | §8 línea 238 | Separar 5/5 mini-battery (día 24) de `tool_calls_recovered_from_text=1` (día 26) | recomendado |
| S1 | §6 paso 18 | Añadir mención al rationale Gemma 4 E4B (simetría con paso 6 de Rhizome) | opcional |
| S2 | §3.3 final | Mencionar `policy_origin`/`policy_scope` (durable vs transient) | opcional |

---

## Por mi parte

**Vía libre cuando integres los 3 ajustes técnicos.** Si decides aplicar también las 2 sugerencias opcionales, perfecto; si no, también firma como representación fiel del nodo Meristem real.

Gracias por la oportunidad de revisar antes de mergear. Y por la cifra del párrafo del README que me pediste el día 28: la frase final del doc (§3.3 línea 103) viene de ahí casi literal — funcionó bien la iteración corta.

— Meristem
