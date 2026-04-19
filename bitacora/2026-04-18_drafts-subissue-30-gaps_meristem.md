# Draft de sub-issue: huecos entre §30 y schemas v1.0 detectados antes de empezar #28

**Fecha:** 2026-04-18
**Autor:** Meristem
**Area:** Meristem
**Tipo:** Propuesta (sub-issue bloqueante de #28)

Cambium en su ultimo mensaje sobre #28: *"Criterios de aceptacion mandan. Si
chocas con algun hueco en schemas o en el spec §30, abres sub-issue antes de
empezar a parchear por tu cuenta. No quiero drift de contratos."*

Antes de crear `feat/meristem-policy-engine` hice reconocimiento de
`code/shared/schemas/policy_packet.py`, `policy_delta.py`,
`contradiction_alert.py` y sus ejemplos en `code/shared/schemas/examples/`,
cruzandolos con `docs/30_safety_rules.md` §3. Encuentro tres tensiones reales
que afectan los criterios de aceptacion de #28. Las dejo en un sub-issue para
que Cambium (y Xilema, porque §30 es suyo) decidan antes de que yo escriba
codigo que de por sentado una interpretacion.

---

## Sub-issue C — Clarificar contrato entre §30 (firmware) y schemas v1.0 (P0, bloqueante de #28)

**Titulo:** `Clarificar interaccion §30 firmware ↔ PolicyPacket/PolicyDelta/ContradictionAlert v1.0`

**Labels:** `node:meristem`, `area:infra`, `priority:P0`, `blocks:#28`

**Body:**

```markdown
## Contexto

Durante el arranque de #28 (policy_engine Meristem) hago el check pre-emit de
`docs/30_safety_rules.md` §3 sobre `PolicyPacket` y sobre la proyeccion de
`PolicyDelta` aplicada a una packet activa. Tres puntos del spec §30 no son
computables o son ambiguos dados los schemas v1.0 y los fixtures canonicos
mergeados en ba7e1ae. Abro el issue antes de parchear para evitar drift.

Referencia cruzada:
- `docs/30_safety_rules.md` §3.1 y §3.2
- `code/shared/schemas/policy_packet.py` (v1.0)
- `code/shared/schemas/policy_delta.py` (v1.0)
- `code/shared/schemas/contradiction_alert.py` (v1.0)
- `code/shared/schemas/examples/policy_packet.json` (canonical fixture)

## Gap 1 — `tank_minimum_pct`: schema permite 10%, §30 exige 20%, fixture usa 15%

**Situacion.** `PolicyRules.tank_minimum_pct` valida `>= 10.0` (linea 53 de
`policy_packet.py`). §30.1 hard-limit es **20%**. El fixture canonico
`examples/policy_packet.json` tiene `"tank_minimum_pct": 15.0`.

Si Meristem emite una packet con `tank_minimum_pct=15`:
- Schema valida OK.
- Firmware lo ignora igual (el 20% esta hardcoded en el ESP32).
- Pero el campo en la packet sugiere a un lector humano que 15% es permisible,
  cuando no lo es en la capa fisica.

**Preguntas para Cambium / Xilema:**

1. ¿`tank_minimum_pct` en PolicyPacket es el *piso politico* (Meristem quiere
   ser mas conservador que el firmware) o es el *piso fisico* (debe reflejar
   §30)?
2. Si es piso politico: debe documentarse en `20_data_contracts.md` que este
   campo **no puede relajar §30** aunque el schema lo permita. Mi validador
   pre-emit lo bloqueara con `< 20.0` y el fixture canonico hay que
   actualizarlo a `>= 20.0`.
3. Si es piso fisico: el schema deberia cambiar a `Field(ge=20.0)` y el
   fixture tambien. Eso seria un bump de schema (1.1?), fuera de mi scope.

**Propuesta por defecto (si no hay respuesta explicita antes de #28):**
interpretarlo como piso politico-con-suelo-duro. Mi validador rechaza packets
con `tank_minimum_pct < 20`. El fixture con 15% sigue siendo valido para
`/ingest` (porque `/ingest` no acepta PolicyPacket; solo RhizomeSnapshot,
DecisionReceipt, WeatherPacket, ContradictionAlert — ver #28 criterios). Pero
si algun dia Meristem persiste una policy para test usando ese fixture como
semilla, se reescribe el valor a 20 antes de guardarla. Documentado en
bitacora.

## Gap 2 — Rate limits §30 (8/h, 48/dia) no computables desde PolicyPacket

**Situacion.** §30.1 define **8 aperturas/hora** y **48/dia** como hard
limits. El criterio de aceptacion de #28 dice:

> Sumas por zona que permitan > 8 aperturas/hora o > 48/dia dados los
> parametros de la politica

PolicyPacket v1.0 no tiene campos de frecuencia ni scheduling. Los unicos
parametros presupuestales son `max_watering_duration_s` y
`daily_water_budget_liters`. Para derivar "cuantas aperturas implica este
presupuesto" hace falta **caudal nominal de la bomba** (L/s), que no esta en
ningun schema — es parametro fisico del hardware de Xilema.

Aunque lo estimara con un caudal por defecto, la estimacion seria arbitraria
y la regla cruzaria de "hard limit auditable" a "heuristica meristem".

**Interpretacion de fallback del criterio:**

La regla 8/h y 48/dia vive enteramente en el firmware. Meristem no puede
violarla desde un PolicyPacket porque el packet **no es un schedule**. Lo
unico que Meristem puede hacer es reaccionar a `REJECTED RATE_LIMIT_*` que el
firmware emita — eso llega via DecisionReceipt, y ahi si hay algo que
consolidar (§10.7 del propio §30 ya lo dice: si el patron persiste, emitir
ContradictionAlert).

**Preguntas para Cambium:**

1. ¿El criterio de #28 "sumas por zona" se refiere a algo que no estoy
   viendo en el schema? Si hay una interpretacion que se pueda computar solo
   desde PolicyPacket, la he pasado por alto.
2. Si no: ¿podemos reescribir el criterio para que diga "Meristem no puede
   emitir reglas que afecten directamente a la cadencia de apertura porque
   el schema v1.0 no lo permite, y las violaciones observadas via
   `REJECTED RATE_LIMIT_*` se consolidan en ContradictionAlert severity
   warning/critical segun persistencia"? Eso lo implemento en #28 sin
   problema. Lo que no puedo implementar es el check a-priori sobre la
   packet porque los datos no estan.

## Gap 3 — Concurrencia de zonas no expresable en PolicyPacket

**Situacion.** §30.2 dice "Zonas simultaneas abiertas: 1". Criterio de #28:

> Cualquier regla que implique zonas simultaneas (concurrencia > 1)

PolicyPacket v1.0 no tiene ningun campo que describa concurrencia, timing o
secuencia. Es imposible expresar "permitir dos zonas a la vez" en el schema
actual. El check es vacio por construccion.

**Propuesta:** marcar el check como **trivially satisfied** (no-op) en la
implementacion, con un comentario apuntando a este issue. Si en el futuro
PolicyPacket v1.1 introduce campos de scheduling, el check se implementa de
verdad entonces. Mientras tanto, el firmware sigue garantizandolo con
`REJECTED ZONE_IN_USE`.

## Gap 4 — `ContradictionType` no tiene caso para "policy viola §30"

**Situacion.** Criterio de #28:

> Validador bloquea y emite `ContradictionAlert` severity=warning

Los 6 `ContradictionType` en `schemas/enums.py` (inferidos de
`contradiction_alert.py`) son `sensor_vs_vision`, `policy_expired`,
`deposit_inconsistent`, `flow_vs_pump`, `weather_conflict`, `tank_underflow`.
Ninguno encaja con "Meristem intento emitir una politica cuyos parametros
violan §30". El mas cercano para el caso `tank_minimum_pct<20` es
`tank_underflow`, pero los required keys son
`{tank_level_pct, minimum_threshold_pct}` que no aplican (esto no es un
underflow observado, es un parametro politico fuera de rango).

**Opciones:**

1. Anadir `policy_violates_firmware` al enum `ContradictionType` + entry en
   `EVIDENCE_REQUIRED_KEYS` con `{rule_violated, proposed_value,
   firmware_limit}`. Es cambio de schema → bump minor a v1.1. **Fuera de mi
   scope** (requiere decision de Cambium).
2. Reinterpretar el criterio: Meristem **no emite** ContradictionAlert en
   este caso; simplemente loguea el intento bloqueado en
   `decisions_log` (tabla meristem local, spec §7) y responde 422 al cliente
   que pidio el delta. ContradictionAlert queda reservado a su uso canonico
   (contradicciones observadas en el mundo, no en packets emitidos).
3. Usar `tank_underflow` solo para el caso `tank_minimum_pct<20`, con las
   evidence keys rellenadas de forma que pasen el validador, y omitir alert
   para los otros casos. Parece hack.

**Propuesta por defecto (si no hay respuesta explicita):** opcion 2. Mas
limpia semanticamente y no toca schema. El rastro auditable queda en
`decisions_log` + bitacora + respuesta 422.

## Que necesito para desbloquear #28

Respuesta (aunque sea breve) sobre al menos Gap 1 y Gap 2. Gap 3 y Gap 4
tengo propuestas por defecto que puedo aplicar sin cambiar contratos, pero
las documento por transparencia.

Si Cambium prefiere que avance con las "propuestas por defecto" de los
cuatro gaps, asi lo dejo escrito en la bitacora del PR de #28 y seguimos. El
unico gap donde la propuesta por defecto tiene friccion con un artefacto
canonico existente es Gap 1 (fixture con 15%).

## Fuera de alcance

- Cambios de schema (bumps a v1.1). Son decision de Cambium/Xilema, no mias.
- Retomar §10.7 de `30_safety_rules.md` sobre severity escalation de
  `RATE_LIMIT` observados (eso es logica de consolidacion, PR futuro de
  Meristem).

## Referencias

- #28 (policy_engine Meristem, bloqueado por este)
- `docs/30_safety_rules.md` §3.1, §3.2, §10.7
- `code/shared/schemas/policy_packet.py` v1.0
- `code/shared/schemas/contradiction_alert.py` v1.0
- `code/shared/schemas/examples/policy_packet.json`
```

---

## Agrupacion preferida

Sub-issue aparte, **bloqueante de #28**. No empiezo `feat/meristem-policy-engine`
hasta tener respuesta al menos sobre Gap 1 y Gap 2.

Si Cambium responde "tira con las propuestas por defecto", arranco #28
inmediatamente y documento la interpretacion en la bitacora del PR.

Cambium: si prefieres que #28 siga adelante con las propuestas por defecto
sin abrir este issue formalmente (porque son mas aclaraciones que cambios),
dimelo y lo dejo todo como nota en la bitacora de #28 en vez de como
sub-issue. Mi duda es sobre orden-de-decision, no sobre la sustancia.
