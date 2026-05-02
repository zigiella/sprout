# meristem_node/

**Estado**: día 14, esqueleto FastAPI funcional stubeado. Construcción
real día 15-17. Demo-ready día 18.

## Qué es

El "cerebro lento doméstico" del ecosistema Sprout. Vive en un portátil
casero del agricultor (no en data center, no en hardware especializado).
Recibe bundles que Pollen trae de cada visita a Rhizome (snapshot +
DecisionReceipts + WeatherDigest + ValidationStamps), evalúa, y emite
un `PolicyPacket` actualizado para que Pollen lleve a Rhizome en la
próxima visita.

Jerarquía explícita del sistema (invariante adoptada review día 13):
*"lo físico manda → Rhizome arbitra → Pollen media → **Meristem afina**"*.

## Stack

- **FastAPI** + Pydantic + SQLite (file-based, sin servicios extra)
- **Inferencia**: cliente al `meristem_inference_adapter` con backend
  `llamacpp` extendido. Modelo: **Gemma 4 E4B Q4_K_M (~5 GB)** sobre
  `llama-server` local.
- **Tool calling Gemma 4** confirmado funcional día 14 (ver
  `verify_tool_calling.py`).

## Endpoints

```
POST /visit              → Pollen entrega bundle, recibe PolicyPacket
GET  /policy/latest      → consulta última policy emitida (debug/demo)
GET  /policy/{policy_id} → consulta policy por id (trazabilidad)
GET  /health             → estado + métricas
GET  /docs               → OpenAPI/Swagger automático
```

## Capas (ver ARCHITECTURE.md)

```
HTTP Layer (FastAPI)
  ↓ IngestService     (validación + persistencia bundle)
  ↓ Evaluator         (4 reglas determinísticas + LLM rationale)
  ↓ PolicyComposer    (construye PolicyPacket válido)
  ↓ Persistence       (SQLite: bundles + policies + decisions)
```

**Decisión crítica**: la decisión NO la toma el LLM. Lógica determinista
con 4 reglas (CONFIRM, CONSERVATIVE, ALERT, REFUSE). El LLM solo
escribe `rationale` (técnico + prosa amable al operador). Aísla riesgo
de drift del modelo de la jerarquía de seguridad.

## Cómo correr (día 14, stub)

```bash
cd code/meristem_node
pip install -r requirements.txt
python -m src.main
# levanta en http://127.0.0.1:13000
# /docs disponible
```

Endpoints todavía devuelven respuestas stubeadas día 14. Lógica real
cierra día 16.

## Referencias

- `ARCHITECTURE.md` — diseño por capas + flujo end-to-end + mini-batería
- `draft_system_prompt_meristem_es.md` — borrador del prompt
- `verify_tool_calling.py` — test que validó tool calling con llama.cpp
- `bitacora/2026-04-29_rhizome-v05-completo-y-tool-calling-validado_meristem.md`
