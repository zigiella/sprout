# Esquemas de montaje electronico e hidraulico

**Autora:** Xilema
**Fecha:** 2026-05-04
**Dia de proyecto:** 19
**Rama:** `docs/hardware-mounting-schematics`

## Estado

Bea necesita empezar el montaje fisico: agua, bomba, riego, sensores y caja.
El sistema ya cruzo Jetson <-> ESP32 el dia 18, pero aun no debemos activar
actuadores 12V.

## Decision

Creo una guia de montaje en `hardware/wiring_diagrams/day19_mounting_schematics.md`
con cuatro capas separadas:

- alimentacion y masas,
- sensores,
- actuadores,
- hidraulica.

La guia distingue explicitamente:

- cableado ya autorizado hoy: USB Jetson<->ESP32 y BME280 por I2C (`GPIO8/9`);
- cableado que se puede montar mecanicamente y etiquetar;
- pines propuestos para firmware futuro;
- pasos que quedan bloqueados hasta PR de firmware y validacion sin carga.

## Hallazgos

El firmware actual no define todavia GPIOs reales para humedad, nivel,
caudalimetro, bomba ni valvulas. Por tanto, seria peligroso publicar un esquema
como si esos pines fueran contrato. La guia propone candidatos, pero los marca
como pendientes.

## Regla mantenida

No conectar bomba, valvulas ni 12V a control hasta revisar:

- fusible,
- driver MOSFET/rele,
- flyback,
- masa comun,
- ausencia de corto,
- prueba sin carga.

## Next step

Cuando Bea tenga el montaje preparado, el siguiente trabajo de Xilema sera:

1. convertir pinout propuesto en contrato de firmware,
2. probar cada GPIO sin actuador,
3. integrar caudalimetro,
4. solo despues habilitar actuadores reales fuera de `DRY_RUN`.

