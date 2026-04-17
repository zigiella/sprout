# Bootstrap Meristem: scaffold FastAPI + Ollama stub + persistencia + tests

**Fecha:** 2026-04-17
**Autor:** Meristem
**Area:** Meristem
**Tipo:** Avance

---

## Contexto

Primera entrada de Meristem. Bea y Cambium autorizaron (via issue #16, `node:meristem` / `area:infra` / `priority:P0`) arrancar el andamio de `code/meristem/` siguiendo el spec de `docs/12_meristem_spec.md` §4, sin meter policy_engine real ni razonamiento estrategico en el primer PR. Ese alcance viene en el PR siguiente con su propia bitacora.

Antes de tipear codigo lei: `CONTRIBUTING.md` completo (especial atencion a §11.1 multi-agente sobre el mismo clone y §12 flujo de tablero), `docs/01_architecture.md`, `docs/20_data_contracts.md`, `docs/30_safety_rules.md`, `docs/12_meristem_spec.md`, y las ultimas bitacoras (`2026-04-16_safety-rules-v1_cambium.md`, `2026-04-16_data-contracts-v1_cambium.md`, `2026-04-17_schemas-pydantic-v2_xilema.md`, `2026-04-17_convenciones-autoria-bilinguismo_cambium.md`).

## Que hicimos

Rama: `feat/meristem-bootstrap`.

### Estructura creada en `code/meristem/`

```
meristem/
├── README.md               # reescrito con estructura real
├── requirements.txt
├── pyproject.toml
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py             # FastAPI app, /health, init SQLite
│   ├── settings.py         # env -> dataclass Settings
│   ├── llm_client.py       # OllamaClient stub (ping /api/tags)
│   ├── persistence.py      # init_db + connect, 5 tablas
│   ├── prompts/
│   │   └── system_v1.txt   # draft del system prompt
│   └── shadow/
│       ├── __init__.py     # vacio a proposito: no carga submodulos
│       ├── shadow_client.py
│       └── compare.py
└── tests/
    ├── conftest.py         # anade code/shared al sys.path
    ├── test_settings.py
    ├── test_health.py
    ├── test_llm_client.py
    ├── test_schemas_importable.py
    └── test_shadow_off.py
```

### Contrato de invocacion local

- `GET /health` → `{status, version, model, shadow_enabled}`. Suficiente para que Pollen verifique liveness en PR siguiente.
- `create_app(settings)` inicializa SQLite (5 tablas segun spec §7) antes de montar rutas.
- Import lazy de shadow dentro de `create_app`: `if settings.shadow_enabled: from .shadow import shadow_client`. Con flag off, el subarbol `src.shadow.*` no se toca.
- `OllamaClient` es stub: constructor + `ping()` contra `/api/tags`. Sin llamadas `/api/generate` aun. Lo usaran los siguientes PRs.

### Schemas

No dupliqué nada. Los 6 schemas canonicos (`RhizomeSnapshot`, `PolicyPacket`, `PolicyDelta`, `WeatherPacket`, `ContradictionAlert`, `DecisionReceipt`) se importan desde `code/shared/schemas/`. El `conftest.py` de los tests anade `code/shared` al `sys.path` para no obligar a `pip install -e ../shared` en cada entorno de CI. El README documenta ambos caminos.

### Test negativo del sombra (lo que Cambium destaco)

`tests/test_shadow_off.py` corre un subproceso Python limpio con `SHADOW_ENABLED=false`, importa `create_app(load_settings())` y comprueba que ni `google.genai` ni `src.shadow.shadow_client` ni `src.shadow.compare` aparecen en `sys.modules`. Es verificacion por construccion, no por inspeccion de codigo.

Matiz que descubrí al correrlo: el paquete namespace `google` puede aparecer en `sys.modules` como side-effect de otros paquetes (protobuf, grpcio, etc.) sin que Meristem haya tocado nada. Lo critico por seguridad es `google.genai` (el cliente del sombra). El test queda restringido a los modulos que realmente significan "shadow cargado", no a cualquier `google.*`.

Test complementario en `test_health.py`: con `SHADOW_ENABLED=true` y `google-genai` no instalado, `create_app` tira `ImportError` al importar `google.genai`. Hace explicito el contrato: flag on exige dependencia opcional presente.

### Resultados

```
$ python -m pytest tests -v
20 passed in 2.52s
```

`code/shared/schemas/tests` sigue pasando 25/25 (no toque nada ahi).

### Identidad git

Este clone es compartido (Cambium escribe tambien desde otra conversacion). Sigo §11.1: **no toco `.git/config`**, paso identidad inline en cada commit:

```
git -c user.name="Meristem" -c user.email="meristem@sprout.local" commit ...
```

## Por que

### Por que no meter policy_engine real en este PR

- El andamio se prueba ejecutable con `/health` y tests. Un policy_engine sin evaluacion robusta de prompts y sin batería de casos es un PR que no puedo defender en review.
- Pollen (Floema) puede empezar a cablear sus mocks HTTP contra `/health` + endpoints-por-venir sin bloquearse en la logica de consolidacion.
- Cada PR pequeno con su bitacora deja mejor rastro para el writeup que un mega-PR que mezcla andamiaje, prompting y evaluacion.

### Por que import lazy de shadow dentro de `create_app`

El spec §2.4 dice que el demo se graba con flag apagado y sin credencial. Si `src/shadow/__init__.py` importa `shadow_client` de serie, un desarrollador descuidado podria tener `google-genai` instalada por accidente y **cargarla** aunque el flag este off. El import lazy elimina esa trampa: para cargar `google.genai` hace falta flag on **y** llamar a `create_app`. Verificado por test.

### Por que SQLite init en `create_app` y no en un comando separado

`create_app` es idempotente (CREATE TABLE IF NOT EXISTS) y el coste es despreciable. Arrancar el servicio sin tablas crearia un error `no such table` en el primer `/ingest`, que es peor UX que aceptar 200µs de latencia de boot.

### Por que tests que leen el schema SQLite tras `create_app`

Afirma el contrato de persistencia en tests, no solo en el spec. Si alguien renombra una tabla sin actualizar el test, el test falla y lo detectamos en review.

### Por que `OllamaClient` es stub y no hace `/api/generate`

- No necesito llamar al modelo para este PR. Solo demostrar que el cliente HTTP se construye con el host del settings y puede pingear.
- Llamar al modelo sin un prompt fijado (system_v1.txt esta en draft) serian experimentos de prompt engineering disfrazados de codigo de produccion. Me lo reservo para el PR siguiente donde entra el prompt versionado.

### Por que `system_v1.txt` es draft y no esta fijado

Cambium lo autorizó explicitamente: "un draft honesto sirve; lo iteramos en PR posteriores con su bitacora". El draft cubre los principios duros (emitir politicas con TTL, prudencia ante contradicciones, respeto a limites firmware §30) sin comprometerse aun a estructura de system+user+schema. Eso se itera con datos reales.

### Por que `.env.example` con `SHADOW_ENABLED=false` explicito

Redundante con el default en `settings.py`, pero el spec §2.4 lo pide visible. Cuando alguien copie `.env.example` a `.env` el primer dia, lo **ve** y no necesita leer spec para saber que el flag existe.

## Que queda pendiente

Para este PR:
- [ ] `git push origin feat/meristem-bootstrap`
- [ ] Avisar a Bea para que pase el mensaje a Cambium: rama lista para PR `Closes #16`

Para los PRs siguientes de Meristem (sin orden fijado):
- [ ] Policy engine: prompt `system_v1` iterado + llamada real a E4B con `structured output` + validacion post-hoc pydantic de `PolicyPacket` / `PolicyDelta`
- [ ] Endpoints `/ingest`, `/policies/{rhizome_id}`, `/deltas/pending/{rhizome_id}`, `/deltas/propose` (consumen los schemas de shared)
- [ ] Consolidator: job que se dispara tras N evidencias y llama al policy_engine
- [ ] `shadow/compare.py` real: harness de comparacion local vs 31B, diffs persistidos en `shadow_comparisons`
- [ ] Tests contra Ollama real (opt-in, skip si el daemon no responde)
- [ ] Respeto explicito de limites firmware §30 en los prompts y validaciones (rechazo pre-emit de cualquier politica con `max_watering_duration_s > 60`, `tank_minimum_pct < 20`, etc.)

## Riesgos asumidos

- **El test negativo de shadow no cubre todos los vectores de leak.** Si alguien en el futuro hace un `import google.genai` en cualquier punto de `src/` fuera de `src/shadow/`, el test seguiria verde mientras la condicion `SHADOW_ENABLED=false` esté activa. Mitigacion razonable: el lint CI puede anadir una regla "no `from google import genai` fuera de `src/shadow/`" cuando queramos reforzarlo. No lo hago en este PR por no aumentar scope.
- **`OllamaClient.ping()` es lo unico probado contra el daemon.** El resto del cliente (generacion, streaming) se cablea en el PR siguiente con tests de contrato reales.
- **`conftest.py` modifica `sys.path` global del proceso.** Es la forma menos invasiva de integrar con `code/shared/` sin forzar instalacion editable. Si en el futuro se adopta `pip install -e ../shared` en CI, se puede eliminar el truco de path — pero no lo bloqueo hoy.

## Enlaces

- [docs/12_meristem_spec.md](../docs/12_meristem_spec.md) — spec fuente
- [docs/20_data_contracts.md](../docs/20_data_contracts.md) — schemas consumidos
- [docs/30_safety_rules.md](../docs/30_safety_rules.md) — limites que respetaran los prompts del PR siguiente
- [CONTRIBUTING.md §11.1](../CONTRIBUTING.md) — multi-agente sobre mismo clone
- Issue `#16` — Bootstrap meristem

---

**Firma:** Meristem
