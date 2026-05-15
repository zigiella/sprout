# firmware_esp32

**Abstract.** This firmware is Sprout's physical safety coprocessor, written in C with ESP-IDF for ESP32-S3. It owns the relay, the pump, the soil moisture reading on `GPIO4` and the relay control on `GPIO16`. It validates every irrigation command against five hard rules (`JETSON_HEARTBEAT_LOST`, `TANK_LOW`, `EVENT_DURATION_OUT_OF_RANGE`, `NO_FLOW_DETECTED`, `ALERT_LATCHED`) and rejects with a legible reason if any fails. The state machine is `SAFE_IDLE → READY → EXECUTING → DEGRADED → ALERT_LATCHED`. The LLM proposes; this firmware disposes.

> **Submission status:** `WATER` remains the conservative contract path and returns `DRY_RUN`; supervised physical actuation is demonstrated through `PUMP_PULSE <ms>` as `TEST_ONLY`. This distinction is intentional: it keeps the autonomous control path conservative while proving the physical pump/soil loop on real hardware. Day 27 validated 12 supervised pulses with measurable soil moisture drop (raw 2278 → 1289 after pulse).

---

Bootstrap of the real firmware for Sprout's hard safety layer.

## Goal of the current milestone

This project does not try to close the full firmware in one go.

The first milestone is:

- always boot in `SAFE_IDLE`
- expose a serial console over **USB Serial/JTAG / CDC-ACM**
- emit `HELLO` on boot
- answer `STATUS`
- emit periodic `HEARTBEAT`
- report `flash_bytes` and `psram_bytes`

`WATER` does not yet activate real actuators: it remains the contractual path with safety in `DRY_RUN`.

For physical bench bring-up, the firmware includes explicit `TEST_ONLY` commands for an MVP pump and real soil moisture reading. These commands do not replace the `WATER` contract; they only allow validating copper, relay, pump and sensor under manual control.

The next immediate milestone adds:

- `HOST_HEARTBEAT` / `JETSON_HEARTBEAT` to refresh Rhizome presence
- `TELEMETRY` to return a stub snapshot of sensors until wiring is in place
- `host_link` and `host_age_ms` in `STATUS_REPORT` and `HEARTBEAT`
- `SET_SENSOR_STUB ...` and `RESET_SENSOR_STUBS` to simulate inputs before real wiring
- `WATER A|B|BOTH <seconds>` in `DRY_RUN` mode, rejected by safety even when no relay is energised yet

The first real sensor integrated in this phase is:

- `BME280` over `I2C`
- commands:
  - `I2C_SCAN`
  - `BME280_PROBE`
  - `BME280_READ`
- pin baseline in both board profiles:
  - `SDA = GPIO8`
  - `SCL = GPIO9`
  - `I2C port = 0`

MVP bench actuators and sensors:

- 12V pump with active-low relay:
  - `GPIO16 = relay IN`
  - `PUMP_OFF`
  - `PUMP_STATUS`
  - `PUMP_PULSE <ms>`
- capacitive soil moisture:
  - `GPIO4 = ADC soil A`
  - `SOIL_READ`

## Stack

- target: `ESP32-S3`
- framework: **ESP-IDF**
- initial board profile: `n16r8_usb_otg`
- planned future board profile: `devkitc_n8r8`

## Structure

- `main/app_main.c` — `SAFE_IDLE` state, protocol loop and heartbeat
- `main/board_profile.[ch]` — separation between firmware logic and board profile
- `main/Kconfig.projbuild` — board profile options and milestone timing
- `sdkconfig.defaults` — USB console and PSRAM baseline

## Milestone-0 protocol

Input: ASCII line terminated by `\n`:

- `HELLO`
- `STATUS`
- `HOST_HEARTBEAT`
- `JETSON_HEARTBEAT`
- `TELEMETRY`
- `I2C_SCAN`
- `I2C_SCAN` currently scans only the `BME280` candidate addresses (`0x76`, `0x77`) to avoid probe noise on an unwired bus. When `ADS1115` enters, this command will be expanded to a general scan or split by sensor family.
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

Output:

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

## Build and flash

## Recommended first bring-up

Before mixing the board with the Jetson, initial boot should happen on a Windows host to isolate USB, driver and toolchain variables.

Recommended sequence for the `ESP32-S3 N16R8 USB OTG`:

1. connect the board to the Windows PC with a data cable
2. enter download mode with `BOOT + RESET` if the port does not appear on first try
3. verify that the host enumerates a `COM` port
4. flash the milestone-0 firmware
5. check that `STATUS_REPORT` exposes `flash_bytes ~= 16777216` and `psram_bytes ~= 8388608`
6. only then move to the Jetson host and validate `/dev/ttyACM*`

### Windows host

```powershell
idf.py set-target esp32s3
idf.py build
idf.py -p COM7 flash monitor
```

### Linux host / Jetson later

```bash
idf.py set-target esp32s3
idf.py build
idf.py -p /dev/ttyACM0 flash monitor
```

## Hardware notes

- `GPIO19 / GPIO20` reserved for native USB
- `GPIO35 / GPIO36 / GPIO37` not used due to Octal PSRAM
- `GPIO45 / GPIO46` avoided on first boot
- `GPIO8 / GPIO9` reserved for `BME280` `I2C` and future `ADS1115` peripherals
- `GPIO4` reserved for the capacitive soil moisture sensor `SOIL_A`
- `GPIO16` reserved for the active-low relay of the MVP pump
- `WATER` does not energise real actuators in this milestone; only `PUMP_PULSE` can, and always as `TEST_ONLY`

## Expected validation

On boot of the `ESP32-S3 N16R8 USB OTG` we should see:

```text
HELLO fw=0.1.0 state=SAFE_IDLE board=n16r8_usb_otg uptime_ms=...
HEARTBEAT state=SAFE_IDLE board=n16r8_usb_otg uptime_ms=...
```

And in response to `STATUS`:

```text
STATUS_REPORT state=SAFE_IDLE fw=0.1.0 board=n16r8_usb_otg uptime_ms=... flash_bytes=16777216 psram_bytes=8388608 telemetry_mode=HYBRID i2c_bus=READY i2c_sda=8 i2c_scl=9 bme280_addr=NONE host_link=MISSING host_age_ms=-1 hb_timeout_ms=5000 tank_min_pct=20 max_water_s=30 last_reject=NONE alert_code=NONE
```

And after sending `HOST_HEARTBEAT`:

```text
ACK command=HOST_HEARTBEAT state=SAFE_IDLE host_link=FRESH host_age_ms=0
```

And in response to `TELEMETRY`:

```text
TELEMETRY_REPORT soil_a_raw=-1 soil_b_raw=-1 tank_level_raw=-1 tank_level_pct=-1 flow_pulses=0 bme280=DISCONNECTED bme280_valid=false bme280_temp_c_x100=-1 bme280_humidity_pct_x100=-1 bme280_pressure_pa=-1 host_link=FRESH host_age_ms=...
```

Sensor simulation example:

```text
SET_SENSOR_STUB SOIL_A 1234
SET_SENSOR_STUB SOIL_B 1450
SET_SENSOR_STUB TANK_LEVEL 820
SET_SENSOR_STUB TANK_LEVEL_PCT 65
SET_SENSOR_STUB FLOW_PULSES 17
SET_SENSOR_STUB BME280 CONNECTED
TELEMETRY
```

Real `BME280` over `I2C` example:

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

With no breadboard or Dupont cables, the expected contract is the disconnected baseline:

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

This baseline is not a failure: it shows that the firmware does not invent a sensor or readings when the bus is live but no peripheral is wired.

MVP pump and real moisture example:

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

Provisional empirical calibration of the moisture sensor:

```text
air:               soil_a_raw ~= 3530-3540
dry soil:          soil_a_raw ~= 2319-2325
before irrigation: soil_a_raw ~= 2278
good moisture:     soil_a_raw ~= 1687-1702
after diffusion:   soil_a_raw ~= 1289-1291
```

Provisional bench rules for this probe and pot:

- `SOIL_RAW_POLARITY=low_is_wet`
- `SOIL_WET_BELOW_RAW=1300`
- `SOIL_DRY_ABOVE_RAW=2200`

Interpretation:

| `soil_a_raw` range | Decision |
|---|---|
| `< 1300` | very moist; do not water further |
| `1300-2199` | intermediate band; observe / defer, no autonomous watering |
| `>= 2200` | dry for the MVP; candidate for watering if all other guardrails pass |

These values are empirical demo numbers. Recalibrate if substrate, pot, sensor depth or irrigation position changes.

`WATER` safety examples:

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

If the USB port does not enumerate on first try with a new S3:

1. hold `BOOT`
2. press and release `RESET / EN`
3. release `BOOT`
4. retry `flash` or open the serial monitor

## Validated operational sources

- Jetson AI Lab, *Gemma 4 on Jetson*, read on `2026-04-25`: https://www.jetson-ai-lab.com/tutorials/gemma4-on-jetson/
- Espressif, *ESP-IDF Get Started for ESP32-S3 (stable v6.0)*, read on `2026-04-25`: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/get-started/index.html
- Espressif, *USB Serial/JTAG Controller Console*, read on `2026-04-25`: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/usb-serial-jtag-console.html
- Espressif, *SPI Flash and External SPI RAM Configuration*, read on `2026-04-25`: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/flash_psram_config.html
- Espressif, *I2C Master Driver*, read on `2026-04-27`: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/i2c.html
- Bosch Sensortec, *BME280_SensorAPI*, commit `c90d419492e26dd95586598a794e65eb2760753a`, read on `2026-04-27`: https://github.com/boschsensortec/BME280_SensorAPI

---

## Note on language

This README is English-first. Internal bitácoras (Spanish-language working journals) and the day-by-day development trace live under [`bitacora/`](../../bitacora/). See the [Language note in the root README](../../README.md#language-note) for the project-wide policy.
