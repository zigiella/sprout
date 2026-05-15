# firmware_esp32

**Abstract.** This firmware is Sprout's physical safety coprocessor, written in C with ESP-IDF for ESP32-S3. It owns the relay, the pump, the soil moisture reading on `GPIO4` and the relay control on `GPIO16`. It validates every irrigation command against five hard rules (`JETSON_HEARTBEAT_LOST`, `TANK_LOW`, `EVENT_DURATION_OUT_OF_RANGE`, `NO_FLOW_DETECTED`, `ALERT_LATCHED`) and rejects with a legible reason if any fails. The state machine is `SAFE_IDLE → READY → EXECUTING → DEGRADED → ALERT_LATCHED`. The LLM proposes; this firmware disposes.

> **Submission status:** `WATER` remains the conservative contract path and returns `DRY_RUN`; supervised physical actuation is demonstrated through `PUMP_PULSE <ms>` as `TEST_ONLY`. This distinction is intentional: it keeps the autonomous control path conservative while proving the physical pump/soil loop on real hardware. Day 27 validated 12 supervised pulses with measurable soil moisture drop (raw 2278 → 1289 after pulse).

---

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

`WATER` todavia no activa actuadores reales: sigue siendo la ruta contractual
con safety en `DRY_RUN`.

Para bring-up fisico de banco, el firmware incluye comandos explicitos
`TEST_ONLY` para una bomba de MVP y lectura real de humedad de suelo. Estos
comandos no sustituyen al contrato `WATER`; solo permiten validar cobre,
rele, bomba y sensor con control manual.

El siguiente hito inmediato añade:

- `HOST_HEARTBEAT` / `JETSON_HEARTBEAT` para refrescar la presencia de Rhizome
- `TELEMETRY` para devolver un snapshot stub de sensores mientras no haya cableado
- `host_link` y `host_age_ms` en `STATUS_REPORT` y `HEARTBEAT`
- `SET_SENSOR_STUB ...` y `RESET_SENSOR_STUBS` para simular entradas antes del cableado real
- `WATER A|B|BOTH <seconds>` en modo `DRY_RUN`, con rechazo por safety aunque todavia no se activen relés

El primer sensor real integrado en esta fase es:

- `BME280` por `I2C`
- comandos:
  - `I2C_SCAN`
  - `BME280_PROBE`
  - `BME280_READ`
- baseline de pines en ambos board profiles:
  - `SDA = GPIO8`
  - `SCL = GPIO9`
  - `I2C port = 0`

Actuadores y sensores MVP de banco:

- bomba 12V con rele active-low:
  - `GPIO16 = rele IN`
  - `PUMP_OFF`
  - `PUMP_STATUS`
  - `PUMP_PULSE <ms>`
- humedad de suelo capacitiva:
  - `GPIO4 = ADC soil A`
  - `SOIL_READ`

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
- `HOST_HEARTBEAT`
- `JETSON_HEARTBEAT`
- `TELEMETRY`
- `I2C_SCAN`
- `I2C_SCAN` escanea de momento solo las direcciones candidatas del `BME280`
  (`0x76`, `0x77`) para evitar ruido de probe en un bus sin cableado. Cuando
  entre `ADS1115`, este comando se ampliara a un scan general o se dividira por
  familia de sensor.
- `BME280_PROBE`
- `BME280_READ`
- `SOIL_READ`
- `PUMP_OFF`
- `PUMP_STATUS`
- `PUMP_PULSE <ms>`
- `SET_SENSOR_STUB SOIL_A <int>`
- `SET_SENSOR_STUB SOIL_B <int>`
- `SET_SENSOR_STUB TANK_LEVEL <int>`
- `SET_SENSOR_STUB TANK_LEVEL_PCT <int>`
- `SET_SENSOR_STUB FLOW_PULSES <int>`
- `SET_SENSOR_STUB BME280 CONNECTED|DISCONNECTED`
- `RESET_SENSOR_STUBS`
- `WATER A <seconds>`
- `WATER B <seconds>`
- `WATER BOTH <seconds>`
- `STOP`
- `RESET_ALERT`

Salida:

- `HELLO fw=... state=SAFE_IDLE board=... uptime_ms=...`
- `STATUS_REPORT state=SAFE_IDLE fw=... board=... uptime_ms=... flash_bytes=... psram_bytes=... telemetry_mode=HYBRID i2c_bus=... i2c_sda=... i2c_scl=... bme280_addr=... host_link=... host_age_ms=...`
- `HEARTBEAT state=SAFE_IDLE board=... uptime_ms=... host_link=... host_age_ms=...`
- `ACK command=HOST_HEARTBEAT state=... host_link=... host_age_ms=...`
- `TELEMETRY_REPORT soil_a_raw=... soil_b_raw=... tank_level_raw=... flow_pulses=... bme280=... bme280_valid=... bme280_temp_c_x100=... bme280_humidity_pct_x100=... bme280_pressure_pa=...`
- `I2C_SCAN count=... addrs=...`
- `BME280_PROBE status=... address=... chip_id=... i2c_bus=...`
- `BME280_REPORT status=... address=... chip_id=... temp_c_x100=... humidity_pct_x100=... pressure_pa=...`
- `SOIL_REPORT soil_a_raw=... soil_a_source=ADC soil_a_gpio=4 adc_unit=1 adc_channel=3 source=command`
- `PUMP_REPORT gpio=16 active_low=true expected_gpio_level=... gpio_level=... state=OFF|ON test_max_ms=... execution=TEST_ONLY source=command`
- `ACK command=PUMP_PULSE gpio=16 active_low=true duration_ms=... final_expected_gpio_level=1 final_gpio_level=1 final_state=OFF execution=TEST_ONLY`
- `ACK command=SET_SENSOR_STUB field=... soil_a_raw=... soil_b_raw=... tank_level_raw=... flow_pulses=... bme280=...`
- `ACK command=WATER plot=... seconds=... execution=DRY_RUN ...`
- `ALERT code=... latched=true|false state=... uptime_ms=...`
- `REJECT reason=UNKNOWN_COMMAND cmd=...`

## Build y flash

## Primer bring-up recomendado

Antes de mezclar la placa con Jetson, el arranque inicial debe hacerse en un host Windows para aislar variables de USB, drivers y toolchain.

Secuencia recomendada para la `ESP32-S3 N16R8 USB OTG`:

1. conectar la placa al PC Windows con cable de datos
2. entrar en modo descarga con `BOOT + RESET` si el puerto no aparece a la primera
3. verificar que el host enumera un puerto `COM`
4. flashear el firmware milestone-0
5. comprobar que `STATUS_REPORT` expone `flash_bytes ~= 16777216` y `psram_bytes ~= 8388608`
6. solo despues pasar al host Jetson y validar `/dev/ttyACM*`

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
- `GPIO8 / GPIO9` quedan reservados para `I2C` del `BME280` / futuros periféricos `ADS1115`
- `GPIO4` queda reservado para el sensor capacitivo de humedad `SOIL_A`
- `GPIO16` queda reservado para el rele active-low de la bomba MVP
- `WATER` no energiza actuadores reales en este hito; solo `PUMP_PULSE` puede
  hacerlo y siempre como `TEST_ONLY`

## Validación esperada

Al arrancar en la `ESP32-S3 N16R8 USB OTG` deberíamos ver:

```text
HELLO fw=0.1.0 state=SAFE_IDLE board=n16r8_usb_otg uptime_ms=...
HEARTBEAT state=SAFE_IDLE board=n16r8_usb_otg uptime_ms=...
```

Y ante `STATUS`:

```text
STATUS_REPORT state=SAFE_IDLE fw=0.1.0 board=n16r8_usb_otg uptime_ms=... flash_bytes=16777216 psram_bytes=8388608 telemetry_mode=HYBRID i2c_bus=READY i2c_sda=8 i2c_scl=9 bme280_addr=NONE host_link=MISSING host_age_ms=-1 hb_timeout_ms=5000 tank_min_pct=20 max_water_s=30 last_reject=NONE alert_code=NONE
```

Y tras enviar `HOST_HEARTBEAT`:

```text
ACK command=HOST_HEARTBEAT state=SAFE_IDLE host_link=FRESH host_age_ms=0
```

Y ante `TELEMETRY`:

```text
TELEMETRY_REPORT soil_a_raw=-1 soil_b_raw=-1 tank_level_raw=-1 tank_level_pct=-1 flow_pulses=0 bme280=DISCONNECTED bme280_valid=false bme280_temp_c_x100=-1 bme280_humidity_pct_x100=-1 bme280_pressure_pa=-1 host_link=FRESH host_age_ms=...
```

Ejemplo de simulacion de sensores:

```text
SET_SENSOR_STUB SOIL_A 1234
SET_SENSOR_STUB SOIL_B 1450
SET_SENSOR_STUB TANK_LEVEL 820
SET_SENSOR_STUB TANK_LEVEL_PCT 65
SET_SENSOR_STUB FLOW_PULSES 17
SET_SENSOR_STUB BME280 CONNECTED
TELEMETRY
```

Ejemplo de `BME280` real por `I2C`:

```text
I2C_SCAN
I2C_SCAN count=1 addrs=0x76

BME280_PROBE
BME280_PROBE status=CONNECTED address=0x76 chip_id=0x60 i2c_bus=READY error=ESP_OK sensor_rslt=0

BME280_READ
BME280_REPORT status=CONNECTED address=0x76 chip_id=0x60 temp_c_x100=2314 humidity_pct_x100=4587 pressure_pa=100812 error=ESP_OK sensor_rslt=0 source=command

TELEMETRY
TELEMETRY_REPORT soil_a_raw=-1 soil_b_raw=-1 tank_level_raw=-1 tank_level_pct=-1 flow_pulses=0 bme280=CONNECTED bme280_valid=true bme280_temp_c_x100=2314 bme280_humidity_pct_x100=4587 bme280_pressure_pa=100812 host_link=... source=command
```

Mientras no haya protoboard ni cables Dupont, el contrato esperado es el
baseline desconectado:

```text
STATUS
STATUS_REPORT ... telemetry_mode=HYBRID i2c_bus=READY i2c_sda=8 i2c_scl=9 bme280_addr=NONE ...

I2C_SCAN
I2C_SCAN count=0 addrs=NONE

BME280_PROBE
BME280_PROBE status=NOT_FOUND address=NONE chip_id=NONE i2c_bus=READY ...

BME280_READ
BME280_REPORT status=NOT_FOUND address=NONE chip_id=NONE temp_c_x100=-1 humidity_pct_x100=-1 pressure_pa=-1 ...
```

Este baseline no es un fallo: demuestra que el firmware no inventa sensor ni
lecturas cuando el bus esta vivo pero no hay periferico conectado.

Ejemplo de bomba MVP y humedad real:

```text
PUMP_STATUS
PUMP_REPORT gpio=16 active_low=true expected_gpio_level=1 gpio_level=1 state=OFF test_max_ms=30000 execution=TEST_ONLY source=command

SOIL_READ
SOIL_REPORT soil_a_raw=2278 soil_a_source=ADC soil_a_gpio=4 adc_unit=1 adc_channel=3 source=command

PUMP_PULSE 3000
ACK command=PUMP_PULSE gpio=16 active_low=true duration_ms=3000 final_expected_gpio_level=1 final_gpio_level=1 final_state=OFF execution=TEST_ONLY

PUMP_OFF
ACK command=PUMP_OFF state=SAFE_IDLE host_link=... host_age_ms=...
```

Calibracion empirica provisional del sensor de humedad:

```text
aire:              soil_a_raw ~= 3530-3540
tierra seca:       soil_a_raw ~= 2319-2325
antes de riego:    soil_a_raw ~= 2278
humedad buena:     soil_a_raw ~= 1687-1702
tras difusion:     soil_a_raw ~= 1289-1291
```

Reglas provisionales de banco para esta sonda y maceta:

- `SOIL_RAW_POLARITY=low_is_wet`
- `SOIL_WET_BELOW_RAW=1300`
- `SOIL_DRY_ABOVE_RAW=2200`

Interpretacion:

| Rango `soil_a_raw` | Decision |
|---|---|
| `< 1300` | muy humedo; no regar mas |
| `1300-2199` | zona intermedia; observar/defer, no riego autonomo |
| `>= 2200` | seco para MVP; candidato a riego si las demas barandillas pasan |

Estos valores son empiricos de demo. Recalibrar si cambia sustrato, maceta,
profundidad del sensor o posicion de riego.

Ejemplos de seguridad para `WATER`:

```text
WATER A 12
REJECT reason=JETSON_HEARTBEAT_LOST cmd=WATER A 12

HOST_HEARTBEAT
SET_SENSOR_STUB TANK_LEVEL_PCT 15
WATER A 12
REJECT reason=TANK_LOW cmd=WATER A 12
ALERT code=TANK_LOW latched=true state=ALERT_LATCHED uptime_ms=...

SET_SENSOR_STUB TANK_LEVEL_PCT 65
HOST_HEARTBEAT
WATER A 12
REJECT reason=ALERT_LATCHED cmd=WATER A 12
RESET_ALERT
ACK command=RESET_ALERT state=SAFE_IDLE host_link=FRESH host_age_ms=...
HOST_HEARTBEAT
WATER A 12
ACK command=WATER plot=A seconds=12 execution=DRY_RUN state=SAFE_IDLE host_link=FRESH tank_level_pct=65
```

Si el puerto USB no enumera a la primera en un S3 nuevo:

1. mantener `BOOT`
2. pulsar y soltar `RESET / EN`
3. soltar `BOOT`
4. volver a intentar `flash` o abrir monitor serie

## Fuentes operativas validadas

- Jetson AI Lab, `Gemma 4 on Jetson`, leída el `2026-04-25`: https://www.jetson-ai-lab.com/tutorials/gemma4-on-jetson/
- Espressif, `ESP-IDF Get Started for ESP32-S3 (stable v6.0)`, leída el `2026-04-25`: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/get-started/index.html
- Espressif, `USB Serial/JTAG Controller Console`, leída el `2026-04-25`: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/usb-serial-jtag-console.html
- Espressif, `SPI Flash and External SPI RAM Configuration`, leída el `2026-04-25`: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/flash_psram_config.html
- Espressif, `I2C Master Driver`, leída el `2026-04-27`: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/i2c.html
- Bosch Sensortec, `BME280_SensorAPI`, commit `c90d419492e26dd95586598a794e65eb2760753a`, leído el `2026-04-27`: https://github.com/boschsensortec/BME280_SensorAPI


---

## Note on language

The English **Abstract** at the top of this file is the canonical public summary. The body below is in Spanish — it is the working language of the team and the place where decisions, trade-offs and trace get written. The contracts, code and tests are inspectable without Spanish context. See [Language note in the root README](../../README.md#language-note) for the project-wide policy.
