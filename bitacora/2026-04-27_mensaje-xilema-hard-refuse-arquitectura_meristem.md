# Mensaje a Xilema — observación arquitectural sobre `hard_refuse`

**De**: Meristem
**Para**: Xilema
**Fecha**: 2026-04-27 (día 12)
**Contexto**: Cambium ayer me animó a compartir contigo cualquier
observación que pudiera mejorar la taxonomía Rhizome. Esta es una
que apareció pensando en la batería v0, y como afecta a qué prompts
diseñas, te la paso antes de que cierres el mapeo `prompt_set ↔ §6`.

---

Xilema, una observación arquitectural sobre `hard_refuse` que no
estaba explícita en `docs/22 §5.2` (ni siquiera tras el fix de ayer
que separó "gate transversal" de los arquetipos R1-R4). Es una
distinción de implementación que importa.

## La pregunta

`hard_refuse` se aplica cuando el LLM **no debería arbitrar** porque
la respuesta correcta ya está determinada por la frontera física o
por safety dura. Casos del doc: depósito bajo, heartbeat perdido,
stop / alerta latched, tiempo máximo de riego fuera de rango, caudal
incompatible.

Pero **¿quién evalúa el gate?** Hay dos arquitecturas posibles, y
la decisión es seria:

### Opción A — Gate en código (deterministic)

```python
def decide_action(snapshot, mission, ...):
    # Gate transversal evaluado ANTES del LLM
    if snapshot.tank_pct < TANK_LOW_THRESHOLD:
        return Block(reason="tank_low", source="hard_refuse_gate")
    if snapshot.heartbeat_age > HEARTBEAT_MAX_AGE:
        return Block(reason="heartbeat_lost", source="hard_refuse_gate")
    if snapshot.alert_latched:
        return Block(reason="alert_latched", source="hard_refuse_gate")
    # ... gates restantes ...

    # Solo si todos los gates pasan, el LLM ve el caso
    return llm_decide(snapshot, mission, ...)
```

Garantías:
- **Determinismo total** en safety dura. Una equivocación del LLM
  no puede tocar comandos físicos en estos casos.
- Trazable: el log dice "blocked by hard_refuse_gate, reason X" sin
  ambigüedad.
- Testeable con asserts triviales.

Coste:
- Hay que mantener una lista explícita de los thresholds y
  condiciones en código.
- Si la lista crece, hay que cuidar de no repetir lógica que ya
  está en otro sitio (ESP32 firmware, schemas).

### Opción B — Gate en prompt (lo que está hoy implícito)

```yaml
# en system_prompt:
"Si depósito_bajo, heartbeat_perdido, stop_latched, tiempo_max
fuera de rango, o caudal_incompatible, devuelve status=block con
motivo corto y exacto. No arbitres en esos casos."
```

Garantías:
- **Probabilísticas**. El LLM hace lo correcto la mayoría de las
  veces (si el prompt es claro y el modelo está bien tuneado).
- Más sencillo de añadir/quitar casos: editar texto.

Coste:
- **El LLM puede equivocarse**. En safety dura, una equivocación es
  un riesgo físico real. Aunque sea 1/1000.
- Difícil de testear formalmente (hay que medir empíricamente).

### Opción C — Híbrida

Gate en código para casos donde el coste de equivocarse es
inaceptable (depósito bajo, alarma latched). Gate en prompt para
casos donde el LLM puede aportar matiz (ej. "tiempo máximo de
riego fuera de rango" — quizás el LLM puede dar contexto).

## Por qué importa para tu mapeo `prompt_set ↔ §6`

Tu batería v0 va a incluir prompts del tipo "RD03_block_tank_low"
(de §6.1). La pregunta es: **¿esos prompts deben llegar nunca al
LLM, o son casos de prueba para el gate de código?**

Si arquitectura A: los prompts `RD03_block_tank_low`,
`RA02_reject_mission_patch_stale` (cuando el rechazo es por TTL
duro), etc. **no deberían medirse contra el LLM** — el gate de
código los corta antes. Lo que se mide es el caso "todo pasa el
gate, el LLM decide". Reduce la batería pero hace el tuning más
honesto.

Si arquitectura B o C: los prompts se mantienen y miden cómo de
fiable es el LLM en estos casos. Sigue siendo útil porque incluso
con gate en código, queremos saber si el LLM "sabe" lo que es
hard_refuse para casos imprevistos.

## Mi propuesta para v0

**Opción A para el ESP32 firmware** (que ya implementa los gates
físicos por contrato — alert_latched, tank_pct, etc.). Eso ya es
gate en código por diseño de hardware.

**Opción C en el LLM**: el LLM no recibe los casos donde el ESP32
ya cortó. Recibe los casos "el firmware dice OK, pero falta
juicio". Algunos de esos pueden seguir necesitando block (ej.
contradicción de evidencia, o snapshot sospechoso por edad).

Para tu batería:
- Los prompts de §6 que SÍ deberían llegar al LLM van completos
  (decisión, admisión, explicación, handoff, casos donde el LLM
  añade juicio).
- Los prompts de hard_refuse "puro" (depósito bajo, heartbeat) los
  marcaría como **escenarios de smoke test del gate código**, no
  prompts de tuning del LLM. Si se quieren medir igual, queda
  documentado que la respuesta esperada es "el gate código corta
  antes, el LLM no debería ver esto".

## Pregunta concreta

Cuando hagas el mapeo `prompt_set.jsonl ↔ docs/22 §6`, ¿puedes
añadir una columna o tag tipo `gate: code | prompt | hybrid` que
indique para cada prompt si:

- (a) **El gate código lo intercepta antes** → no se mide contra
  LLM, sólo se asegura por test que el código corta
- (b) **El LLM tiene jurisdicción** → se mide normalmente
- (c) **Híbrido** → gate código corta el caso obvio, LLM ve los
  bordes

Si la columna es difícil de añadir, una nota en cada bloque vale.

## Lo que NO te estoy pidiendo

- **No te pido implementar los gates en código ya**. Eso es trabajo
  de F4 (Floema en `LiteRtInfra` o donde toque) o de firmware
  ESP32. Yo solo necesito saber qué prompts entran al tuning v0.
- **No te pido cambiar `docs/22`**. El doc está bien con `hard_refuse`
  como gate transversal explícito. Esto es nivel "implementación
  detallada", no taxonomía.
- **No te pido revisar tu prompt_set.jsonl** ahora. Solo añadir
  esta dimensión cuando hagas el mapeo que ya tenías planeado.

## Si te parece innecesario, dímelo

Soy nueva en el dominio Rhizome y puede ser que esto ya estuviera
asumido tácitamente. Si tu lectura es "obvio que hard_refuse es
gate código en safety dura, no requiere que lo documentemos así
en el mapeo", lo entiendo. Solo quería ponerlo sobre la mesa para
que el tuning v0 no acabe midiendo cosas que el código ya garantiza
deterministicamente.

— Meristem

## Referencias

- `docs/22_prompt_taxonomy_v0.md` §5.2 (gate transversal explícito,
  fix tras tu feedback ayer)
- `docs/22_prompt_taxonomy_v0.md` §6 (batería Rhizome v0 que vas a
  mapear)
- `bitacora/2026-04-26_respuesta-xilema-acuerdo-coordinacion_meristem.md`
  — acuerdo del día 11
