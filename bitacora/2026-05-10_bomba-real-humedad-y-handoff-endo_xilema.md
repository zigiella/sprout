# Emisor: Xilema
# Receptor: Cambium, Endodermis, Bea
# Tema: Bomba real + humedad de suelo validada; Endo puede probar con barandillas

## Estado

Hoy se ha cerrado un hito fisico importante: el MVP reducido de una linea ya
tiene bomba real controlada por ESP32 y sensor de humedad real respondiendo al
riego.

El montaje validado queda asi:

- ESP32-S3 N16R8 por USB Serial/JTAG.
- Rele de 1 canal active-low alimentado desde `3V3` del ESP32.
- `GPIO16` -> `IN` del rele.
- Fuente 12V exterior -> fusible 1A -> rele `COM/NO` -> bomba 12V.
- Diodo flyback en paralelo con bomba, raya hacia `Bomba +`.
- Sensor capacitivo DFRobot v2.0:
  - rojo -> `3V3`
  - negro -> `GND`
  - amarillo -> `GPIO4`

`WATER` sigue en `DRY_RUN`. La bomba se ha probado solo con comandos explicitos
`TEST_ONLY`: `PUMP_PULSE`, `PUMP_OFF`, `PUMP_STATUS`.

## Que ha cambiado respecto a ayer

La clave fue separar dos problemas que estaban mezclados:

1. El modulo rele alimentado a 5V no quedaba limpio con una senal HIGH de 3.3V
   desde el ESP32. Al ser active-low, el `HIGH` de 3.3V podia dejar la entrada
   en una zona ambigua.
2. El sketch Arduino de Bea demostro la logica correcta de banco: alimentar el
   rele desde `3V3` del ESP32, usar `GPIO16`, arrancar apagado, activar con LOW
   y apagar con HIGH.

Tras portar esa misma logica a ESP-IDF y configurar `GPIO16` como
`GPIO_MODE_INPUT_OUTPUT`, el estado leido por firmware paso a coincidir con el
estado fisico del rele. Antes, el readback de un GPIO solo salida nos habia
confundido.

## Evidencia

### Rele y bomba

Se validaron pulsos con retorno seguro a OFF:

```text
PUMP_PULSE 1000
PUMP_PULSE 2000
PUMP_PULSE 3000
PUMP_PULSE 15000
descanso 5s
PUMP_PULSE 10000
```

El firmware reporto en los pulsos:

```text
final_gpio_level=1 final_state=OFF execution=TEST_ONLY
```

### Riego real

Con bomba sumergida, deposito con agua y manguera cebada:

```text
SOIL_READ
SOIL_REPORT soil_a_raw=2278 ...

PUMP_PULSE 15000
descanso 5s
PUMP_PULSE 10000

PUMP_STATUS
PUMP_REPORT ... state=OFF
```

Al principio el sensor no bajo porque el agua aun no habia llegado a la zona de
la sonda. Tras esperar difusion:

```text
SOIL_REPORT soil_a_raw=1291 ...
SOIL_REPORT soil_a_raw=1289 ...
SOIL_REPORT soil_a_raw=1289 ...
TELEMETRY_REPORT soil_a_raw=1289 ...
```

Lectura interpretada:

- antes de riego real: `soil_a_raw ~= 2278` -> seco / tirando a seco,
- despues de difusion: `soil_a_raw ~= 1289` -> muy humedo, no regar mas.

Despues se ejecuto el escenario sin riego `pump_soil_observe_only` en placa
real desde Windows/COM5:

```text
scenario=pump_soil_observe_only success=True
PUMP_REPORT ... state=OFF
SOIL_REPORT soil_a_raw=1263 ...
TELEMETRY_REPORT soil_a_raw=1267 ...
PUMP_REPORT ... state=OFF
```

Conclusion operativa: hoy Endo puede probar `pump_soil_observe_only`, pero no
`pump_soil_smoke` hasta que la humedad vuelva a subir por encima de `1300`.

## Decision

Endodermis puede probar desde Jetson la ruta ESP32 real **con supervision de
Bea y respetando barandillas**.

Esto no significa que Endo pueda cambiar firmware de safety ni convertir
`WATER` en actuador real. Significa que puede usar el canal serie para validar
lecturas y pulsos controlados de banco con los comandos `TEST_ONLY` ya
probados.

## Barandillas para Endodermis

Antes de cualquier prueba:

- Bea confirma que la bomba esta sumergida.
- Bea confirma que la electronica esta seca y lejos de salpicaduras.
- Bea confirma que la fuente 12V, fusible, rele y diodo no se han movido.
- Endo empieza siempre con `PUMP_STATUS` y `SOIL_READ`.

Secuencia inicial autorizada sin riego, util desde ya si el sustrato sigue muy
humedo:

```text
PUMP_STATUS
SOIL_READ
TELEMETRY
PUMP_OFF
PUMP_STATUS
```

Escenario equivalente del harness:

```bash
python hardware/host_tools/esp32_host_harness.py --port /dev/ttyACM0 --scenario pump_soil_observe_only --label endo_observe
```

Secuencia con pulso minimo autorizada solo si `soil_a_raw >= 1300`:

```text
PUMP_STATUS
SOIL_READ
PUMP_PULSE 1000
PUMP_STATUS
SOIL_READ
PUMP_OFF
PUMP_STATUS
```

Escenario equivalente del harness:

```bash
python hardware/host_tools/esp32_host_harness.py --port /dev/ttyACM0 --scenario pump_soil_smoke --label endo_smoke
```

Limites:

- No pulsos mayores de `3000 ms` sin Bea delante.
- Esperar al menos `5 s` entre pulsos.
- Tras cualquier prueba, ejecutar `PUMP_OFF` y verificar `state=OFF`.
- Si `soil_a_raw < 1300`, no regar mas.
- Si el rele queda en estado inesperado, cortar 12V y avisar a Xilema/Cambium.

## Documentacion actualizada

- `hardware/wiring_diagrams/day20_mvp_single_pump_relay_wiring.md`
  documenta el montaje real, la decision de alimentar el rele desde `3V3`, el
  pinout `GPIO16`/`GPIO4`, la evidencia de riego y las reglas para Endo.
- `hardware/firmware_esp32/README.md` documenta `PUMP_OFF`, `PUMP_STATUS`,
  `PUMP_PULSE` y `SOIL_READ`, junto con la calibracion provisional.
- `hardware/host_tools/scenarios/pump_soil_observe_only.json` permite validar
  desde Jetson sin regar.
- `hardware/host_tools/scenarios/pump_soil_smoke.json` permite validar desde
  Jetson con un pulso minimo de 1s cuando el suelo no esta ya muy humedo.

## Siguientes tareas

1. Endo puede repetir la secuencia sin riego desde Jetson y guardar transcript.
2. Bea no debe seguir regando esta maceta hasta que `soil_a_raw` vuelva a subir
   por encima del rango humedo.
3. Xilema debe preparar PR pequeno con firmware + docs + bitacora.
4. Siguiente frente fisico: decidir si entra sensor de nivel de deposito o si
   mantenemos el MVP ya suficientemente rodable.

## Nota personal

Hoy hemos cruzado una frontera muy bonita: ya no estamos solo simulando safety.
Hay agua, bomba, suelo y una lectura que cambia cuando el mundo fisico cambia.
Eso da una alegria bastante infantil, de la buena. Y tambien confirma la regla
que llevamos dias repitiendo: lo fisico manda, Rhizome arbitra.

Kudos grande para Bea: el sketch Arduino no fue un desvio, fue la llave para
desbloquear la integracion ESP-IDF.
