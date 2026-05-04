# hardware/

Integracion fisica del proyecto: firmware ESP32, diagramas de cableado, fotos de montaje.

## Estructura

- `firmware_esp32/` — proyecto **ESP-IDF** de la capa dura de seguridad
- `host_tools/` — harness y utilidades host-side para hablar con el ESP32 por serie
- `wiring_diagrams/` — esquematicos de montaje (Markdown/Mermaid ahora; Fritzing, KiCad o imagenes despues)
- `photos/` — fotos del montaje real en Castellar de n'Hug (evidencia + B-roll de video)

### Baseline del firmware

- framework: **ESP-IDF**
- target: **ESP32-S3**
- board profile inicial: `n16r8_usb_otg`
- hito 0: `SAFE_IDLE + HELLO + STATUS + HEARTBEAT`

## Rol de la capa dura

El ESP32 es **la capa que la IA no puede saltarse**. Vive entre Rhizome (Jetson) y los actuadores (bomba, valvulas).

Reglas minimas del firmware:
- No regar si el deposito cae por debajo del minimo
- No regar si la bomba esta activa pero el caudalimetro no confirma paso de agua
- No superar duracion maxima por accion (seguro absoluto por tiempo)
- No ejecutar accion si el sistema esta en modo alerta fuerte
- Heartbeat obligatorio con Jetson, si se pierde bloqueo automatico

## Comunicacion Jetson <-> ESP32

- **USB Serial/JTAG / CDC-ACM** como baseline MVP
- UART 3V3 solo como fallback si el USB nativo da problemas
- Protocolo simple: `HELLO`, `STATUS`, `STATUS_REPORT`, `HEARTBEAT`, `REJECT`
- Cada comando lleva ID, duracion maxima, parcela objetivo

Para el primer milestone no hay control de agua todavia. Solo arranque seguro, consola serie y estado observable.

## Montaje fisico

La guia operativa vigente para empezar el cableado esta en:

- `wiring_diagrams/day19_mounting_schematics.md`

Regla: actuadores 12V solo despues de revisar fusible, driver, flyback, masa
comun y prueba sin carga. La escena de seguridad es rodable en `DRY_RUN`; el
agua real no se activa por prisa.

## Fotos obligatorias para el video

- Plano detalle del ESP32 + cableado
- Plano general del nodo completo
- Plano exterior con la terraza, pueblo al fondo
- Plano del caudalimetro midiendo en vivo
- Plano de la bomba parando cuando el ESP32 la corta
