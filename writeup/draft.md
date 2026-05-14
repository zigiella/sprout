# Sprout: local criteria for water when nobody is there

**Subtitle:** Open, local AI for water decisions under absence, with expiring authority, signed receipts and a physical veto.

## The problem

Remote irrigation fails when decisions arrive late. A plot changes every hour: soil dries, tanks empty, weather shifts, valves fail, pests appear, and priorities change. The person who understands the field visits periodically. The network appears intermittently. The decision still has to happen near the water.

Sprout targets that decision gap. Immediate irrigation criteria live in the field. Human intent enters during the visit. Longer-term policy is reviewed at home, after receipts and visit bundles have been carried back.

The demo uses living pots as stand-ins for small plots, community gardens, rural school greenhouses, and cooperative zones where connectivity and human presence arrive in fragments.

## What Sprout is

Sprout is a local-first AI architecture for water decisions under absence. It combines three Gemma 4 nodes with one physical veto layer:

- **Rhizome** reads the plot and arbitrates immediate action.
- **Pollen** mediates the visit and compiles human intent.
- **Meristem** refines the next policy window at home.
- **ESP32** owns the physical safety boundary.

The operating invariant is simple: **physical layer prevails, Rhizome arbitrates, Pollen mediates, Meristem refines**. Physical authority increases near water; context and policy authority increase away from it.

Every intelligence has jurisdiction. Every instruction has expiry.

## Rhizome and ESP32

Rhizome runs Gemma 4 E2B on a Jetson Orin Nano Super through `llama.cpp`. It reads local telemetry, applies deterministic safety and need gates, and chooses among `WATER`, `DEFER`, `SKIP`, and `BLOCK`.

Rhizome does not move water directly. It emits a candidate action and a signed `DecisionReceipt`. The receipt records evidence, active policy, candidate action, ESP32 outcome, final action, and rationale. When a person returns, the system explains what happened through receipts. The explanation is grounded in recorded evidence.

Gemma 4 E2B improves the local rationale over facts already closed by deterministic logic. The action is set by the steward and safety gates. The explanation becomes useful to a human without becoming the source of physical authority.

The ESP32 safety coprocessor runs custom ESP-IDF firmware and owns the physical layer. It checks heartbeat, tank state, duration limits, alert state, and actuator safety. It blocks unsafe commands and records legible reasons such as `JETSON_HEARTBEAT_LOST`, `TANK_LOW`, `EVENT_DURATION_OUT_OF_RANGE`, and `ALERT_LATCHED`.

The physical bench path includes a relay, a 12V pump, soil moisture readings, and supervised `PUMP_PULSE` tests. Autonomous `WATER` remains conservative in `DRY_RUN`; supervised physical proof uses `TEST_ONLY`.

## The dual-agent pattern

Sprout includes a local dual-agent pattern inside Rhizome. The primary steward closes the decision through deterministic gates: telemetry, policy, TTL, cooldown, tank state, safety state, and execution mode. A second local agent, `ShadowSkeptic`, audits the decision and records objections with `affects_decision=false`.

`ShadowSkeptic` creates safety evidence. It flags conservative alternatives, distrust signals, and reasons to review a situation. It never irrigates, never vetoes, never rewrites the final action, and never touches the ESP32 path.

That boundary gives the second agent a precise jurisdiction: observe, question, record. Each disagreement becomes a measurable event. Future versions can promote recurring, useful objections into deterministic gates. Even skepticism has jurisdiction.

## Pollen

Pollen runs on Android with Gemma 4 E4B through LiteRT-LM. It converts a human visit into structured intelligence the field can use immediately.

A person says: “I’ll be back Friday. This plant can stay drier than you think; water it a bit less.” Pollen captures local audio, feeds it to Gemma 4 E4B, compiles the instruction into an expiring `MissionPatch`, validates the patch with deterministic guardrails, and refuses incoherent or unsafe instructions.

A `MissionPatch` carries a short TTL because it belongs to a specific visit. Late objects expire. Expired objects are rejected and logged with a legible reason.

Pollen also carries context between disconnected Rhizomes. It transports `WeatherDigest` objects, visit reports, receipts, validations, and mission patches. A phone reaches many places before stable connectivity does.

Pollen also gives Rhizome a human interface. When a person asks what happened since the last visit, Pollen translates receipts and local summaries into language the person can act on.

## Meristem

Meristem runs on the farmer’s home laptop with Gemma 4 E4B through `llama.cpp`. It ingests bundles carried by Pollen, evaluates recent decisions with deterministic logic and tool-calling-assisted review, and emits durable `PolicyPacket` objects for the next policy window.

Meristem does not decide immediate irrigation. It refines criteria after the pressure of minutes has passed: which plot needs attention, which sensor deserves less trust, how water budgets should change, and which pattern emerges across visits.

A `PolicyPacket` carries a validity window. Its authority belongs to days, not seconds. Rhizome validates it before use. The ESP32 remains above it in the safety hierarchy.

## Why Gemma 4 matters here

Sprout uses Gemma 4 where local intelligence changes the system.

Gemma 4 E2B gives Rhizome local explanation and bounded reasoning on constrained edge hardware. Gemma 4 E4B gives Pollen multimodal audio understanding on Android through LiteRT-LM, so spoken field knowledge becomes a validated `MissionPatch` without a cloud roundtrip or a separate speech-to-text service. Gemma 4 E4B gives Meristem tool-calling-assisted policy review on a home laptop through `llama.cpp`.

The model configuration work is part of the engineering. We tested context size, output budget, prompt discipline, and thinking behavior across local runtimes. A practical result shaped the demo path: output length drove latency more strongly than input context in the Meristem path. Shorter structured outputs preserved the contract and improved usability.

Each node has a different model profile. Rhizome needs short, stable, bounded outputs. Pollen needs audio understanding, refusal, and schema fidelity. Meristem spends more time on policy review and rationale. Model configuration becomes a property of jurisdiction.

## Safety and trust

Sprout signs decisions, expires authority, and records refusals.

The critical path starts with deterministic checks: schema validation, TTL, authority, cooldown, tank state, heartbeat, hard limits, and receipt creation. Gemma 4 writes rationales, compiles human criteria, adapts surface language, and supports review. The final physical authority stays with the safety layer.

A `MissionPatch` represents the visit and carries a short TTL. A `PolicyPacket` represents a wider policy window and carries validity. A `WeatherDigest` expires before weather context becomes stale. Late objects are rejected and logged.

The dual-agent layer follows the same rule. `ShadowSkeptic` records objections. Those objections become data. Proven objections can later become deterministic rules. The current agent remains observational.

## What we built

The MVP implements the pattern across hardware, mobile, and laptop paths.

Rhizome runs on Jetson with Gemma 4 E2B via `llama.cpp`. It produces local rationales over deterministic decisions, persists receipts, and exposes summaries for Pollen.

Pollen has an Android demo flavor and a device path using LiteRT-LM with Gemma 4 E4B and audio input. It compiles voice into `MissionPatch`, validates the result, and returns refusal states for unsafe or incoherent instructions.

Meristem runs locally with deterministic evaluation and Gemma 4 E4B tool-calling support. It ingests visit bundles and produces policy windows.

The ESP32 firmware runs on real hardware and exposes the safety path. It supports supervised pump pulses and soil moisture readings. The demo keeps autonomous water conservative and physical proof explicit.

Rhizome also includes `ShadowSkeptic`, a second local auditor. It disagrees safely, writes evidence, and keeps `affects_decision=false`.

## Why the pattern scales

Sprout’s unit of value is a decision with bounded authority. That unit scales from two pots to multiple plots because the contracts stay small: `DecisionReceipt`, `MissionPatch`, `WeatherDigest`, `ValidationStamp`, `FieldVisit`, and `PolicyPacket`.

A cooperative can run Rhizomes in dispersed plots, carry Pollen on routine visits, and review policy at home. A community garden can preserve volunteer knowledge as expiring mission patches with clear scope and TTL.

## Future work

Next iterations extend the same authority model. A flow meter will close production semantics for autonomous `WATER`. A local weather station will enrich `WeatherDigest` objects. Camera input will add visible plant evidence while remaining non-authoritative. Pollen will support full-duplex field conversation. Meristem will add seasonal rules, multi-crop policy evaluation, and stronger tool-assisted review.

The dual-agent pattern will mature through measurement. `ShadowSkeptic` already records objections without actuation authority. Future runs will compare objections against later outcomes, measure false positives and false negatives, and promote proven recurring objections into deterministic gates.

Language is part of the roadmap. Sprout keeps internal contracts stable, while Pollen adapts the surface language at the edge. Future work includes fine-tuning Gemma 4 for local agricultural vocabulary and minority languages.

## Conclusion

Sprout preserves field criteria during absence. It turns visits into operational intelligence. It rejects expired instructions. It records what happened. It gives local AI a second skeptical voice before giving that voice any authority.

**Sprout is open, local AI for water decisions under absence: expiring authority, signed receipts, a second local voice that audits without authority, and a physical layer that can say no.**

---

**Repository:** https://github.com/zigiella/sprout · Apache 2.0
**Entry point for reviewers:** [`SUBMISSION.md`](../SUBMISSION.md)
**Spanish reference:** [`writeup/draft_es_long.md`](draft_es_long.md) — extended Spanish working draft kept for bilingual traceability.

*Built on Gemma 4 by Google. Gemma is a trademark of Google LLC. This project is not affiliated with or endorsed by Google.*
