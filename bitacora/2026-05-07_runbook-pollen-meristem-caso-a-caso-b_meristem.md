# Runbook — Casos completos Pollen ↔ Meristem (A: descarga policies / B: carga datos)

**Autora**: Meristem
**Fecha**: 2026-05-07 (día 22)
**Para**: Bea (operadora de la demo) + equipo
**Aplica desde**: PR #104 mergeado (UI funcional v1) + i18n añadido en
este PR
**Tipo**: instrucciones paso a paso reproducibles

---

## TL;DR

- **Dos modos** según lo que tengas a mano:
  - **MODO MOCK** (ya hoy, sin Pollen Android): mock client Python
    simula Pollen conectado. Útil para que veas el flujo completo,
    para demos internas, y para grabar screencast.
  - **MODO REAL** (cuando Floema entregue cliente Kotlin/OkHttp): el
    móvil Android conecta de verdad. Mismo runbook, solo cambia el
    "cliente Pollen" del Paso 2.
- **Caso A — Descarga de policies**: Pollen retira PolicyPackets que
  Meristem tiene listas para llevar al campo. Botón UI: "Cargar
  policies".
- **Caso B — Carga de datos**: Pollen empuja Bundles recogidos del
  campo. Meristem los procesa y emite policies. Botón UI: "Recoger
  visitas".
- **Tiempo total** del runbook completo (A + B): 5-10 min en MODO
  MOCK; 10-15 min en MODO REAL (latencia LLM si activo).

---

## Pre-requisitos comunes (haz esto una vez)

Desde la raíz del repo `T6-GEMMA`:

```bash
cd code/meristem_node
pip install -r requirements.txt
# Solo la primera vez, instala el cliente WS Python para el modo mock:
pip install websockets httpx
```

**Comprobación**: que `python -m src.main --help` no rompa o que
`python -c "import fastapi, uvicorn, websockets, httpx; print('OK')"`
imprima `OK`.

---

## Setup común (haz esto al empezar cada sesión)

### Terminal 1 — Levantar Meristem-nodo

Desde `code/meristem_node/`:

```bash
# Modo rápido (sin LLM real, todo en stub determinista, ~10s arrancando)
MERISTEM_USE_LLM=false python -m src.main
```

O modo completo (con LLM Gemma 4 E4B, ~30-60s para que llama-server
arranque, ~2 min/bundle):

```bash
# 1. En otra terminal: llama-server con E4B
llama-server -m models/gemma-4-E4B-it-Q4_K_M.gguf --port 8080

# 2. En otra terminal: meristem_inference_adapter en :12000
python -m meristem_inference_adapter.main

# 3. En esta terminal: Meristem
MERISTEM_USE_LLM=true python -m src.main
```

**Comprobación**: en el navegador, `http://localhost:13000/ui/` carga
la pantalla de Meristem (estado vacío al principio).

**Idioma**: por defecto castellano. Click en `EN` del topbar para
cambiar a inglés. Persiste en `localStorage`, recarga conserva la
preferencia.

---

## MODO MOCK — sin Pollen Android (hoy mismo)

### Terminal 2 — Levantar mock cliente Pollen

Desde `code/meristem_node/`:

```bash
python scripts/mock_pollen_ws_client.py --interactive --timeout 600
```

Esto simula un Pollen que:
1. Abre WebSocket a `ws://localhost:13000/ws/pollen-sync`
2. Envía `pollen_hello` con `pollen_id="pollen_mock_01"` y declara
   2 bundles pendientes + 2 policies a recoger para Rhizomes
   `rhizome_01` y `rhizome_02`
3. Mantiene conexión 10 minutos enviando heartbeats cada 10s

**Comprobación inmediata**:

- En la UI Meristem (Zona 2 *"Sincronización con Pollen"*) deberías
  ver: chip topbar pasa a verde "Pollen: pollen_mock_01" y la
  línea de estado dice *"Pollen pollen_mock_01 conectado · hace Xs"*.
- Los botones **"Recoger visitas"** y **"Cargar policies"** se
  habilitan (azules).

### Terminal 3 — Cargar bundles ejemplo (data Caso B)

Necesitamos algunos bundles representativos en la DB para que
"Recoger visitas" tenga algo que mostrar. Ejecuta desde
`code/meristem_node/`:

```bash
# Bundle limpio (camino feliz, normal)
curl -s -X POST http://localhost:13000/visit \
  -H "Content-Type: application/json" \
  --data-binary @examples/bundle_M1_clean.json

# Bundle de emergencia (alert)
curl -s -X POST http://localhost:13000/visit \
  -H "Content-Type: application/json" \
  --data-binary @examples/bundle_R2_emergency.json

# Bundle disputed (conservative)
curl -s -X POST http://localhost:13000/visit \
  -H "Content-Type: application/json" \
  --data-binary @examples/bundle_M2_disputed.json
```

**Comprobación en UI**:

- Zona 1 *"Tu parcela hoy"* muestra 2 cards: `rhizome_01` en verde
  NORMAL, `rhizome_02` en rojo ALERT.
- Zona 4 *"Visitas recibidas"* muestra 3 filas (3 bundles
  procesados).
- Zona 5 *"Políticas emitidas"* muestra 3 policies (orden DESC).
- Trazabilidad pills: `confirm: 1`, `conservative: 1`, `alert: 1`.

---

## CASO A — Descarga de policies (Pollen → llevarse al campo)

**Lo que el agricultor hace**: llega a casa, conecta su móvil al
Wi-Fi del ordenador con Meristem, abre la app Pollen. Quiere recoger
las políticas que Meristem ha preparado para llevar al campo.

### Pasos

1. **Verifica setup común**: Meristem en Terminal 1, mock client en
   Terminal 2, bundles cargados (Terminal 3).
2. **Abre la UI Meristem** en `http://localhost:13000/ui/`.
3. **Verifica que Pollen está conectado**: chip verde topbar +
   estado en Zona 2.
4. **Click en botón *"Cargar policies"*** (Zona 2, botón secundario,
   azul claro).
5. **Observa el progreso**:
   - La línea de progreso debajo de los botones cambia a *"Cargar
     policies en curso…"* (azul, italic).
   - Tras un instante: *"Cargar policies enviado · trace cmd_xxxxxxxx"*.
6. **Verifica en Zona 3 *"Operaciones recientes"***:
   - Aparece nueva fila `→ command [cmd_xxxxxxxx]` (Meristem→Pollen).
7. **En Terminal 2 (mock client)** verás el log del comando recibido:
   ```
   << [recv] command {"command": "pull_policies", "expected_count": 0}
   ```
8. **(Modo MOCK)**: el mock client recibe el comando pero **no actúa
   con HTTP** (no implementa el flujo completo de retirada). En MODO
   REAL, Pollen Android haría `GET /policy/by-target/rhizome_01` y
   `GET /policy/by-target/rhizome_02` para descargar los packets.
9. **Verifica en backend** que las policies están disponibles:
   ```bash
   curl -s http://localhost:13000/policy/by-target/rhizome_01 | python -m json.tool
   curl -s http://localhost:13000/policy/by-target/rhizome_02 | python -m json.tool
   ```
   Cada respuesta es un `PolicyPacket` con `policy_id`, `valid_until`,
   `mode_default`, `rules`, `rationale`.

**Resultado esperado**: el agricultor (tú en la UI) ha disparado el
comando, Pollen ha sido notificado por WebSocket, y los endpoints
REST `/policy/by-target/{id}` están listos para servir las policies
cuando Pollen Android las pida (Modo REAL) o cuando tú las pruebes
con curl (Modo MOCK).

### En MODO REAL (cuando Floema entregue cliente Kotlin)

Sustituye el paso 7 con:

7. **Pollen Android** (con cliente WS Kotlin de Floema) recibe el
   comando, hace los GET HTTP a Meristem, descarga los `PolicyPacket`,
   los guarda en local, y notifica al usuario *"2 políticas listas
   para llevar al campo"*.

Y añade paso 10:

10. **El agricultor sale al campo** con Pollen en el bolsillo. En la
    siguiente visita a un Rhizome físico, Pollen aplicará la policy.

---

## CASO B — Carga de datos (Pollen → Meristem)

**Lo que el agricultor hace**: vuelve del campo, conecta su móvil al
Wi-Fi del ordenador con Meristem, abre la app Pollen. Pollen tiene
en local varios bundles (visitas a Rhizomes con sensor data, decision
receipts, alertas). Quiere que Meristem los procese y emita políticas
nuevas si toca.

### Pasos

1. **Verifica setup común**: Meristem en Terminal 1, mock client en
   Terminal 2.
2. **(Distintivo del MODO MOCK)**: en MODO MOCK no hay bundles "en
   Pollen" porque el mock no almacena bundles. Para simular el flujo
   completo, los bundles se POSTean directamente desde Terminal 3
   (como en el setup), simulando que Pollen los empuja vía HTTP.
3. **Abre la UI Meristem** en `http://localhost:13000/ui/`.
4. **Verifica que Pollen está conectado**: chip verde topbar.
5. **Click en botón *"Recoger visitas"*** (Zona 2, botón primario,
   azul oscuro).
6. **Observa el progreso**:
   - Línea de progreso: *"Recoger visitas en curso…"*.
   - Tras un instante: *"Recoger visitas enviado · trace cmd_xxxxxxxx"*.
7. **Verifica en Zona 3 *"Operaciones recientes"***: nueva fila
   `→ command [cmd_xxxxxxxx]`.
8. **En Terminal 2 (mock client)**:
   ```
   << [recv] command {"command": "push_bundles", "expected_count": 0}
   ```
9. **(Modo MOCK)**: para simular el push real desde Pollen, ahora
   POSTeas bundles en Terminal 3:
   ```bash
   curl -s -X POST http://localhost:13000/visit \
     -H "Content-Type: application/json" \
     --data-binary @examples/bundle_M1_clean.json
   ```
10. **Observa el efecto en la UI**:
    - Zona 1 actualiza (si el target es nuevo, nueva card; si
      existe, refresca con el último estado).
    - Zona 4 *"Visitas recibidas"* incrementa contador y lista la
      nueva fila.
    - Zona 5 *"Políticas emitidas"* incrementa si el bundle no fue
      REFUSE.
    - Trazabilidad pills se actualizan.

**Resultado esperado**: el agricultor (tú) ha disparado el comando,
Pollen ha sido notificado, y la UI Meristem refleja los bundles
procesados con sus policies emitidas en tiempo real.

### En MODO REAL (cuando Floema entregue cliente Kotlin)

Sustituye el paso 9 con:

9. **Pollen Android** (cliente Kotlin de Floema) recibe el comando,
   recorre su lista de bundles pendientes, hace `POST /visit` a
   Meristem para cada uno, espera respuesta `VisitResponse` con
   `policy_packet`, y notifica al usuario *"3 visitas procesadas, 3
   políticas listas en Meristem"*.

Y añade paso 11:

11. **Pollen marca los bundles como entregados** localmente y los
    elimina (o los archiva). Ya no están "pendientes" en el móvil.

---

## Combinando A + B en una sola sesión

Flujo realista que el agricultor hace en una sesión típica de
10-15 minutos:

1. Llega a casa con Pollen en el bolsillo.
2. Setup común (1 sola vez al día, Terminal 1).
3. Conecta Pollen al Wi-Fi (chip verde aparece en topbar).
4. **Caso B primero**: click *"Recoger visitas"*. Pollen empuja los
   bundles del día. Meristem procesa y emite policies. UI muestra
   los nuevos datos.
5. El agricultor revisa la UI (cards de Zona 1, log de Zona 3,
   trazabilidad). Si hay alerta roja, sabe que algo pasa.
6. **Caso A después**: click *"Cargar policies"*. Pollen retira las
   policies recién emitidas + las ya disponibles para los Rhizomes
   que va a visitar mañana.
7. Cierra la app, deja el móvil cargando, mañana al campo con
   policies actualizadas.

---

## Verificaciones de salud y debug

### `/health` — estado global

```bash
curl -s http://localhost:13000/health | python -m json.tool
```

Campos relevantes:
- `bundles_received_total`: cuántos bundles ha recibido
- `policies_emitted_total`: cuántas policies ha emitido
- `decisions_by_rule`: distribución por regla del Evaluator
- `targets_known`: lista de Rhizomes que han enviado bundles
- `pollen_connection`: `{connected, alive, pollen_id, ...}`
- `ws_events_by_type`: conteo de eventos WS recibidos/enviados

### `/sync-state` — estado WS y log

```bash
curl -s http://localhost:13000/sync-state | python -m json.tool
```

Devuelve los últimos 20 eventos WS con dirección, evento, payload,
trace_id y timestamp.

### `/docs` — Swagger / OpenAPI

`http://localhost:13000/docs` te da una UI Swagger interactiva con
todos los endpoints, schemas, y posibilidad de probar requests
directamente desde el navegador.

---

## Troubleshooting

| Síntoma | Diagnóstico | Solución |
|---|---|---|
| UI carga vacía sin chip Pollen verde | Mock client no levantado o se cayó | Re-ejecutar Terminal 2 (`python scripts/mock_pollen_ws_client.py --interactive --timeout 600`) |
| Botones siempre disabled | `pollen_connection.alive=false` (no hay heartbeat reciente) | Verificar mock client está enviando heartbeats; reiniciar |
| `POST /visit` devuelve 500 | LLM no disponible en modo `MERISTEM_USE_LLM=true` | Cambiar a stub mode (`MERISTEM_USE_LLM=false`) o verificar adapter en :12000 |
| Click en *Recoger* / *Cargar* devuelve 409 | Pollen no conectado al WS | Esperar a que el mock client haga `pollen_hello` (~1s tras lanzar) |
| UI no actualiza tras POST /visit | Polling cada 2s; espera 1-3s | Sino: `Ctrl+R` recarga la página, mantiene locale |
| Toggle ES/EN no cambia idioma | localStorage bloqueado (modo privado) | Usa modo normal del navegador |

---

## Limpieza al terminar

```bash
# Terminal 1: Ctrl+C para parar Meristem-nodo
# Terminal 2: Ctrl+C para parar mock client (o se autoapaga a los 600s)
# (Opcional) borrar BBDD de prueba:
rm code/meristem_node/meristem_node.db
```

---

## Lo que aún NO está disponible (espera Floema/Endo)

- **Cliente Pollen Android real**: Floema lo está implementando (PR
  #92 spec del Mini-Evaluator + WS Variante D). Día 22-23 estimado.
- **Endpoint `POST /policy` en fachada Rhizome**: Endo lo implementa
  para la feature beta voz→política (Mini-Evaluator). Día 21-22.
- **Pollen aplica políticas descargadas en Rhizome físico**: requiere
  ESP32 + firmware de Xilema. Funcional en Jetson de Endo en demo.

Todos estos componentes estarán disponibles para el E2E completo
hacia el día 22-25. Mientras tanto, el MODO MOCK te permite ver el
flujo Meristem-Pollen al 100% en tu portátil.

---

## Referencias

- PR #104 (mergeado): UI funcional v1 con Zonas 4 y 5
- PR #92 (mergeado): spec Mini-Evaluator Kotlin Pollen
- `code/meristem_node/scripts/mock_pollen_ws_client.py` — cliente
  Python referencia para tu Kotlin
- `code/meristem_node/UI_SPEC_v0_meristem-a-venation.md` — spec UI
  para Venation rebrand
- `bitacora/2026-05-04_acepto-variante-d-websocket-protocolo_meristem-a-floema.md`
  — protocolo WS v1.0
- `bitacora/2026-05-05_diagnostico-rh02-bisection-plan_meristem-a-endodermis.md`
  — plan bisección RH02

---

Buen runbook, Bea. Si algún paso no cuadra, lo ajustamos.

— Meristem
