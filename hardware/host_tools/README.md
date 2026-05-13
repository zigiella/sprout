# host_tools

Herramientas host-side para hablar con el `ESP32-S3` por serie sin depender todavía de Jetson.

## Objetivo

El primer uso de este directorio es automatizar secuencias del protocolo serie de
`hardware/firmware_esp32/` y guardar evidencia reproducible para:

- rehearsal de escenas del video
- regresiones del guardián físico
- integración futura con `Rhizome`
- validación antes de meter sensores reales

## Requisitos

- Python 3.11+
- `pyserial`

Instalación rápida:

```powershell
python -m pip install -r hardware/host_tools/requirements.txt
```

## Script principal

```powershell
python hardware/host_tools/esp32_host_harness.py --port COM5 --scenario guardian_demo
```

Linux / Jetson:

```bash
python hardware/host_tools/esp32_host_harness.py --port /dev/ttyACM0 --scenario guardian_demo
```

## Qué hace

- abre el puerto serie
- carga un escenario versionado en `scenarios/`
- envía comandos ASCII terminados en `\n`
- espera la respuesta del ESP32 tras cada comando
- valida expectativas mínimas por paso
- guarda transcript y resumen JSON en `reports/`

## Escenarios incluidos

- `bme280_disconnected_baseline`
  - valida el contrato `I2C_SCAN` / `BME280_PROBE` / `BME280_READ` cuando todavia no
    hay sensor cableado
- `bme280_connected_smoke`
  - smoke test previsto para el dia de cableado real del `BME280`
- `guardian_demo`
  - enseña el hilo completo del guardián: heartbeat perdido, depósito bajo latched,
    reset y `ACK_DRY_RUN`
- `pump_soil_smoke`
  - smoke test seguro para Endodermis: `PUMP_STATUS`, `SOIL_READ`, pulso de
    bomba `TEST_ONLY` de 3s y verificacion final `OFF`
- `pump_soil_observe_only`
  - lectura sin riego: estado de bomba, humedad real y telemetria; util cuando
    el sustrato ya esta humedo
- `telemetry_stub_roundtrip`
  - rellena telemetría stub, la lee y vuelve al baseline

Listar escenarios:

```powershell
python hardware/host_tools/esp32_host_harness.py --list-scenarios
```

## Artefactos

Por defecto se generan dos artefactos en `hardware/host_tools/reports/`:

- `<timestamp>_<scenario>.log`
- `<timestamp>_<scenario>.json`

El `.log` guarda el transcript con dirección `TX` / `RX`.  
El `.json` guarda metadatos, resultado, pasos y expectativas satisfechas o fallidas.

## Flujo recomendado con la N16R8

1. flashear por el puerto `CH343` (`COM3` en el caso validado)
2. mover el cable al USB nativo
3. identificar el `COM` real que Windows haya asignado
4. ejecutar el harness contra ese puerto

Ejemplo real validado:

- `COM3` para `flash`
- `COM5` para `monitor` / harness

## Nota de ergonomía

El firmware mantiene `host_link` fresco solo durante `5000 ms`. El harness envía los
comandos mucho más rápido que una prueba manual y evita falsos rechazos por tecleo lento.

## Troubleshooting de puerto serie

Si Windows lista un `COM` pero el harness responde que no puede abrirlo, trátalo
como puerto fantasma o ocupado:

- desconectar y reconectar el USB
- cerrar cualquier monitor serie abierto
- volver a listar puertos en el Administrador de dispositivos
- usar el `COM` que aparece activo tras reconectar, no uno recordado de sesiones previas

El caso observado en la `N16R8` fue: Windows mostraba `COM3`, `COM4` y `COM5`,
pero `esptool` y el harness recibían `FileNotFoundError` al abrirlos.

## Trabajo sin protoboard / Dupont

Hasta que haya cableado físico, el escenario útil para el carril BME280 es:

```powershell
python hardware/host_tools/esp32_host_harness.py --port COM5 --scenario bme280_disconnected_baseline --label pre_cableado
```

Ese transcript debe demostrar:

- el bus `I2C` arranca en `READY`
- `GPIO8/GPIO9` quedan publicados en `STATUS_REPORT`
- `I2C_SCAN` no inventa dispositivos
- `BME280_PROBE` y `BME280_READ` devuelven `NOT_FOUND`
- `TELEMETRY` conserva `bme280=DISCONNECTED` y lecturas centinela `-1`

Cuando llegue el cableado, este mismo escenario debe fallar de forma informativa
en `I2C_SCAN` y se sustituye por el escenario conectado con `count=1` y
`BME280_REPORT status=CONNECTED`.

Escenario previsto para el primer test real:

```powershell
python hardware/host_tools/esp32_host_harness.py --port COM5 --scenario bme280_connected_smoke --label primer_bme280
```

Escenario seguro sin riego para la ruta bomba + humedad desde Jetson:

```bash
python hardware/host_tools/esp32_host_harness.py --port /dev/ttyACM0 --scenario pump_soil_observe_only --label endo_observe
```

Escenario con pulso supervisado perceptible de bomba desde Jetson:

```bash
python hardware/host_tools/esp32_host_harness.py --port /dev/ttyACM0 --scenario pump_soil_smoke --label endo_smoke
```

Antes de ejecutarlo, Bea debe confirmar que la bomba esta sumergida, que la
electronica esta seca y que el sustrato no esta ya muy humedo. Si
`SOIL_READ` esta por debajo de `1300`, usar solo `pump_soil_observe_only`.

Para Steward/Rhizome en modo autonomo, la calibracion provisional de esta
sonda es:

```bash
SOIL_RAW_POLARITY=low_is_wet
SOIL_WET_BELOW_RAW=1300
SOIL_DRY_ABOVE_RAW=2200
```

La banda `1300-2199` se trata como ambigua: se observa o se aplaza, pero no se
promociona a riego autonomo. `pump_soil_smoke` es solo una prueba fisica
supervisada de 3s, no una decision agronomica.
