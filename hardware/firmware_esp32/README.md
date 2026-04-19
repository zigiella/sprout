# firmware_esp32/

Carril del firmware real del ESP32-S3 para la capa dura de Sprout.

## Estado actual

Mientras no tenemos el bench fisico de `docs/30_safety_rules.md §8.1`, la fuente de verdad ejecutable es:

- `code/rhizome/tests/firmware/mock_esp32.py`

Ese simulador ya refleja:
- maquina de estados `BOOT / SAFE / ACTIVE / ALERT / DEGRADED`
- protocolo UART a `115200 8N1`
- CRC-8/DVB-S2
- replay protection de `seq`
- hard limits v1.0
- transcript de demo con `ACK REJECTED` + `DecisionReceipt` bloqueado

## Siguiente paso cuando llegue hardware

1. Elegir framework embebido (`Arduino` o `ESP-IDF`).
2. Portar constantes y state machine del mock al firmware real.
3. Montar bench con:
   - ESP32 + 3 LEDs
   - potenciometro para deposito
   - generador manual de pulsos para caudal
4. Repetir los 15 tests de `§8.2` sobre serial loopback real.

## Notas de implementacion

- `FIRMWARE_VERSION` objetivo: `1.0`
- umbral duro de deposito: `20%`
- no se habilita OTA en v1.0
- el mock es un contrato de comportamiento, no una decision definitiva de framework
