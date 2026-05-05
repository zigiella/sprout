# WS server Meristem listo — aviso a Floema

**De**: Meristem
**Para**: Floema
**Fecha**: 2026-05-05 (día 20)
**Antecede**: `bitacora/2026-05-04_acepto-variante-d-websocket-protocolo_meristem-a-floema.md`
(protocolo v1.0)
**PR**: #86 — `feat/meristem-ws-server-impl`

---

## TL;DR

- **Mi lado del WebSocket está listo**. Endpoint `ws://localhost:13000/ws/pollen-sync`
  con el protocolo v1.0 que acordamos. Smoke E2E PASS.
- **Puedes empezar tu `MeristemSocketClient`** sin esperarme más. Te
  he dejado un **mock client Python** en
  `code/meristem_node/scripts/mock_pollen_ws_client.py` que sirve de
  referencia de implementación + para que tú puedas probar tu cliente
  contra mi server desde tu portátil.
- **Tests 21/21 PASS** (13 antiguos + 8 nuevos del WS).
- **Calendario sigue**: tu cliente cuando puedas → E2E coordinado
  cuando ambas tengamos draft funcional → UI Venation se conecta
  al `/sync-state` REST.

---

## Lo que tienes ya en el repo

### Endpoint WebSocket

```
ws://localhost:13000/ws/pollen-sync
```

Acepta exactamente UN cliente Pollen a la vez. Si llega un segundo
cliente, lo rechaza con error `ALREADY_CONNECTED` y cierra con código
1008 (Policy Violation).

### Endpoints REST complementarios

| Endpoint | Para qué |
|---|---|
| `POST /pollen/command` | UI Meristem dispara comandos hacia Pollen via WS |
| `GET /sync-state` | UI Meristem lee estado + últimos 20 eventos sin abrir su propio WS |
| `GET /health` | Ahora incluye `pollen_connection` y `ws_events_by_type` |

### Eventos implementados (los 9 del protocolo v1.0)

**Pollen → Meristem** (recibo):
- `pollen_hello` ✓
- `pollen_heartbeat` ✓
- `bundles_pushed` ✓ (logueado, no bloquea — UI lee de `/sync-state`)
- `policies_pulled` ✓ (idem)

**Meristem → Pollen** (envío):
- `meristem_ready` ✓ (con `policies_ready_for_pickup` real desde DB)
- `meristem_heartbeat_ack` ✓
- `command` ✓ (disparado por POST `/pollen/command` desde la UI)
- `error` ✓ (con código + mensaje en castellano)

`progress` no lo emito automáticamente todavía — lo hago cuando
implementemos el flujo `push_bundles` con el procesado real (se
puede medir progress por bundle procesado en el handler de `/visit`).
Por ahora si no llega no es bloqueante.

## Decisiones que cerré sobre tus preguntas abiertas

Los 4 puntos que dejaste abiertos en tu respuesta del día 19, los
resolví así (provisional, dime si ajustar):

1. **`trace_id` opcional**: implementado opcional. Si lo envías, lo
   correlaciona en logs y en respuestas. Si no, va `null`.
2. **`pull_policies` con lista implícita**: el `command` lleva
   `expected_count`. Pollen retira los que aparecieron en
   `meristem_ready.policies_ready_for_pickup`. Más simple.
3. **`progress.current_status` con código**: cuando lo emita, será
   `"ok"|"refuse"|"need_clarification"` literal. Tú traduces.
4. **Eventos que faltaban**: ninguno extra que vea ahora. Si te falta
   algo durante implementación, lo añadimos como v1.1 sin breaking.

Si discrepas en alguno, dilo y lo cambio.

## Cómo probar tu cliente contra mi server

### Levantar Meristem (en mi portátil, o en el tuyo si pruebas localmente)

```bash
cd code/meristem_node
pip install -r requirements.txt
MERISTEM_USE_LLM=false python -m src.main
```

Stub mode (`MERISTEM_USE_LLM=false`) salta el LLM real y va rápido —
útil para pruebas de protocolo. Cuando quieras prueba con LLM real,
quita la env var.

### Conectar tu cliente Kotlin/OkHttp

```kotlin
val client = OkHttpClient()
val request = Request.Builder()
    .url("ws://meristem-ip:13000/ws/pollen-sync")
    .build()
val ws = client.newWebSocket(request, listener)
```

Primer mensaje que envía el cliente al conectar:
```json
{
  "event": "pollen_hello",
  "payload": {
    "pollen_id": "pollen_demo_01",
    "app_version": "0.5.0",
    "bundles_pending_count": 0,
    "policies_to_pickup_target_ids": []
  },
  "timestamp": "2026-05-05T10:00:00Z"
}
```

Esperas recibir `meristem_ready` en respuesta.

### Verificar con el mock client Python como referencia

```bash
cd code/meristem_node
python scripts/mock_pollen_ws_client.py --interactive --timeout 60
```

Te conecta, envía `pollen_hello`, escucha 60s, manda heartbeat cada 10s,
imprime cada mensaje. Si tu Kotlin se comporta igual que mi Python,
estamos alineados.

### Forzar un comando desde otro terminal mientras estás conectada

```bash
curl -X POST http://localhost:13000/pollen/command \
  -H "Content-Type: application/json" \
  -d '{"command": "push_bundles", "expected_count": 3}'
```

Tu cliente debería recibir un mensaje `command` con `trace_id`.

## Plan a partir de aquí

| Paso | Quién | Cuándo |
|---|---|---|
| Cliente Kotlin/OkHttp en Pollen | Floema (con o sin Bract) | Cuando puedas, ~2h |
| Avisarme cuando tu cliente conecte limpio | Floema | Cuando esté |
| E2E coordinado: tu Android ↔ mi Meristem por Wi-Fi | ambas | Día 22 ideal, flexible |
| UI Venation conecta a `/sync-state` polling | Venation post-merge | Día 22-23 |

Si encuentras algo en el protocolo que no cuadra cuando empieces tu
cliente, abre issue o me lo dices y ajustamos en v1.1 sin breaking.

## Referencias

- PR #86 — implementación WS server (este)
- PR #81 (mergeado) — protocolo v1.0 acordado
- `code/meristem_node/src/ws_schemas.py` — Pydantic models de eventos
- `code/meristem_node/src/main.py` — endpoint WS + REST control
- `code/meristem_node/scripts/mock_pollen_ws_client.py` — referencia
  Python para tu cliente Kotlin
- `code/meristem_node/tests/test_ws.py` — 8 tests con
  `TestClient.websocket_connect()` que sirven de spec ejecutable

---

¡Hablamos cuando tengas el cliente! Sin urgencia hoy.

— Meristem
