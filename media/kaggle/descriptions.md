# Sprout · image descriptions (EN)

English alt text + caption for every image in this delivery.
Use **alt** for `alt=""` attributes, og:image:alt, and screen-readers.
Use **caption** for figure captions, deck slide notes, social posts.

The "kind" column matches the naming convention (`sprout-{kind}-{slug}-NN`).

---

## photo · hero / cover (16:9 · 1920×1080)

### sprout-photo-plot-hero-02.png  ★ main hero
**alt:** Stone-walled terrace garden with a green raised planter labeled PLOT_01, a white outdoor enclosure labeled RHIZOME_01 mounted on the wall, and Pyrenean rooftops in the background.
**caption:** The hero shot of Sprout. PLOT_01 is the physical garden bed; RHIZOME_01 is the field node that runs the model and owns the valve. Everything decision-making happens behind that white box, on this terrace — no cloud, no datacenter.

### sprout-photo-plot-hero-01.png
**alt:** Composite render of the Sprout terrace setup with overlaid PLOT_01 label and a Rhizome field box on a stone wall.
**caption:** Stylized version of the hero with overlaid type. Useful as an alternate when the photo's chrome clashes with surrounding layout — or as the "drawing" half of a draw-vs-photo pair.

### sprout-photo-terrace-wide-01.png
**alt:** Wide view of the terrace garden, with a green raised planter and Pyrenean mountain village rooftops behind a stone wall.
**caption:** Context shot. Establishes where Sprout lives: a real garden, in a real village, where uplinks die for days. The "plots the network forgets."

---

## photo · rhizome hardware (16:9 · 1920×1080)

### sprout-photo-rhizome-open-01.png
**alt:** White outdoor electrical enclosure mounted on a stone wall, hinged door open, revealing two compartments — a Jetson single-board computer with cooling fan on cardboard above, and an ESP32 dev board with tangled wiring below.
**caption:** RHIZOME_01 with the door open. Two compartments, two responsibilities: the Jetson runs the slow AI loop, the ESP32 owns the physical safety floor. Everything in the paper is inside this box.

### sprout-photo-rhizome-internal-01.png
**alt:** Close-up of a Jetson Orin Nano single-board computer inside a white plastic enclosure, with a black cooling fan on top, USB and Ethernet cables connected.
**caption:** Inside detail of the upper Rhizome compartment. The Jetson Orin Nano hosting Gemma sits on cardboard, fan on top, gigabit Ethernet hanging out the front. Pragmatic — but it works.

---

## photo · editorial (3:2 · 1500×1000)

### sprout-photo-workshop-wide-01.png
**alt:** Workshop desk with three monitors showing code and dashboards, a laptop in front, and an ESP32 development board on a white block.
**caption:** Where Sprout was built. Three screens for code, agent output and dashboards; ESP32 on the workbench. Useful for the "how it was made" beat in a deck.

### sprout-photo-rhizome-macro-01.png
**alt:** Macro photograph of an ESP32 microcontroller on a breadboard with a tangle of jumper wires in red, yellow, blue and black.
**caption:** ESP32 macro. The "safety coprocessor" up close — and the cables that prove this thing is real, not a render.

### sprout-photo-meristem-macro-01.png
**alt:** Macro photograph of a Jetson Orin Nano single-board computer with heatsink, M.2 slot and pin headers visible.
**caption:** Meristem hardware reference. The home-node Jetson that consolidates Pollen visits into the slow weekly bundle.

### sprout-photo-meristem-boot-01.png
**alt:** Computer monitor on a desk displaying a green NVIDIA boot splash screen.
**caption:** Bring-up moment. The first time Meristem powered on cleanly. Good for the bring-up / engineering-process page.

---

## photo · feed vertical (4:5 · 1080×1350)

### sprout-photo-bom-overview-01.png
**alt:** Top-down view on a wooden table of the Sprout bill of materials: a power relay, a small water pump, a flow sensor, fuses, terminal blocks and a CPC-branded retail package.
**caption:** The full BOM in one frame. Answers "what's actually inside" before anyone asks.

### sprout-photo-rhizome-desk-01.png
**alt:** Workspace with an ESP32 board on a white plinth in front of two monitors showing code and a chat-style agent interface.
**caption:** Work-in-progress shot during a Rhizome bring-up session.

### sprout-photo-planter-detail-01.png
**alt:** Top-down view of a green raised planter bed with strawberry, pepper, tomato and basil plants in three fabric grow-bags.
**caption:** The biological subject, top-down. The plants Sprout is actually irrigating. Strong on feed because the texture earns the scroll-stop.

### sprout-photo-terrace-empty-01.png
**alt:** Stone-walled terrace with two empty green raised planters, before planting, with mountain rooftops behind.
**caption:** Terrace before the plants went in. Useful as the "before" half of a before-after pair with the hero shot.

---

## photo · mobile / stories (9:16 · 1080×1920)

### sprout-photo-rhizome-bench-01.png
**alt:** Test-bench setup with cardboard, relays, a multimeter and exposed wiring on a wooden desk.
**caption:** Raw bench shot — useful for storytelling, not for the cover. The kind of frame that says "we actually built it."

### sprout-photo-terrace-vertical-01.png
**alt:** Vertical view of the terrace garden with the green raised planter, white Rhizome enclosure on the stone wall, and a mountain village skyline behind.
**caption:** Best mobile cover from this batch. Replaces the horizontal hero on phone-first surfaces.

### sprout-photo-planter-setup-01.png
**alt:** Two green raised planters on a terrace — one with plants, one empty in the foreground — with rooftops of a Pyrenean village in the background.
**caption:** Mid-setup moment. Reads as "how it was assembled" in vertical format.

---

## ui · meristem dashboard (16:9 · 1920×1080)

### sprout-ui-meristem-01.png
**alt:** Top section of the Meristem web dashboard showing the "Your plot today" panel, a "Sync with Pollen" action and a "Recent operations" log.
**caption:** Meristem dashboard, upper view. The home node's morning glance: plot health, sync status, what happened overnight.

### sprout-ui-meristem-02.png
**alt:** Lower section of the Meristem web dashboard showing "Visits received" and "Policies issued" lists, with the footer label "Meristem mer_01 v0.1 · domestic slow brain".
**caption:** Meristem dashboard, lower view. The audit half: who visited, what policy changes were issued in response.

---

## ui · pollen mobile (1080w native · ~9:19.5)

### sprout-ui-pollen-home-01.png
**alt:** Android phone screen for the Pollen App showing the heading "Pollen App (Sprout system)", a green pill labeled "Federated AI carried by Pollen app", a list of two associated Rhizomes (RHIZOME_01 North Plot, RHIZOME_02 South Plot), and a "Home Node (Meristem) · Slow brain · weekly handoff" card.
**caption:** Pollen home. The phone that ferries decisions between field nodes and the home node. Two rhizomes, one Meristem, federated by walking.

### sprout-ui-pollen-decision-01.png
**alt:** Android phone screen showing a Rhizome_01 plot view with a BLOCK decision card timestamped 2026-04-13, rationale text "Nivel de depósito insuficiente (8%) para ciclo de riego", and buttons for Explain Decision (LLM), Audit History, Voice Command (beta), View generated policy (JSON) and Chat with Rhizome.
**caption:** The decision detail screen — the most important page in Pollen. The model proposed an action; the deterministic gate blocked it; the user can read why, audit it, or override it by voice. This is the jury's screen.

### sprout-ui-pollen-voice-01.png
**alt:** Android phone screen with a Google voice input overlay in Spanish, microphone icon, the partially-transcribed phrase "vuelvo el viernes esta planta", and a red "Stop Recording" button at the bottom.
**caption:** Voice command in action, Spanish (España). Demonstrates the human-in-the-loop: spoken intent goes in, a candidate policy comes out, and the deterministic gate still has the final word.

### sprout-ui-pollen-telemetry-01.png
**alt:** Android phone screen showing current telemetry for Rhizome_01 — water 72%, soil moisture 38% — a green CTA "What happened since my absence?", and a Last Decision log including a WATER_A event and a SKIP event with timestamps.
**caption:** Telemetry + recent decisions. The "what did the plot do while I was away" view. Designed so a non-technical owner can scan it in under five seconds.

### sprout-ui-pollen-visit-01.png
**alt:** Android phone screen with a "visit checklist" for Rhizome_01 showing three checked steps: Connect to rhizome (BLE / WiFi · 0.4s), Pull snapshot (6.2 KB), Sync receipts (24h Window).
**caption:** The Pollen visit. Three steps, four KB, half a second of radio. This is what a "data uplink" looks like on Sprout — done by a person, on a phone, while walking past.

---

## ui · receipt log (16:9 · 1920×1080)

### sprout-ui-receipt-terminal-01.png
**alt:** Terminal window on a black background showing a Sprout DecisionReceipt replay log — color-coded lines for INFO, CMD, RX, GATE, ACK and REC events tracing a WATER_A decision through ESP32 acknowledgment.
**caption:** A full DecisionReceipt, replayed. AI proposes (GATE → candidate), deterministic gate validates, ESP32 acknowledges, the valve only opens after ACK. The receipt is the auditable proof.

---

## diagram (PNG · 2× from 1180w SVG source)

### sprout-diagram-architecture-overview.png  (2360×1040)
**alt:** System architecture diagram on a warm-grey background showing three jurisdictions — Field (ESP32 + Rhizome), Mobile (Pollen) and Home (Meristem) — connected by labeled flows for MissionPatch, DecisionReceipt, Bundle and PolicyDiff.
**caption:** Three jurisdictions, one water decision. Field is deterministic-first, Mobile is the ferry, Home is the slow consolidator. The valve never opens without ESP32 ACK.

### sprout-diagram-authority-stack.png  (2360×720)
**alt:** Horizontal flow diagram on a warm-grey background reading "Gemma · Rhizome → candidate → ESP32 → final → valve", with sample JSON payloads under each stage and a DecisionReceipt seal on the right.
**caption:** The authority stack. The model proposes; Rhizome shapes; ESP32 validates; only then does the valve move. The model never touches the valve — this is the invariant.

### sprout-diagram-double-agent.png  (2360×960)
**alt:** Dual-agent diagram on a warm-grey background: a State bundle (telemetry, policy, TTL, cooldown, safety state) is ingested in parallel by an Operational Steward and a ShadowSkeptic. The Steward emits a DecisionReceipt (action + rationale) on a solid authoritative arrow; ShadowSkeptic emits a Disagreement log (affects_decision=false) on a dashed observational arrow.
**caption:** A second voice without authority. Disagreement becomes data, not action. Proven recurring objections can later be promoted into deterministic gates — even skepticism has jurisdiction.

---

## suggested usage by surface

| surface           | first picks                                                                |
|-------------------|-----------------------------------------------------------------------------|
| Kaggle cover      | plot-hero-02 (or local-first-ai cover already on file)                      |
| Landing hero      | plot-hero-02 horizontal, terrace-vertical-01 for ≤768px                     |
| "What it is"      | plot-hero-02 + planter-detail-01                                            |
| "Where it lives"  | terrace-wide-01, terrace-empty-01, terrace-vertical-01                      |
| "What's inside"   | rhizome-open-01, rhizome-internal-01, bom-overview-01                       |
| "How it decides"  | diagram-authority-stack, receipt-terminal, pollen-decision                  |
| "How it federates"| diagram-architecture-overview, pollen-home, pollen-visit                    |
| "Engineering"     | workshop-wide-01, rhizome-desk-01, rhizome-bench-01, meristem-boot-01       |
| Pollen sequence   | pollen-home → pollen-decision → pollen-voice → pollen-telemetry → pollen-visit |
| Social (feed)     | planter-detail-01, bom-overview-01, rhizome-desk-01, terrace-empty-01       |
| Social (stories)  | terrace-vertical-01, planter-setup-01, rhizome-bench-01                     |
