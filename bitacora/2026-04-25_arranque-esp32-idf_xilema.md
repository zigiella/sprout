# Arranque ESP32-S3 en ESP-IDF

**Fecha:** 2026-04-25
**Autor:** Xilema
**Area:** Hardware / Rhizome
**Tipo:** Decision / Avance

## Contexto
Tras el pivote v2, el ESP32 sube a coprocesador de seguridad y pasa a ser bloqueante para la demo. El hito del dia 10 ya no es "todo el firmware", sino `SAFE_IDLE + HELLO + STATUS + HEARTBEAT` sobre la `ESP32-S3 N16R8 USB OTG`, manteniendo abierta la puerta a una `DevKitC-1 N8R8` como placa de banco.

## Que hicimos / decidimos
- baseline del repo fijado en **ESP-IDF**, no Arduino
- perfil inicial de placa fijado en `n16r8_usb_otg`
- scaffold creado en `hardware/firmware_esp32/`
- estado de arranque fijado en `SAFE_IDLE`
- protocolo hito 0 fijado en ASCII por linea:
  - `HELLO`
  - `STATUS`
  - `STATUS_REPORT`
  - `HEARTBEAT`
  - `REJECT`
- docs alineadas:
  - `docs/13_esp32_spec.md`
  - `hardware/README.md`

## Por que
El firmware ya no es un sketch de relays. Necesita:

- consola USB estable
- estado observable
- NVS
- timers / tareas
- separacion limpia entre perfil de placa y logica de estados

ESP-IDF encaja mejor con ese camino que Arduino. La `N16R8` se toma como placa de arranque porque ya esta en mesa, pero sin acoplar la logica del firmware a una sola board.

## Que queda pendiente
- [ ] instalar toolchain ESP-IDF en el host de firmware
- [ ] `idf.py set-target esp32s3 && idf.py build`
- [ ] flash real y verificacion por puerto serie (`HELLO`, `STATUS_REPORT`, `HEARTBEAT`)
- [ ] anadir telemetria de sensores criticos
- [ ] anadir reglas duras de `docs/30_safety_rules.md`
- [ ] preparar el path `Jetson /dev/ttyACM* -> ESP32`

## Enlaces
- [spec ESP32](../docs/13_esp32_spec.md)
- [spec Rhizome](../docs/10_rhizome_spec.md)
- [reglas de seguridad](../docs/30_safety_rules.md)
- [guia Jetson Gemma 4 E2B](../docs/51_rhizome_gemma4_e2b_jetson_guide.md)
- Jetson AI Lab, `Gemma 4 on Jetson` (leido 2026-04-25): https://www.jetson-ai-lab.com/tutorials/gemma4-on-jetson/
- Espressif, `ESP-IDF Get Started for ESP32-S3` stable v6.0 (leido 2026-04-25): https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/get-started/index.html
- Espressif, `USB Serial/JTAG Controller Console` (leido 2026-04-25): https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/usb-serial-jtag-console.html
- Espressif, `SPI Flash and External SPI RAM Configuration` (leido 2026-04-25): https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/flash_psram_config.html
