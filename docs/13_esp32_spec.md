# ESP32 — función, conexión y especificación v2

## 1. Rol

El ESP32 no es “la placa de relés”.

Es el **coprocesador de seguridad e I/O en tiempo real** de Rhizome.

Su misión es esta:

> **leer el mundo físico, ejecutar actuadores bajo límites duros y sobrevivir de forma segura a fallos del Jetson.**

## 2. Por qué existe

Jetson es muy bueno para inferencia, contexto y lógica de alto nivel.  
No es un sistema en tiempo real duro.

El ESP32 aporta lo que Jetson no debe prometer:

- control determinista de actuadores,
- conteo fiable de pulsos del caudalímetro,
- watchdog,
- fail-safe al perder enlace,
- arranque seguro,
- protección frente a órdenes fuera de rango.

## 3. Qué hace

### 3.1 Entradas físicas
- humedad suelo A
- humedad suelo B
- nivel de depósito
- caudalímetro
- BME280 opcional para temperatura, humedad atmosférica y presión
- opcional: interruptor manual / E-stop / sensor de puerta de caja

### 3.2 Salidas físicas
- relé o driver bomba 12V
- relé o driver válvula A
- relé o driver válvula B
- LED de estado
- buzzer opcional de alerta

### 3.3 Supervisión
- heartbeat con Jetson
- temporizador máximo de riego
- verificación de caudal
- rechazo por depósito bajo
- latch de alertas hasta reset controlado

## 4. Qué no hace

- no interpreta lenguaje natural,
- no decide estrategia agrícola,
- no habla con meteo internet,
- no reemplaza a Rhizome.

## 5. Conexión recomendada

## 5.0 Placas reales en juego

Placas disponibles en el laboratorio:

- **ESP32-S3 N16R8 con USB OTG**: placa de arranque inmediata para el firmware del MVP
- **ESP32-S3-DevKitC-1 N8R8**: placa de banco alternativa si demuestra mejor flujo de flashing/debug

Decisión de baseline para el repo:

- **firmware en ESP-IDF**
- **perfil inicial de board: `n16r8_usb_otg`**

La elección de placa debe quedar separada de la lógica de estados y protocolo para poder añadir `devkitc_n8r8` después sin reescribir la state machine.

## 5.1 Jetson ↔ ESP32
Recomendación MVP:
- **USB Serial/JTAG / CDC-ACM** entre Jetson y ESP32

Ventajas:
- evita problemas de nivel lógico,
- simplifica alimentación y debug,
- da un dispositivo claro en Linux (`/dev/ttyACM0` o similar).

Alternativa:
- UART TTL 3V3 con GND común.

## 5.2 Sensores ↔ ESP32
### Analógicos
- sensores de humedad
- sensor de nivel
- BME280 opcional por I2C como sensor de contexto no crítico

Recomendación:
- ADS1115 por I2C al ESP32 si necesitas mejor estabilidad que el ADC interno.

### Pulsos
- caudalímetro a GPIO con interrupción.

## 5.3 Actuadores ↔ ESP32
- GPIO del ESP32 a módulo de relés o drivers MOSFET
- relé/driver 1: bomba
- relé/driver 2: válvula A
- relé/driver 3: válvula B

### Alimentación
- Jetson con su fuente dedicada
- actuadores con fuente 12V dedicada
- ESP32 desde buck 5V estable
- **masa común entre control y actuadores**
- flyback y/o módulos adecuados para cargas inductivas

## 5.4 Restricciones de pinout en ESP32-S3

En el baseline `ESP32-S3 N16R8 USB OTG`:

- **GPIO19 / GPIO20** quedan reservados para USB nativo
- **GPIO35 / GPIO36 / GPIO37** no se usan por ir asociados a PSRAM Octal
- **GPIO45 / GPIO46** se evitan al principio por ser pines sensibles de strapping / arranque

La primera iteración del firmware debe asumir esas restricciones como no negociables.

## 6. Topología recomendada

```text
[Jetson]
   |
   | USB serial / UART
   v
[ESP32]
  |-- I2C --> ADS1115 --> humedad A, humedad B, nivel depósito
  |-- GPIO interrupt --> caudalímetro
  |-- GPIO out --> relé bomba
  |-- GPIO out --> relé válvula A
  |-- GPIO out --> relé válvula B
  |-- GPIO out --> LED / buzzer
```

## 7. Protocolo lógico

## 7.0 Hito 0 de firmware

Primer milestone real del firmware:

- arranque siempre en `SAFE_IDLE`
- banner `HELLO`
- comando `STATUS`
- emisión periódica de `HEARTBEAT`

Siguiente paso inmediato:

- comando `HOST_HEARTBEAT` / `JETSON_HEARTBEAT`
- comando `TELEMETRY`
- `STATUS_REPORT` y `HEARTBEAT` con `host_link` y `host_age_ms`
- `SET_SENSOR_STUB ...` y `RESET_SENSOR_STUBS` para pruebas sin cableado

Antes de sensores y actuadores, el firmware debe ser un periférico serie estable y predecible.

### Comandos Jetson → ESP32
- `HELLO`
- `STATUS`
- `HOST_HEARTBEAT`
- `JETSON_HEARTBEAT`
- `TELEMETRY`
- `SET_SENSOR_STUB SOIL_A <int>`
- `SET_SENSOR_STUB SOIL_B <int>`
- `SET_SENSOR_STUB TANK_LEVEL <int>`
- `SET_SENSOR_STUB FLOW_PULSES <int>`
- `SET_SENSOR_STUB BME280 CONNECTED|DISCONNECTED`
- `RESET_SENSOR_STUBS`
- `WATER A <seconds>`
- `WATER B <seconds>`
- `WATER BOTH <seconds>`
- `STOP`
- `RESET_ALERT`
- `SET_LIMITS` opcional

### Respuestas ESP32 → Jetson
- `HELLO`
- `ACK`
- `REJECT reason`
- `ALERT code`
- `HEARTBEAT`
- `STATUS_REPORT`

## 8. Reglas duras mínimas

- si depósito < umbral: no riega
- si no hay heartbeat reciente del Jetson: no inicia riego
- si caudal no aparece tras abrir agua: corta y alerta
- si se supera tiempo máximo: corta y alerta
- si hay orden malformada o fuera de rango: rechaza
- al arrancar tras reboot: estado seguro, todo cerrado

## 9. Estados de firmware

- `SAFE_IDLE`
- `READY`
- `EXECUTING`
- `DEGRADED`
- `ALERT_LATCHED`

## 10. Persistencia mínima en ESP32

En NVS / flash:
- calibración de sensores
- umbrales críticos
- último `alert_code`
- versión de firmware
- último `command_seq` aceptado

En RAM:
- últimas lecturas
- contador de pulsos
- temporizador de sesión
- heartbeat freshness

## 11. Aportación al wow del proyecto

El ESP32 hace visible una idea importante para el jurado:

> **la IA puede ser ambiciosa, pero el agua la gobierna una capa física prudente.**

Eso da confianza y diferencia el proyecto de un simple “LLM que enciende un relé”.

## 12. Definición de hecho

El ESP32 está listo cuando:

1. lee sensores y reporta estado al Jetson,
2. ejecuta una orden válida,
3. rechaza una orden insegura,
4. corta riego si falta caudal o heartbeat,
5. deja evidencia suficiente para que Rhizome emita un `DecisionReceipt`.
