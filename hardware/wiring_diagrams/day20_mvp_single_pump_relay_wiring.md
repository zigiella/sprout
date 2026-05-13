# Dia 20-23 - MVP una linea: bomba 12V, rele y humedad real

**Objetivo:** documentar el montaje fisico validado del MVP reducido: una unica
linea de riego con bomba 12V, rele, fusible, diodo flyback y un sensor de
humedad capacitivo.

Alcance fisico validado:

```text
Deposito -> bomba 12V sumergida -> tubo -> planta/parcela A
```

Alcance electrico validado:

- fuente 12V DC exterior,
- fusible en positivo de 12V,
- modulo rele de 1 canal, contacto `COM/NO`,
- bomba 12V,
- diodo flyback en paralelo con bomba,
- ESP32-S3 alimentado por USB,
- rele alimentado desde `3V3` del ESP32 para evitar ambiguedad de nivel logico,
- sensor capacitivo de humedad en `GPIO4`.

El caudalimetro queda fisicamente disponible, pero no es bloqueante para el MVP
actual.

## 0. Barandilla

No manipular el cableado con la fuente 12V enchufada.

Antes de energizar:

- inspeccion visual del cableado,
- continuidad sin cortos entre `+12V` y `GND`,
- fusible colocado en el positivo de 12V,
- contacto del rele en `COM` + `NO`, nunca `NC`,
- orientacion del diodo flyback confirmada,
- fuente 12V desconectada mientras se cambian cables,
- ESP32 en `SAFE_IDLE`,
- `WATER` sigue en `DRY_RUN`; los comandos `PUMP_*` son solo `TEST_ONLY`.

El ESP32 **no alimenta la bomba**. Solo alimenta y controla el modulo rele de
laboratorio desde `3V3` para esta prueba MVP.

## 1. Componentes usados

| Pieza | Uso | Estado |
|---|---|---|
| Fuente 12V DC exterior | Alimenta la bomba | Validada |
| Fusible 1A | Protege la rama de 12V | Validado en prueba MVP |
| Portafusible | En positivo de 12V, cerca de la fuente | Validado |
| Modulo rele 1 canal `JQC3F-05VDC-C` | Conmuta el positivo de la bomba | Validado a `3V3` |
| Bomba 12V sumergible | Actuador unico del MVP | Validada con agua |
| Diodo 1N400x | Flyback en paralelo con bomba | Validado visualmente |
| ESP32-S3 N16R8 | Control logico | Validado |
| DFRobot capacitive soil moisture sensor v2.0 | Humedad de suelo | Validado en `GPIO4` |

Nota sobre fusible: `1A` funciono en la prueba real. Si saltara por pico de
arranque de la bomba, revisar consumo nominal y cableado antes de subir valor.
No sustituirlo por un valor mayor "a ciegas".

## 2. Esquema electrico completo

```text
                             DOMINIO 12V

          Fuente 12V +
              |
              | rojo
              v
        [FUSIBLE 1A]
              |
              | +12V_PROTEGIDO
              v
        Rele canal 1 COM
        Rele canal 1 NO
              |
              | +12V conmutado
              v
          Bomba +
          Bomba -
              |
              v
          Fuente 12V -


        Diodo flyback en paralelo con la bomba:

          Bomba + ----|<|---- Bomba -
                    raya
                    del diodo
                    hacia Bomba +


                             DOMINIO ESP32 / LOGICA

          ESP32 3V3  ------------------> Rele VCC
          ESP32 GND  ------------------> Rele GND
          ESP32 GPIO16 ----------------> Rele IN

          ESP32 3V3  ------------------> Sensor humedad VCC / rojo
          ESP32 GND  ------------------> Sensor humedad GND / negro
          ESP32 GPIO4 -----------------> Sensor humedad AO / amarillo
```

El modulo de rele probado es **active-low**:

- `GPIO16 = HIGH` -> rele apagado -> `COM/NO` abierto -> bomba OFF.
- `GPIO16 = LOW` -> rele activado -> `COM/NO` cerrado -> bomba ON.

## 3. Conexion de potencia, cable a cable

| Desde | Hasta | Cable / nota |
|---|---|---|
| Fuente 12V `+` | Entrada portafusible | Rojo, fuente desconectada. |
| Salida portafusible | Rele canal 1 `COM` | Rojo, `+12V_PROTEGIDO`. |
| Rele canal 1 `NO` | Bomba `+` | Rojo, positivo conmutado. |
| Bomba `-` | Fuente 12V `-` | Negro, retorno de bomba. |
| Diodo lado con raya | Bomba `+` | Flyback, catodo. |
| Diodo lado sin raya | Bomba `-` | Flyback, anodo. |

No usar `NC`. Queremos que la bomba este apagada por defecto si el rele no esta
activado.

## 4. Conexion ESP32 -> rele

| Desde | Hasta | Nota |
|---|---|---|
| ESP32 `3V3` | Rele `VCC` | Alimentacion MVP validada para este modulo. |
| ESP32 `GND` | Rele `GND` | Referencia comun logica. |
| ESP32 `GPIO16` | Rele `IN` | Control active-low. |

Por que no usamos el buck 5V en el MVP actual:

- con rele alimentado a `5V`, el `HIGH` de `3.3V` del ESP32 podia dejar la
  entrada `IN` en zona ambigua;
- alimentando el modulo desde `3V3`, `HIGH` apaga limpio y `LOW` enciende;
- la bobina nominal de 5V del modulo probado conmuto correctamente a `3V3`.

Esta decision es de banco/MVP. Para una version mas robusta se recomienda un
driver dedicado, MOSFET, rele compatible 3.3V real o modulo con aislamiento
`JD-VCC/VCC` correctamente documentado.

## 5. Conexion del sensor de humedad

Sensor: `DFRobot Capacitive Soil Moisture Sensor v2.0`.

| Desde | Hasta |
|---|---|
| ESP32 `3V3` | Sensor rojo / VCC |
| ESP32 `GND` | Sensor negro / GND |
| ESP32 `GPIO4` | Sensor amarillo / AO |

Lectura provisional:

- valor ADC alto -> tierra mas seca,
- valor ADC bajo -> tierra mas humeda.

Calibracion empirica de banco:

| Situacion | `soil_a_raw` aprox. |
|---|---:|
| Aire | 3530-3540 |
| Tierra seca | 2319-2325 |
| Tierra antes de riego real | 2278 |
| Humedad buena tras difusion | 1687-1702 |
| Muy humedo / no regar | 1208-1291 |

Umbrales provisionales para razonamiento:

| Rango | Lectura |
|---|---|
| `>= 2200` | seco; candidato a riego si pasan las demas barandillas |
| `1300-2199` | zona intermedia; observar/defer, no riego autonomo |
| `< 1300` | muy humedo, no regar mas |

Estos umbrales son de demo y deben recalibrarse con maceta, sustrato y posicion
final del sensor.

## 6. Comandos de firmware usados

`WATER` continua siendo la ruta contractual con safety en `DRY_RUN`. Para el
bring-up fisico de banco se usan comandos explicitos de prueba:

```text
PUMP_OFF
PUMP_STATUS
PUMP_PULSE <ms>
SOIL_READ
TELEMETRY
```

`PUMP_PULSE` es `TEST_ONLY` y esta limitado por firmware con
`CONFIG_SPROUT_PUMP_TEST_MAX_MS`.

## 7. Evidencia validada

### 7.1 Rele y bomba

Secuencias probadas:

```text
PUMP_PULSE 1000
PUMP_PULSE 2000
PUMP_PULSE 3000
PUMP_PULSE 15000
descanso 5000 ms
PUMP_PULSE 10000
```

El firmware devolvio siempre:

```text
final_gpio_level=1 final_state=OFF execution=TEST_ONLY
```

### 7.2 Riego real y humedad

Con manguera cebada:

```text
SOIL_READ
SOIL_REPORT soil_a_raw=2278 ...

PUMP_PULSE 15000
descanso 5s
PUMP_PULSE 10000

SOIL_READ
SOIL_REPORT soil_a_raw=2280 ...
```

Tras esperar a que el agua alcanzara el sensor:

```text
SOIL_READ
SOIL_REPORT soil_a_raw=1291 ...
SOIL_REPORT soil_a_raw=1289 ...
SOIL_REPORT soil_a_raw=1289 ...
```

Conclusion: el sistema ya tiene evidencia real de:

- bomba fisica controlada por ESP32,
- retorno seguro a OFF,
- sensor de humedad real respondiendo al riego,
- descenso coherente de `soil_a_raw` cuando el agua llega a la sonda.

## 8. Reglas para Endodermis / Jetson

Endodermis puede probar la ruta desde Jetson **solo si** se cumplen estas
condiciones:

- Bea confirma que hay agua suficiente y la bomba esta sumergida.
- Bea confirma que no hay electronica en zona de salpicaduras.
- La primera prueba desde Jetson debe empezar con `PUMP_STATUS` y `SOIL_READ`.
- No ejecutar pulsos mayores de `3000 ms` sin Bea delante.
- Entre pulsos, esperar al menos `5 s` y comprobar `PUMP_STATUS`.
- Tras cualquier prueba, enviar `PUMP_OFF` y verificar `state=OFF`.
- Si `soil_a_raw < 1300`, no regar mas: el sustrato ya esta muy humedo.

Secuencia segura inicial para Endo sin riego:

```text
PUMP_STATUS
SOIL_READ
TELEMETRY
PUMP_OFF
PUMP_STATUS
```

Escenario equivalente:

```bash
python hardware/host_tools/esp32_host_harness.py --port /dev/ttyACM0 --scenario pump_soil_observe_only --label endo_observe
```

Secuencia con pulso minimo, solo si `soil_a_raw >= 1300`:

```text
PUMP_STATUS
SOIL_READ
PUMP_PULSE 1000
PUMP_STATUS
SOIL_READ
PUMP_OFF
PUMP_STATUS
```

Escenario equivalente:

```bash
python hardware/host_tools/esp32_host_harness.py --port /dev/ttyACM0 --scenario pump_soil_smoke --label endo_smoke
```

## 9. Decision MVP

Las electrovalvulas quedan fuera de MVP. La semantica visible del sistema se
mantiene como `WATER A`, pero fisicamente solo existe una linea de riego:

```text
PUMP_ON -> agua hacia parcela A
PUMP_OFF -> sin riego
```

`WATER B` y `WATER BOTH` pueden seguir rechazandose o mantenerse como rutas no
montadas hasta que vuelva el diseno de dos parcelas.
