# Handoff minimo Rhizome -> Meristem

**De:** Xilema
**Fecha:** 2026-04-30
**Contexto:** dia 15, posible entrada de Meristem-nodo al MVP

## Decision

Preparo un paquete minimo para que Meristem pueda ejercitar su camino MVP sin
esperar a que Rhizome exponga todos los endpoints reales.

El codigo actual de Meristem consume evidencias como envelopes individuales
`/ingest` y valida `PolicyDelta` en `/deltas/propose`. Por eso el paquete no
implementa todavia `FieldVisit`/`SyncBundle` v2: esos contratos estan en docs,
pero no existen aun como Pydantic compartido.

## Entrega

Carpeta:

- `code/meristem/examples/rhizome_minimal_handoff/`

Incluye:

- `active_policy_seed.json`: `PolicyPacket` seguro para `rhizome_01`.
- `ingest_rhizome_snapshot_tank_low.json`: snapshot con deposito al 18%.
- `ingest_decision_receipt_tank_low.json`: receipt de bloqueo `TANK_LOW`.
- `ra04_safety_downgrade_delta.json`: delta que intenta bajar
  `rules.tank_minimum_pct` a 15%.

## Criterio de seguridad

RA04 debe rechazarse:

- HTTP esperado: `422`
- reason: `violates_safety_rule`
- violation: `rules.tank_minimum_pct`
- proposed_value: `15.0`
- firmware_limit: `20.0`

Esto materializa la barandilla del review dia 13:

`lo fisico manda, Rhizome arbitra, Pollen media, Meristem afina`.

## Verificacion

Añado test ejecutable:

- `code/meristem/tests/test_rhizome_minimal_handoff_examples.py`

Comprueba:

- fixtures parsean con schemas actuales,
- RA04 falla contra `safety_rules`,
- flujo HTTP Meristem acepta las evidencias y rechaza el delta peligroso.

## Nota BME280

El BME280 de banco queda bloqueado por hardware fisico: el modulo llego a
encender LED verde, pero nunca respondio por I2C (`I2C_SCAN count=0`) y tras
reintentos de soldadura dejo de encender. Firmware ESP32, bus I2C y harness se
mantienen listos para repetir con modulo presoldado.
