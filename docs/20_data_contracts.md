# Contratos de datos — v2

## 1. Principios

- todo viaja en JSON legible,
- cada objeto lleva `created_at`, `origin_node_id`, `ttl_s` o `valid_until` cuando proceda,
- toda acción relevante deja rastro,
- Pollen no transporta datos “sin sentido”; transporta contexto útil.

## 2. Campos base

Comunes a todos los contratos:

- `schema_version`
- `id`
- `created_at`
- `origin_node_id`
- `target_node_id` cuando aplique
- `ttl_s` o `valid_until` cuando aplique
- `trace_id` opcional
- `confidence` opcional

## 3. Contratos mínimos

## 3.1 RhizomeSnapshot
Foto lógica del estado local.

Campos clave:
- `plot_states`
- `active_policy_id`
- `mode`
- `sensor_state`
- `device_health`
- `pending_alerts`

## 3.2 DecisionReceipt
Recibo de una decisión local.

Campos clave:
- `decision_type`
- `subject_plot`
- `evidence`
- `policy_id`
- `candidate_action`
- `esp32_outcome`
- `final_action`
- `why_short`

## 3.3 AlertEvent
Evento de alerta emitido por Rhizome o ESP32.

Campos clave:
- `severity`
- `code`
- `subject`
- `details`
- `recommended_mode`

## 3.4 PolicyPacket
Política duradera para Rhizome.

Campos clave:
- `horizon_h`
- `watering_windows`
- `soil_thresholds`
- `max_seconds_per_event`
- `daily_budget_ml`
- `priority_order`
- `failsafe_defaults`

### Barandilla sobre hard limits físicos

**Ningún campo de un `PolicyPacket` emitido por Meristem puede reducir hard limits del firmware ESP32.** Específicamente:

- `soil_thresholds.tank_minimum_pct` no puede caer por debajo del umbral del firmware.
- `max_seconds_per_event` no puede exceder el tiempo máximo del firmware.
- Cualquier campo que rebase un hard limit es **rechazado por Rhizome al validar el paquete** (regla de aceptación §5).

Meristem puede recomendar **más conservador** (umbrales más altos, ventanas más cortas, presupuestos más bajos). No puede relajar safety. Esta cláusula es invariante del MVP, registrada en el review meeting del día 13 (`bitacora/2026-04-28_review-meeting-tuning_cambium.md`) tras propuesta de Xilema desde el frente firmware.

Patrón general: *lo físico manda, Rhizome arbitra, Pollen media, Meristem afina.* La autoridad fluye de arriba a abajo cuando se trata de afinar criterio; se invierte cuando se trata de seguridad física.

#### Nomenclatura: `HARD_LIMIT_DOMAIN` ≡ `SAFETY_DOWNGRADE` (equivalentes jurisdiccionales)

Acordado entre Meristem y Xilema día 26. `HARD_LIMIT_DOMAIN` (cómo Meristem nombra el rechazo cuando un bundle intenta relajar un hard limit del firmware, perspectiva del emisor) y `SAFETY_DOWNGRADE` (cómo Rhizome/Pollen nombran el intento de bajar safety al validar, perspectiva del validador) son **la misma realidad vista desde dos lados**: no son códigos duplicados que haya que fusionar, son **equivalentes jurisdiccionales**.

Implicaciones operativas:

- Si un `ValidationStamp` de Rhizome trae `reason: "SAFETY_DOWNGRADE"`, Meristem lo interpreta como sinónimo de su propio `HARD_LIMIT_DOMAIN` al consolidar evidencia y al redactar rationale al operador.
- Para el writeup/demo, citar cualquiera de los dos términos es válido; ambos apuntan al mismo invariante: lo físico manda.
- Esta equivalencia no requiere rename en código — coexisten como sinónimos.

## 3.5 MissionPatch
Intención humana compilada por Pollen.

Campos clave:
- `horizon_h`
- `priority_plot`
- `budget_cap_ml`
- `avoid_hours`
- `goal_mode`
- `operator_note`

## 3.6 WeatherDigest
Contexto meteorológico resumido y transportable.

Campos clave:
- `source_type`
- `observed_at`
- `window_h`
- `summary`
- `signals`
- `recommended_effect`

## 3.7 ValidationStamp
Resultado de una visita.

Campos clave:
- `status`: `confirmed | disputed | caution`
- `subject`
- `basis`
- `notes`
- `recommended_action`

## 3.8 VisitAmendment
Ajuste temporal emitido por Pollen con vida corta.

Campos clave:
- `expires_at`
- `scope`
- `changes`
- `safety_expectation`
- `needs_meristem_review`

## 3.9 FieldVisit
Acta compacta de una visita.

Campos clave:
- `visited_node_id`
- `started_at`
- `ended_at`
- `received_objects`
- `created_objects`
- `delivered_objects`
- `human_note`

## 3.10 SyncBundle
Contenedor de transporte.

Campos clave:
- `from_node`
- `to_node`
- `objects`
- `acked_ids`
- `bundle_kind`: `visit | return | meristem_sync`

## 3.11 DecisionExplanationResponse
Respuesta de la API local de Rhizome para `GET /explain/decision/{id}`.

Campos clave:
- `explanation`: texto breve y legible para Pollen / operador

Regla de interoperabilidad:
- la respuesta debe ser JSON object
- no se acepta texto plano crudo
- forma exacta mínima:

```json
{
  "explanation": "El modelo decidió regar A porque el suelo estaba bajo el umbral y el depósito era suficiente."
}
```

## 4. Autoridad por contrato

- `RhizomeSnapshot`: Rhizome
- `DecisionReceipt`: Rhizome
- `AlertEvent`: Rhizome o ESP32 vía Rhizome
- `PolicyPacket`: Meristem o bootstrap local
- `MissionPatch`: Pollen
- `WeatherDigest`: Pollen o Rhizome con estación
- `ValidationStamp`: Pollen
- `VisitAmendment`: Pollen
- `FieldVisit`: Pollen
- `SyncBundle`: cualquier nodo transportador, normalmente Pollen

## 5. Regla de aceptación en Rhizome

Rhizome acepta un objeto solo si:

1. valida schema,
2. no está caducado,
3. su autoridad es correcta,
4. no contradice una regla dura del ESP32,
5. no rebaja seguridad por debajo del mínimo permitido.

## 6. Regla de rechazo visible

Todo rechazo importante debe poder verse y explicarse.
Eso significa que un objeto rechazado no se “pierde”; genera evento y texto corto.

## 7. Ejemplo mínimo — MissionPatch

```json
{
  "schema_version": "2.0",
  "id": "mission_patch_001",
  "created_at": "2026-04-22T10:00:00Z",
  "origin_node_id": "pollen_01",
  "target_node_id": "rhizome_01",
  "ttl_s": 21600,
  "horizon_h": 72,
  "priority_plot": "A",
  "budget_cap_ml": 900,
  "avoid_hours": [12, 13, 14, 15],
  "goal_mode": "survival",
  "operator_note": "Vuelvo el viernes. Prioriza la albahaca."
}
```

## 8. Ejemplo mínimo — DecisionReceipt

```json
{
  "schema_version": "2.0",
  "id": "decision_receipt_001",
  "created_at": "2026-04-22T10:05:00Z",
  "origin_node_id": "rhizome_01",
  "subject_plot": "A",
  "decision_type": "WATER",
  "policy_id": "policy_009",
  "candidate_action": {"seconds": 18},
  "esp32_outcome": "ACK",
  "final_action": {"seconds": 18},
  "why_short": "Suelo por debajo del mínimo y presupuesto disponible."
}
```
