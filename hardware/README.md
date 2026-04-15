# hardware/

Integracion fisica del proyecto: firmware ESP32, diagramas de cableado, fotos de montaje.

## Estructura

- `firmware_esp32/` — codigo Arduino/PlatformIO de la capa dura de seguridad
- `wiring_diagrams/` — esquematicos (Fritzing, KiCad o imagenes)
- `photos/` — fotos del montaje real en Castellar de n'Hug (evidencia + B-roll de video)

## Rol de la capa dura

El ESP32 es **la capa que la IA no puede saltarse**. Vive entre Rhizome (Jetson) y los actuadores (bomba, valvulas).

Reglas minimas del firmware:
- No regar si el deposito cae por debajo del minimo
- No regar si la bomba esta activa pero el caudalimetro no confirma paso de agua
- No superar duracion maxima por accion (seguro absoluto por tiempo)
- No ejecutar accion si el sistema esta en modo alerta fuerte
- Heartbeat obligatorio con Jetson, si se pierde bloqueo automatico

## Comunicacion Jetson <-> ESP32

- UART (9600 o 115200 baud) o I2C
- Protocolo simple: comandos + ACK + timeouts
- Cada comando lleva ID, duracion maxima, parcela objetivo

## Fotos obligatorias para el video

- Plano detalle del ESP32 + cableado
- Plano general del nodo completo
- Plano exterior con la terraza, pueblo al fondo
- Plano del caudalimetro midiendo en vivo
- Plano de la bomba parando cuando el ESP32 la corta
