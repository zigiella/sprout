# meristem/

Nodo estrategico local. Corre en el portatil de Bea (16 GB) con `gemma4:e4b` via Ollama.

Detalle completo en [`docs/12_meristem_spec.md`](../../docs/12_meristem_spec.md).

## Rol

- Consume evidencia entregada por Pollen (snapshots, alerts, packets, deltas propuestos)
- Consolida y revisa politicas
- Emite policy_packets o valida/reajusta policy_deltas
- Sirve endpoint HTTP local que Pollen consume

## Stack

- Python 3.11+
- Ollama (Gemma 4 E4B local) via cliente HTTP
- `fastapi` + `uvicorn` para API HTTP local
- `pydantic` v2 para schemas (reutiliza `code/shared/schemas/`, no duplica)
- `sqlite3` para persistencia
- `google-genai` **solo si** `SHADOW_ENABLED=true` (Meristem sombra para validacion en dev)

## Estructura actual

```
meristem/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py             # FastAPI app, /health + router /ingest, /policies, /deltas
│   ├── routes.py           # endpoints HTTP
│   ├── settings.py         # env vars -> Settings
│   ├── llm_client.py       # Ollama client (ping + generate_json)
│   ├── persistence.py      # SQLite schema + helpers CRUD
│   ├── safety_rules.py     # validador pre-emit §30 (max_duration, tank_min)
│   ├── policy_engine.py    # consolidacion: evidence + policy -> LLM -> validate -> persist
│   ├── prompts/
│   │   └── system_v1.txt   # system prompt de Meristem
│   └── shadow/             # Meristem sombra (solo dev, flag-gated)
│       ├── __init__.py
│       └── shadow_client.py
└── tests/
    ├── conftest.py
    ├── test_settings.py
    ├── test_health.py
    ├── test_shadow_off.py         # negativo: shadow no carga con flag off
    ├── test_schemas_importable.py
    ├── test_llm_client.py
    ├── test_safety_rules.py       # validador §30 (unit)
    ├── test_ingest.py             # /ingest con fixtures canonicos + 422
    ├── test_policies.py           # GET /policies/{rhizome_id}
    ├── test_deltas.py             # /deltas/pending + /deltas/propose (§30)
    ├── test_policy_engine.py      # engine con LLM mock (happy + §30)
    └── test_smoke_ollama.py       # marcado @pytest.mark.ollama (skip sin daemon)
```

## Variables de entorno

Ver `.env.example`. Claves:

| Var | Default | Nota |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Endpoint del daemon Ollama |
| `OLLAMA_MODEL` | `gemma4:e4b` | Modelo local del spec §2.1 |
| `MERISTEM_PORT` | `7070` | Puerto del servicio HTTP |
| `DB_PATH` | `./meristem.db` | SQLite local |
| `SHADOW_ENABLED` | `false` | **Regla dura del spec §2.4.** Demo se graba con esto en false. |
| `GEMINI_API_KEY` | (vacio) | Solo requerido si `SHADOW_ENABLED=true` |
| `SHADOW_MODEL` | `gemma-4-31b-it` | Modelo cloud del sombra |

## Como correr

```bash
cd code/meristem
pip install -r requirements.txt
ollama pull gemma4:e4b        # fuera del scope de este bootstrap
cp .env.example .env
python -m src.main            # expone en http://localhost:7070
```

Los schemas compartidos (`code/shared/schemas/`) se importan via `PYTHONPATH`. En un entorno estable:

```bash
pip install -e ../shared
```

El `conftest.py` de los tests ya anade `code/shared` al path, asi que `python -m pytest tests` funciona sin instalar shared.

## Endpoints

| Metodo | Path | Descripcion |
|---|---|---|
| `GET` | `/health` | Liveness + metadata (version, modelo, shadow_enabled). |
| `POST` | `/ingest` | Pollen empuja evidencia. Envelope `{"kind": "...", "payload": {...}}`. Kinds validos: `rhizome_snapshot`, `decision_receipt`, `weather_packet`, `contradiction_alert`. Responde 202 con `{stored_id, kind}`. 422 si el payload no valida el schema del kind. |
| `GET` | `/policies/{rhizome_id}` | Policy activa (no expirada) mas reciente para ese nodo. 404 si no hay. |
| `GET` | `/deltas/pending/{rhizome_id}` | Lista los `PolicyDelta` con status `pending` para ese nodo. |
| `POST` | `/deltas/propose` | Pollen propone un `PolicyDelta`. Meristem valida el schema, comprueba que la `base_policy_id` sea la policy activa del nodo (409 si no), proyecta el delta y valida la proyeccion contra §30. Responde 201 si validated, 422 con `reason=violates_safety_rule` y lista de violaciones si no. **Idempotente por `delta_id`: reenviar el mismo delta sobrescribe la fila existente.** |

### Limites duros del firmware (docs/30 §3) aplicados pre-emit

`safety_rules.py` bloquea la emision/aceptacion si un PolicyPacket o la proyeccion de un PolicyDelta infringe:

- `rules.max_watering_duration_s > 60` → bloquea (§30.1).
- `rules.tank_minimum_pct < 20` → bloquea (§30.2).

Rate limits 8/h y 48/dia y concurrencia de zonas NO son pre-checkables desde PolicyPacket v1.0 (no hay campos de scheduling ni caudal). Se consolidaran post-hoc via `REJECTED RATE_LIMIT_*` observados en DecisionReceipts en un PR futuro. Ver bitacora `2026-04-18_drafts-subissue-30-gaps_meristem.md` y aclaracion de Cambium (2026-04-19).

## Policy engine

`policy_engine.consolidate(db_path, target_node_id, evidence, llm)` es la API interna (no expuesta HTTP en este PR):

1. Lee la policy activa y la pasa al user prompt como contexto.
2. Llama a Ollama con `system_v1.txt` + schema de `PolicyPacket` como structured output.
3. Valida la salida contra `PolicyPacket` (pydantic).
4. Si es valida, aplica `safety_rules.check_policy_packet`.
5. Si pasa, persiste como policy activa. Si no, loguea el intento en `decisions_log` con action `blocked_by_safety` o `blocked_invalid_schema` y retorna `EngineResult(packet=None, reason=...)`.

## Tests

```bash
cd code/meristem
python -m pytest tests -v               # suite completa (skippea Ollama smoke)
python -m pytest -m ollama tests -v     # solo smoke, requiere daemon + gemma4:e4b
```

Cobertura: settings, /health + init SQLite, cliente Ollama, shadow off por construccion, importacion de los 6 schemas canonicos, validador §30 (unit + integrado), los 4 endpoints, policy_engine con LLM mock.

## Regla dura del sombra

El Meristem sombra (Gemma 4 31B via Google AI Studio) es **solo herramienta de validacion en desarrollo**. `docs/12_meristem_spec.md` §2.4 lo deja explicito:

- Flag `SHADOW_ENABLED=false` por defecto
- Codigo aislado en `src/shadow/`
- El demo grabado se rueda con flag apagado y sin `GEMINI_API_KEY`

`tests/test_shadow_off.py` verifica por construccion que con el flag apagado no se carga ni `google.genai` ni los modulos de shadow.
