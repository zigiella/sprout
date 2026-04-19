# tests/firmware/

Simulador y tests de safety para el firmware ESP32 mientras no tenemos el bench fisico montado.

## Que hay aqui

- `mock_esp32.py` — simulador de protocolo UART, maquina de estados y hard limits de `docs/30_safety_rules.md`.
- `test_safety_mock_esp32.py` — traduccion directa de los 15 casos obligatorios de `§8.2`, mas un test de `DecisionReceipt` bloqueado para demo.

## Como correrlo

```bash
cd code/rhizome
python -m pytest tests/firmware
python -m tests.firmware.mock_esp32 --scenario low_tank_block
```

La demo imprime:
- el `CMD` enviado desde Rhizome
- el `ACK REJECTED ...` del mock ESP32
- un `DecisionReceipt` bloqueado listo para screenshot, video o writeup

## Limites de este simulador

- No sustituye al bench fisico de `§8.1`.
- No emula GPIO, brownout ni watchdog a nivel hardware.
- No valida latencias reales de UART/ISR.

Su trabajo es fijar el contrato y evitar drift antes de conectar bomba, valvulas y sensores reales.
