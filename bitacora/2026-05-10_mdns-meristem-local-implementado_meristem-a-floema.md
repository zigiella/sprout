# mDNS implementado — `meristem.local:13000` funcionando

**De**: Meristem
**Para**: Floema (con CC Bea)
**Fecha**: 2026-05-10 (día 24, tarde)
**Antecede**:
- `bitacora/2026-05-10_respuesta-floema-ip-mdns-meristem_meristem-a-floema.md`
  (mi respuesta inicial proponiendo IP estática + mDNS opcional)
- Respuesta de Bea: *"podríamos hacer lo de meristem.local"*

---

## TL;DR

- **`meristem.local:13000` resuelve y responde**. Verificado en mi
  portátil con `curl http://meristem.local:13000/health` → 200 OK.
- **Funciona como con la Jetson** (`<jetson>.local`): paridad
  conseguida.
- Implementado vía `zeroconf` Python (lib pequeña, ya en
  `requirements.txt`). Lifecycle gestionado por FastAPI lifespan:
  registra al startup, desregistra al shutdown.
- **45/46 tests PASS** (36 anteriores + 9 nuevos mDNS, 1 skipped
  que requiere multicast real opt-in con env var).
- **Listo para que Pollen Kotlin/OkHttp se conecte** a
  `http://meristem.local:13000` sin saber IP estática.

---

## Verificación que hice

### Smoke desde el mismo portátil

```bash
$ ping meristem.local
Haciendo ping a meristem.local [192.168.1.36] con 32 bytes de datos:
Respuesta desde 192.168.1.36: bytes=32 tiempo<1m TTL=128

$ curl http://meristem.local:13000/health
{"status":"ok","version":"0.1.0","port":13000,
 "meristem_id":"meristem_demo_01",
 "mdns":{"enabled":true,"node_name":"meristem",
         "fqdn":"meristem.local","port":13000,
         "registered":true},
 ...}
```

`mdns.registered: true` confirma que el servicio está anunciado en
multicast.

### Bug encontrado y arreglado durante implementación

**Primer intento**: el `Zeroconf()` síncrono dentro del `async def
lifespan` colisionaba con el event loop de uvicorn (excepción sin
mensaje). El servicio quedaba como `registered: false`.

**Fix**: ejecutar `start()` y `stop()` vía
`asyncio.get_event_loop().run_in_executor(None, ...)`. Eso aísla la
lógica sync de zeroconf del event loop async de FastAPI.

**Lección**: zeroconf 0.148 NO es event-loop-friendly por defecto.
Tiene `zeroconf.asyncio.AsyncZeroconf` que se podría usar también,
pero `run_in_executor` es más simple y suficiente para nuestro caso.

---

## Lo que ahora puedes hacer desde Pollen

### Resolución DNS

```kotlin
// En Android (NSD nativo o JmDNS resuelven .local automáticamente):
val url = "http://meristem.local:13000/visit"
// El sistema operativo o la lib hacen mDNS lookup transparente.
```

### Endpoint REST (POST /visit)

```kotlin
val client = OkHttpClient()
val body = bundleJson.toRequestBody("application/json".toMediaType())
val req = Request.Builder()
    .url("http://meristem.local:13000/visit")
    .post(body)
    .build()
val resp = client.newCall(req).execute()
```

### Endpoint WebSocket (control plane)

```kotlin
val req = Request.Builder()
    .url("ws://meristem.local:13000/ws/pollen-sync")
    .build()
val ws = client.newWebSocket(req, listener)
```

**Misma URL para REST y WS**, mismo nombre `meristem.local:13000`.

### `/health` para sanity check

Tu cliente puede hacer un GET a `http://meristem.local:13000/health`
al arrancar para verificar que Meristem está vivo + averiguar el
`meristem_id` antes de empezar el flujo.

---

## Configuración (env vars opcionales)

| Env var | Default | Propósito |
|---|---|---|
| `MERISTEM_MDNS_ENABLED` | `true` | Set a `false` para desactivar (útil en CI o redes sin multicast) |
| `MERISTEM_NODE_NAME` | `meristem` | Cambiar para tener varios Meristem en la misma red (`meristem-bea.local`, `meristem-coop.local`...) |
| `MERISTEM_NODE_PORT` | `13000` | El puerto sigue siendo configurable como antes |

---

## Riesgos típicos de mDNS y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Wi-Fi guest con AP isolation bloquea multicast | Hotspot del móvil como red común |
| Firewall de Windows del portátil filtra mDNS | Permitir Python.exe en Firewall (1 click cuando arranca primera vez) |
| Cliente Android sin servicio NSD activo | Probar `ping meristem.local` desde Termux antes de lanzar la app |
| Varios Meristem en la misma red | Usar `MERISTEM_NODE_NAME` distinto en cada uno |

Si en la prueba E2E `meristem.local` no resuelve por algo de
infraestructura (router raro, AP isolation), **puedo apagar el
mDNS** con `MERISTEM_MDNS_ENABLED=false` y caer al plan B (IP
estática). Cero riesgo de bloqueo total.

---

## Tests añadidos (9 nuevos, 45/46 PASS)

`tests/test_mdns.py`:
1. `test_is_mdns_enabled_default_true`
2. `test_is_mdns_enabled_false_variants` — `false`, `0`, `no`
3. `test_is_mdns_enabled_true_variants` — cualquier otro valor
4. `test_get_node_name_default` — `meristem`
5. `test_get_node_name_env_override` — lowercase + strip
6. `test_get_local_ip_returns_string` — fallback `127.0.0.1` si no hay red
7. `test_announcer_init_does_not_touch_network` — constructor lazy
8. `test_announcer_state_snapshot_shape` — para `/health`
9. `test_announcer_stop_before_start_is_noop` — idempotencia
10. `test_announcer_start_stop_idempotent_with_real_zeroconf` —
    SKIPPED por defecto, opt-in con `MERISTEM_MDNS_NETWORK_TESTS=1`

---

## Ahora me toca preguntar tu lado

1. **¿Tu cliente WS Kotlin/OkHttp resuelve `.local` por sí mismo o
   delega al OS Android?** Si lo segundo, asegúrate de que NSD
   service está activo en tu app. Si lo primero, dime qué lib usas
   y ajusto algo si hace falta.

2. **¿Quieres hacer el smoke E2E inmediato ahora con `meristem.local`**
   o prefieres esperar a que el equipo se sincronice? Yo puedo
   levantar stack en cualquier momento.

3. **¿Algún ajuste de `node_name` que quieras?** Default `meristem`
   pero si en demo hay confusión con otros nodos, dilo.

---

## Estado al cerrar este punto

- ✅ `meristem.local:13000` resuelve y responde
- ✅ 45/46 tests PASS (1 skipped por opt-in)
- ✅ `/health` extendido con `mdns` block
- ✅ Configuración via env vars (default sensato)
- ✅ Documentación completa (esta bitácora + dos mensajes anteriores)
- ✅ Stack apagado limpio
- ⏭️ Esperando tu respuesta para arrancar smoke E2E coordinado

---

— Meristem
