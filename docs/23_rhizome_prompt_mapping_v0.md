# Rhizome prompt mapping v0 — docs/22 §6 vs prompt_set actual

**Autor:** Xilema  
**Fecha:** 2026-04-27  
**Contexto:** coordinacion con Meristem para tuning Rhizome  

## 1. Decision

La bateria actual de `code/rhizome/bench/prompt_set.jsonl` no debe usarse
tal cual como bateria Rhizome v0 de calidad.

Si sirve como base, pero hay que depurarla:

- conserva bien `decide_action`, explicacion, handoff y parte de safety
- arrastra contratos v1 (`PolicyDelta`, `WeatherPacket`, `ContradictionAlert`)
- incluye vision y multimodalidad pre-pivote, que quedan fuera de ruta critica
- mezcla performance y quality; desde ahora `bench/` mide performance y `tuning/` mide quality

La bateria Rhizome v0 para `code/tuning/` debe reescribirse en contratos v2
manteniendo la intencion de los mejores prompts existentes.

## 2. Marco cerrado

- `hard_refuse` es gate transversal, no arquetipo de negocio.
- Arquetipos validos:
  - `decide_action`
  - `admit_external_context`
  - `explain_local_decision`
  - `summarize_for_handoff`
- Stack target:
  - `Gemma 4 E2B`
  - `llama.cpp`
  - Jetson
  - `thinking off`
- Idioma:
  - castellano
- `code/rhizome/bench/`:
  - performance
- `code/tuning/`:
  - quality

## 3. Mapeo de docs/22 §6

| docs/22 id | Arquetipo | Prompt actual mas cercano | Accion | Nota |
|---|---|---|---|---|
| `RD01_water_a_low_moisture` | `decide_action` | `decision_water_a_from_snapshot` | `migrar_v2` | Buen caso base. Reescribir con `RhizomeSnapshot` v2 + `PolicyPacket` v2 y `tank_minimum_pct=20`. |
| `RD02_skip_healthy_idle` | `decide_action` | `decision_skip_if_healthy` | `migrar_v2` | Conserva la intencion. Quitar vision si no aporta al MVP. |
| `RD03_block_tank_low` | `hard_refuse` gate + `decide_action` | `decision_block_if_tank_low`, `tank_recovery_plan` | `partir` | La decision de bloqueo es determinista por gate. El LLM solo debe explicar o materializar receipt, no arbitrar. |
| `RD04_defer_due_to_dispute` | `decide_action` | `decision_defer_due_to_warning_contradiction`, `contradiction_triage_warning` | `migrar_v2` | Reemplazar `ContradictionAlert` v1 por `ValidationStamp(disputed/caution)` o `VisitAmendment` v2. |
| `RD05_use_fresh_weather` | `decide_action` / `admit_external_context` | `decision_use_fresh_ferried_weather` | `rehacer_v2` | Reemplazar `WeatherPacket` v1 por `WeatherDigest` v2. |
| `RD06_ignore_stale_weather` | `admit_external_context` | `decision_reject_stale_weather` | `rehacer_v2` | Debe evaluar TTL en `WeatherDigest` v2 y responder rechazo/ignore. |
| `RD07_allocate_budget_priority_a` | `decide_action` | `two_parcel_prioritization`, `decision_water_b_from_snapshot` | `crear_v2` | El prompt actual prioriza B. Crear variante A con presupuesto limitado. |
| `RD08_choose_dose_not_just_yes_no` | `decide_action` | `esp32_command_sanity`, `decision_water_a_from_snapshot` | `crear_v2` | Debe producir dosis candidata prudente, respetando max duration ESP32 y presupuesto. |
| `RA01_accept_mission_patch_valid` | `admit_external_context` | ninguno directo | `crear_v2` | Gap principal. Input: `MissionPatch` valido + snapshot/policy. |
| `RA02_reject_mission_patch_stale` | `admit_external_context` | ninguno directo | `crear_v2` | Debe rechazar por TTL o vigencia, sin reinterpretar intencion caducada. |
| `RA03_accept_validation_stamp_caution` | `admit_external_context` | `contradiction_triage_warning` parcial | `crear_v2` | Migrar la idea de contradiccion a `ValidationStamp(status=disputed/caution)`. |
| `RA04_limit_visit_amendment_if_risky` | `admit_external_context` | ninguno directo | `crear_v2` | Caso critico: aceptar solo si no baja seguridad ni pisa hard limits. |
| `RA05_accept_policy_packet_bootstrap_or_meristem` | `admit_external_context` | `policy_window_validation`, `no_pollen_48h_conservative_shift` parcial | `crear_v2` | Debe distinguir bootstrap valido, Meristem valido y policy stale/incoherente. |
| `RE01_explain_last_water` | `explain_local_decision` | `receipt_success_overlay` | `migrar_v2` | Buen prompt. Migrar `DecisionReceipt` v2 y hacerlo evaluable por groundedness. |
| `RE02_explain_last_block` | `explain_local_decision` | `receipt_blocked_overlay`, `tank_recovery_plan` | `migrar_v2` | Incluir causa fisica ESP32 (`DEPOSITO_BAJO`, `HEARTBEAT_PERDIDO`, etc.). |
| `RE03_explain_mode_shift_conservative` | `explain_local_decision` | `no_pollen_48h_conservative_shift`, `budget_guardrail_check` | `migrar_v2` | Debe explicar modo conservador sin inventar consecuencias futuras. |
| `RH01_prepare_pollen_handoff` | `summarize_for_handoff` | `sync_summary_for_pollen_handoff`, `short_state_summary_for_pollen` | `migrar_v2` | Reescribir con objetos v2 que Pollen realmente puede transportar. |
| `RH02_prioritize_human_attention` | `summarize_for_handoff` | `audit_snapshot_for_risks`, `receipt_postmortem` | `crear_v2` | Debe producir prioridades humanas: deposito, alertas, disputa, sensores dudosos. |

## 4. Prompt_set actual por destino

### 4.1 Conservar como semilla

Estos prompts tienen buena intencion y deben sobrevivir, pero migrados a v2:

- `decision_water_a_from_snapshot`
- `decision_skip_if_healthy`
- `decision_defer_due_to_warning_contradiction`
- `receipt_success_overlay`
- `receipt_blocked_overlay`
- `short_state_summary_for_pollen`
- `audit_snapshot_for_risks`
- `tank_recovery_plan`
- `no_pollen_48h_conservative_shift`
- `receipt_postmortem`
- `sync_summary_for_pollen_handoff`
- `esp32_command_sanity`

### 4.2 Rehacer por contratos v1

Estos no deben entrar tal cual:

- `decision_use_fresh_ferried_weather`
- `decision_reject_stale_weather`
- `weather_conflict_resolution`
- `local_vs_ferried_preference`
- `policy_delta_apply_budget_change`
- `policy_delta_audit_for_trigger_growth`
- `policy_window_validation`
- `budget_guardrail_check`
- `contradiction_triage_warning`
- `contradiction_triage_critical`

Motivo:

- `WeatherPacket` -> `WeatherDigest`
- `PolicyDelta` -> `MissionPatch` / `PolicyPacket` segun caso
- `ContradictionAlert` -> `ValidationStamp` / `VisitAmendment` segun caso

### 4.3 Retirar de bateria v0 quality

Estos pueden seguir en `bench/` si sirven a performance, pero no deben
ser parte de la primera bateria quality:

- prompts multimodales / vision pre-pivote
- casos dependientes de camara fija
- cualquier caso que mida reconocimiento visual antes de tener imagen real

## 5. Gaps que Meristem debe cubrir

Prioridad alta para crear desde cero:

- `RA01_accept_mission_patch_valid`
- `RA02_reject_mission_patch_stale`
- `RA03_accept_validation_stamp_caution`
- `RA04_limit_visit_amendment_if_risky`
- `RA05_accept_policy_packet_bootstrap_or_meristem`
- `RD08_choose_dose_not_just_yes_no`

Prioridad media:

- `RD07_allocate_budget_priority_a`
- `RH02_prioritize_human_attention`

## 6. Bateria Rhizome v0 propuesta

Mantener los 18 ids de `docs/22 §6`, pero con estas reglas:

1. `hard_refuse` se evalua antes de arquetipos.
2. Los casos `RD03` y safety dura deben tener dos salidas posibles:
   - gate determinista: `BLOCK` / rechazo estructurado
   - explicacion LLM: breve, grounded, sin reinterpretar el bloqueo
3. `admit_external_context` es el bloque mas importante a escribir de cero.
4. `WeatherDigest` sustituye completamente a `WeatherPacket`.
5. `MissionPatch` sustituye los casos de cambio temporal de intencion.
6. `PolicyPacket` queda para bootstrap o policy oficial, no para parches humanos.
7. `ValidationStamp` y `VisitAmendment` sustituyen la idea vieja de contradiccion.
8. La vision queda fuera de v0 quality.

## 7. Criterios de scoring por arquetipo

### `hard_refuse`

- motivo correcto
- no propone agua
- no suaviza hard limits
- no introduce alternativas peligrosas

### `decide_action`

- accion correcta
- dosis prudente si aplica
- respeta `tank_minimum_pct`, heartbeat y max duration
- JSON estable

### `admit_external_context`

- TTL respetado
- autoridad del objeto respetada
- no acepta patches que bajen seguridad
- distingue `MissionPatch`, `WeatherDigest`, `ValidationStamp`, `VisitAmendment` y `PolicyPacket`

### `explain_local_decision`

- grounded en receipt/snapshot
- breve
- no inventa ids, horas, litros ni causas
- legible para operador

### `summarize_for_handoff`

- compacto
- transportable por Pollen
- prioriza alertas y atencion humana
- no mete estrategia global de Meristem

## 8. Entrega para Meristem

Meristem puede empezar por crear la bateria v0 en `code/tuning/` con estos
18 ids y envelope comun. Mi recomendacion es no importar literalmente el
texto actual de `prompt_set.jsonl`, sino usarlo como semilla de casos.

Orden recomendado:

1. Crear los 18 casos con contratos v2.
2. Mantener castellano y `thinking off`.
3. Ejecutar primero con proxy local `Gemma 4 E2B`.
4. Marcar resultados como `HIGH/MEDIUM/LOW` segun transferibilidad a Jetson.
5. Repetir en Jetson + `llama.cpp` cuando Rhizome target este disponible.
