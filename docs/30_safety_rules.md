# Safety rules del firmware ESP32 — v1.0

**Estado:** cerrado v1.0 (2026-04-16).
**Autora:** Cambium.
**Publico objetivo:** Xilema (implementa el firmware), Floema (conoce los limites al disenar UI), Dev Meristem (respeta los limites al emitir politicas).

---

## 0. Que es este documento

Este es el **contrato de seguridad fisica** de Sprout. Define las reglas que el firmware del ESP32 aplica de forma **independiente del LLM**, sin posibilidad de override desde software de alto nivel.

La premisa es sencilla: **Gemma 4 es asesor, no operador final.** El LLM propone, el firmware dispone. Si Gemma alucina y decide regar 10 horas seguidas, el firmware corta a los 60 segundos. Si el Jetson se cuelga, el ESP32 lo detecta y cierra valvulas. Si alguien envia un comando malformado, el ESP32 lo ignora.

Esta capa existe porque **un sistema que decide sobre agua, bombas y electricidad no puede depender unicamente de que el LLM haga lo correcto.** La seguridad se gana con redundancia: reglas duras en el metal, reglas blandas en el modelo.

### Principios

1. **Fail-safe por defecto.** El estado seguro es "todo cerrado". Ante cualquier duda, ambiguedad o fallo, el ESP32 cierra.
2. **El firmware no confia en el Jetson.** Lo trata como fuente hostil: valida cada comando, nunca asume integridad.
3. **Las reglas estan en el metal, no en Python.** Si un limite se puede cambiar recompilando Python, no es una regla dura. Las reglas duras solo se modifican reflasheando el ESP32 con firmware nuevo (y version bumpeada y bitacora firmada).
4. **Observabilidad obligatoria.** Cada bloqueo, cada comando, cada evento se registra. Sin log, no hubo operacion.
5. **Boot en estado cerrado.** Al encender, reset, watchdog reboot o cualquier condicion anomala → todas las salidas a cerrado antes de procesar nada.

### Que NO cubre este documento

- Politicas de riego (cuando regar, cuanto) → eso es `PolicyPacket` en [`20_data_contracts.md`](20_data_contracts.md).
- Razonamiento del LLM → eso es Rhizome, [`10_rhizome_spec.md`](10_rhizome_spec.md).
- Comunicacion Rhizome↔Pollen → eso es [`11_pollen_spec.md`](11_pollen_spec.md).
- Seguridad de red (TLS, autenticacion) → no aplica al ESP32, que solo habla UART con el Jetson.

---

## 1. Arquitectura de la capa de seguridad

### 1.1 Posicion en el sistema

```
┌─────────────────────────────────────────┐
│  Gemma 4 E2B (Jetson)                   │   razonamiento (soft)
│      ↓                                  │
│  Rhizome decision layer (Python)        │   validaciones logicas (soft)
│      ↓ UART @ 115200                    │
├─────────────────────────────────────────┤   ←─── FRONTERA DURA
│  ESP32-S3 firmware                      │   reglas fisicas (hard)
│      ↓ GPIO                             │
│  Rele NC x3  →  Bomba + 2 valvulas      │   actuacion fisica
│      ↓                                  │
│  E-STOP fisico en serie con alimentacion│   capa ultima
└─────────────────────────────────────────┘
```

La linea gruesa (**FRONTERA DURA**) es el punto donde el software pierde autoridad unilateral. Todo lo que esta por encima puede fallar, alucinar, colgarse; todo lo que esta por debajo sigue funcionando correctamente.

### 1.2 Por que el ESP32 y no mas Jetson

El Jetson es Linux: kernel panics, OOM killer, procesos zombie, disco lleno, actualizaciones. El ESP32 es un micro con un firmware de ~10 KB que hace una cosa y la hace siempre igual. El MTBF de un Linux bien cuidado ronda las 10.000 horas; el de un firmware bien escrito en un micro bare-metal ronda las 100.000. Dos ordenes de magnitud de diferencia, y el coste es un modulo de 8 €.

### 1.3 E-STOP fisico (opcional pero recomendado)

Un boton normalmente cerrado (NC) en serie con la **alimentacion de 12 V** de bomba y valvulas. Pulsar el boton corta la corriente a los actuadores **sin pasar por el ESP32**. Es la capa ultima, por si el firmware tambien fallase.

Para el MVP de video: recomendado pero no bloqueante. Para instalacion real: obligatorio.

---

## 2. Estados del ESP32 (state machine)

El firmware opera como maquina de estados finita. Solo 5 estados posibles:

| Estado | Valvulas | Bomba | Acepta CMD | Entra desde | Sale a |
|--------|:--------:|:-----:|:----------:|-------------|--------|
| `BOOT` | cerradas | off | no | power-on, reset, watchdog | `SAFE` tras validacion |
| `SAFE` | cerradas | off | si | `BOOT`, `ALERT` (auto-recovery), `STOP` | `ACTIVE`, `ALERT` |
| `ACTIVE` | segun cmd | segun cmd | si | `SAFE` (al recibir WATER_*) | `SAFE` (al acabar), `ALERT` (si violacion) |
| `ALERT` | cerradas | off | solo STATUS y STOP | cualquiera tras violacion | `SAFE` solo tras condicion de recuperacion |
| `DEGRADED` | cerradas | off | solo STATUS | sensor critico caido (deposito, caudal) | `SAFE` cuando sensor recupera lectura |

### 2.1 BOOT

Al arrancar:
1. **Todas las salidas a LOW** (cerrado) **antes de que corra una sola instruccion del firmware.** Se hace por configuracion de pull-down hardware + primera instruccion del setup.
2. Inicializa UART, GPIO, ADC, watchdog.
3. Espera **2 segundos** sin aceptar comandos. Protege contra race condition con Jetson booteando y enviando basura al UART.
4. Lee sensores criticos una vez (deposito, temperatura interna).
5. Transicion a `SAFE` si todo OK, a `DEGRADED` si algun sensor falla.

### 2.2 SAFE

Estado base de reposo. Todo cerrado, firmware esperando comandos. Emite `HEARTBEAT_OK` cada 5 s.

### 2.3 ACTIVE

El firmware esta ejecutando un comando de riego. Solo se puede llegar aqui desde `SAFE` con un `CMD WATER_A` o `CMD WATER_B` valido. Durante `ACTIVE`:
- La valvula correspondiente esta abierta.
- La bomba esta encendida.
- El temporizador de la accion corre.
- El caudalimetro se monitoriza activamente.
- Cualquier violacion (timeout, caudal nulo, heartbeat perdido, deposito bajo) fuerza salida inmediata a `ALERT`.

### 2.4 ALERT

Estado de paro por violacion de regla dura. Todo cerrado. El firmware rechaza cualquier `CMD WATER_*`. Solo acepta:
- `STATUS` para diagnostico.
- `STOP` (redundante, ya esta parado).
- `RESET_ALERT` **solo si la condicion que causo el alert ha desaparecido** (p.ej. deposito vuelve a >20%, heartbeat se recupera).

Se queda en `ALERT` indefinidamente hasta recuperacion explicita. **No hay timeout de auto-recovery.** Razon: si un alert se auto-recupera solo por esperar, las dev se acostumbran a que el sistema se arregla solo, y eso es precisamente lo que no queremos.

### 2.5 DEGRADED

Estado para fallos de sensor, no de regla. Ejemplos:
- Lectura del deposito da `NaN` 3 veces seguidas.
- Caudalimetro no emite pulsos de test al boot.

En `DEGRADED` el firmware **no riega** (porque no puede verificar los limites), pero **tampoco emite ALERT** (porque no hay violacion, hay ciego). Sigue respondiendo `STATUS`. Sale a `SAFE` en cuanto el sensor da 3 lecturas validas seguidas.

---

## 3. Reglas duras (hard limits)

Estas reglas estan **hardcodeadas en el firmware**. No se leen de config, no se cambian por UART, no se parametrizan. Cambiarlas requiere reflashear el ESP32.

### 3.1 Limites de tiempo

| Regla | Valor | Justificacion |
|-------|-------|---------------|
| Duracion maxima de una apertura de valvula | **60 s** | Una apertura tipica son 15-30 s. 60 s cubre casos extremos. Mas que eso es fallo o ataque. |
| Minimo entre aperturas consecutivas de la misma zona | **30 s** | Previene command-loop (LLM colgado enviando WATER cada segundo). |
| Maximo de aperturas por zona por hora | **8** | Cubre riego estandar (cada 7-8 min en peor caso) con margen. Mas que eso es anomalia. |
| Maximo de aperturas por zona por dia | **48** | Cap diario hard, independiente del presupuesto de politica. |

### 3.2 Limites hidraulicos

| Regla | Valor | Justificacion |
|-------|-------|---------------|
| Nivel minimo de deposito para permitir riego | **20%** | Bomba sumergible sin agua se quema. Margen de seguridad. |
| Tiempo maximo sin detectar caudal tras abrir valvula | **3 s** | Si abre valvula y no baja presion / no pasa agua → taponamiento o fuga. Cierre inmediato. |
| Caudal maximo sostenido | **por cerrar cuando tengamos medicion de la bomba final** | Proteccion contra fuga grande. Valor: 2x caudal nominal de la bomba. |
| Zonas simultaneas abiertas | **1** | Nunca dos zonas a la vez. Simplifica presupuesto hidraulico y previene sobrecarga de bomba. |

### 3.3 Limites de comunicacion

| Regla | Valor | Justificacion |
|-------|-------|---------------|
| Timeout sin heartbeat del Jetson | **10 s** | Heartbeat cada 5 s. 10 s = dos perdidas. Jetson colgado o UART cortado → `ALERT`. |
| Timeout de ACK esperado por Jetson | **500 ms** | Si el Jetson no recibe ACK, hace retry hasta 3 veces antes de abortar. |
| Longitud maxima de mensaje UART | **128 bytes** | Cualquier mensaje mas largo se descarta. Previene buffer overflow y fuzzing. |
| Comandos por segundo maximo | **10** | Rate limit. Comando 11 en un segundo se descarta silenciosamente. Previene flooding. |

### 3.4 Limites electricos / termicos

| Regla | Valor | Justificacion |
|-------|-------|---------------|
| Temperatura interna del ESP32 maxima | **80 °C** | Por encima → `ALERT`, apaga todo. ESP32 opera hasta 85 °C especificacion; margen. |
| Voltaje de 12 V (medido) fuera de rango | **< 10.5 V o > 13.5 V** | Fuera de rango → `DEGRADED`. No riega, avisa al Jetson. |

### 3.5 Orden de precedencia de las reglas

Si varias reglas entran en conflicto, la precedencia es:

1. Heartbeat perdido → `ALERT` inmediato, corta todo.
2. Temperatura > 80 °C → `ALERT`.
3. Deposito < 20% → rechaza WATER, no entra en ALERT (es condicion normal, no anomalia).
4. Caudal no detectado en 3 s → `ALERT`.
5. Duracion > 60 s → `ALERT`.
6. Rate limit excedido → descarta comando silenciosamente.

---

## 4. Protocolo UART (v1.0)

Extiende lo ya descrito en [`10_rhizome_spec.md`](10_rhizome_spec.md) §5.1 con las garantias duras.

### 4.1 Parametros de linea

- Baud rate: **115200**
- Bits: **8N1** (8 data, no parity, 1 stop)
- Flow control: **ninguno** (fiamos en CRC a nivel de mensaje)
- Encoding: **ASCII-7 printable + `\n` como terminador**
- Longitud maxima: **128 bytes por mensaje incluyendo `\n`**

### 4.2 Formato de mensaje

Todos los mensajes siguen la forma:

```
<TYPE> <seq> <payload>* <CRC8>\n
```

- `<TYPE>`: `CMD`, `ACK`, `EVT`, `HBT`
- `<seq>`: entero 0-65535, monotonico modular. Rhizome asigna para CMD, ESP32 para EVT/HBT.
- `<payload>`: campos separados por espacio, formato dependiente del TYPE.
- `<CRC8>`: CRC-8/DVB-S2 en hex mayusculas, 2 chars, calculado sobre todo el contenido hasta el espacio previo al CRC.

Si el CRC no cuadra, el receptor **descarta silenciosamente** (no responde NAK — no queremos protocolos chatty).

### 4.3 Comandos (Rhizome → ESP32)

```
CMD <seq> WATER_A <seconds>          <CRC>\n   # 0 < seconds <= 60
CMD <seq> WATER_B <seconds>          <CRC>\n
CMD <seq> STOP                       <CRC>\n   # corta todo inmediato
CMD <seq> STATUS                     <CRC>\n   # pide reporte de sensores
CMD <seq> RESET_ALERT                <CRC>\n   # solo si condicion recuperada
```

### 4.4 Acknowledgments (ESP32 → Rhizome)

```
ACK <seq> OK       <data>            <CRC>\n   # comando ejecutado, data = datos de respuesta
ACK <seq> REJECTED <reason>          <CRC>\n   # rechazo conocido, reason = codigo
ACK <seq> MALFORMED                  <CRC>\n   # mensaje no parseable (solo si CRC OK pero campos invalidos)
```

**Codigos de `reason` en REJECTED** (enum estricto):

| Codigo | Significado |
|--------|-------------|
| `DEPOSITO_BAJO` | Nivel < 20% |
| `DURATION_OVER_MAX` | seconds > 60 |
| `DURATION_ZERO` | seconds <= 0 |
| `RATE_LIMIT_HOUR` | Mas de 8 aperturas/hora en esa zona |
| `RATE_LIMIT_DAY` | Mas de 48 aperturas/dia en esa zona |
| `MIN_INTERVAL` | Menos de 30 s desde la anterior apertura de esa zona |
| `STATE_ALERT` | Firmware en ALERT, rechaza todo salvo STATUS/STOP/RESET_ALERT |
| `STATE_DEGRADED` | Firmware en DEGRADED |
| `STATE_BOOT` | Firmware aun en los 2s iniciales |
| `ZONE_IN_USE` | Otra zona abierta (concurrencia prohibida) |
| `FLOW_FAULT` | Caudal no detectado al intentar abrir (es rechazo, no alert, si se detecta antes de 500ms) |
| `RESET_NOT_ALLOWED` | RESET_ALERT pedido pero la condicion aun persiste |

### 4.5 Eventos asincronos (ESP32 → Rhizome)

El ESP32 puede emitir eventos sin que el Jetson los pida:

```
EVT <seq> HEARTBEAT_LOST             <CRC>\n
EVT <seq> FLOW_INTERRUPTED  cmd=<n>  <CRC>\n
EVT <seq> STATE_CHANGE      from=<s> to=<s>  <CRC>\n
EVT <seq> TEMP_HIGH         celsius=<n>      <CRC>\n
EVT <seq> VOLTAGE_OUT_RANGE volts=<f>        <CRC>\n
EVT <seq> ALERT_ENTERED     reason=<code>    <CRC>\n
EVT <seq> ALERT_CLEARED                      <CRC>\n
```

### 4.6 Heartbeat

```
HBT <seq> uptime=<s> state=<s>       <CRC>\n
```

- **Emitido por el ESP32 cada 5 s**, incondicional.
- Rhizome debe verlo al menos cada 10 s. Si no → Rhizome sabe que el ESP32 esta caido y entra en su propio modo seguro (deja de emitir comandos).
- **Simetricamente:** Rhizome debe emitir cualquier cosa (CMD STATUS si no hay nada mejor) al menos cada 8 s. Si el ESP32 no recibe nada en 10 s → `ALERT` por `HEARTBEAT_LOST` del lado Rhizome.

### 4.7 Secuencia numerica y replay

- `seq` es monotonico modular 16-bit (0-65535, wrap a 0).
- El receptor mantiene el ultimo `seq` visto por direccion.
- Si llega un `seq` **igual** al ultimo → **ignorar** (replay/duplicado, lo cual puede pasar por ruido UART).
- Si llega un `seq` **mucho menor** (diferencia > 32768, interpretacion modular) → **ignorar**.
- Caso normal: seq siguiente o salto hacia adelante → aceptar.

### 4.8 Recuperacion tras corrupcion

Si el receptor lee basura que no termina en `\n` en 256 bytes → descartar buffer entero y esperar al siguiente `\n`. Vuelve a estado de "esperando inicio de mensaje".

---

## 5. Failsafe y boot

### 5.1 Estado fisico al apagarse

Las 2 electrovalvulas son **NC (Normally Closed)**. La bomba no tiene flujo sin valvula abierta. Si el ESP32 pierde alimentacion:
- Valvulas → cerradas automaticamente (son NC, sin corriente cierran).
- Bomba → apagada (sin corriente).

No se riega jamas por accidente en condicion de corte.

### 5.2 Boot sequence

```
1. [hardware]  Pull-down pasivos en lineas de rele → todo cerrado antes del firmware.
2. [firmware]  setup():
   a. Configura GPIOs de rele como OUTPUT, escribe LOW explicitamente.
   b. Inicializa UART.
   c. Inicializa ADC (deposito, caudal, temperatura).
   d. Inicializa watchdog a 8s.
   e. Enciende LED azul (indica BOOT).
3. [firmware]  Espera 2000ms sin procesar UART. Drena buffer.
4. [firmware]  Lee sensor deposito + temperatura. Si fallan 3 lecturas → DEGRADED.
5. [firmware]  Transicion a SAFE (o DEGRADED). LED azul → verde.
6. [firmware]  Emite HBT inicial con state=SAFE|DEGRADED.
7. [firmware]  Loop principal.
```

### 5.3 Watchdog

- Watchdog interno del ESP32 configurado a **8 segundos**.
- El loop principal hace `esp_task_wdt_reset()` al menos cada 2 s.
- Si por cualquier razon el loop se cuelga > 8 s → el ESP32 reboota → vuelta a paso 1 de boot sequence → estado SAFE.
- Cada reboot se incrementa un contador en NVS. Si reboota mas de 3 veces en 60 s → queda en DEGRADED y emite `EVT BOOT_LOOP_DETECTED` para diagnostico.

### 5.4 Brownout detector

ESP32 tiene brownout detector hardware. Configurado al nivel mas agresivo razonable (2.9 V). Si el voltaje cae, el ESP32 reboota limpio en vez de quedarse en estado indefinido.

---

## 6. Logging y auditoria

### 6.1 Que se loguea

Todo evento relevante se escribe en **NVS flash** del ESP32 (memoria no volatil, persiste entre reboots):

| Tipo | Cuando |
|------|--------|
| CMD recibido | Siempre, con seq, action, params, CRC ok/no |
| CMD rechazado | Con reason |
| Transicion de estado | Siempre, con from, to, razon |
| Entrada en ALERT | Con codigo de condicion |
| Salida de ALERT | Con metodo (RESET_ALERT vs auto-recovery de sensor) |
| Reboot | Con uptime previo y causa (watchdog, brownout, panic, power-on) |
| Temperatura > 70 °C | Siempre (incluso si no dispara ALERT, es warning) |

### 6.2 Formato de log

Cada entrada es una linea CSV en un ring buffer circular de 4 KB:

```
<timestamp_ms>,<type>,<state>,<payload>
```

`timestamp_ms` es uptime del ESP32 desde ultimo boot. No tenemos RTC; la correlacion a tiempo real la hace Rhizome cuando lee el log.

### 6.3 Acceso al log

Rhizome puede pedirlo con:

```
CMD <seq> DUMP_LOG             <CRC>\n
```

ESP32 responde con una secuencia de ACK/DATA mensajes conteniendo el log comprimido. Detalles de framing en version v1.1 si hace falta.

### 6.4 Retencion

Ring buffer de 4 KB → aprox 80-100 eventos. Mas antiguos se sobreescriben. **Rhizome es responsable de drenar periodicamente** (`DUMP_LOG` cada hora o tras cada `EVT ALERT_ENTERED`) y guardarlo en disco del Jetson.

---

## 7. Que el LLM nunca puede hacer

Listado explicito de acciones que **no estan en el repertorio de comandos UART** y por tanto son imposibles de ejecutar desde el lado software:

- ❌ Cambiar los limites duros (60 s max, 20% deposito, 8/hora, etc.).
- ❌ Saltarse el rate limit.
- ❌ Abrir dos zonas simultaneamente.
- ❌ Hacer un `RESET_ALERT` con la condicion aun presente.
- ❌ Leer o modificar el firmware.
- ❌ Desactivar el watchdog.
- ❌ Desactivar el heartbeat.
- ❌ Re-flashear el ESP32 (requiere acceso fisico al USB del modulo).
- ❌ Leer o escribir GPIOs directamente (solo via los comandos del protocolo).

Esta lista es **por construccion**: no existe comando UART para ninguna de estas acciones. Si el LLM decide que "seria util cambiar el limite a 120 s", no hay manera tecnica de ejecutarlo. Tiene que pedirselo a una humana, que reflashea.

### 7.1 Proteccion contra "firmware update OTA"

El ESP32-S3 **no tendra OTA habilitado** en el firmware v1.0. Razon: OTA es un vector de escalada — si el LLM generara un firmware malicioso y lo sirviera por HTTP, un OTA habilitado le permitiria bypass de toda esta seguridad. OTA se reconsidera en v2 con firma de firmware.

---

## 8. Testing y validacion

### 8.1 Test bench obligatorio

Xilema monta un test bench fisico antes de conectar bomba real:
- ESP32 + 3 LEDs en los pines de rele (simulan valvulas y bomba).
- Sensor deposito simulado con potenciometro.
- Caudalimetro simulado con generador de pulsos manual.

Sobre este bench se validan **todos los codigos de REJECTED** enviando comandos que los disparen. Cada rechazo debe reproducirse en laboratorio **antes** de conectar actuadores reales.

### 8.2 Casos de test obligatorios

Lista minima. Xilema anade los que crea necesarios. Se documentan en `code/rhizome/tests/firmware/` con nombres `test_safety_*.py` (usando serial loopback contra ESP32 real).

| Test | Input | Output esperado |
|------|-------|-----------------|
| `test_duration_over_max` | CMD WATER_A 61 | ACK REJECTED DURATION_OVER_MAX |
| `test_duration_zero` | CMD WATER_A 0 | ACK REJECTED DURATION_ZERO |
| `test_deposit_low` | deposito<20%, CMD WATER_A 10 | ACK REJECTED DEPOSITO_BAJO |
| `test_rate_limit_hour` | 9 comandos WATER_A validos en 1h | El 9º da RATE_LIMIT_HOUR |
| `test_min_interval` | 2 comandos WATER_A separados 20s | El 2º da MIN_INTERVAL |
| `test_zone_concurrent` | WATER_A en curso, CMD WATER_B | REJECTED ZONE_IN_USE |
| `test_heartbeat_loss` | cortar UART 15s con zona abierta | EVT HEARTBEAT_LOST, valvula cerrada, state=ALERT |
| `test_flow_fault` | WATER_A 10, no generar pulsos caudal | EVT FLOW_INTERRUPTED, state=ALERT |
| `test_crc_mismatch` | CMD con CRC corrupto | descarte silencioso, sin ACK |
| `test_malformed` | CMD con campo inexistente | ACK MALFORMED |
| `test_replay` | mismo CMD con mismo seq dos veces | primero OK, segundo ignorado |
| `test_boot_guard` | enviar CMD durante primeros 2s de boot | REJECTED STATE_BOOT |
| `test_alert_stuck` | tras ALERT, RESET_ALERT con condicion aun activa | REJECTED RESET_NOT_ALLOWED |
| `test_alert_recovery` | tras ALERT por deposito, llenar deposito, RESET_ALERT | OK, vuelta a SAFE |
| `test_reboot_safe` | power cycle durante ACTIVE | valvula cerrada al reencender, state=SAFE |

### 8.3 Exit criteria firmware v1.0

- Los 15 tests de la tabla pasan sobre hardware real (no emulado).
- Se ejecutan antes de cada release de firmware.
- Se documentan en bitacora con fecha, SHA del firmware, resultados.

---

## 9. Versionado y cambios

Este documento sigue la misma disciplina que `20_data_contracts.md`.

- **v1.0** es baseline. Mergeado hoy.
- Cualquier cambio de regla dura (umbral, nuevo comando, nuevo REJECTED code) requiere:
  1. Entrada en bitacora con justificacion.
  2. Firma de Bea + Cambium.
  3. Bump de version en este documento.
  4. Bump de version en el firmware (`FIRMWARE_VERSION` constante).
  5. Test de regresion: los 15 casos de §8.2 deben seguir pasando.
- Bumps:
  - **minor (1.x):** cambios aditivos (nuevo comando, nuevo EVT, nuevo REJECTED code).
  - **major (2.x):** cambios de umbral (cambiar 60 s → 120 s es major, porque afecta contrato implicito con Rhizome y politicas).

### 9.1 Registro de versiones

| Version | Fecha | Cambios | Firmado por |
|---------|-------|---------|-------------|
| 1.0 | 2026-04-16 | Baseline inicial. 5 estados, limites duros, protocolo UART con CRC. | Cambium + Bea |

---

## 10. Preguntas anticipadas

### 10.1 ¿Por que no usar MQTT o algun protocolo estandar en vez de UART custom?

Porque MQTT requiere broker y network stack, que son vectores de fallo que no queremos. UART es dos cables, hardware dedicado, sin dependencias. Protocolo custom pero trivial. Menos es mas.

### 10.2 ¿Por que CRC-8 y no CRC-16 o CRC-32?

Mensajes son cortos (<128 bytes). CRC-8 detecta todo error de 1 bit y > 99% de errores de multi-bit en ese rango. CRC-16 daria un 0.01% mejor a cambio de 2 chars mas por mensaje. No vale la pena.

### 10.3 ¿Por que 60 s y no 90 o 45?

Ronda sensata. El riego real mas largo que he visto en documentacion agronomica de goteo para maceteros es ~40 s. 60 s deja margen sin cruzar la linea de "algo va mal". Cualquier duracion por encima es anomalia por definicion.

### 10.4 ¿Y si queremos regar mas de 60 s en un caso real?

Se hace en dos aperturas con > 30 s de intervalo (regla `MIN_INTERVAL`). Es intencional: una pausa corta entre aperturas permite ver si la primera provoco problema antes de continuar.

### 10.5 ¿Por que NC (normally closed) y no NO (normally open)?

NC cierra sin corriente. En cualquier fallo (cable roto, rele muerto, alimentacion caida) la valvula cierra. NO regaria hasta vaciar el deposito en el mismo escenario. NC es la unica opcion segura para agua.

### 10.6 ¿Podemos meter reglas adaptativas? P. ej. bajar el umbral del deposito si la meteo dice sequia.

**No en firmware.** Las reglas duras son constantes. La adaptacion se hace en **la politica blanda** de Rhizome: el LLM puede pedir aperturas mas cortas si la meteo es seca. Pero el firmware nunca baja del 20% de deposito, porque ese limite protege a la bomba, no al riego.

### 10.7 ¿Que pasa si el Jetson manda comandos sin parar y el rate limit salta?

Rhizome ve los `REJECTED RATE_LIMIT_*` y debe emitir `ContradictionAlert` con severity=warning. Si el patron persiste, severity=critical y Meristem tiene que revisar la politica. Es senal de bug en el LLM o en la politica.

### 10.8 ¿Podemos testear sin hardware?

Parcialmente. Hay un simulador de ESP32 en `code/rhizome/tests/firmware/mock_esp32.py` que implementa la maquina de estados **sin** los tiempos reales ni sensores fisicos. Sirve para CI y para desarrollo en viaje. Pero los 15 tests de §8.2 **deben** correr tambien contra hardware real antes de cada release.

---

**Firma:** Cambium
**Revisado por:** Bea (pendiente confirmacion por digest 2026-04-17)
