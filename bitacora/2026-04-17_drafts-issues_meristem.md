# Drafts de issues propuestos por Meristem

**Fecha:** 2026-04-17
**Autor:** Meristem
**Area:** Meristem
**Tipo:** Propuesta

Fichero untracked. Cambium: copia/pega los cuerpos para abrir los issues en GitHub. Cuando esten creados, borrame el fichero o commitealo segun prefieras.

---

## Issue A — Policy engine (P0)

**Titulo:** `Implementar policy_engine Meristem sobre Gemma E4B + endpoints ingest/policies/deltas`

**Labels:** `node:meristem`, `area:infra`, `priority:P0`

**Body:**

```markdown
## Contexto

Segundo PR de Meristem, sobre el andamio mergeado en #17 (commit cd326b2).
Aqui entra el razonamiento estrategico real: Pollen empuja evidencia,
Meristem la consolida, llama al E4B local via Ollama, valida contra los
6 schemas canonicos de `code/shared/schemas/` y emite `PolicyPacket` o
`PolicyDelta` respetando los limites duros del firmware.

Spec: `docs/12_meristem_spec.md` §5, §6, §7.
Contratos: `docs/20_data_contracts.md` v1.0.
Limites fisicos: `docs/30_safety_rules.md` §3.

## Criterios de aceptacion

### Endpoints HTTP

- [ ] `POST /ingest` — acepta `RhizomeSnapshot`, `DecisionReceipt`, `WeatherPacket` o `ContradictionAlert`. Valida via pydantic (schemas de shared, sin duplicar). Persiste en tabla `evidence` con `kind` discriminador. 422 en payload invalido.
- [ ] `GET /policies/{rhizome_id}` — devuelve el `PolicyPacket` activo (no expirado) para ese nodo. 404 si no hay.
- [ ] `GET /deltas/pending/{rhizome_id}` — lista los `PolicyDelta` con status `pending` para ese nodo.
- [ ] `POST /deltas/propose` — recibe delta propuesto por Pollen, valida (ver seccion §30 abajo) y lo persiste con status `validated` / `rejected` + razon.

### Policy engine

- [ ] `prompts/system_v1.txt` iterado a version funcional (fijar contrato de system prompt + schema en el user prompt).
- [ ] `policy_engine.py` construye contexto desde `evidence` + policy activa, llama a Ollama E4B con structured output, valida output con pydantic, persiste resultado.
- [ ] Latencia objetivo del spec (<60s E2E) medida en test de smoke y documentada en bitacora.

### Respeto pre-emit de limites firmware (no negociable)

Todo `PolicyPacket` o delta-aplicado-a-packet que Meristem emita tiene que
respetar `docs/30_safety_rules.md` §3 **antes** de persistirse. Validador
bloquea y emite `ContradictionAlert` severity=warning si:

- [ ] `rules.max_watering_duration_s > 60`
- [ ] `rules.tank_minimum_pct < 20`
- [ ] Sumas por zona que permitan > 8 aperturas/hora o > 48/dia dados los parametros de la politica
- [ ] Cualquier regla que implique zonas simultaneas (concurrencia > 1)

Racional: el firmware va a rechazar igual, pero pre-empt en Meristem
evita ruido en el tablero de alertas y deja rastro auditable del intento.

### Tests

- [ ] Tests contra fixtures canonicas de `code/shared/schemas/examples/` (mergeadas en ba7e1ae). Un test por schema verificando que `/ingest` las acepta.
- [ ] Test de smoke contra Ollama real, marcado `@pytest.mark.ollama`, skip si el daemon no responde (para CI).
- [ ] Test negativo: `/deltas/propose` con delta que haria `max_watering_duration_s=120` => 409/422 con `reason=violates_safety_rule`.
- [ ] Test negativo: policy_engine que intenta emitir politica que viola §30 no la persiste como activa.
- [ ] El test negativo del sombra (`test_shadow_off.py`) sigue verde tras los nuevos imports.

### Entregables de repo

- [ ] Bitacora `bitacora/YYYY-MM-DD_policy-engine-meristem_meristem.md` antes del PR.
- [ ] `code/meristem/README.md` actualizado (endpoints + como correr con Ollama).
- [ ] PR con `Closes #<este issue>`.

## Fuera de alcance (para el PR siguiente)

- Consolidator job automatico disparado por N evidencias (por ahora endpoints sincronos).
- Meristem sombra activo (`compare.py` real contra Gemma 31B). Queda con flag off.
- RAG / memoria estacional profunda.
- Revocaciones programadas de politica (`policy_revocation` no esta aun en schemas v1.0).

## Dependencias

- #17 — bootstrap Meristem (merged cd326b2)
- PR #19 — ejemplos canonicos JSON en `code/shared/schemas/examples/` (merged ba7e1ae)

## Referencias

- `docs/12_meristem_spec.md` §5 (prompt engineering), §6 (ciclo de consolidacion), §7 (persistencia)
- `docs/20_data_contracts.md` (RhizomeSnapshot, PolicyPacket, PolicyDelta, WeatherPacket, ContradictionAlert)
- `docs/30_safety_rules.md` §3 (hard limits)
- `CONTRIBUTING.md` §12 (flujo de tablero)
```

---

## Issue B — Lint anti-leak del sombra (P2)

**Titulo:** `Anadir test AST que prohiba import de google.genai fuera de src/shadow/`

**Labels:** `node:meristem`, `area:infra`, `priority:P2`

**Body:**

```markdown
## Contexto

En `bitacora/2026-04-17_bootstrap-meristem_meristem.md` (seccion "Riesgos
asumidos") deje constancia de que `tests/test_shadow_off.py` verifica el
no-leak en runtime pero no en codigo fuente. Un futuro refactor podria
introducir `from google import genai` fuera de `src/shadow/` y el test
seguiria verde mientras `SHADOW_ENABLED=false`, porque el submodulo no
se importaria.

Este issue cierra ese hueco con un lint estatico minimo.

## Criterios de aceptacion

- [ ] `tests/test_no_genai_leak.py` que recorre `src/` (excluyendo `src/shadow/`) con `ast` de stdlib y falla si encuentra:
  - `from google import genai`
  - `import google.genai`
  - `from google.genai import ...`
- [ ] Test positivo: confirma que el check NO falla sobre `src/shadow/shadow_client.py` (que legitimamente importa `google.genai`).
- [ ] Test negativo sintetico (en tmp dir, no tocando repo real): inyecta un fichero con import prohibido y verifica que el linter lo detecta.
- [ ] Sin dependencias nuevas: solo `ast` + pytest.

## Fuera de alcance

- Integrar ruff/flake8 como lint global (es decision de coordinacion, no de Meristem).
- Cubrir casos ofuscados (`importlib.import_module("google.genai")`). El modelo de amenaza es "desarrollador descuidado", no "atacante con evasion".

## Dependencias

- Ninguna. Ortogonal al issue A.

## Referencias

- `docs/12_meristem_spec.md` §2.4 (reglas duras del sombra)
- Bitacora `bitacora/2026-04-17_bootstrap-meristem_meristem.md` seccion "Riesgos asumidos"
```

---

## Agrupacion preferida

Side-issue aparte, no dentro del PR del policy_engine. Razones:

- El PR del policy_engine ya trae 4 endpoints + validador §30 + engine + suite nueva. Meter el lint hincha diff y complica review.
- El lint es ortogonal, <50 LoC + un test. Side-issue se mergea rapido como limpieza de deuda.

Arranco lint inmediatamente despues del PR del policy_engine (una tarjeta a la vez, §12.2).
