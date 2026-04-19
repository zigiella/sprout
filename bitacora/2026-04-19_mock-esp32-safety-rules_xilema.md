# 2026-04-19 — mock ESP32 safety rules — Xilema

## Contexto

Arranco `#4` sin hardware fisico todavia, siguiendo la instruccion de Cambium: priorizar un mock fiel del firmware que sirva para demo, writeup y para desbloquear integracion con Rhizome.

## Decision

No he fijado aun `Arduino` vs `ESP-IDF` para el firmware real. En esta iteracion implemento primero el simulador previsto por `docs/30_safety_rules.md §10.8` en:

- `code/rhizome/tests/firmware/mock_esp32.py`

Asi dejamos estable el contrato antes de soldar nada.

## Alcance de esta iteracion

- protocolo UART con `CRC-8/DVB-S2`
- maquina de estados `BOOT / SAFE / ACTIVE / ALERT / DEGRADED`
- replay protection de `seq`
- hard limits clave de `v1.0`
- 15 tests espejo de `§8.2`
- demo `low_tank_block` que imprime:
  - `CMD`
  - `ACK REJECTED`
  - `DecisionReceipt` bloqueado

## Criterio deliberado

He usado el umbral duro de deposito en `20%` segun `docs/30_safety_rules.md`, sin depender del fixture viejo de `PolicyPacket` que aun arrastra `15%` en `main`.

## Siguiente paso

Cuando llegue el hardware:

1. elegir framework real
2. portar la state machine del mock
3. montar el bench de `§8.1`
4. repetir los 15 tests sobre serial loopback real
