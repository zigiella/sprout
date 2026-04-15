# meristem/

Nodo estrategico local. Corre en el portatil de Bea (16 GB) con `gemma4:e4b` via Ollama.

Detalle completo en [`docs/12_meristem_spec.md`](../../docs/12_meristem_spec.md).

## Rol

- Consume evidencia entregada por Pollen (snapshots, alerts, packets, deltas propuestos)
- Consolida y revisa politicas
- Emite policy_packets o valida/reajusta policy_deltas
- Sirve endpoint HTTP local que Pollen consume

## Stack

- Python 3.11
- Ollama client (para Gemma 4 E4B local)
- `fastapi` + `uvicorn` para API HTTP local
- `pydantic` para validacion de schemas
- `sqlite3` para persistencia
- `google-genai` **solo si** `SHADOW_ENABLED=true` (Meristem sombra para validacion)

## Estructura (a construir)

```
meristem/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── main.py             # FastAPI app
│   ├── consolidator.py
│   ├── policy_engine.py
│   ├── validator.py
│   ├── llm_client.py       # Ollama client
│   ├── shadow/             # solo dev - Gemma 4 31B cloud
│   │   ├── shadow_client.py
│   │   └── compare.py
│   ├── prompts/
│   │   └── system_v1.txt
│   └── persistence.py      # SQLite
└── tests/
```

## Variables de entorno

```
# .env
SHADOW_ENABLED=false          # true solo en desarrollo
GEMINI_API_KEY=               # solo si SHADOW_ENABLED=true
OLLAMA_HOST=http://localhost:11434
MERISTEM_PORT=7070
DB_PATH=./meristem.db
```

## Como correr

```bash
pip install -r requirements.txt
ollama pull gemma4:e4b        # ya deberia estar pulled
cp .env.example .env
python -m src.main
```

Expone API en `http://localhost:7070`.

## Endpoints principales (draft)

- `POST /ingest` — Pollen empuja evidencia nueva
- `GET /policies/{rhizome_id}` — Pollen recoge politica vigente
- `GET /deltas/pending/{rhizome_id}` — Pollen recoge deltas a entregar
- `POST /deltas/propose` — Pollen propone delta para validacion
- `GET /health` — liveness
