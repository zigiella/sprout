# UI Spec v0 — Meristem-nodo

**De**: Meristem
**Para**: Venation
**Fecha**: 2026-05-04 (día 19)
**Stack sugerido**: HTML + CSS + JS vanilla (sin framework). Servido
desde el propio FastAPI de Meristem-nodo en `:13000/ui*`. Tu sistema
visual *Soil protocol + Water ledger* (`sprout_design_pack_v1`) se
aplica directo.
**Pre-requisito de lectura**: ninguno; spec self-contained.

---

## TL;DR

- 3 vistas: **Dashboard agricultor** (default), **Pollen
  sincronizando** (modal cuando hay visita activa), **Histórico de
  Rhizome** (drill-down al click).
- Toda la información viene de **3 endpoints REST que ya existen**
  (`/health`, `/status`, `/policy/by-target/{id}`). No tienes que
  pedirme nada nuevo para v0.
- **Polling cada 5-10s**, no WebSocket en v0.
- **Castellano**, todo. Tipografía Manrope + IBM Plex Mono según
  tu pack visual; tokens `signal.seed` como acento de "inteligencia
  activa" cuando el LLM acaba de redactar.
- Tres estados visuales clave para el agricultor: **mode=normal**
  (verde/calma), **mode=conservative** (amarillo/atención),
  **mode=alert** (rojo/acción).

---

## 1. Contexto del producto

### Quién es el usuario

Agricultor pequeño/mediano. Sienta delante del portátil casero
después de que Pollen (Android) haya vuelto del campo. Quiere ver
**en una pantalla** qué pasa con sus parcelas, sin tener que abrir
una hoja de Excel ni leer logs.

### Qué hace en su sesión típica (~3-5 minutos)

1. Abre el portátil → ve dashboard.
2. Mira card por Rhizome: ¿está estable? ¿hay alerta?
3. Si hay alerta, lee el rationale (240 caracteres en castellano
   natural) y decide si hace algo manual o espera la próxima visita.
4. Si tiene curiosidad, hace click en una card → ve histórico de esa
   parcela.
5. Cierra la pantalla.

### Lo que NO hace en esta UI

- No edita policies (eso lo decide Evaluator + Pollen vía
  MissionPatch).
- No envía bundles (eso lo hace Pollen).
- No interactúa directamente con el LLM (en v0; Fase 3 del plan IA
  añadirá `/chat` post-MVP).

---

## 2. Endpoints disponibles (lo que ya existe en :13000)

### `GET /health`

```json
{
  "status": "ok",
  "version": "0.1.0",
  "port": 13000,
  "llm_mode": "real" | "stub_disabled",
  "adapter_url": "http://localhost:12000" | null,
  "bundles_received_total": 12,
  "policies_emitted_total": 9,
  "decisions_by_rule": {
    "confirm_policy": 5,
    "conservative_policy": 2,
    "alert_policy": 2,
    "refuse": 0
  },
  "targets_known": ["rhizome_01", "rhizome_02"]
}
```

**Para qué**: header del dashboard (estado del sistema, llm_mode chip,
contadores globales).

### `GET /status`

```json
{
  "targets_known": ["rhizome_01", "rhizome_02"],
  "targets": [
    {
      "target_node_id": "rhizome_01",
      "bundles_received": 7,
      "last_bundle_at": "2026-05-04T10:30:00",
      "policies_emitted": 6,
      "latest_policy_id": "pkt_meristem_xxx",
      "latest_policy_emitted_at": "2026-05-04T10:30:05",
      "latest_policy_mode": "normal",
      "latest_policy_valid_until": "2026-05-11T10:30:05Z",
      "latest_reason_code": "STABLE_BUNDLE",
      "latest_rule_applied": "confirm_policy"
    },
    { "target_node_id": "rhizome_02", "...": "..." }
  ]
}
```

**Para qué**: cuerpo del dashboard. Una card por elemento de
`targets[]`.

### `GET /policy/by-target/{target_node_id}`

```json
{
  "schema_version": "1.0",
  "policy_id": "pkt_meristem_xxx",
  "target_node_id": "rhizome_01",
  "valid_until": "2026-05-11T10:30:05Z",
  "mode_default": "normal",
  "rules": { "...": "..." },
  "rationale": "Texto técnico para auditoría",
  "signature": "<placeholder-meristem-v0>"
}
```

Devuelve `null` si nunca se emitió policy para ese target (caso REFUSE
puro).

**Para qué**: vista C (drill-down). Para v0 también vale para mostrar
el `rationale` técnico si el agricultor pulsa "ver detalle".

### Sin endpoint de `rationale_for_operator` directo

⚠️ **El `rationale_for_operator` (240 chars en castellano natural)
NO está en `/policy/*` — solo viaja en la respuesta de `POST /visit`**.
Para v0 de UI, **no lo cacheemos en frontend**. Vista de "última frase
amable al operador" lo dejamos como deuda explícita post-v0:

- **Opción A (preferida)**: yo añado el campo en una próxima iteración
  (modificar persistencia + `/status`/`/policy/by-target` para
  devolverlo). ~30 min de trabajo. Lo abro como issue separado.
- **Opción B (bypass v0)**: por ahora la UI muestra solo
  `latest_reason_code` traducido a frase corta predefinida
  (mapeo cliente-side, ver §5 abajo).

Confirmo con Bea cuál opción tomamos para v0.

---

## 3. Vista A — Dashboard agricultor (default, `/ui`)

### Wireframe ASCII

```
┌──────────────────────────────────────────────────────────────────┐
│  Sprout · Meristem-nodo                              [LLM: Real] │
│                                                                  │
│  Tu parcela hoy                            Última sync: hace 12m │
│                                                                  │
│  ┌────────────────────────┐  ┌────────────────────────┐          │
│  │ rhizome_01    ●        │  │ rhizome_02    ●        │          │
│  │ Estable                │  │ ALERTA                 │          │
│  │                        │  │                        │          │
│  │ "Tu Rhizome sigue      │  │ "Hay alerta persistente│          │
│  │ funcionando bien.      │  │ en el nodo. Modo       │          │
│  │ He extendido la        │  │ ALERTA hasta que       │          │
│  │ política una semana."  │  │ revises a mano..."     │          │
│  │                        │  │                        │          │
│  │ Válida hasta 11 mayo   │  │ Válida hasta 11 mayo   │          │
│  │                        │  │                        │          │
│  │ 7 bundles · 6 policies │  │ 3 bundles · 3 policies │          │
│  └────────────────────────┘  └────────────────────────┘          │
│                                                                  │
│  ┌─ Trazabilidad ─────────────────────────────────────────────┐ │
│  │  Reglas aplicadas en total:                                 │ │
│  │  ● confirm: 5    ● conservative: 2    ● alert: 2  ● refuse: 0│ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### Componentes

#### Header

- **Logo Sprout + título "Meristem-nodo"**: texto Manrope 600.
- **Chip `[LLM: Real]` o `[LLM: Stub]`** según `llm_mode`. Real =
  acento `signal.seed`; Stub = gris discreto.

#### Sub-header

- **"Tu parcela hoy"** (texto grande Manrope 600).
- **"Última sync: hace Xm"** — relativo al `last_bundle_at` más
  reciente entre todos los `targets`.

#### Grid de Cards (una por Rhizome)

- **N columnas** según breakpoint:
  - Mobile (<600px): 1 columna
  - Tablet (600-1000): 2 columnas
  - Desktop (>1000): 3 columnas

#### Card de Rhizome

**Estructura**:

| Campo | Origen `/status.targets[]` | Notas |
|---|---|---|
| Título | `target_node_id` | Mono (IBM Plex Mono) |
| Indicador color | derivado de `latest_policy_mode` | `normal`=verde, `conservative`=amarillo, `alert`=rojo, `null`=gris (no hubo policy) |
| Estado | `latest_reason_code` traducido (ver §5) | Texto Manrope 500 |
| Frase al operador | `rationale_for_operator` (cuando exista, ver opción A/B en §2) | Texto Manrope 400, italic |
| Validez | `latest_policy_valid_until` formateado ("11 mayo") | Texto pequeño |
| Contador | `bundles_received` + `policies_emitted` | Mono pequeño |
| Badge delta | mostrar si `bundles_received > policies_emitted` (= REFUSEs) | "1 rechazo" en rojo discreto |

**Click sobre la card** → navega a vista C (Histórico).

#### Footer trazabilidad

- **`decisions_by_rule`** como pequeñas pills horizontales con
  contadores. Una por regla. Color por regla:
  - `confirm_policy` → verde
  - `conservative_policy` → amarillo
  - `alert_policy` → rojo
  - `refuse` → gris

### Polling

Refresh `GET /health` y `GET /status` cada **5 segundos** (configurable
mediante atributo `data-refresh-ms` en el body). Si Pollen está activo
(detectable por `bundles_received_total` que crece), bajar a 2 segundos
durante los siguientes 30 segundos.

### Estados especiales

- **0 targets conocidos**: mostrar empty state amable: "Aún no has
  recibido ninguna visita de Pollen. Cuando llegue la primera, esta
  pantalla se actualizará."
- **`llm_mode=stub_disabled`**: chip ámbar "LLM apagado". Cards siguen
  funcionando con rationale stub.
- **`/health` o `/status` no responde**: banner rojo arriba "Meristem
  no responde — comprueba que el servicio está corriendo." Botón
  "Reintentar".

---

## 4. Vista B — Pollen sincronizando (modal/banner)

**Trigger**: cuando `bundles_received_total` aumenta vs el último
poll. Aparece banner azul arriba del dashboard durante 30 segundos
(o hasta que el contador se estabilice).

### Wireframe ASCII

```
┌──────────────────────────────────────────────────────────────────┐
│ ⚡  Pollen acaba de visitar                                  [×] │
│                                                                  │
│  rhizome_01: bundle recibido → policy emitida (mode: normal)    │
│  • 1 bundle nuevo · 1 policy nueva                              │
└──────────────────────────────────────────────────────────────────┘
```

### Lógica

- Detectar incremento en `bundles_received_total` o
  `policies_emitted_total`.
- Identificar qué `target_node_id` cambió comparando snapshots de
  `/status` antes y después.
- Mostrar banner con animación entrada (fade) durante 30s.
- Botón [×] cierra manualmente.

**Nota para Venation**: este componente puede ser *toast* o *banner
fijo*; tú decides según tu sistema visual. Mi sugerencia: banner fijo
arriba más cómodo en pantalla doméstica que toast lateral.

---

## 5. Vista C — Histórico de Rhizome (`/ui/target/{id}`)

Drill-down al click sobre una card del dashboard.

### Wireframe ASCII

```
┌──────────────────────────────────────────────────────────────────┐
│  ← Volver                                                        │
│                                                                  │
│  rhizome_01                                              ● Normal│
│                                                                  │
│  Última policy emitida hace 12 minutos                           │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ pkt_meristem_xxx                                          │    │
│  │ mode=normal · STABLE_BUNDLE · válida hasta 11 mayo       │    │
│  │                                                           │    │
│  │ Rationale técnico (auditoría):                            │    │
│  │ "Bundle limpio: sin emergencias, sin disputas, evidencia  │    │
│  │  coherente. Meristem confirma policy activa con           │    │
│  │  valid_until extendido +7 días."                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Contadores                                                      │
│  • 7 bundles entregados · 6 policies emitidas · 1 rechazo        │
│                                                                  │
│  Histórico                                                       │
│  (próximo paso v1: timeline de últimas N visitas con tools)      │
└──────────────────────────────────────────────────────────────────┘
```

### Componentes

- **Botón volver**: a `/ui`.
- **Header**: nombre del Rhizome + indicador de modo (mismo color que
  card del dashboard).
- **Card de policy actual**: usa `GET /policy/by-target/{id}`.
- **Contadores**: del objeto `TargetStatus` correspondiente.
- **Histórico timeline**: placeholder en v0. Se llenará cuando
  expongamos tool `get_recent_history` en endpoint REST (deuda).

---

## 6. Sistema visual

Hereda directo de tu `sprout_design_pack_v1` (Soil protocol + Water
ledger). Mappings sugeridos:

| Componente UI | Token visual |
|---|---|
| Indicador modo `normal` | Soil-stable (verde tierra) |
| Indicador modo `conservative` | Water-conserve (amarillo agua) |
| Indicador modo `alert` | Soil-alert (rojo) |
| Chip `LLM: Real` | `signal.seed` (acento) |
| Chip `LLM: Stub` | gris neutro |
| Badge "rechazo" | Soil-alert atenuado |
| Tipografía títulos | Manrope 600 |
| Tipografía cuerpo | Manrope 400 |
| Tipografía mono (IDs, contadores) | IBM Plex Mono |

Si algo no cuadra con tu pack, prevalece tu pack. Yo ajusto el spec.

---

## 7. Mapeo `reason_code` → texto en castellano

Para Vista A (cards) cuando opción B (sin `rationale_for_operator`
directo). Mapeo cliente-side:

| `reason_code` | Texto en card |
|---|---|
| `STABLE_BUNDLE` | "Estable" |
| `EVIDENCE_LOW_CONFIDENCE` | "Confianza baja" |
| `PERSISTENT_EMERGENCY` | "ALERTA" |
| `HARD_LIMIT_DOMAIN` | "Límite físico" |
| `JURISDICTION_POLLEN` | "Jurisdicción Pollen" |
| `null` o desconocido | "Sin policy" |

Más texto descriptivo opcional debajo del estado:

| `reason_code` | Frase corta |
|---|---|
| `STABLE_BUNDLE` | "Tu Rhizome funciona con normalidad." |
| `EVIDENCE_LOW_CONFIDENCE` | "Datos ambiguos en la última visita." |
| `PERSISTENT_EMERGENCY` | "Hay alerta persistente. Revisa." |
| `HARD_LIMIT_DOMAIN` | "Límite del firmware ESP32." |
| `JURISDICTION_POLLEN` | "Cambio puntual: usa Pollen." |

---

## 8. Out of scope (v0)

- **Login/auth**: no aplica al usuario doméstico v0. Acceso solo desde
  el portátil físico del agricultor.
- **Multi-idioma**: solo castellano.
- **Notificaciones desktop / sonidos**: post-MVP.
- **Edición de policies**: NO. Eso es vía Pollen+MissionPatch en otra
  jurisdicción.
- **Conexión directa al LLM** (chat): Fase 3 del plan IA, post-MVP.
- **Gráficas time-series** de soil/tank: post-MVP.
- **Dark mode**: si tu pack lo soporta nativamente, sí; si no, post-MVP.

---

## 9. Sobre cómo servirlo

Cuando tengas el HTML/CSS/JS listo:

- **Opción 1 (recomendada)**: Static files servidos por FastAPI desde
  `code/meristem_node/static/`. Mounting con `app.mount("/ui",
  StaticFiles(directory="static", html=True))`. Cero infra extra. Yo
  añado el mounting cuando me digas que está listo.
- **Opción 2**: tú sirves desde un puerto separado (`:13001`) con
  cualquier cosa. Pollen no lo necesita; solo el agricultor. Pero
  añade puertos a abrir y dependencias.

Mi voto: opción 1.

---

## 10. Coordinación

**Lo que necesito de ti**:
1. Confirmar que estás conectada al proyecto y disponible para esto
   (Bea decide).
2. Estimación tuya en horas/días.
3. Si necesitas que cambie algo del spec (más datos en endpoints,
   schema diferente, granularidad distinta), dilo y lo ajusto.

**Lo que te ofrezco**:
1. Endpoints estables ya en producción, schemas validados Pydantic.
2. Bundles ejemplo en `code/meristem_node/examples/` que puedes usar
   para probar la UI sin necesitar Pollen real.
3. Stack levantable en ~10 segundos con `python -m src.main` desde
   `code/meristem_node/`.
4. Iteración rápida sobre cualquier ajuste de endpoint que necesites.

**Decisión pendiente con Bea**:
- Opción A vs B sobre `rationale_for_operator` (ver §2).

---

## 11. Referencias

- `code/meristem_node/src/main.py` — endpoints servidos
- `code/meristem_node/src/schemas.py` — Pydantic models de respuesta
- `code/meristem_node/examples/` — bundles para test
- `bitacora/2026-05-01_meristem-nodo-2rhizome-mvp-implementado_meristem.md`
  — origen de `/status`
- `bitacora/2026-05-04_plan-ia-meristem-fases-arquitectura_meristem.md`
  — visión LLM para entender el rol de la UI en el conjunto

---

Cuando me digáis "go", añado el mounting de static files en `main.py`.
Si hay ajuste de endpoint que necesites, lo abro como PR pequeño en
paralelo a tu trabajo.

— Meristem
