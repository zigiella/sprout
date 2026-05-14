# Sprout — Roadmap

> Sprout is a safety-bounded decision network for water under absence.
> This roadmap extends the same authority model: every new feature respects the rule that **physical safety prevails, Rhizome arbitrates, Pollen mediates, Meristem refines** — and that every intelligence has jurisdiction and expiry.

The MVP delivered in the Gemma 4 Good Hackathon (May 2026) is intentionally minimum but real. The roadmap below is a list of direct extensions, not a wishlist.

---

## 1. Production water semantics

**Goal**: close the autonomous `WATER` command into a contractual production path.

**Why pending**: the MVP keeps autonomous `WATER` in `DRY_RUN` while supervised `PUMP_PULSE` runs as `TEST_ONLY`. The distinction protects users while the production loop is closed.

**What it requires**:
- Flow meter integration on `FLOW_PULSES` (currently stubbed).
- `NO_FLOW_DETECTED` rule promoted to active firmware enforcement.
- Field calibration of `SOIL_WET_BELOW_RAW` / `SOIL_DRY_ABOVE_RAW` per soil type.
- Bench validation of 24h continuous autonomous loops without operator presence.

---

## 2. Dual-agent maturation

**Goal**: promote `ShadowSkeptic` from observer to bounded second authority.

**Why pending**: the current `ShadowSkeptic` runs deterministic with `affects_decision=false`. Before giving authority to a second voice, Sprout measures whether that voice actually improves safety.

**What it requires**:
- Comparative analysis of `ShadowSkeptic` objections vs later outcomes (false positives / false negatives).
- Promotion of recurring proven objections into deterministic gates of the primary steward.
- Optional Gemma 4 promotion of the auditor itself, with jurisdiction strictly limited to "question the first agent, not decide".

---

## 3. Language fine-tuning

**Goal**: bring Sprout into local agricultural vocabularies and minority languages.

**Why pending**: the current Pollen path uses Gemma 4 E4B base for audio compilation. It works in English and Spanish. Local farms speak local languages.

**What it requires**:
- Fine-tuning of Gemma 4 E4B over agricultural corpora in Pular, Wolof, Swahili, Quechua, Catalan, Basque and others.
- Universal Presentation Layer pattern preserved: contracts stay in stable English; only surface language adapts in Pollen.
- Validation against local field operators per language.

---

## 4. Sensor and actuator expansion

**Goal**: more evidence, more zones, more autonomy.

**What it requires**:
- **Vision input** through Gemma 4 multimodal: cameras detect visible water stress, pests, growth — non-authoritative evidence to inform Rhizome rationale.
- **Multi-zone irrigation**: independent valves per soil profile within a single plot, sharing the same physical safety envelope.
- **Conductivity, pH, soil temperature** sensors as optional Rhizome inputs.
- **Local weather station** to replace or enrich `WeatherDigest` objects carried by Pollen when stable connectivity is intermittent.
- **Integration with public meteorological APIs** (AEMET, MeteoCat, etc.) when network is available — still as one input among others.

---

## 5. Full-duplex voice

**Goal**: Pollen also speaks back to the operator.

**Why pending**: the current Pollen path is voice-in (operator speaks → MissionPatch). The natural next step is voice-out (Pollen also reads receipts, asks clarification, gives proactive warnings).

**What it requires**:
- Two-way audio pipeline through LiteRT-LM.
- Pre-alert conversational pattern for low tank, expired policy, flagged anomaly.
- Refusal as conversation: when Pollen does not understand, it asks back instead of returning a code.

---

## 6. Energy and federation

**Goal**: longer field autonomy and multi-plot scale.

**What it requires**:
- **Solar power for Rhizome**: Jetson MAXN_SUPER + PV panel + LiFePO4 battery for complete energy autonomy.
- **Federation between multiple Jetsons** in larger farms (>10 plots): scheduler local coordinator + cross-Jetson context sharing without requiring central network.
- **Scheduler local agent** coordinating N logical nodes within a single Jetson for clustered plots.

---

## 7. Meristem capability scaling

**Goal**: richer slow-brain policy reasoning.

**What it requires**:
- Evaluator extended from 4 rules to 8–12 (seasonality, heterogeneous crops, multi-month budgets).
- Fine-tuning E4B over synthetic + real agricultural datasets.
- Parallel-LLM mode comparing rationales across multiple model variants for policy quality auditing.

---

## Out of scope (deliberately)

- **Cloud control plane**: Sprout's thesis is local-first. Adding a mandatory cloud roundtrip would invalidate the architecture.
- **Replacing the farmer**: Sprout preserves the farmer's criteria during absence. It is not an autonomous farm AI.
- **LLM as physical authority**: the ESP32 firmware veto is non-negotiable. No model output, fine-tuned or otherwise, ever signs the final physical action.

---

## How this roadmap evolves

The Sprout project keeps a public `bitacora/` (development journal). Every architectural decision is recorded there with a date, a reason and a context. The roadmap above is the synthesis of intentions documented in the bitácora; the bitácora is where the live thinking lives.

**Sprout is open, local AI for water decisions under absence: expiring authority, signed receipts, a second local voice that audits without authority, and a physical layer that can say no.**

*Apache 2.0 · Built on Gemma 4 by Google. Gemma is a trademark of Google LLC.*
