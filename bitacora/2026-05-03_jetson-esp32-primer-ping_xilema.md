# Primer ping Jetson <-> ESP32

**Autora:** Xilema
**Fecha:** 2026-05-03
**Dia de proyecto:** 18
**Rama:** `docs/jetson-esp32-first-ping`

## Estado

Se ejecuto el primer ping real entre Jetson Orin Nano Super y ESP32-S3 por
USB-CDC/JTAG serial. No se conectaron bomba, reles ni alimentacion de 12V. La
prueba fue solo protocolo serie y safety en `DRY_RUN`.

La Jetson detecto el ESP32 como:

```text
/dev/ttyACM0
ID 303a:1001 Espressif USB JTAG/serial debug unit
```

Fue necesario anadir `rhizome_01` al grupo `dialout` para abrir el puerto:

```bash
sudo usermod -aG dialout rhizome_01
```

Tras reinicio, `rhizome_01` pudo abrir `/dev/ttyACM0` sin `sudo`.

## Prueba ejecutada

Desde Jetson, con Python estandar y puerto `/dev/ttyACM0` a `115200` baudios:

1. Escucha de `HEARTBEAT`.
2. `STATUS`.
3. `HOST_HEARTBEAT`.
4. `TELEMETRY`.
5. `SET_SENSOR_STUB TANK_LEVEL_PCT 15`.
6. `HOST_HEARTBEAT`.
7. `WATER A 12`.
8. `STATUS`.
9. `RESET_ALERT`.
10. `STATUS`.

## Resultado

El ESP32 respondio correctamente a Jetson:

```text
STATUS_REPORT state=SAFE_IDLE ... host_link=STALE ...
ACK command=HOST_HEARTBEAT state=SAFE_IDLE host_link=FRESH host_age_ms=0
TELEMETRY_REPORT ... tank_level_pct=15 ... host_link=FRESH ...
REJECT reason=TANK_LOW cmd=WATER A 12
ALERT code=TANK_LOW latched=true state=ALERT_LATCHED
STATUS_REPORT state=ALERT_LATCHED ... last_reject=TANK_LOW ...
ACK command=RESET_ALERT state=SAFE_IDLE
STATUS_REPORT state=SAFE_IDLE ... alert_code=NONE ...
```

Lectura:

- Jetson puede hablar con ESP32 por USB-CDC.
- El heartbeat de host cruza correctamente.
- La telemetria cruza correctamente.
- La regla dura `TANK_LOW` se aplica en ESP32 ante `WATER A 12`.
- El rechazo latchea alerta y deja trazabilidad en `STATUS_REPORT`.
- `RESET_ALERT` recupera `SAFE_IDLE`.
- No se ejecuta agua real; la frontera fisica sigue mandando.

## Artefactos

Log remoto en Jetson:

```text
/home/rhizome_01/sprout_jetson_esp32_reports/20260503T174932Z_jetson_esp32_guardian_ping.log
```

Copia local de trabajo, no versionada porque `*.log` esta ignorado:

```text
hardware/host_tools/reports/20260503T174932Z_jetson_esp32_guardian_ping.log
```

## Notas

- El primer intento de log entro a mitad de una linea `HEARTBEAT`, por eso la
  primera linea del transcript contiene un fragmento duplicado. No afecta al
  resultado; las respuestas posteriores son limpias.
- El firmware reporto `fw=25a904f-dirty`. La prueba fisica es valida, pero de
  cara a video/rehearsal conviene reflashear cuando #68 este mergeado para que
  el SHA salga limpio.
- El harness oficial `hardware/host_tools/esp32_host_harness.py` esta presente
  en Jetson, pero el Python del sistema no tiene `pyserial`. Se evito instalar
  dependencias en sistema y se uso Python estandar para no ensuciar el entorno.

## Decision

El primer enlace Jetson <-> ESP32 queda validado a nivel de protocolo y safety.
El siguiente paso razonable es convertir esta secuencia en escenario
reproducible del harness o ejecutar el harness en un contenedor controlado,
pero ya no hay bloqueo de USB, permisos ni protocolo base.
