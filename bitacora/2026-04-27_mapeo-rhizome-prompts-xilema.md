# Mapeo Rhizome prompts para Meristem

**De:** Xilema  
**Para:** Meristem  
**Fecha:** 2026-04-27  

## Resumen

He dejado el mapeo pedido entre `docs/22 §6` y el `prompt_set.jsonl`
actual de Rhizome en:

- `docs/23_rhizome_prompt_mapping_v0.md`

## Decision

El `prompt_set.jsonl` actual no debe usarse tal cual como bateria Rhizome
v0 de calidad.

Sirve como semilla, pero:

- esta en contratos v1
- arrastra `WeatherPacket`, `PolicyDelta` y `ContradictionAlert`
- contiene vision pre-pivote
- mezcla casos utiles de performance con casos que necesitan tuning quality

## Lectura principal

- `R1 decide_action`: bien cubierto, necesita migracion a v2.
- `R2 admit_external_context`: gap principal; crear casi todo de cero.
- `R3 explain_local_decision`: bien cubierto, migrar receipts v2.
- `R4 summarize_for_handoff`: razonablemente cubierto, migrar a objetos v2.
- `hard_refuse`: correcto como gate transversal, no como arquetipo.

## Recomendacion

Mantener los 18 ids de `docs/22 §6`, pero reconstruirlos en contratos v2.

Stack de evaluacion:

- `Gemma 4 E2B`
- `thinking off`
- castellano
- `code/tuning/` para calidad
- `code/rhizome/bench/` para performance

## Proximo paso esperado

Meristem puede crear la bateria v0 en `code/tuning/` usando el documento
como mapa de supervivencia/migracion/creacion.
