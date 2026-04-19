# Policy engine Meristem — implementacion y resolucion de los 4 gaps de §30

**Fecha:** 2026-04-19
**Autor:** Meristem
**Area:** Meristem
**Tipo:** PR bitacora (cierra #28)

## Contexto

Segundo PR de Meristem sobre el andamio mergeado en #17 (cd326b2). Entrega
el razonamiento estrategico real: endpoints `/ingest`, `/policies/*`,
`/deltas/*`, validador pre-emit de los limites duros del firmware §30, y el
nucleo de consolidacion `policy_engine.consolidate(...)` con llamada real a
Ollama E4B via structured output.

Arranque documentado en la bitacora complementaria
`2026-04-18_drafts-subissue-30-gaps_meristem.md` (reconocimiento previo que
detecto 4 tensiones entre §30 y schemas v1.0). Cambium cerro los 4 gaps el
2026-04-19 y me desbloqueo; este PR aplica las decisiones acordadas.

## Resolucion de los 4 gaps

| Gap | Tension | Decision de Cambium | Implementacion |
|---|---|---|---|
| 1 | `tank_minimum_pct` schema `>=10`, §30 `>=20`, fixture a 15 | §30 manda. Validador rechaza `<20`. Fixture canonico se sube a 20 en este mismo PR via `builders.py`. Schema queda en 10 (bump a v1.1 no se aborda ahora). | `safety_rules.FIRMWARE_TANK_MINIMUM_PCT = 20.0`. `code/shared/schemas/examples/builders.py` subido a 20.0; JSONs regenerados via `make generate-examples`. Rationale del `decision_receipt_blocked` actualizado coherentemente (11% → 18%, "15%" → "20%"). |
| 2 | Rate limits 8/h y 48/dia no computables desde PolicyPacket | No-op en pre-emit. Se consolidan post-hoc via `REJECTED RATE_LIMIT_*` observados en DecisionReceipts. | No implementado en este PR. Documentado como N/A en `safety_rules.check_policy_packet` (comentario explicito). PR futuro para consumir `DecisionReceipt` agregados. |
| 3 | Concurrencia de zonas (1 max) no expresable en PolicyPacket | No-op con comentario. | Mismo modulo, mismo comentario. El firmware lo garantiza con `REJECTED ZONE_IN_USE`. |
| 4 | `ContradictionType` no cubre "policy viola §30" | Opcion 2: `decisions_log` local + 422 con `reason=violates_safety_rule`. `ContradictionAlert` queda para contradicciones observadas, no pre-emit. | Aplicado en `routes.propose_delta` y en `policy_engine.consolidate`: intento bloqueado escribe fila en `decisions_log` con `action="blocked_by_safety"` o `"blocked_invalid_schema"`. 422 al cliente con violaciones desglosadas. |

## Decisiones de diseno de este PR

**Endpoint `/ingest` con envelope `{kind, payload}`.** Alternativas consideradas:
(a) sub-paths por tipo `/ingest/snapshot`..., (b) adivinar el tipo por forma
del payload. Escogi envelope explicito por claridad y por evitar ambiguedad
cuando dos schemas comparten campos. Sus cuatro `kind` validos estan en
`routes.INGEST_KINDS`; anadir un kind nuevo es un diff unilinea + un test.

**`/deltas/propose` valida sincrono.** El spec permite validacion en batch
asincrona, pero este PR no expone job de consolidacion (queda para el
siguiente). Un delta valido sale como `validated`; `pending` queda reservado
para el flujo futuro. El estado `pending` ya vive en el schema de la tabla
`deltas` y `/deltas/pending/*` lista lo que haya, este o no alimentado en
este PR.

**Proyeccion de delta sobre base.** Validar el delta aislado no basta:
`replace rules.max_watering_duration_s = 60` es valido en si pero la
proyeccion podria quedar bien; en cambio `= 120` si necesita comparar contra
el limite duro. La proyeccion se hace en `safety_rules.project_delta` con
mutacion de un `model_dump()` y re-validacion completa via pydantic. Eso
tambien detecta patches que rompen invariantes inter-campo (ej: `target_pct
< min_pct`): se rechazan como `projection_invalid_schema`.

**Policy engine no expuesto por HTTP.** `consolidate(...)` es API interna
para invocar desde un consolidator job futuro o desde tests. Integrarlo en
un endpoint (p.ej. `POST /policies/consolidate/{rhizome_id}`) requeriria
ademas decidir que subset de evidencia se pasa al LLM, y eso es logica de
consolidator (fuera de alcance). El test negativo del engine ("LLM devuelve
packet con duration=120 => no persiste") cubre el criterio #28 con `_FakeOllama`.

**Timeout del cliente Ollama a 120s por defecto.** `/api/generate` con E4B
en hardware modesto tarda 20-40s segun tamano del user prompt. El timeout
del `ping` queda aparte a 2s.

## Tests (55 pasan, 1 skip)

```
tests/test_health.py            3 passed   /health + SQLite init + shadow-on-raises
tests/test_settings.py         13 passed   defaults + parsing
tests/test_llm_client.py        3 passed   ping ok/fail, modelo expuesto
tests/test_schemas_importable 1 passed   6 schemas importables desde shared
tests/test_shadow_off.py        1 passed   subproceso verifica no-leak runtime
tests/test_safety_rules.py     12 passed   unit del validador §30
tests/test_ingest.py            7 passed   fixtures canonicos + 422
tests/test_policies.py          3 passed   GET activa / 404 / expirada
tests/test_deltas.py            7 passed   pending + propose (OK + 409 + 422)
tests/test_policy_engine.py     5 passed   happy + §30 + invalid_schema + prompt
tests/test_smoke_ollama.py      1 skipped  (no daemon en CI)
```

Regresion: los 20 tests del bootstrap siguen verdes (incluido el negativo
critico `test_shadow_off.py`).

Tests de `code/shared/schemas/tests/` siguen verdes (33 passed) tras editar
`builders.py` y regenerar los JSONs canonicos.

## Entregables

- `code/meristem/src/safety_rules.py` — validador pre-emit §30.
- `code/meristem/src/policy_engine.py` — consolidator (API interna).
- `code/meristem/src/routes.py` — 4 endpoints HTTP.
- `code/meristem/src/persistence.py` — helpers CRUD sobre las 5 tablas.
- `code/meristem/src/llm_client.py` — `generate_json()` con structured output.
- `code/meristem/src/prompts/system_v1.txt` — prompt funcional.
- 6 suites de tests nuevas.
- `code/meristem/README.md` actualizado (endpoints, engine, tests).
- `code/shared/schemas/examples/builders.py` — `tank_minimum_pct` 15 → 20 (Gap 1).
- `code/shared/schemas/examples/policy_packet.json` y `decision_receipt_blocked.json` — regenerados.
- Drafts-file del 2026-04-18 incluido (reconocimiento previo).

## Latencia

El smoke test (`test_smoke_ollama.py`) mide E2E contra un Ollama real. No
corre en CI. Budget fijado a 90s con objetivo 60s (spec §6). Cuando Bea lo
ejecute en el portatil, anota el resultado como comentario en la PR para
cerrar el criterio.

## Fuera de alcance (PRs siguientes)

- Consolidator job automatico (disparador por N evidencias).
- Endpoint `POST /policies/consolidate` que invoque el engine.
- Consolidacion post-hoc de `REJECTED RATE_LIMIT_*` observados (Gap 2 + §30 §10.7).
- Meristem sombra activo (`compare.py` real). Flag sigue off.
- RAG / memoria estacional.
- Revocaciones programadas (schema no lo modela en v1.0).

## Riesgos y deuda asumida

- **Gap 1 inconsistente a nivel de schema.** Schema sigue aceptando `>=10`
  aunque el validador nuestro rechace `<20`. Si manana Pollen propone un
  delta que deja la policy en 15, el schema lo valida y el validador lo
  rechaza. El comportamiento es correcto (fail-closed), pero el contrato
  queda con friccion. Cambium autorizo dejarlo asi y aplazar el bump a v1.1.
- **`generate_json` confia en `format=<schema>` de Ollama.** Versiones
  anteriores a 0.1.30 no lo soportan; ahi cae a `format="json"` sin
  garantia estructural y la validacion pydantic absorbe el posible drift.
  `ollama --version` deberia salir en el README de deployment cuando lo
  haya.
- **El smoke test puede fallar en CI si alguien anade soporte Ollama.** El
  marker `@pytest.mark.ollama` lo aisla; ademas el `client.ping()` skipea
  si el daemon no responde. Hay que recordar no correr `-m ollama` en CI.

## Referencias

- Issue #28 (policy_engine, cerrado por este PR).
- Drafts-file `bitacora/2026-04-18_drafts-subissue-30-gaps_meristem.md`.
- Respuesta de Cambium a los 4 gaps (2026-04-19, en canal Bea).
- `docs/12_meristem_spec.md` §5, §6, §7.
- `docs/20_data_contracts.md` v1.0.
- `docs/30_safety_rules.md` §3.
- `CONTRIBUTING.md` §11.1 (multi-agent clone), §12 (flujo de tablero).
