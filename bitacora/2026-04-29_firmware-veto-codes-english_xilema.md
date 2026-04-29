# Firmware ESP32: códigos de veto en inglés

**De:** Xilema  
**Fecha:** 2026-04-29  
**Contexto:** día 14, cascada de códigos de veto tras review día 13

## Decisión aplicada

Se alinean las strings literales del firmware ESP32 y del host harness con los
códigos de veto en inglés ya adoptados en `docs/30_safety_rules.md`,
`docs/23_rhizome_prompt_mapping_v0.md` y writeup.

Cambios:

- `HEARTBEAT_PERDIDO` -> `JETSON_HEARTBEAT_LOST`
- `DEPOSITO_BAJO` -> `TANK_LOW`
- `FUERA_DE_RANGO` -> `EVENT_DURATION_OUT_OF_RANGE`
- `SIN_CAUDAL` -> `NO_FLOW_DETECTED`
- `ALERTA_LATCHED` -> `ALERT_LATCHED`

Nota: `NO_FLOW_DETECTED` queda como código de contrato, pero la detección real
de caudal todavía no está implementada en firmware porque no hay actuadores ni
caudalímetro integrados. No había string `SIN_CAUDAL` activa que reemplazar.

## Archivos tocados

- `hardware/firmware_esp32/main/app_main.c`
- `hardware/host_tools/scenarios/guardian_demo.json`
- `hardware/host_tools/tests/test_esp32_host_harness.py`
- `hardware/firmware_esp32/README.md`

## Verificación

- `python -m pytest hardware\host_tools\tests` -> 3 passed
- `idf.py build` con ESP-IDF v6.0 -> binario generado correctamente

El build emite una advertencia no bloqueante sobre `ESP_ROM_ELF_DIR` al generar
gdbinit, derivada del entorno local ESP-IDF, no del firmware. La imagen
`sprout_esp32.bin` se genera correctamente.

## Pendiente

Cuando la placa esté conectada, flashear esta versión y correr `guardian_demo`
para guardar transcript físico con los códigos nuevos.

