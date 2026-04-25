# firmware_esp32

Bootstrap del firmware real de la capa dura de seguridad para `Sprout`.

## Objetivo del milestone actual

Este proyecto no intenta cerrar todo el firmware de una vez.

El primer hito es:

- arrancar siempre en `SAFE_IDLE`
- exponer consola serie por **USB Serial/JTAG / CDC-ACM**
- emitir `HELLO` al arrancar
- responder `STATUS`
- emitir `HEARTBEAT` periódico
- reportar `flash_bytes` y `psram_bytes`

Todavía **no** controla bomba, válvulas ni sensores.

## Stack

- target: `ESP32-S3`
- framework: **ESP-IDF**
- board profile inicial: `n16r8_usb_otg`
- board profile futuro previsto: `devkitc_n8r8`

## Estructura

- `main/app_main.c` — estado `SAFE_IDLE`, loop de protocolo y heartbeat
- `main/board_profile.[ch]` — separación entre lógica del firmware y perfil de placa
- `main/Kconfig.projbuild` — opciones de board profile y timing del milestone
- `sdkconfig.defaults` — baseline de consola USB y PSRAM

## Protocolo del hito 0

Entrada por línea ASCII terminada en `\n`:

- `HELLO`
- `STATUS`

Salida:

- `HELLO fw=... state=SAFE_IDLE board=... uptime_ms=...`
- `STATUS_REPORT state=SAFE_IDLE fw=... board=... uptime_ms=... flash_bytes=... psram_bytes=...`
- `HEARTBEAT state=SAFE_IDLE board=... uptime_ms=...`
- `REJECT reason=UNKNOWN_COMMAND cmd=...`

## Build y flash

### Windows host

```powershell
idf.py set-target esp32s3
idf.py build
idf.py -p COM7 flash monitor
```

### Linux host / Jetson más adelante

```bash
idf.py set-target esp32s3
idf.py build
idf.py -p /dev/ttyACM0 flash monitor
```

## Notas de hardware

- `GPIO19 / GPIO20` reservados para USB nativo
- `GPIO35 / GPIO36 / GPIO37` no se usan por PSRAM Octal
- `GPIO45 / GPIO46` se evitan en el primer arranque
- no conectar actuadores en este hito

## Validación esperada

Al arrancar en la `ESP32-S3 N16R8 USB OTG` deberíamos ver:

```text
HELLO fw=0.1.0 state=SAFE_IDLE board=n16r8_usb_otg uptime_ms=...
HEARTBEAT state=SAFE_IDLE board=n16r8_usb_otg uptime_ms=...
```

Y ante `STATUS`:

```text
STATUS_REPORT state=SAFE_IDLE fw=0.1.0 board=n16r8_usb_otg uptime_ms=... flash_bytes=16777216 psram_bytes=8388608
```

## Fuentes operativas validadas

- Jetson AI Lab, `Gemma 4 on Jetson`, leída el `2026-04-25`: https://www.jetson-ai-lab.com/tutorials/gemma4-on-jetson/
- Espressif, `ESP-IDF Get Started for ESP32-S3 (stable v6.0)`, leída el `2026-04-25`: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/get-started/index.html
- Espressif, `USB Serial/JTAG Controller Console`, leída el `2026-04-25`: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/usb-serial-jtag-console.html
- Espressif, `SPI Flash and External SPI RAM Configuration`, leída el `2026-04-25`: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/flash_psram_config.html
