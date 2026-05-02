# docs/

Documentacion del producto y la arquitectura. Orden de lectura sugerido por numeracion.

## Indice

| # | Documento | Tema |
|---|-----------|------|
| 00 | [00_brief.md](00_brief.md) | Brief inicial del proyecto |
| 01 | [01_architecture.md](01_architecture.md) | Arquitectura del sistema y alcance del MVP |
| 02 | [02_bom.md](02_bom.md) | Bill of materials (hardware) |
| 10 | [10_rhizome_spec.md](10_rhizome_spec.md) | Spec del nodo Rhizome (Jetson) |
| 11 | [11_pollen_spec.md](11_pollen_spec.md) | Spec del nodo Pollen (Pixel 10 Pro) |
| 12 | [12_meristem_spec.md](12_meristem_spec.md) | Spec del nodo Meristem (local + shadow) |
| 13 | [13_esp32_spec.md](13_esp32_spec.md) | Spec del coprocesador ESP32 |
| 20 | 20_data_contracts.md | Schemas JSON: weather_packet, policy_delta, contradiction_alert (pendiente) |
| 23 | [23_rhizome_prompt_mapping_v0.md](23_rhizome_prompt_mapping_v0.md) | Mapeo de prompts Rhizome v0/v0.5 |
| 30 | 30_safety_rules.md | Reglas fisicas duras del ESP32 (pendiente) |
| 40 | 40_naming_guidelines.md | Cumplimiento naming Gemma (pendiente) |
| 51 | [51_rhizome_gemma4_e2b_jetson_guide.md](51_rhizome_gemma4_e2b_jetson_guide.md) | Guia Gemma 4 E2B + llama.cpp en Jetson |
| 52 | [52_endodermis_jetson_bringup_brief.md](52_endodermis_jetson_bringup_brief.md) | Briefing operativo para Endodermis |

## Convenciones

- Numeracion: `00-09` foundational, `10-19` especificaciones de nodos, `20-29` contratos, `30-39` seguridad, `40-49` compliance, `50-59` guias operativas
- Cuando un doc supera 5-6 paginas, dividir en subdocs numerados dentro de una carpeta
- Cambios en arquitectura → entrada en `../bitacora/` explicando el porque
