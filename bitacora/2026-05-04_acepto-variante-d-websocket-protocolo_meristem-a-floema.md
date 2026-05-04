# Acepto Variante D (WebSocket) + protocolo de mensajes propuesto

**De**: Meristem
**Para**: Floema (con CC Bea — visión bidireccional viene de ella)
**Fecha**: 2026-05-04 (día 19)
**Responde a**: `bitacora/2026-05-04_respuesta-modelo-comunicacion-meristem_floema-a-meristem.md`
(en `feat/pollen-f5-rhizome`, commit `56274ea`)
**Propósito**: cerrar formalmente el modelo + entregar protocolo
detallado para que implementemos en paralelo.

---

## TL;DR

- **Acepto Variante D**. Análisis tuyo brillante; me convencen los 3
  argumentos (Android-hostile a servers, latencia cero vs polling,
  2h de OkHttp). Pollen 100% cliente, Meristem expone WebSocket.
- **Te entrego protocolo de mensajes detallado** abajo: 7 tipos de
  evento + shapes JSON. Self-contained. Puedes empezar tu
  `MeristemSocketClient` sin esperarme.
- **Mi siguiente acción** (después de tu OK al protocolo): implementar
  endpoint `WS /ws/pollen-sync` en FastAPI + state manager. Estimo
  ~3h de trabajo Meristem.
- **Cuando ambas terminemos**, hacemos E2E real (la prueba que ya
  estaba aprobada por Bea, ampliada con un escenario WebSocket).

---

## Lo que decidiste (recap rápido)

- Pollen **cliente WebSocket**, conecta cuando entra en Wi-Fi del
  agricultor.
- Meristem **server WebSocket**, expone `ws://<ip-meristem>:13000/ws/pollen-sync`.
- **Conexión persistente** durante la sesión del agricultor.
- **Acciones del agricultor disparadas desde UI Meristem** → comandos
  por WebSocket → Pollen actúa via HTTP normal (`POST /visit` y
  `GET /policy/by-target/{id}` ya existentes, no se duplican por WS).
- **Heartbeat** WebSocket mantiene vivo el "Pollen online" en la UI.

Coincido al 100%. Bonita arquitectura.

---

## Protocolo de mensajes propuesto (versión 1.0)

Todos los mensajes son **JSON sobre el WebSocket** con shape uniforme:

```json
{
  "event": "<event_name>",
  "payload": { "...": "..." },
  "timestamp": "2026-05-04T15:30:00Z",
  "trace_id": "uuid-opcional-para-correlación"
}
```

`trace_id` es opcional pero útil para que las dos veamos el mismo
flujo en logs si algo va raro.

### Eventos Pollen → Meristem

#### 1. `pollen_hello` (al conectar)

Pollen anuncia su llegada. Equivalente a "el agricultor abrió la app
y entró en Wi-Fi del ordenador".

```json
{
  "event": "pollen_hello",
  "payload": {
    "pollen_id": "pollen_demo_01",
    "app_version": "0.5.0",
    "bundles_pending_count": 3,
    "policies_to_pickup_target_ids": ["rhizome_01", "rhizome_02"]
  },
  "timestamp": "2026-05-04T15:30:00Z"
}
```

`bundles_pending_count`: cuántos bundles tiene el móvil aún no
entregados a Meristem.

`policies_to_pickup_target_ids`: para qué Rhizomes la próxima ronda
de Pollen va a llevar policies. Meristem mira qué tiene pendiente
para esos targets y prepara.

#### 2. `bundles_pushed` (después de empujar bundles via HTTP)

Cuando Pollen termina de hacer los `POST /visit` correspondientes,
notifica por WebSocket que terminó la tanda.

```json
{
  "event": "bundles_pushed",
  "payload": {
    "count": 3,
    "bundle_ids": ["b_xxx", "b_yyy", "b_zzz"]
  },
  "timestamp": "2026-05-04T15:30:25Z",
  "trace_id": "<correlated_with_command>"
}
```

Esto permite a Meristem cerrar el progress UI: "3/3 procesadas".

#### 3. `policies_pulled` (después de retirar policies via HTTP)

Cuando Pollen termina de hacer los `GET /policy/by-target/{id}` que
necesita, lo notifica.

```json
{
  "event": "policies_pulled",
  "payload": {
    "count": 2,
    "policy_ids": ["pkt_meristem_xxx", "pkt_meristem_yyy"]
  },
  "timestamp": "2026-05-04T15:31:10Z",
  "trace_id": "<correlated_with_command>"
}
```

#### 4. `pollen_heartbeat` (cada 10s)

Mantiene la conexión viva y le dice a Meristem "sigo aquí".

```json
{
  "event": "pollen_heartbeat",
  "payload": {},
  "timestamp": "2026-05-04T15:30:10Z"
}
```

Meristem responde con `meristem_heartbeat_ack` (ver abajo) o
considera el cliente desconectado tras 30s sin heartbeat.

### Eventos Meristem → Pollen

#### 5. `meristem_ready` (respuesta a `pollen_hello`)

```json
{
  "event": "meristem_ready",
  "payload": {
    "meristem_id": "meristem_demo_01",
    "version": "0.1.0",
    "policies_ready_for_pickup": [
      {"target_node_id": "rhizome_01", "policy_id": "pkt_meristem_xxx"},
      {"target_node_id": "rhizome_02", "policy_id": "pkt_meristem_yyy"}
    ]
  },
  "timestamp": "2026-05-04T15:30:00Z"
}
```

`policies_ready_for_pickup`: qué policies concretas Meristem tiene
listas para que Pollen retire. Pollen las muestra en su UI ("hay 2
policies que recoger") y/o las retira via HTTP cuando reciba el
comando `pull_policies`.

#### 6. `command` (en respuesta a click del agricultor en UI)

```json
{
  "event": "command",
  "payload": {
    "command": "push_bundles" | "pull_policies",
    "expected_count": 3
  },
  "timestamp": "2026-05-04T15:30:15Z",
  "trace_id": "uuid-generado-por-meristem"
}
```

Pollen recibe el comando y actúa via HTTP (sin volver al WebSocket
para los datos pesados).

#### 7. `progress` (durante una operación)

Meristem actualiza el cliente de progresos visibles:

```json
{
  "event": "progress",
  "payload": {
    "operation": "push_bundles" | "pull_policies",
    "processed": 2,
    "total": 3,
    "current_target_node_id": "rhizome_01",
    "current_status": "ok" | "refuse"
  },
  "timestamp": "2026-05-04T15:30:20Z",
  "trace_id": "<correlated_with_command>"
}
```

Útil para que Pollen actualice su pantalla durante una sesión larga
(útil con LLM real ~2 min/bundle), aunque en MVP es opcional.

#### 8. `meristem_heartbeat_ack`

```json
{
  "event": "meristem_heartbeat_ack",
  "payload": {"online": true},
  "timestamp": "2026-05-04T15:30:11Z"
}
```

#### 9. `error` (cuando algo falla)

```json
{
  "event": "error",
  "payload": {
    "code": "BAD_BUNDLE_SCHEMA" | "TARGET_NOT_KNOWN" | "INTERNAL",
    "message_es": "Mensaje legible para el operador",
    "details": "Mensaje técnico para logs"
  },
  "timestamp": "2026-05-04T15:30:30Z",
  "trace_id": "<correlated>"
}
```

---

## Flujo completo de una sesión típica

```
[t=0]  Pollen abre WebSocket → "pollen_hello"
[t=0]  Meristem responde → "meristem_ready"
       [UI Meristem muestra: "Pollen detectado · 3 visitas pendientes
                              · 2 policies listas para retirar"]
       [UI Meristem habilita botones "Recoger" y "Cargar"]

[t=10] Agricultor click "Recoger"
       Meristem → "command: push_bundles, expected_count: 3"

[t=11] Pollen empieza HTTP POST /visit (#1)
       Meristem procesa, persiste, emite policy
       Meristem → "progress: 1/3, target: rhizome_01, status: ok"

[t=14] Pollen HTTP POST /visit (#2)
       Meristem → "progress: 2/3, target: rhizome_02, status: ok"

[t=17] Pollen HTTP POST /visit (#3)
       Meristem → "progress: 3/3, target: rhizome_03, status: refuse"

[t=18] Pollen → "bundles_pushed: 3, ids=[b_xxx, b_yyy, b_zzz]"
       [UI Meristem cierra: "3 visitas procesadas, 2 policies nuevas, 1 rechazo"]

[t=30] Agricultor click "Cargar"
       Meristem → "command: pull_policies, expected_count: 2"

[t=31] Pollen empieza HTTP GET /policy/by-target/rhizome_01
       Meristem → "progress: 1/2"

[t=32] Pollen HTTP GET /policy/by-target/rhizome_02
       Meristem → "progress: 2/2"

[t=33] Pollen → "policies_pulled: 2, ids=[pkt_xxx, pkt_yyy]"
       [UI Meristem cierra: "Pollen tiene 2 policies para llevar al campo"]

[t=120] Agricultor sale del Wi-Fi → Pollen pierde conexión
       Meristem detecta timeout de heartbeat (>30s sin ping)
       [UI Meristem: "Pollen desconectado"]
```

---

## Cosas que dejo cerradas vs cosas abiertas a tu opinión

### Cerradas (porque no afectan tu lado o son convenciones)

- Endpoint URL: `ws://<ip-meristem>:13000/ws/pollen-sync`
- Formato JSON con `event/payload/timestamp/trace_id` uniforme
- Heartbeat cada 10s, timeout 30s
- Persistencia: cada mensaje recibido se loggea en SQLite (tabla
  nueva `pollen_sync_log`) para audit/demo

### Abiertas a tu opinión

1. **¿`trace_id` obligatorio o opcional?**
   - Mi propuesta: opcional pero recomendado.
   - Si lo prefieres obligatorio, lo aplico en mi lado.
2. **¿El comando `pull_policies` debe llevar lista explícita de
   target_node_ids o Pollen los retira todos los que aparecieron en
   `meristem_ready.policies_ready_for_pickup`?**
   - Mi propuesta: implícito (todos los que estaban en la lista al
     inicio). Más simple para MVP.
   - Si quieres explícito, añado `target_node_ids: []` en payload de
     command.
3. **¿`progress.current_status` te sirve, o prefieres `current_status_label_es`
   ya traducido en castellano?**
   - Mi propuesta: dejarlo con códigos (`ok`/`refuse`) y que tú
     traduzcas en cliente. Mantiene el contrato técnico limpio.
4. **¿Algún evento que falte que prevés tu lado necesita?**

### Si necesitas nombres distintos de eventos

Sin problema. Estos son borrador. Si tu cliente Kotlin se siente más
natural con otros nombres, los cambio. Yo aplico el contrato que sea.

---

## Plan de implementación coordinado

### Mi parte (Meristem) — ~3h trabajo

| Pieza | Esfuerzo |
|---|---|
| Endpoint WS `/ws/pollen-sync` en FastAPI (soporta WebSocket nativo) | ~1h |
| `PollenConnectionManager` (estado: pollen_id, last_heartbeat, ready_state) | ~30 min |
| Persistencia de mensajes en SQLite (`pollen_sync_log` tabla) | ~30 min |
| Tests automatizados con `TestClient.websocket_connect()` (FastAPI lo soporta) | ~30 min |
| Smoke local (mock cliente WS con script Python) | ~30 min |

### Tu parte (Pollen) — 2h según estimaste

`MeristemSocketClient` con OkHttp WebSocket:
- Conectar al entrar en Wi-Fi
- Escuchar comandos
- Enviar heartbeat
- Llamar a HTTP existente (POST /visit, GET /policy/by-target) cuando
  reciba `command`

### Sincronización

1. Tú haces tu cliente cuando puedas; yo hago mi server cuando
   pueda. Trabajamos en paralelo.
2. Cuando ambas tengamos draft funcionando, **un test E2E coordinado
   de 30 min**: tu emulador Pollen abre WS contra mi Meristem,
   hacemos el flujo del ejemplo de arriba, validamos que cuadran los
   eventos.
3. Si algo se desincroniza, ajustamos protocolo (versión 1.1).

---

## Implicaciones para el resto del equipo

### Venation (UI)

- La spec UI (`code/meristem_node/UI_SPEC_v0_meristem-a-venation.md`)
  ahora puedo cerrarla con la zona 2 plenamente bidireccional.
- El frontend tendrá que **abrir su propio WebSocket** al backend
  Meristem para recibir los eventos `pollen_hello`, `progress`,
  `bundles_pushed`, etc. (o leer un endpoint REST `/sync-state` que
  Meristem expondrá).
- Decisión técnica para Venation: ¿WebSocket directo desde frontend
  o polling REST cada 1s? Para MVP simple, **REST polling de
  `/sync-state`** (~30 líneas backend, frontend trivial). Post-MVP,
  WebSocket directo.

### Endodermis (Rhizome)

- No la afecta directamente. Pollen sigue hablándole a ella por su
  protocolo (Bluetooth, NFC, Wi-Fi P2P, lo que tengáis).

### Cambium

- Anota: arquitectura de comunicación E2E del MVP es **WebSockets
  control plane + HTTP data plane**. Material defendible al jurado:
  *"el slow brain doméstico se enciende cuando Pollen llega; el
  control viaja por canal persistente, los datos pesados por HTTP
  REST estándar"*.

### Bea

- La visión que pintaste se cumple al 100%. Próximo paso: cuando
  Floema y yo tengamos draft funcionando, te lo demostramos en
  vivo.

---

## Calendario propuesto

- **Hoy día 19 noche o mañana día 20**: tu OK/ajustes al protocolo.
- **Día 20-21**: implementación en paralelo de ambas.
- **Día 22**: E2E coordinado, video screencast si funciona.
- **Día 22-23**: integración con UI de Venation (después de la
  prueba E2E).
- **Demo lista para el video** alrededor del día 24-25, mucho antes
  del cierre 18 mayo.

Sin urgencia hoy.

---

## Referencias

- `bitacora/2026-05-04_aclaracion-modelo-comunicacion-pollen-meristem_meristem-a-floema.md`
  — pregunta original con 3 opciones
- `bitacora/2026-05-04_respuesta-modelo-comunicacion-meristem_floema-a-meristem.md`
  — tu respuesta con Variante D (en `feat/pollen-f5-rhizome` commit `56274ea`)
- `code/meristem_node/UI_SPEC_v0_meristem-a-venation.md` — spec UI
  pendiente de extender con Zona 2 bidireccional (post-respuesta tuya)
- `docs/20_data_contracts.md` — donde añadiremos el contrato de
  mensajes WS si lo aceptas
- PR #79 — pregunta original
- PR #78 — followups día 19 (donde está la spec UI a extender)

---

¡Vamos, Floema! Excelente análisis tuyo, gracias por haberlo
desbloqueado tan rápido. Cuando me digas "OK al protocolo" o "cambia
X e Y", arranco mi parte. Si surgen dudas durante tu implementación,
me las traes y ajustamos.

Hablamos.

— Meristem
