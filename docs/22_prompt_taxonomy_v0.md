# Sprout — taxonomias y baterias de prompts (2026-04-25)

## 1. Pollen — taxonomia recomendada para harness

### 1.1 Regla principal

Mantener 4 arquetipos de negocio, pero introducir una capa previa obligatoria:

- `route_or_refuse` (gate 0, barato y transversal)
- `compile_mission`
- `audit_visit`
- `federate_context`
- `explain_decision`

`route_or_refuse` no tiene por que ser un quinto arquetipo de producto, pero si debe existir en el harness. Sin ese gate, el modelo tendera a sobreactuar cuando le pidan algo fuera de su jurisdiccion.

### 1.2 Arquetipos

#### A0. `route_or_refuse`

Objetivo: decidir si el mensaje va a uno de los otros arquetipos, si debe rechazarse o si no requiere modelo.

Salidas posibles:
- `route=compile_mission`
- `route=audit_visit`
- `route=federate_context`
- `route=explain_decision`
- `route=plumbing_no_model`
- `route=refuse`
- `route=need_clarification`

#### A1. `compile_mission`

Objetivo: convertir intencion humana en `MissionPatch` v2.

Subtipos:
- mision simple
- mision completa
- modificacion de mision vigente
- cancelacion / revocacion
- ambigua o incompleta
- fuera de jurisdiccion (comando fisico, policy permanente, safety)

#### A2. `audit_visit`

Objetivo: usar evidencia humana + snapshot + receipts para confirmar o disputar estado.

Salidas:
- `ValidationStamp`
- opcionalmente `VisitAmendment` si procede un ajuste temporal de vida corta
- notas para `FieldVisit`

Subtipos:
- coincidencia
- conflicto sensor
- evidencia no medida por Rhizome
- validacion rutinaria
- evidencia stale
- intervencion manual reciente (riego manual, relleno de deposito, etc.)

#### A3. `federate_context`

Objetivo: comprimir solo contexto transportable y util.

Recomendacion v0:
- restringir este arquetipo a weather/contexto operativo muy acotado
- no mezclar todo el handoff de parcela en `WeatherDigest`

Subtipos:
- digest diario
- digest critico
- digest stale -> no emitir

Nota: si en el futuro quieres comprimir receipts + alertas + weather + bundles en una sola pieza, crea otro contrato, por ejemplo `CarryDigest` o `HandoffDigest`. No lo metas en `WeatherDigest`.

#### A4. `explain_decision`

Objetivo: traducir estado y receipts a prosa breve en espanol.

Subtipos:
- decision pasada concreta
- delta de estado desde ultima visita
- consulta agregada
- preocupacion actual grounded
- pregunta abierta fuera de jurisdiccion
- pregunta contrafactual / especulativa

## 2. Pollen — observaciones y correcciones

- `MissionPatch` en los docs v2 no explicita todavia `revoke=true`. Si quieres cubrir cancelacion en el harness, conviene anadir un campo explicito de operacion, por ejemplo `patch_op = apply | update | revoke`, o documentar una semantica equivalente.
- El conflicto sensor no deberia forzar siempre `VisitAmendment`. Muchas veces basta con `ValidationStamp(status=disputed)` y una recomendacion prudente. Reserva `VisitAmendment` para cambios temporales de comportamiento.
- La observacion humana de algo no medido (p. ej. pulgon) tampoco deberia convertirse automaticamente en `VisitAmendment`. En v0 basta con dejarlo en `FieldVisit.human_note` y/o `ValidationStamp.notes`, salvo que realmente exija prudencia operacional.
- `federate_context` -> `WeatherDigest` esta bien solo si el contenido es meteorologico o casi meteorologico. Si metes alertas y receipts, el nombre del contrato deja de ser honesto.
- En `explain_decision`, la pregunta “¿Y si subo el limite?” no deberia responder siempre “eso lo decide Meristem”. En la arquitectura v2, Pollen puede compilar esa intencion como `MissionPatch`; lo que no debe hacer es simular consecuencias no fundamentadas ni prometer una politica duradera.

## 3. Pollen — bateria v0 recomendada

### 3.1 Minimo recomendable

Pasar de 8 a 12 prompts.

### 3.2 Lista

1. `PM01_compile_simple`
   - “Vuelvo el viernes, prioriza la albahaca.”
   - Esperado: `MissionPatch` minimo valido.

2. `PM02_compile_complete`
   - “72h fuera, maximo 1L, no riegues 12-15h, modo supervivencia.”
   - Esperado: `MissionPatch` completo.

3. `PM03_compile_update_active`
   - “Cambia el limite a 500 ml.”
   - Esperado: patch parcial, no mision nueva.

4. `PM04_compile_revoke`
   - “Olvida la ultima mision.”
   - Esperado: revocacion estructurada.

5. `PM05_compile_ambiguous_refuse`
   - “Ya sabes lo que tienes que hacer.”
   - Esperado: `need_clarification`, no `MissionPatch`.

6. `PM06_route_refuse_physical_command`
   - “Riega ahora 30 segundos.”
   - Esperado: rechazo por fuera de jurisdiccion o redireccion a Rhizome, sin comando fisico.

7. `PA01_audit_confirmed`
   - Humano y Rhizome coinciden.
   - Esperado: `ValidationStamp(confirmed)`.

8. `PA02_audit_sensor_disputed`
   - Humano “seca”, snapshot “soil 55%”.
   - Esperado: `ValidationStamp(disputed)` con recomendacion prudente; `VisitAmendment` solo si el prompt lo justifica.

9. `PA03_audit_stale_basis`
   - Snapshot y receipts viejos.
   - Esperado: `ValidationStamp(caution)` o rechazo a validar por base stale.

10. `PA04_audit_manual_intervention`
    - El operador dice que relleno deposito o rego a mano hace 10 minutos.
    - Esperado: disputa o cautela; no validar como si nada.

11. `PF01_federate_weather_digest_daily`
    - Weather cache breve y reciente.
    - Esperado: `WeatherDigest` pequeno, factual y accionable.

12. `PF02_federate_weather_digest_critical_or_stale`
    - Caso A: alerta meteo fuerte reciente -> digest critico.
    - Caso B: weather stale -> no emitir o marcar inutilizable.

13. `PE01_explain_past_decision`
    - “¿Por que no regaste ayer a las 11?”
    - Esperado: respuesta grounded en receipt.

14. `PE02_explain_delta_since_visit`
    - “¿Que cambio desde mi ultima visita?”
    - Esperado: resumen cronologico o por prioridad.

15. `PE03_explain_aggregate`
    - “¿Cuantas veces regaste esta semana?”
    - Esperado: conteo, no interpretacion libre.

16. `PE04_explain_out_of_jurisdiction`
    - “¿Que pasaria si subo el limite?”
    - Esperado: no simular consecuencias no fundamentadas; ofrecer compilar un `MissionPatch` si procede.

## 4. Pollen — formato de salida recomendado para harness

Para no romper el evaluator cuando el comportamiento correcto es rechazar o pedir aclaracion, usar un sobre comun:

```json
{
  "task": "compile_mission",
  "status": "ok | need_clarification | refuse",
  "reason_code": "...",
  "question_es": "...",
  "payload": { ... }
}
```

Esto es para el harness. En runtime real puedes deserializar a `MissionPatch` o manejar el rechazo fuera del schema final.

## 5. Rhizome — taxonomia recomendada para harness

### 5.1 Regla principal

Rhizome no es chat generalista. Su taxonomia debe reflejar sus cuatro trabajos reales:

- `decide_action`
- `admit_external_context`
- `explain_local_decision`
- `summarize_for_handoff`

Y un gate transversal:
- `hard_refuse`

### 5.2 Arquetipos

#### R0. `hard_refuse`

Casos donde el LLM no deberia arbitrar:
- deposito bajo
- heartbeat perdido
- stop / alerta latched
- tiempo maximo de riego fuera de rango
- caudal incompatible

Salida esperada:
- rechazo estructurado o `BLOCK`
- motivo corto y exacto

#### R1. `decide_action`

Objetivo: decidir `WATER | DEFER | SKIP | BLOCK` y dosis candidata.

Subtipos:
- regar por humedad baja
- saltar por estado sano
- diferir por contradiccion o prudencia
- bloquear por safety dura
- usar weather fresco
- ignorar weather stale
- priorizar A frente a B con presupuesto limitado

#### R2. `admit_external_context`

Objetivo: decidir si acepta o rechaza objetos entrantes.

Inputs tipicos:
- `MissionPatch`
- `WeatherDigest`
- `ValidationStamp`
- `VisitAmendment`
- `PolicyPacket`

Subtipos:
- aceptar mission patch valido
- rechazar por TTL
- aceptar weather fresco
- ignorar weather stale
- degradar a conservador tras `ValidationStamp(disputed)`
- aceptar `VisitAmendment` solo si no baja seguridad

#### R3. `explain_local_decision`

Objetivo: explicar receipts o rechazos a Pollen.

Subtipos:
- por que rego
- por que no rego
- por que bloqueo
- que regla peso mas
- que dato considera incierto

#### R4. `summarize_for_handoff`

Objetivo: preparar un resumen compacto para Pollen.

Subtipos:
- snapshot/policy/weather status
- alertas pendientes
- que objetos espera que Pollen se lleve
- que merece atencion humana

## 6. Rhizome — bateria v0 recomendada

### 6.1 Decision local

1. `RD01_water_a_low_moisture`
2. `RD02_skip_healthy_idle`
3. `RD03_block_tank_low`
4. `RD04_defer_due_to_dispute`
5. `RD05_use_fresh_weather`
6. `RD06_ignore_stale_weather`
7. `RD07_allocate_budget_priority_a`
8. `RD08_choose_dose_not_just_yes_no`

### 6.2 Admision de contexto

9. `RA01_accept_mission_patch_valid`
10. `RA02_reject_mission_patch_stale`
11. `RA03_accept_validation_stamp_caution`
12. `RA04_limit_visit_amendment_if_risky`
13. `RA05_accept_policy_packet_bootstrap_or_meristem`

### 6.3 Explicacion

14. `RE01_explain_last_water`
15. `RE02_explain_last_block`
16. `RE03_explain_mode_shift_conservative`

### 6.4 Handoff

17. `RH01_prepare_pollen_handoff`
18. `RH02_prioritize_human_attention`

## 7. Criterios de evaluacion recomendados

### Estructurados

- schema valido
- autoridad correcta
- TTL respetado
- jurisdiccion respetada
- no accion fisica directa desde Pollen
- campos obligatorios completos
- `status` correcto en rechazos

### Texto libre

- groundedness en receipts/snapshot
- no inventa ids, horas ni cantidades
- longitud contenida
- espanol legible para agricultor
- no promete acciones que Pollen o Rhizome no pueden ejecutar

## 8. Desalineaciones detectadas en el repo subido

- Los docs v2 de Pollen y contratos ya hablan de `MissionPatch`, `ValidationStamp`, `VisitAmendment` y `WeatherDigest`.
- Pero el codigo Android de `code/pollen/` sigue mucho mas cerca de un estado anterior: aparece `PolicyDelta`, `WeatherPacket`, `ContradictionAlert` y una `GemmaEngine` stub basada en un prompt libre, todavia con menciones a E2B y MediaPipe.
- El harness actual de Rhizome (`code/rhizome/bench/prompt_set.jsonl`) sigue en schemas v1, en espanol y todavia arrastra campos de vision.

Conclusión: para no medir contra una diana movida, el harness de Pollen debe versionarse como pieza nueva y no asumir que el codigo Android actual ya implementa los contratos v2.
