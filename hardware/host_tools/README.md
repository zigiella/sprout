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

- `guardian_demo`
  - enseña el hilo completo del guardián: heartbeat perdido, depósito bajo latched,
    reset y `ACK_DRY_RUN`
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
