# Handoff Endodermis -> Floema — POST /policy Rhizome

**Fecha:** 2026-05-06 (dia 21)  
**Endpoint principal:** `POST http://192.168.1.60:13010/policy`  
**Demo rhizome_02:** `POST http://192.168.1.60:13020/policy`

---

## Contrato operativo

Pollen envia un `PolicyPacket` JSON transitorio generado durante visita.

Campos que la fachada Rhizome exige de forma especifica:

- `schema_version="1.0"`
- `policy_origin="pollen-visit"`
- `policy_scope="transient"` u omitido
- `target_node_id` igual al Rhizome de destino (`rhizome_01` o `rhizome_02`)
- `valid_until` con TTL maximo 12h desde `created_at`
- `rules.soil_moisture_thresholds` puede contener una sola sonda en MVP

Respuesta OK:

```json
{
  "status": "accepted",
  "policy_id": "pkt_example",
  "policy_origin": "pollen-visit",
  "policy_scope": "transient",
  "active_for_next_decision": true,
  "hard_limits_checked_by_facade": false
}
```

Respuesta de rechazo:

```json
{
  "error": "policy_rejected",
  "reason_code": "policy_origin_invalid",
  "detail": "POST /policy acepta solo policy_origin='pollen-visit'",
  "node_id": "rhizome_01"
}
```

## Endpoint de lectura

```text
GET /policy/active
```

Devuelve la politica activa y metadatos de aceptacion. Si no hay politica:
404 `policy_not_found`.

## Limite importante

La fachada no valida hard limits fisicos. Ese campo queda explicitamente en
`false` para evitar confusion:

```json
"hard_limits_checked_by_facade": false
```

Hard limits siguen en Mini-Evaluator antes del envio y en ESP32 al ejecutar.

## Smoke local Jetson

```bash
cd ~/sprout/code/rhizome/jetson
./smoke_policy.sh
FACADE_URL=http://127.0.0.1:13020 TARGET_NODE_ID=rhizome_02 ./smoke_policy.sh
```

## Nota para UI/demo

`rhizome_02` es simulacion host-side para demostrar interoperabilidad
multi-Rhizome desde una sola Jetson. No representa un segundo ESP32 ni un
segundo actuador fisico.
