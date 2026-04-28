# Harness host serie para ESP32

**Fecha:** 2026-04-26  
**Autor:** Xilema  
**Area:** Hardware / Rhizome  
**Tipo:** Avance

## Contexto

Tras validar manualmente en placa la `ESP32-S3 N16R8` con `SAFE_IDLE`, telemetria
stub y guardián físico en `DRY_RUN`, el siguiente cuello de botella era la propia
interacción manual por consola. Para rehearsal, evidencia reproducible e
integración futura con `Rhizome`, necesitábamos automatizar secuencias serie sin
depender de tecleo humano ni de `idf_monitor`.

## Que hicimos / decidimos

- Se abrió el issue `#54` para formalizar el trabajo del harness host-side.
- Se creó `hardware/host_tools/` como directorio separado de `firmware_esp32/`.
- Se implementó `hardware/host_tools/esp32_host_harness.py`.
- El harness:
  - abre un puerto serie (`COMx` o `/dev/ttyACM*`)
  - carga escenarios versionados en `hardware/host_tools/scenarios/`
  - envía comandos ASCII terminados en `\n`
  - captura líneas `RX` con timestamps relativos
  - valida expectativas mínimas por paso
  - guarda transcript `.log` y resumen `.json` en `hardware/host_tools/reports/`
- Se versionaron dos escenarios iniciales:
  - `guardian_demo`
  - `telemetry_stub_roundtrip`
- Se añadió documentación de uso en `hardware/host_tools/README.md`.
- Se añadió `requirements.txt` con `pyserial`.
- Se añadió un test sin hardware real en
  `hardware/host_tools/tests/test_esp32_host_harness.py`.
- Se actualizó `hardware/README.md` para reflejar el nuevo carril host-side.

## Por que

- El firmware ya estaba lo bastante maduro como para ensayar secuencias completas,
  pero hacerlo a mano hacía difícil repetir el mismo caso dos veces.
- El `host_link` con timeout de `5000 ms` es correcto para safety, pero en pruebas
  manuales puede esconder el caso que realmente queremos observar. El harness
  elimina ese ruido sin aflojar el guardián.
- Separar `host_tools/` de `firmware_esp32/` mantiene clara la frontera: una cosa
  es el coprocesador físico y otra el cliente host que lo ejercita.
- Los artefactos `.log` + `.json` nos sirven tanto para vídeo/writeup como para
  pruebas futuras con Jetson o con `Rhizome` real.

## Que queda pendiente

- [ ] Ejecutar `guardian_demo` contra la placa real y guardar el primer transcript versionable
- [ ] Ejecutar `telemetry_stub_roundtrip` contra la placa real
- [ ] Decidir si el siguiente paso es `BME280` por I2C o el primer canal analógico serio
- [ ] Valorar un campo futuro de `root_alert_code` en firmware para no perder la causa raíz cuando `last_reject` pasa a `ALERTA_LATCHED`

## Enlaces

- [hardware/host_tools/README.md](../hardware/host_tools/README.md)
- [docs/13_esp32_spec.md](../docs/13_esp32_spec.md)
- [issue #54](https://github.com/zigiella/sprout/issues/54)
