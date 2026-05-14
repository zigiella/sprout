# meristem_node/

**Abstract.** Meristem is Sprout's slow brain. It runs on a home laptop (FastAPI + SQLite), ingests bundles that Pollen carries from Rhizome nodes, applies a deterministic evaluator (four rules: confirm / conservative / alert / refuse) and emits durable `PolicyPacket` objects for the next window. Rationale composition and an operator-facing read-only chat use Gemma 4 E4B via `llama.cpp` with tool calling (recent-history lookup, cross-target comparison, previous-policy diff); **the evaluator itself never depends on the model**. Pollen talks to Meristem either over WebSocket or a parallel HTTP fallback (added after a real field test on day 27), discovered via mDNS as `meristem.local:13000`. **Nothing leaves the home network — no cloud, no accounts, no telemetry.**

---

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
