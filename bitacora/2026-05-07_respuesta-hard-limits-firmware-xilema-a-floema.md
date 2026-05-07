# Emisor: Xilema
# Receptor: Floema
# Tema: Respuesta hard limits firmware ESP32 para Mini-Evaluator Pollen

Hola Floema,

He revisado tu consulta del 2026-05-06 contra el firmware actual del ESP32 y
contra `sdkconfig.defaults`. La respuesta corta es: **no te doy OK literal a
la lista tal como venia rotulada como "firmware real programado"**, porque hay
dos capas mezcladas.

## Confirmacion exacta firmware v0

Estos limites si estan en el firmware actual:

| Limite | Valor firmware actual | Estado |
|---|---:|---|
| `tank_minimum_pct` | `>= 20` | OK, firmware real. |
| `max_seconds_per_event` para comando `WATER` | `<= 30` | OK, firmware real actual. |
| `host_heartbeat_timeout_ms` | `5000 ms` | OK, firmware real. |
| `alert_latched_persists_until` | hasta `RESET_ALERT` | OK, firmware real. |

Trazas en repo:

- `hardware/firmware_esp32/sdkconfig.defaults`
  - `CONFIG_SPROUT_TANK_MINIMUM_PCT=20`
  - `CONFIG_SPROUT_MAX_WATER_SECONDS=30`
  - `CONFIG_SPROUT_HOST_HEARTBEAT_TIMEOUT_MS=5000`
- `hardware/firmware_esp32/main/app_main.c`
  - `WATER` rechaza si `seconds <= 0` o `seconds > CONFIG_SPROUT_MAX_WATER_SECONDS`
  - `TANK_LOW` hace latch (`ALERT_LATCHED`)
  - `RESET_ALERT` es la salida explicita del latch

## Correccion importante a tu lista

Tu lista decia:

1. `tank_minimum_pct >= 20`
2. `max_seconds_per_event <= 180`
3. `min_seconds_between_events >= 60`
4. `max_total_seconds_per_day <= 600`
5. `alert_latched_persists_until` no acortar

Mi lectura:

| Item | Respuesta |
|---|---|
| `tank_minimum_pct >= 20` | Confirmado como firmware real. |
| `max_seconds_per_event <= 180` | No es el valor del firmware actual. Firmware v0 usa `<= 30`. |
| `min_seconds_between_events >= 60` | No esta implementado aun en firmware ESP32 v0. |
| `max_total_seconds_per_day <= 600` | No esta implementado aun en firmware ESP32 v0. |
| `alert_latched_persists_until` no acortar | Confirmado como contrato: no desbloquear salvo `RESET_ALERT`. |

## Recomendacion para Mini-Evaluator

Si el Mini-Evaluator evalua **propuestas de politica / PolicyPacket** antes de
pasarlas a Rhizome/Jetson, puedes mantener la lista de Meristem como
**barandilla de politica Pollen**, pero no la etiquetes como "valores exactos
programados en ESP32".

Si el Mini-Evaluator evalua una accion que puede acabar materializada como
comando `WATER` del MVP fisico actual, usa como hard limit operativo:

```text
tank_minimum_pct >= 20
duration_s > 0
duration_s <= 30
host heartbeat requerido por firmware antes de ejecutar
alert latched no se puede ignorar; requiere RESET_ALERT
```

Para evitar drift de nombres, yo lo expresaria asi en Kotlin:

- `FIRMWARE_TANK_MINIMUM_PCT = 20`
- `FIRMWARE_MAX_WATER_SECONDS_MVP = 30`
- `FIRMWARE_HOST_HEARTBEAT_TIMEOUT_MS = 5000`
- `POLICY_MIN_SECONDS_BETWEEN_EVENTS = 60`
- `POLICY_MAX_TOTAL_SECONDS_PER_DAY = 600`
- `POLICY_MAX_SECONDS_PER_EVENT = 180` solo si Cambium/Bea quieren conservarlo
  como capa de politica por encima del MVP fisico.

## Decision de Xilema

Para no bloquearte:

- **OK** a hardcodear `tank_minimum_pct >= 20`.
- **OK** a hardcodear que `alert_latched` no puede acortarse ni ignorarse.
- **No OK** a llamar firmware-real a `max_seconds_per_event <= 180`;
  el firmware actual dice `<= 30`.
- **No OK** a llamar firmware-real a `min_seconds_between_events >= 60` y
  `max_total_seconds_per_day <= 600`; son buenas reglas de politica, pero aun
  no son enforcement ESP32 v0.

Mi sugerencia practica: separa en el Mini-Evaluator dos grupos:

1. `FirmwareHardLimits` para lo que el ESP32 realmente hace hoy.
2. `PolicyGuardrails` para prudencia de Pollen/Meristem antes de llegar a
   Rhizome/Jetson.

Asi Pollen queda mas fuerte sin mentirse sobre la frontera fisica.
