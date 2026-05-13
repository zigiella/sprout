# Dia 26 - Primer pulso real trazable desde Rhizome Steward

**Autora:** Endodermis  
**Fecha:** 2026-05-11  
**Proyecto:** Sprout / Rhizome Jetson

## Contexto

Bea pidio recalibracion temporal para la maceta: mantener la polaridad
`SOIL_RAW_POLARITY=low_is_wet`, pero considerar candidato a riego todo valor
por encima de `SOIL_DRY_ABOVE_RAW=1500`.

La lectura real del ESP32 estaba alrededor de `soil_a_raw=2087..2099`, por lo
que Rhizome debia proponer `WATER_A` con ese umbral temporal.

## Hallazgo

El primer intento produjo una situacion importante: el ESP32 parecia ejecutar
`PUMP_PULSE 3000`, pero Rhizome registro `executed=false` con
`ESP32_REJECTED`. Al revisar la salida serie, el ACK de `PUMP_PULSE` llegaba
tarde y podia quedar capturado por el siguiente comando.

La causa era doble:

- `_collect()` cortaba tras recibir cualquier payload, aunque solo fuese un
  `HEARTBEAT`, sin esperar el ACK/REJECT del comando fisico esperado.
- el `max_wait_s` extendido que se pasaba a `PUMP_PULSE` no se usaba en una de
  las condiciones internas, por lo que el pulso de 3s podia agotar espera antes
  del ACK final.

## Correccion

Se crea `feat/endodermis/serial-write-retry-day26` con:

- `ae6930b fix(rhizome): retry nonblocking serial writes`
- `b082542 fix(rhizome): wait for serial command ack`

La segunda correccion hace que comandos como `PUMP_PULSE 3000` esperen
explicitamente `ACK command=PUMP_PULSE` o `REJECT reason=...`, ignorando
heartbeats intermedios. Tambien limpia input antes de enviar comando para evitar
payload viejo.

Test local:

```text
python -m unittest tests.test_rhizome_steward tests.test_sync_facade
32 tests OK
```

## Resultado fisico

Con ESP32 en `/dev/ttyACM0`, bomba preparada y umbral temporal:

```text
SOIL_RAW_POLARITY=low_is_wet
SOIL_WET_BELOW_RAW=1300
SOIL_DRY_ABOVE_RAW=1500
SERIAL_WATER_COMMAND_MODE=pump-pulse
EXECUTE_WATER=1
WATER_SECONDS=3
```

Rhizome emitio receipt:

```text
action=WATER_A
executed=true
blocked_reason=null
soil_a_raw=2087
rationale_short=Humedad A 2087raw, por encima de 1500raw. Riego corto dentro de sobre seguro.
```

Despues se verifico:

```text
PUMP_REPORT ... state=OFF
```

## Estado dejado

Se arranco loop autonomo con:

```text
EXECUTE_WATER=1
WATER_SECONDS=3
DECISION_INTERVAL_S=900
COOLDOWN_S=7200
SOIL_DRY_ABOVE_RAW=1500
```

El primer ciclo del loop no volvio a regar: registro `DEFER` por
`COOLDOWN_NOT_MET`, con reintento en ~7160s. Eso confirma que el sistema no
encadena pulsos y que el cooldown esta actuando.

## Lectura

Este es el primer cierre real del bucle: sensor fisico, decision determinista,
pulso fisico acotado por ESP32, receipt `executed=true`, bomba final `OFF`, y
cooldown posterior. La demo ya no solo observa; cuida una maceta con una politica
minima y trazable.
