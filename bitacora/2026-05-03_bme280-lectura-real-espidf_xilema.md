# BME280 con lectura real en ESP-IDF

## Estado

Bea verifico con un sketch Arduino que el `BME280` respondia en `0x76` usando:

- `SDA = GPIO8`
- `SCL = GPIO9`
- `SDO = GND`

Eso descarto cableado, modulo y pines como causa principal. El fallo estaba en
la integracion ESP-IDF.

## Hallazgos

- `I2C_SCAN_ALL` diagnostico encontraba `0x76`.
- Lectura cruda de `chip_id` devolvia `0x60`, correcto para `BME280`.
- La ruta inicial basada en `bme280_init()` / `bme280_set_sensor_settings()`
  activaba caminos internos de la SensorAPI Bosch que podian hacer `soft_reset`
  al reconfigurar el sensor.
- En nuestra placa/modulo, esa ruta dejaba lecturas no validas o fallos
  `ESP_ERR_INVALID_RESPONSE` al pasar a medicion.
- Un disparo crudo de medicion forzada (`CTRL_HUM=0x01`, `CTRL_MEAS=0x25`)
  demostro que el sensor si producia datos reales.

## Decision tecnica

La ruta estable queda asi:

- cargar calibracion Bosch sin `soft_reset`
- esperar a que `STATUS.im_update` este limpio
- configurar oversampling en modo sleep:
  - `CTRL_HUM`
  - `CTRL_MEAS`
  - `CONFIG`
- en cada `BME280_READ`, lanzar una medicion `FORCED`
- esperar el tiempo calculado por `bme280_cal_meas_delay`
- usar la SensorAPI Bosch solo para parseo/compensacion de datos

`I2C_SCAN` queda como probe simple de presencia en direcciones candidatas
`0x76/0x77`. `BME280_PROBE` es quien valida `chip_id=0x60`.

## Verificacion

Flasheo limpio en placa real:

```powershell
idf.py -p COM5 flash
```

Smoke test conectado:

```powershell
python hardware/host_tools/esp32_host_harness.py --port COM5 --scenario bme280_connected_smoke --label day18_bme280_connected_clean_final
```

Resultado:

- `scenario=bme280_connected_smoke success=True`
- `I2C_SCAN count=1 addrs=0x76`
- `BME280_PROBE status=CONNECTED address=0x76 chip_id=0x60`
- `BME280_REPORT status=CONNECTED ... error=ESP_OK sensor_rslt=0`
- `TELEMETRY_REPORT ... bme280=CONNECTED bme280_valid=true`

Artefactos:

- `hardware/host_tools/reports/20260503_171302_bme280_connected_smoke_day18_bme280_connected_clean_final.log`
- `hardware/host_tools/reports/20260503_171302_bme280_connected_smoke_day18_bme280_connected_clean_final.json`

Tests host-side:

```powershell
python -m pytest hardware/host_tools/tests -q
```

Resultado:

- `3 passed`

## Nota

Los comandos de diagnostico crudo usados durante el aislamiento
(`BME280_FORCE_RAW`, dumps de registros, scan total del bus) no se dejan en el
firmware final de este cambio. Sirvieron para acotar, pero el contrato publico
queda en `I2C_SCAN`, `BME280_PROBE`, `BME280_READ` y `TELEMETRY`.
