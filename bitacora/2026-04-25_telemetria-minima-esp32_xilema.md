# Telemetria minima y latido del host en ESP32

**Fecha:** 2026-04-25  
**Autor:** Xilema  
**Area:** Hardware / Rhizome  
**Tipo:** Avance

## Contexto

Tras cerrar el hito `SAFE_IDLE + HELLO + STATUS + HEARTBEAT` sobre la `ESP32-S3 N16R8`, el siguiente paso util sin cableado adicional es empezar a modelar la frontera Rhizome ↔ ESP32.

## Que se anade

- `HOST_HEARTBEAT` / `JETSON_HEARTBEAT` para refrescar la presencia del host
- `TELEMETRY` para devolver un snapshot stub de sensores
- `SET_SENSOR_STUB ...` y `RESET_SENSOR_STUBS` para inyectar lecturas de prueba
- `host_link` y `host_age_ms` en `STATUS_REPORT` y `HEARTBEAT`
- `WATER A|B|BOTH <seconds>` en `DRY_RUN` con rechazo por `HEARTBEAT_PERDIDO`, `DEPOSITO_BAJO` o `FUERA_DE_RANGO`
- `ALERT code=...` y `RESET_ALERT` para hacer visible y controlable el latch de seguridad
- timeout configurable de frescura del host (`CONFIG_SPROUT_HOST_HEARTBEAT_TIMEOUT_MS`)

## Por que

Esto permite probar ya tres cosas importantes antes de leer sensores reales:

1. que el ESP32 distingue entre enlace fresco y enlace ausente
2. que el protocolo serie ya puede devolver una telemetria estructurada
3. que Rhizome tendra una base clara para decidir prudencia por perdida de heartbeat
4. que el equipo puede ensayar logica de decision y receipts antes del cableado real
5. que la capa fisica ya puede bloquear agua de forma demostrable sin conectar la bomba
6. que el estado materializado del ESP32 ya cuente el ultimo rechazo y el ultimo intento de agua

## Lo que no hace aun

- no lee sensores reales
- no ejecuta actuadores
- no aplica reglas duras de agua
- no persiste ultimas lecturas ni limites

## Siguiente paso

- validar en placa `HOST_HEARTBEAT` -> `ACK`
- validar `TELEMETRY_REPORT`
- pasar luego a telemetria real de sensores sin actuadores
