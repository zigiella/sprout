# docs/

Architecture, specifications, contracts and operational guides for Sprout.

The project values its development trail. Some documents here are **canonical references** for the current v1.0 state; others are **historical evidence of process** preserved intentionally — early specs, working drafts and operational briefs from the 30-day build. Each entry below states its status. Where a historical document carries fact-level drift from v1.0, it also carries a status header inside the file.

## Canonical (current v1.0 reference)

| # | Document | Topic |
|---|---|---|
| 01 | [`01_architecture.en.md`](01_architecture.en.md) | System architecture — three jurisdictions, ten contracts, authority model |
| 13 | [`13_esp32_spec.md`](13_esp32_spec.md) | ESP32 safety coprocessor specification |
| 20 | [`20_data_contracts.md`](20_data_contracts.md) | JSON schemas for the ten MVP contracts |
| 30 | [`30_safety_rules.en.md`](30_safety_rules.en.md) | ESP32 hard safety rules and priority order |

## Working references and operational notes

| # | Document | Topic |
|---|---|---|
| 02 | [`02_bom.md`](02_bom.md) | Bill of materials (hardware) |
| 10 | [`10_rhizome_spec.md`](10_rhizome_spec.md) | Rhizome node specification (Jetson) |
| 40 | [`40_meristem_quickstart_usuario_domestico.md`](40_meristem_quickstart_usuario_domestico.md) | Meristem quickstart for the home user |
| 40 | [`40_pitch_video.md`](40_pitch_video.md) | Video production notes |
| — | [`external/`](external/) | External references and compliance audits |
| — | [`figures/`](figures/) | Diagrams and figures used by other docs |

## Historical evidence of process (preserved intentionally)

These documents reflect the project at earlier moments. They are kept as *rastro de proceso* — to show how the system evolved, not as canonical reference. Where they carry fact-level drift, the file itself opens with a status header pointing to the canonical source.

| # | Document | Era | Note |
|---|---|---|---|
| 00 | [`00_brief.md`](00_brief.md) | day 1 | Initial project brief |
| 00 | [`00_positioning.md`](00_positioning.md) | day 7 | First positioning note, superseded by [`../writeup/draft.md`](../writeup/draft.md) |
| 00 | [`00_estado_vivo.md`](00_estado_vivo.md) | day 28 | Internal living state journal (Spanish) |
| 01 | [`01_architecture.md`](01_architecture.md) | day 15 | Original Spanish working draft; canonical English is `01_architecture.en.md` |
| 11 | [`11_pollen_spec.md`](11_pollen_spec.md) | day 7 | Original Pollen spec; current reality in `01_architecture.en.md` §3.2 + [`../code/pollen/README.md`](../code/pollen/README.md) |
| 12 | [`12_meristem_spec.md`](12_meristem_spec.md) | day 7 | Original Meristem spec; carries fact-level drift (target model, runtime). See status header inside the file. Current reality in `01_architecture.en.md` §3.3 + [`../code/meristem_node/README.md`](../code/meristem_node/README.md) |
| 22 | [`22_prompt_taxonomy_v0.md`](22_prompt_taxonomy_v0.md) | day 15 | v0 prompt taxonomy, working document |
| 23 | [`23_rhizome_prompt_mapping_v0.md`](23_rhizome_prompt_mapping_v0.md) | day 15 | v0 Rhizome prompt mapping vs §6 of doc 22 |
| 30 | [`30_safety_rules.md`](30_safety_rules.md) | day 15 | Original Spanish; canonical English is `30_safety_rules.en.md` |
| 50 | [`50_pollen_gemma4_e4b_guide.md`](50_pollen_gemma4_e4b_guide.md) | day 7 | Pre-implementation guide for Gemma 4 E4B + LiteRT-LM on Pixel 10 Pro |
| 51 | [`51_rhizome_gemma4_e2b_jetson_guide.md`](51_rhizome_gemma4_e2b_jetson_guide.md) | day 7 | Pre-implementation guide for Gemma 4 E2B + llama.cpp on Jetson |
| 52 | [`52_endodermis_jetson_bringup_brief.md`](52_endodermis_jetson_bringup_brief.md) | day 17 | Operational briefing handed off to Endodermis agent |

## Numbering convention

- `00-09` foundational / brief / positioning / state journal
- `10-19` node specifications
- `20-29` data contracts
- `30-39` safety rules
- `40-49` operational notes (production, quickstarts)
- `50-59` technical guides (model + hardware bring-up)

## On language

Canonical documents are English-first. Original Spanish drafts are preserved alongside as evidence of process. See the [Language note in the root README](../README.md#language-note) for the project-wide policy.
