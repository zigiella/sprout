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

## Estructura actual (bootstrap)

```
meristem/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py             # FastAPI app, /health
│   ├── settings.py         # env vars -> Settings
│   ├── llm_client.py       # Ollama client (stub)
│   ├── persistence.py      # SQLite schema init
│   ├── prompts/
│   │   └── system_v1.txt   # draft del system prompt de Meristem
│   └── shadow/             # Meristem sombra (solo dev, flag-gated)
│       ├── __init__.py
│       ├── shadow_client.py
│       └── compare.py
└── tests/
    ├── conftest.py
    ├── test_settings.py
    ├── test_health.py
    ├── test_shadow_off.py      # negativo: shadow no carga con flag off
    ├── test_schemas_importable.py
    └── test_llm_client.py
```

El policy_engine real (consolidacion + llamada a E4B) entra en PR siguiente, con su propia bitacora.

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

- `GET /health` — liveness

Endpoints de ingest/emision (`/ingest`, `/policies/*`, `/deltas/*`) se anaden en PR siguiente.

## Tests

```bash
cd code/meristem
python -m pytest tests -v
```

Cobertura del bootstrap: settings, /health + init SQLite, cliente Ollama, shadow off por construccion, importacion de los 6 schemas canonicos.

## Regla dura del sombra

El Meristem sombra (Gemma 4 31B via Google AI Studio) es **solo herramienta de validacion en desarrollo**. `docs/12_meristem_spec.md` §2.4 lo deja explicito:

- Flag `SHADOW_ENABLED=false` por defecto
- Codigo aislado en `src/shadow/`
- El demo grabado se rueda con flag apagado y sin `GEMINI_API_KEY`

`tests/test_shadow_off.py` verifica por construccion que con el flag apagado no se carga ni `google.genai` ni los modulos de shadow.
