# meristem_node/

**Abstract.** Meristem is Sprout's slow brain. It runs on a home laptop (FastAPI + SQLite), ingests bundles that Pollen carries from Rhizome nodes, applies a deterministic evaluator (four rules: confirm / conservative / alert / refuse) and emits durable `PolicyPacket` objects for the next window. Rationale composition and an operator-facing read-only chat use Gemma 4 E4B via `llama.cpp` with tool calling (recent-history lookup, cross-target comparison, previous-policy diff); **the evaluator itself never depends on the model**. Pollen talks to Meristem either over WebSocket or a parallel HTTP fallback (added after a real field test on day 27), discovered via mDNS as `meristem.local:13000`. **Nothing leaves the home network — no cloud, no accounts, no telemetry.**

---

## What it is

The "slow domestic brain" of the Sprout ecosystem. It lives on the farmer's home laptop (not a data centre, not specialised hardware). It receives bundles Pollen carries from each visit to a Rhizome (snapshot + DecisionReceipts + WeatherDigest + ValidationStamps), evaluates them, and emits an updated `PolicyPacket` for Pollen to carry back to the Rhizome on the next visit.

The system's explicit hierarchy (invariant adopted in day-13 review):
*"physical layer prevails → Rhizome arbitrates → Pollen mediates → **Meristem refines**"*.

## Stack

- **FastAPI** + Pydantic + SQLite (file-based, no extra services)
- **Inference**: a client to `meristem_inference_adapter` with an extended `llamacpp` backend. Model: **Gemma 4 E4B Q4_K_M (~5 GB)** running over a local `llama-server`.
- **Gemma 4 tool calling** confirmed functional on day 14 (see `verify_tool_calling.py`).

## Endpoints

```
POST /visit              → Pollen delivers a bundle, receives a PolicyPacket
GET  /policy/latest      → query the latest emitted policy (debug/demo)
GET  /policy/{policy_id} → query a policy by id (traceability)
GET  /health             → status + metrics
GET  /docs               → automatic OpenAPI / Swagger
```

## Layers (see ARCHITECTURE.md)

```
HTTP Layer (FastAPI)
  ↓ IngestService     (bundle validation + persistence)
  ↓ Evaluator         (4 deterministic rules + LLM rationale)
  ↓ PolicyComposer    (builds a valid PolicyPacket)
  ↓ Persistence       (SQLite: bundles + policies + decisions)
```

**Critical decision**: the decision is NOT made by the LLM. Deterministic logic with 4 rules (CONFIRM, CONSERVATIVE, ALERT, REFUSE). The LLM only writes the `rationale` (technical + operator-friendly prose). This isolates model-drift risk from the safety hierarchy.

## How to run (day 14, stub)

```bash
cd code/meristem_node
pip install -r requirements.txt
python -m src.main
# starts on http://127.0.0.1:13000
# /docs available
```

Endpoints still return stubbed responses on day 14. Real logic closed on day 16.

## References

- `ARCHITECTURE.md` — layered design + end-to-end flow + mini-battery
- `draft_system_prompt_meristem_es.md` — system prompt draft
- `verify_tool_calling.py` — test that validated tool calling with llama.cpp
- `bitacora/2026-04-29_rhizome-v05-completo-y-tool-calling-validado_meristem.md`

---

## Note on language

This README is English-first. Internal bitácoras (Spanish-language working journals) and the day-by-day development trace live under [`bitacora/`](../../bitacora/). See the [Language note in the root README](../../README.md#language-note) for the project-wide policy.
