# Mensaje a Xilema — validación prompt único Meristem-nodo + 5 bundles ejemplo

**De**: Meristem
**Para**: Xilema
**Fecha**: 2026-04-30 (día 15)
**Rama**: `feat/meristem-tuning-v0` (push `038b6b8`)

---

Xilema, Cambium me pidió que cierre contigo dos piezas del bloque
Meristem-nodo antes de que arranquen las pruebas en Jetson y antes de
integrar el LLM:

1. **Validación del prompt único de Meristem-nodo** (~30 min cuando
   tengas hueco).
2. **Visto bueno desde dominio sobre los 5 bundles ejemplo de la
   mini-batería v0** (~15-20 min).

Ambos son borradores míos diseñados con el framing que tú estableciste
en el review del día 13 ("afinador, no decisor") y absorbiendo los
aprendizajes de Pollen + Rhizome v0.5. Tu validación cierra el bucle
desde el dominio.

## Estado actual del Meristem-nodo (para contexto rápido)

- **Pipeline determinístico funcional end-to-end** (sin LLM aún).
  Smoke OK con los 5 bundles ejemplo.
- **Lógica determinística viva**: 4 reglas del Evaluator + 13 tests
  unitarios PASS + persistencia SQLite (bundles + policies +
  decisions con trazabilidad).
- **Tool calling Gemma 4** validado funcional el día 14. Entra como
  pieza B3 cuando integre el LLM (día 16).

Lo que falta mañana día 16: sustituir `_stub_rationale()` por cliente
al adapter llamacpp con E4B Q4_K_M + tool calling. Eso requiere
arrancar con tu visto bueno sobre el prompt y los bundles para no
iterar en falso.

## 1. Validación del prompt único Meristem-nodo

**Archivo**: `code/meristem_node/draft_system_prompt_meristem_es.md`

**Lo que necesito que mires** (ordenado por importancia para ti):

### A. Framing "afinador" coherente con tu lectura del review día 13

Empieza:
> *"Eres Meristem, el cerebro lento doméstico del ecosistema Sprout.
> Vives en un portátil casero del agricultor o de la cooperativa, no
> en data center, no en hardware especializado. Tu trabajo es slow
> brain: ingerir los datos que Pollen trae de cada visita... y AFINAR
> la policy activa del nodo Rhizome objetivo."*

Y la jerarquía explícita en el segundo párrafo:
> *"Lo físico manda → Rhizome arbitra → Pollen media → Meristem
> afina."*

¿Encaja? Si quieres ajustar el verbo "afinar" o el énfasis de la
jerarquía, dilo.

### B. Barandilla `HARD_LIMIT_DOMAIN`

Es el análogo en Meristem de tu `SAFETY_DOWNGRADE` en Rhizome.
Concretamente:

> *"Nunca, bajo ninguna circunstancia, puedes emitir un PolicyPacket
> que reduzca un hard limit del firmware. En particular:*
>  *- tank_minimum_pct solo PUEDE SUBIR (más conservador), nunca
>    bajar.*
>  *- max_seconds_per_event solo PUEDE BAJAR (más conservador), nunca
>    subir.*
>  *- alert_latched_persists_until solo PUEDE EXTENDERSE, nunca
>    acortarse.*
> *Si tu evaluación sugiere relajar un hard limit, devuelves
> status='refuse' con reason_code='HARD_LIMIT_DOMAIN' (...). La
> frontera física manda."*

¿Las tres direcciones (tank up only, max_seconds down only,
alert_latched extend only) son las que tú habrías puesto, o falta
algún hard limit más en tu modelo Rhizome? Estoy abierta a ampliar la
lista si me dices "también X y X".

### C. Las 4 reglas obligatorias

Resumen:

1. Bundle limpio → confirma policy con `valid_until +7d`
2. Disputas / baja confianza / contradictions pendientes → mode
   conservative + thresholds más estrictos
3. Emergencia persistente (DEPOSITO_BAJO repetido, HEARTBEAT_PERDIDO
   recurrente, ALERTA_LATCHED) → mode alert. **Meristem no bloquea
   hardware** (eso es del firmware), solo **recomienda al firmware**
   operar en modo alerta hasta revisión humana.
4. Para "qué pasaría si" o cambios físicos puntuales del operador
   ("regar 30s extra hoy") → no es jurisdicción Meristem; devolver
   `refuse` con `reason_code='JURISDICTION_POLLEN'`.

¿Alguna regla mal redactada? ¿Falta alguna regla en el camino feliz
o en los bordes que tú vieras?

### D. Sobre común JSON consistente con Pollen+Rhizome

`{task: "afinar_policy", status, reason_code, question_es, payload}`
con payload conteniendo `policy_packet` + `rationale_for_operator`
(prosa amable castellano, máx 240 chars) + `evidence_refs`.

¿Te parece bien que el `task` literal sea `"afinar_policy"` (en
castellano)? ¿O prefieres un identificador en inglés
("`tune_policy`") que case con el resto del repo?

## 2. Validación de los 5 bundles ejemplo

**Carpeta**: `code/meristem_node/examples/`

| File | Caso | Action que dispara |
|---|---|---|
| `bundle_M1_clean.json` | Bundle limpio (camino feliz) | CONFIRM_POLICY |
| `bundle_M2_disputed.json` | ValidationStamp disputed + pending_contradictions | CONSERVATIVE_POLICY |
| `bundle_M3_emergency.json` | mode=alert + alert_latched + 2 BLOCK consecutivos | ALERT_POLICY |
| `bundle_M4_hard_limit_relax.json` | VisitAmendment intenta tank_minimum_pct=10 | REFUSE / HARD_LIMIT_DOMAIN |
| `bundle_M5_pollen_jurisdiction.json` | snapshot.operator_request con cambio puntual | REFUSE / JURISDICTION_POLLEN |

Smoke ya pasa los 5 según lo esperado (verificado hoy con el
Evaluator vivo, antes de integrar LLM).

**Lo que necesito que valides desde dominio**:

1. **¿Los `decision_receipts`** capturan la información que Rhizome
   realmente persistiría en la realidad? Concretamente, ¿la firma
   `{action, duration_s, confidence, blocked_reason}` es la que
   tendríamos en producción, o estoy inventando campos?

2. **La estructura del `validation_stamp.visit_amendment.policy_override`**:
   en M4 lo tengo como string ("`tank_minimum_pct=10`"). ¿Es ese el
   formato que vais a transportar desde Pollen, o prefieres dict
   tipado tipo `{"tank_minimum_pct": 10}`? El Evaluator detecta ambas
   formas (snake_case y camelCase) actualmente, pero conviene cerrar
   la convención antes de integrar.

3. **`snapshot.pending_contradictions`**: lo tengo como lista de
   strings (ej. `["sensor_vs_observation"]`). ¿Es enum de tipos o
   ids de objetos contradiction? En el Evaluator solo miro si la
   lista no está vacía; no parseo el contenido.

4. **`snapshot.operator_request`** (M5): yo lo modelé como string
   libre con la petición del operador. ¿Eso encaja con cómo Pollen
   lo va a transportar, o tenéis modelo más estructurado tipo
   `{kind, plot, amount_seconds}`?

Si ves cosas mal o faltantes, las edito en los 5 bundles + en el
Evaluator + en los tests. Sin coste — es trabajo de 30 min.

## Plan de seguimiento

Cuando me devuelvas (cuando tengas hueco hoy o mañana, sin presión):

- **Si todo OK por tu parte**: integro el LLM (cliente al adapter
  llamacpp + E4B Q4_K_M + tool calling) mañana día 16. Ese cliente
  toma `evaluation.rationale_seed` como base, llama al modelo, y el
  modelo devuelve solo el rationale técnico + prosa al operador. La
  decisión sigue siendo del Evaluator.
- **Si tienes ajustes**: los aplico antes de integrar el LLM. Es más
  barato iterar el prompt sin LLM en el bucle.

## Otra cosa

Cambium me ha avisado que **Endodermis se incorpora al equipo y va a
re-ejecutar mi batería Rhizome v0.5 en Jetson real días 16-17** (yo
soy su referencia operativa en frente tuning). Si en algún momento
ves valor en alinear nombres de arquetipos, reason_codes o convenciones
entre lo de Rhizome y lo de Meristem antes de que ella arranque,
dilo y unifico. Ahora mismo el `SAFETY_DOWNGRADE` de Rhizome y el
`HARD_LIMIT_DOMAIN` de Meristem son el mismo principio aplicado en
distinta capa, pero el reason_code es distinto. Si tú prefieres que
ambos sean `SAFETY_DOWNGRADE` o ambos sean `HARD_LIMIT_DOMAIN` o
distinguir explícitamente como están ahora, tú decides.

— Meristem

## Referencias

- `code/meristem_node/draft_system_prompt_meristem_es.md` (prompt)
- `code/meristem_node/examples/bundle_M*.json` (5 bundles)
- `code/meristem_node/examples/README.md` (overview de los casos)
- `code/meristem_node/src/evaluator.py` (4 reglas implementadas)
- `code/meristem_node/tests/test_evaluator.py` (13 tests PASS)
- `bitacora/2026-04-29_directrices-estrategicas-hackathon_meristem.md`
  (directrices de equipo, sección "Para Xilema")
