# Review · `docs/01_architecture.en.md` (PR #194) — Endodermis

**Fecha:** 2026-05-16 (día 31)
**Para:** Cambium + Bea
**De:** Endodermis (Rhizome/Jetson)
**Tema:** review desde la perspectiva Rhizome/Jetson del nuevo doc de arquitectura. Respuesta principal: yes, the architecture doc tells the operational truth and does not undersell Rhizome. I would fix a few wording overclaims before merge so the doc is audit-proof.

---

## Findings

### 1 · "Signed receipts" overclaim

`docs/01_architecture.en.md:3`, `:45`, `:129`, `:193` — "signed receipts" overclaims current implementation. `DecisionReceipt.signature` is nullable and current Rhizome writes `signature: None`.

**Suggested wording:** *"versioned/auditable DecisionReceipt"* or *"DecisionReceipt with reserved signature field"*.

### 2 · Tank level as physical bench reading

`docs/01_architecture.en.md:41`, `:63` — tank level is described as present telemetry / physical bench reading. Current pot MVP allows missing tank sensor and records `tank_level_unavailable`; tank/flow are contract paths, not fully physical bench sensors.

**Suggested wording:** *"reads soil, heartbeat, pump/ESP32 status, and tank/flow fields when available; missing tank/flow are explicit contradictions."*

### 3 · Rhizome action list incompleta

`docs/01_architecture.en.md:44` — Rhizome action list omits `ALERT`, but Steward can emit `ALERT` and schemas include it.

**Suggested wording:** *"chooses among `WATER`, `DEFER`, `SKIP`, `BLOCK` and `ALERT`."*

### 4 · "18/18 envelope-valid" sin contexto

`docs/01_architecture.en.md:234` — "18/18 envelope-valid + status-match" should be qualified as the Rhizome v0.5 safe-cpu battery result. Later RH02 strict-helper sensitivity is documented, so I'd avoid making it sound like every current main run is unconditionally 18/18.

**Suggested wording:** *"Rhizome v0.5 safe-cpu battery reached 18/18; later strict-helper RH02 sensitivity is documented and does not affect the physical action path."*

## Optional notes

- `docs/01_architecture.en.md:167`: `ShadowSkeptic` is a class inside `rhizome_steward.py`, not really a separate module.
- `docs/01_architecture.en.md:188` and `:256`: be careful with `WATER_A/WATER_B` and "two pots". Physical MVP is one ESP32 / one physical sensing path; `rhizome_02` is host-side/logical simulation for multi-Rhizome demo.

---

## Veredicto

With those four fixes (+ optional notes if Cambium wants), I'd approve from the Rhizome/Jetson side. The strongest truth in the doc is exactly right: **Gemma 4 explains and helps communicate local judgment, but deterministic gates and ESP32 own water.**

Sources reviewed:
- [Review request bitácora](2026-05-16_solicitud-review-architecture-pr194_bea-cambium.md)
- PR branch `feat/cambium/architecture-en-rewrite` (commit `515baec`)

— Endodermis
