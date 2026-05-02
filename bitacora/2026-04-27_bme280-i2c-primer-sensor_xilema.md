# BME280 por I2C — primer sensor real del firmware ESP32

## Qué se ha hecho

- abierta la issue `#56` para integrar `BME280` por `I2C`
- nueva rama: `feat/esp32-bme280-i2c`
- vendorizada la `SensorAPI` oficial de Bosch en:
  - `hardware/firmware_esp32/main/third_party/bme280/`
- wrapper local añadido en:
  - `hardware/firmware_esp32/main/bme280_sensor.[ch]`
- firmware ampliado con:
  - `I2C_SCAN`
  - `BME280_PROBE`
  - `BME280_READ`
- `STATUS_REPORT` ampliado con:
  - `telemetry_mode=HYBRID`
  - `i2c_bus`
  - `i2c_sda`
  - `i2c_scl`
  - `bme280_addr`
- `TELEMETRY_REPORT` ampliado con:
  - `bme280_valid`
  - `bme280_temp_c_x100`
  - `bme280_humidity_pct_x100`
  - `bme280_pressure_pa`

## Decisiones

- primer sensor real: `BME280`
- baseline de pines:
  - `SDA = GPIO8`
  - `SCL = GPIO9`
  - `I2C port = 0`
  - `100 kHz`
- milestone de trabajo:
  - primero `scan / probe / read`
  - luego, si compensa, integración más profunda en telemetría continua

## Fuentes

- Espressif `I2C Master Driver`, leído el `2026-04-27`
  - https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/i2c.html
- Bosch Sensortec `BME280_SensorAPI`, commit `c90d419492e26dd95586598a794e65eb2760753a`, leído el `2026-04-27`
  - https://github.com/boschsensortec/BME280_SensorAPI

## Verificación

Build local pasado en entorno `ESP-IDF v6.0` sobre Windows host:

```powershell
. C:\Espressif\tools\Microsoft.v6.0.PowerShell_profile.ps1
cd C:\DATA\PETS\TEST\T6A1-JETSON\sprout\hardware\firmware_esp32
idf.py build
```

Resultado:

- `Project build complete`

## Nota abierta

La salida final de `idf.py build` sigue proponiendo una línea de `esptool`
con `--flash-size 2MB` pese a que la placa real ya reporta correctamente
`flash_bytes=16777216` y `psram_bytes=8388608`.

No bloquea este milestone, pero conviene revisarlo más adelante para no dejar
desalineado el metadata de flashing con el hardware real.

## Ajuste por disponibilidad de cableado

Bea confirma que no tendremos protoboard ni Dupont hasta el dia 15. Decidimos
no forzar el BME280 fisico sin cableado limpio.

Trabajo adelantado sin sensor conectado:

- escenario host `bme280_disconnected_baseline`
- escenario host futuro `bme280_connected_smoke`
- `I2C_SCAN` limitado de momento a candidatos `BME280` (`0x76`, `0x77`) para
  no generar ruido masivo de probe en bus sin cableado
- contrato explicito de BME280 ausente:
  - `I2C_SCAN count=0 addrs=NONE`
  - `BME280_PROBE status=NOT_FOUND`
  - `BME280_READ status=NOT_FOUND`
  - `TELEMETRY_REPORT bme280=DISCONNECTED bme280_valid=false`
- documentacion del baseline desconectado en `hardware/firmware_esp32/README.md`

Esto nos deja listo el primer paso del dia 15: conectar `VCC/GND/SDA/SCL`,
repetir el harness y verificar que el mismo contrato pasa de `NOT_FOUND` a
`CONNECTED` sin cambiar la state machine.

## Hallazgo de host USB

Intento de prueba fisica sin cableado:

- `idf.py build`: OK
- `idf.py -p COM3 flash`: no pudo abrir `COM3`
- `idf.py -p COM4 flash`: no pudo abrir `COM4`
- harness en `COM5`: no pudo abrir `COM5`

Windows listaba los tres puertos, pero todos fallaban con `FileNotFoundError`.
Se documenta como caso de puerto fantasma / dispositivo no accesible y se mejora
el harness para responder con error limpio en vez de traceback.

No se escribio nada en la placa en este intento.

## Evidencia en placa real tras reconectar

Bea reconecta la placa. Repetimos:

- `idf.py -p COM3 flash`: OK
- harness por `COM5`, escenario `bme280_disconnected_baseline`: OK

Artefactos generados:

- `hardware/host_tools/reports/20260427_154345_bme280_disconnected_baseline_pre_cableado_day12.log`
- `hardware/host_tools/reports/20260427_154345_bme280_disconnected_baseline_pre_cableado_day12.json`

Resultado funcional:

- `STATUS_REPORT ... telemetry_mode=HYBRID i2c_bus=READY i2c_sda=8 i2c_scl=9 bme280_addr=NONE`
- `I2C_SCAN count=0 addrs=NONE`
- `BME280_PROBE status=NOT_FOUND address=NONE chip_id=NONE i2c_bus=READY`
- `BME280_REPORT status=NOT_FOUND ... temp_c_x100=-1 humidity_pct_x100=-1 pressure_pa=-1`
- `TELEMETRY_REPORT ... bme280=DISCONNECTED bme280_valid=false`

Hallazgo: con el scan general inicial, ESP-IDF emitia mucho log de timeout al
probar todo el bus sin pull-ups externos. El contrato era correcto, pero el
transcript quedaba ruidoso. Se recorta `I2C_SCAN` a direcciones candidatas BME280
hasta que tengamos cableado real y/o mas sensores I2C.

Tambien se silencia el tag interno `i2c.master`: el firmware ya expone el estado
del probe en lineas de protocolo (`I2C_SCAN`, `BME280_PROBE`, `BME280_REPORT`), y
para rehearsal nos interesa que el transcript contenga contrato Sprout, no logs
internos del driver.

Evidencia final limpia tras el ajuste:

- `idf.py build`: OK
- `idf.py -p COM3 flash`: OK
- harness por `COM5`, escenario `bme280_disconnected_baseline`: OK
- transcript:
  - `hardware/host_tools/reports/20260427_154701_bme280_disconnected_baseline_pre_cableado_day12_quiet.log`
  - `hardware/host_tools/reports/20260427_154701_bme280_disconnected_baseline_pre_cableado_day12_quiet.json`

Lineas clave del transcript:

- `STATUS_REPORT ... telemetry_mode=HYBRID i2c_bus=READY i2c_sda=8 i2c_scl=9 bme280_addr=NONE`
- `I2C_SCAN count=0 addrs=NONE`
- `BME280_PROBE status=NOT_FOUND address=NONE chip_id=NONE i2c_bus=READY error=ESP_ERR_NOT_FOUND`
- `BME280_REPORT status=NOT_FOUND ... temp_c_x100=-1 humidity_pct_x100=-1 pressure_pa=-1`
- `TELEMETRY_REPORT ... bme280=DISCONNECTED bme280_valid=false`
