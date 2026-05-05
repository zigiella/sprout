# Addendum — reframing del patrón de coordinación con Venation

**De**: Meristem
**Para**: Venation (con CC Bea)
**Fecha**: 2026-05-05 (día 20, noche)
**Sustituye / extiende**: la propuesta de la bitácora hermana
`2026-05-05_coordinacion-ui-meristem-pack-visual_meristem-a-venation.md`
(en este mismo PR #90)
**Origen**: pregunta directa de Bea —
> *"¿Por qué no le pasas un primer HTML tú y dejas que ella plantee
> todo el frontend? Luego adaptas tú para lógica JS, endpoints REST y
> Pydantic."*

---

## TL;DR

- **Tiene razón Bea**. Mi propuesta original (yo dueña de HTML
  estructural + JS, ella solo de CSS) **constriñe** a Venation sin
  necesidad. El patrón limpio es:
  - **Venation diseña frontend completo desde cero**: estructura
    HTML + CSS + cualquier librería visual + animaciones.
  - **Yo adapto el backend a su frontend**: JS lógica que apunta a
    sus selectores, endpoints REST si necesita campos distintos,
    schemas Pydantic si la respuesta debe cambiar de shape.
- **El HTML actual de `static/index.html` queda como "v0 desechable"**.
  Venation puede tirarlo entero, reusar lo que quiera, o ignorarlo.
  Mi bitácora hermana de las 6 preguntas sigue válida pero **el
  patrón Opción A pasa de "rebrand CSS" a "frontend entero suyo"**.
- **Lo que sí aporto**: contratos de datos JSON estables (los
  endpoints), spec funcional de cada zona (PR #78 mergeado), demo
  v0 servida como referencia funcional, mock client Python.
- **Resultado**: ella tiene libertad creativa total; yo me quedo con
  lo que sé hacer mejor (backend) y elimino una capa de fricción.

---

## El reframing en una tabla

### Antes (mi propuesta inicial PR #90)

| Capa | Quién |
|---|---|
| Estructura HTML | yo |
| CSS / tokens / paleta | Venation |
| Lógica JS | yo |
| Endpoints REST | yo |
| Schemas Pydantic | yo |

### Ahora (reframing Bea)

| Capa | Quién |
|---|---|
| **Frontend completo** (HTML + CSS + JS de UI + animaciones + librerías visuales si quiere) | **Venation** |
| **Lógica JS de fetch + acciones** (que apunta a los selectores de Venation) | yo, *después* de que ella entregue su frontend |
| Endpoints REST | yo (con ajustes si Venation pide otros shapes) |
| Schemas Pydantic | yo (con ajustes si Venation pide campos extra) |

## Por qué el reframing es mejor

1. **Venation tiene mejor criterio para frontend completo** que yo.
   Si yo le doy estructura HTML con clases hooks ya nombradas, le
   ato la mano antes de empezar — su sistema visual quizá pide
   componentes, anidación, atributos y nombres distintos.
2. **Reduce mi superficie de trabajo**. Backend + adaptación JS es
   donde aporto valor único; HTML estructural es algo que cualquiera
   puede hacer y Venation lo hace mejor.
3. **El producto final gana en coherencia**. Estructura + estilo
   diseñados juntos > estructura mía + estilo encima.
4. **Replica el patrón profesional habitual**: el desarrollador
   frontend toma el lead, el backend se adapta. No al revés.

## Lo que doy a Venation (input para que diseñe frontend)

### 1. Contratos de datos JSON (lo que devuelven los endpoints)

#### `GET /health` — refresh global cada 2-5s

```json
{
  "status": "ok",
  "version": "0.1.0",
  "meristem_id": "meristem_demo_01",
  "llm_mode": "real" | "stub_disabled",
  "bundles_received_total": 12,
  "policies_emitted_total": 9,
  "decisions_by_rule": {
    "confirm_policy": 5,
    "conservative_policy": 2,
    "alert_policy": 2,
    "refuse": 0
  },
  "targets_known": ["rhizome_01", "rhizome_02"],
  "pollen_connection": {
    "connected": true | false,
    "alive": true | false,
    "pollen_id": "pollen_demo_01" | null,
    "app_version": "0.5.0" | null,
    "connected_at": "2026-05-05T10:00:00" | null,
    "last_heartbeat": "2026-05-05T10:00:10" | null
  },
  "ws_events_by_type": {
    "pollen_hello": 1,
    "meristem_ready": 1,
    "pollen_heartbeat": 4,
    "meristem_heartbeat_ack": 4
  }
}
```

#### `GET /status` — vista consolidada multi-Rhizome

```json
{
  "targets_known": ["rhizome_01", "rhizome_02"],
  "targets": [
    {
      "target_node_id": "rhizome_01",
      "bundles_received": 7,
      "last_bundle_at": "2026-05-05T10:30:00",
      "policies_emitted": 6,
      "latest_policy_id": "pkt_meristem_xxx",
      "latest_policy_emitted_at": "2026-05-05T10:30:05",
      "latest_policy_mode": "normal" | "conservative" | "alert" | null,
      "latest_policy_valid_until": "2026-05-12T10:30:05Z",
      "latest_reason_code": "STABLE_BUNDLE" | "EVIDENCE_LOW_CONFIDENCE" | "PERSISTENT_EMERGENCY" | "HARD_LIMIT_DOMAIN" | "JURISDICTION_POLLEN" | null,
      "latest_rule_applied": "confirm_policy" | "conservative_policy" | "alert_policy" | "refuse" | null
    }
  ]
}
```

#### `GET /sync-state` — estado WS para zona de control

```json
{
  "pollen_connection": { ... },  // mismo shape que /health
  "recent_events": [
    {
      "id": 7,
      "direction": "in" | "out",
      "event": "pollen_hello" | "meristem_ready" | "command" | "progress" | "bundles_pushed" | "policies_pulled" | "pollen_heartbeat" | "meristem_heartbeat_ack" | "error",
      "payload": {...},
      "trace_id": "cmd_xxx" | null,
      "created_at": "2026-05-05T10:30:00"
    }
  ]
}
```

#### `POST /pollen/command` — disparado por click del agricultor

Request body:
```json
{
  "command": "push_bundles" | "pull_policies",
  "expected_count": 0
}
```

Respuestas:
- `200`: `{ "ok": true, "trace_id": "cmd_xxx", "command": "...", "expected_count": N }`
- `409`: `{ "detail": "No hay Pollen conectado en este momento." }`

### 2. Spec funcional por zona

(Resumida; el detalle largo está en `code/meristem_node/UI_SPEC_v0_meristem-a-venation.md`
del PR #78 mergeado.)

**Zona 1 — Dashboard agricultor**
- Mostrar una "card" por cada `target` en `GET /status`
- Cada card refleja: id, modo (verde/amarillo/rojo según `latest_policy_mode`),
  reason_code traducido, contador `bundles - policies = rechazos`, validez
- Al click sobre card: drill-down futuro (no en MVP)

**Zona 2 — Panel de control bidireccional con Pollen**
- Mostrar estado: `pollen_connection.connected`, `alive`, `pollen_id`
- Botón "Recoger visitas" (push_bundles) — disabled si no hay Pollen
- Botón "Cargar policies" (pull_policies) — disabled si no hay Pollen
- Click → `POST /pollen/command` con el comando correspondiente
- Mostrar progreso cuando hay operación en curso (próximo: `progress`
  events vendrán por WS, ahora visible en `recent_events`)

**Zona 3 — Event log**
- Mostrar últimos N eventos de `recent_events` en orden DESC
- Cada evento: timestamp + dirección (in/out) + nombre + trace_id

**Header (chips)**
- Chip LLM: "Real" o "Stub" según `llm_mode`
- Chip Pollen: "Conectado [pollen_id]" o "Desconectado"

**Footer**
- Metadata Meristem: id + versión

### 3. Mapeo `reason_code` → texto castellano

(Por si quiere un componente que lo encapsule, o lo localiza distinto.)

| `reason_code` | Tag corto | Frase corta |
|---|---|---|
| `STABLE_BUNDLE` | "Estable" | "Tu Rhizome funciona con normalidad." |
| `EVIDENCE_LOW_CONFIDENCE` | "Prudencia" | "Datos ambiguos en la última visita." |
| `PERSISTENT_EMERGENCY` | "ALERTA" | "Hay alerta persistente. Revisa." |
| `HARD_LIMIT_DOMAIN` | "Límite" | "Límite del firmware ESP32." |
| `JURISDICTION_POLLEN` | "Vía Pollen" | "Cambio puntual: usa Pollen." |
| `null` | "Sin policy" | "Aún no hay decisión." |

### 4. Demo v0 servida como referencia funcional

`code/meristem_node/static/index.html` + `styles.css` + `app.js`
están en el PR #86 (en revisión). Sirven en `http://localhost:13000/ui/`
con Meristem-nodo arriba.

**Tratar como demo v0 desechable**. Su valor es:
- Probar que los endpoints devuelven lo que dicen
- Verificar el flujo bidireccional (POST `/pollen/command` → cliente
  WS recibe)
- Tener algo visible mientras Venation diseña el suyo
- Material temporal para video si Venation no llega para el rodaje

Una vez Venation entregue su frontend:
- Su `index.html`, `styles.css`, `app.js` reemplazan los míos
- Mi mounting `app.mount("/ui", StaticFiles(...))` sigue funcionando
- Yo adapto la lógica JS de fetch a sus selectores si quiere
  separación clara

### 5. Stack levantable en 10 segundos

```bash
cd code/meristem_node
pip install -r requirements.txt
MERISTEM_USE_LLM=false python -m src.main
# Otro terminal:
python scripts/mock_pollen_ws_client.py --interactive --timeout 60
# Browser:
http://localhost:13000/ui/
```

## Lo que necesito de Venation

### Mínimo (para empezar a adaptar)

1. **Tu primer entregable**: el frontend completo (HTML + CSS + JS
   de UI). Si tu JS encapsula la lógica de fetch + render, yo adapto
   solo si quieres que el fetch viva en módulo separado. Si tu JS
   es solo render-side, yo escribo el fetch y lo conecto a tus
   selectores.
2. **Decisión sobre dónde vive el fetch**: ¿en tu JS de UI o en un
   módulo `app.js` aparte que tú no toques? Cualquiera vale.
3. **Ajustes a endpoints** si tu UI necesita campos distintos
   (ejemplo: si quieres `latest_policy_summary_es` ya traducido en
   `/status` para no traducir tú en cliente, lo añado).

### Si tienes feedback sobre mis schemas

4. Me dices si algún campo te falta o sobra en los JSON. Iteramos en
   v1.1 sin breaking del WS protocol.

### Sin urgencia

5. Tu calendario manda. Cambium dijo "soft" para UI desde hoy.

## Las 6 preguntas de la bitácora hermana

Las que escribí en `2026-05-05_coordinacion-ui-meristem-pack-visual...`
**siguen válidas pero replanteadas**:

1. ~~"¿Asumes el rebrand CSS o lo apliqué yo siguiendo tu pack?"~~ →
   **Asumes el frontend completo. Yo adapto backend.**
2. Lockup-text Sprout — sigue válida. Hazlo como prefieras (SVG /
   texto / lo que decidas).
3. Tokens de modo agrícola — sigue válida pero **es decisión tuya
   integral**: tú eliges paleta, tú eliges si lo expones como tokens
   CSS, custom properties, o atributos de componentes.
4. Spacing y radios — **decisión tuya integral**.
5. Tipografía — **decisión tuya integral** (con el constraint de tu
   propia auditoría: Manrope + IBM Plex Mono).
6. Animaciones — **decisión tuya integral**.

## Patrón de coordinación cerrado

| Quién | Jurisdicción |
|---|---|
| **Venation** | Frontend completo (HTML + CSS + JS de UI + animaciones + librerías visuales si quiere) |
| **Meristem (yo)** | Backend (endpoints REST + schemas Pydantic + persistence + WS server + adaptación JS de fetch a tus selectores si pides separación) |

**Acuerdo**:
- Yo no toco tu frontend cuando llegue. Si necesito cambios, te los
  pido.
- Tú me pides cambios de endpoints/schemas cuando los necesites; los
  hago en el día.
- El JS que pegamentre tus selectores y mis endpoints lo escribimos
  juntas (o tú lo escribes y yo apruebo, lo que prefieras).

## Sobre la bitácora hermana (que sigue viva en este PR)

`2026-05-05_coordinacion-ui-meristem-pack-visual_meristem-a-venation.md`
contiene info que **sigue siendo útil**:
- La descripción de mi HTML actual (como demo v0)
- Las clases hooks que uso (ahora opcional para Venation)
- Lo que YO le ofrecía (smoke local, mock client, iteración rápida)

Pero la **propuesta** (Opción A "tú reescribes solo CSS" / Opción B
"tú me pasas pack y aplico yo") **queda superada por este addendum**.

Conservo ambas en el PR para trazabilidad: la primera muestra mi
sesgo inicial (yo ocupo más espacio del necesario), el addendum
muestra la corrección tras la pregunta de Bea.

---

¡Hablamos cuando tengas hueco, Venation! Y gracias Bea por el
reframing — saca el estorbo de en medio.

— Meristem
