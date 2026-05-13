# Sprout — local criteria for water when nobody is there

**Subtitle:** A Gemma 4 decision network for irrigation under absence: the plot decides in minutes, the human visit changes criteria, and the home laptop refines policy when the day is calm again.

Imagine this pot is a whole plot.

Sprout’s demo happens on a terrace, with living pots, a small pump and a soil sensor. But the situation it represents is much larger: rural plots, community gardens, small farms and peripheral land where the farmer cannot be present every day and the network cannot always be trusted. In those places, the problem is not only water scarcity. It is the latency between what happens in the plot and the decision that should correct it.

Sprout starts from a simple thesis: when the field, the human and the network do not coincide in time, intelligence must be distributed. It is not enough to send data to a cloud that may not be reachable. The immediate decision has to live near the water. Human intent has to enter when a person visits. Longer-term policy should be composed later, calmly, at home.

That is why Sprout is organized as three Gemma 4 nodes and one physical veto layer.

**Rhizome** lives in the plot. It runs Gemma 4 E2B on a Jetson Orin Nano Super through `llama.cpp`. It reads local state, soil moisture, tank level, telemetry and the active policy. Its question is short and urgent: should I irrigate now, defer, skip, or block? Rhizome never moves water directly. It proposes a decision and writes a rationale, but physical authority belongs to an ESP32 safety coprocessor.

**The ESP32** runs custom firmware and owns the physical layer. It is the piece that can say no. If the Jetson heartbeat is lost, if the tank is below minimum, if the event duration is out of range, if flow is missing, or if an alert is latched, the command does not pass. The LLM can propose. The firmware disposes. This separation is the safety constitution of the system.

**Pollen** lives on the farmer’s Android phone. It runs Gemma 4 E4B through LiteRT-LM and turns every human visit into something more valuable than a sync. The farmer can speak naturally: “I’ll be back Friday. This plant can stay drier than you think; water it a bit less.” Pollen takes local audio, compiles it into an expiring structured `MissionPatch`, validates the proposed change with a deterministic mini-evaluator, and refuses incoherent instructions. Refusal is not a product failure; it is a safety feature.

Pollen also lets isolated plots learn from each other without requiring direct network connectivity. It carries context, `WeatherDigest` objects, visit reports, receipts and validations. The phone often arrives before good connectivity does. Sprout turns that fact into architecture: the human visit is not an interruption; it is an input channel for local intelligence.

**Meristem** lives on the farmer’s home laptop. It runs Gemma 4 E4B through `llama.cpp`. It is the slow brain: it receives bundles, evaluates them with deterministic logic and tool calling, and emits durable policy for the next window. Meristem does not decide immediate irrigation. It refines criteria after the pressure of minutes is gone.

The authority rule is intentionally strict: the physical layer prevails, Rhizome arbitrates, Pollen mediates, Meristem refines. The farther a node is from the water, the less physical authority it has. Every intelligence has jurisdiction. And expiry.

Expiry is central. A `MissionPatch` from Pollen carries a short TTL because it represents a specific visit. A `PolicyPacket` from Meristem carries a validity window because the world changes. A `WeatherDigest` expires before it becomes meteorological superstition. If an object arrives late, Sprout does not apply it silently: it rejects it and records a legible reason in the `DecisionReceipt`.

The demo shows a minimum but real version of this pattern. Rhizome runs on edge hardware. Pollen has an Android demo flavor and a device flavor with LiteRT-LM. Meristem has an evaluator and tool-calling path. The ESP32 firmware has been tested on real hardware, and the physical bench path includes a 12V pump, relay, soil moisture reading and supervised pulses. The autonomous `WATER` command remains conservative in `DRY_RUN`; real physical pulses run as supervised `TEST_ONLY` until the production semantics are closed. That honesty matters: Sprout does not pretend full autonomy while it is still validating safety.

Gemma 4 is used concretely, not decoratively. In Rhizome, E2B helps explain local decisions that are already bounded by deterministic rules. In Pollen, E4B brings local multimodal audio and compiles human intent into JSON contracts. In Meristem, E4B supports tool calling and policy rationales. Three models, three jurisdictions, no mandatory cloud roundtrip.

Sprout also contains an idea we call a local dual-agent pattern. In Rhizome, next to the operational agent, a secondary auditor named `ShadowSkeptic` observes decisions, writes objections and logs disagreements without changing the action. Its `affects_decision=false` field is intentional. Before giving authority to a second voice, Sprout measures whether that voice actually improves safety. It is a cautious path toward local agents that audit each other without bypassing the physical layer.

The result is not an AI irrigation timer. It is a decision network with physical limits, human language and traceability. A pot in the demo represents a larger pattern: small farms, dispersed plots, communities with intermittent connectivity and limited water.

Sprout does not replace the farmer. It preserves the farmer’s criteria when they are away, makes each visit count more, and prevents old instructions or unsafe inferences from silently governing water.


Another piece makes Sprout publishable as an open project: contracts matter more than UI. The browser demo does not pretend to run Gemma 4; it uses deterministic mocks so any judge can inspect object shapes and refusal paths instantly. The repository, meanwhile, documents the real execution paths: `llama.cpp` in Rhizome and Meristem, LiteRT-LM in Pollen, ESP-IDF firmware for the ESP32, and tests that verify guardrails. This separation between explanatory demo and technical proof reduces the risk of hackathon theater.

We also learned something practical: the system must value “no” as much as “yes”. When Pollen does not understand a voice instruction, it asks for rephrasing. When Rhizome sees an expired policy, it rejects it. When the ESP32 detects an unsafe condition, it blocks. In isolated agriculture, a legible refusal can be more valuable than confident automation. That is why logs, receipts and reason codes are not decoration; they are the trust interface of the system.

The architecture is ready to grow without changing philosophy. A local weather station can replace or enrich the `WeatherDigest`. A camera can add visual evidence without becoming absolute authority. A flow meter can close the production semantics of autonomous `WATER`. Meristem can add more rules or model auditors. Pollen can be tuned for local agricultural languages. In every case, the same rule remains: intelligence helps formulate criteria, but physical safety keeps the final word.

What we want to show the judges is not that a pot needs Gemma 4. We want to show that a pot can stand in for a plot forgotten by the network, and that the full pattern — local edge, roaming mobile node, slow home brain, expiring contracts and physical veto — is a replicable way to bring open AI to places where the cloud is not enough.

**Sprout is a safety-bounded decision network for water under absence.**

---

**Repository:** https://github.com/zigiella/sprout · Apache 2.0
**Entry point for judges:** [`SUBMISSION.md`](../SUBMISSION.md)
**Spanish version:** [`writeup/draft_es_long.md`](draft_es_long.md) — extended Spanish working draft kept as bilingual reference.

*Built on Gemma 4 by Google. Gemma is a trademark of Google LLC. This project is not affiliated with or endorsed by Google.*

