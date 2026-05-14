# Media gallery

Stable assets for submission, README embedding and Kaggle media gallery.

## Diagrams (SVG)

| File | Use | Caption |
|------|-----|---------|
| `architecture_overview.svg` | First technical image in writeup / media gallery | Sprout distributes irrigation criteria across three Gemma 4 nodes with different jurisdictions and one physical veto layer. |
| `authority_stack.svg` | Safety & Trust proof image | The farther a node is from the water, the less physical authority it has. The ESP32 can always say no. *Every intelligence has jurisdiction. And expiry.* |
| `pollen_visit_cycle.svg` | Pollen mediator visualization | A human visit becomes an expiring MissionPatch on Android via LiteRT-LM. Visits move context between disconnected Rhizomes. |
| `data_contracts.svg` | Contracts inventory | Ten JSON contracts of the MVP with explicit authority and expiry. |
| `double_agent.svg` | Dual-agent pattern in Rhizome | ShadowSkeptic audits without authority. Even skepticism has jurisdiction. |

## Recommended Kaggle media gallery set (5 images max)

1. **Cover** — `sprout-cover-local-first-ai.png` (TBD: composed image with terrace/pot/hardware + architecture overlay, 16:9, 1920×1080). *Pending: Bea provides photo from Castellar.*
2. `architecture_overview.svg` → can be exported to PNG `sprout-architecture-overview.png` for Kaggle.
3. `authority_stack.svg` → `sprout-authority-stack.png`.
4. `sprout-physical-build.jpg` — TBD: real photo of Jetson / Rhizome box / ESP32 / pump / pot.
5. `sprout-pollen-missionpatch.png` — Pollen Android screenshot showing voice → MissionPatch → validation.

## Optional 6th image

`sprout-esp32-decisionreceipt.png` — terminal log showing one safety path (either `DRY_RUN logged` for the autonomous contract, or `PUMP_PULSE 3000ms` + `SOIL_READ raw=2278 → raw=1289` for the supervised hardware proof).

## Naming convention

```text
sprout-<topic>-<modifier>.png
```

Lowercase, kebab-case, descriptive. No timestamps in filename.
