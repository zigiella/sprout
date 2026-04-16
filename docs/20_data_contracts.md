# Data contracts de Sprout — v1.0

**Estado:** cerrado v1.0 (2026-04-16).
**Autora:** Cambium.
**Publico objetivo:** Xilema (Rhizome), Floema (Pollen), Dev Meristem (cuando entre).

---

## 0. Que es este documento

Este es el **contrato de datos** entre los tres nodos de Sprout. Define exactamente que viaja por el sistema, con que forma, que es obligatorio, que es opcional, y quien lo produce y lo consume.

Es un contrato duro. Una vez mergeada esta v1.0, **no se reabre salvo bitacora + acuerdo de Bea y Cambium**. Si surge un bloqueo real, se escribe entrada en bitacora, se discute, y se bumpea la version.

### Por que importa

Sin este documento, Xilema escribe un `RhizomeSnapshot` con un campo, Floema lo parsea esperando otro, y nada funciona. Con este documento, cada una puede trabajar en paralelo, con mocks, y sabe que cuando se integren va a encajar.

### Principios

1. **Un solo source of truth.** Los schemas se implementan en Python (Pydantic) en `code/shared/schemas/` y se replican en Kotlin (Pollen) con `kotlinx.serialization`. Si divergen, gana la version Pydantic.
2. **Todo en JSON.** No hay formatos binarios en v1.0. Serializacion directa, legible, debuggeable con `curl`.
3. **UTF-8 + ISO-8601 UTC.** Sin excepciones.
4. **Campos opcionales explicitos.** Si un campo puede faltar, el schema lo marca con `Optional` / `nullable`. No hay campos "a veces aparecen".
5. **IDs humanamente legibles.** Nada de UUIDs puros. Los IDs llevan prefijo semantico y timestamp para que al verlos en un log o en un overlay de video se entiendan solos.

---

## 1. Convenciones comunes

### 1.1 Campos base (presentes en TODOS los schemas)

| Campo | Tipo | Obligatorio | Descripcion |
|-------|------|:-----------:|-------------|
| `schema_version` | string `"major.minor"` | si | En v1.0: siempre `"1.0"` |
| `created_at` | string ISO-8601 UTC | si | Instante de creacion, ej: `"2026-04-16T14:32:05Z"` |
| `origin_node_id` | string | si | Nodo que creo el objeto |
| `signature` | string o `null` | no | HMAC-SHA256 hex. En MVP puede ser `null`. Reservado para integridad futura. |

### 1.2 Formato de IDs

Formato canonico: `<prefijo>_<node>_<iso_compact>_<nonce>`

- `<prefijo>`: `snap`, `pol`, `delta`, `pkt`, `alert`, `rec`
- `<node>`: `rhizome_01`, `pollen_01`, `meristem_01` (kebab)
- `<iso_compact>`: `YYYYMMDDThhmmss` (ISO-8601 sin separadores)
- `<nonce>`: 4 chars hex aleatorios

**Ejemplos validos:**
```
snap_rhizome_01_20260416T143205_a3f2
pol_rhizome_01_20260416T090000_b814
delta_meristem_01_20260416T100000_c92d
pkt_rhizome_01_20260416T083015_d5e7
alert_pollen_01_20260416T112230_f108
rec_rhizome_01_20260416T143210_91ba
```

Longitud tipica: ~35-40 chars. Legible a simple vista. Ordenable alfabeticamente por tiempo.

### 1.3 Enums

#### `NodeType`
```
"rhizome" | "pollen" | "meristem"
```

#### `Mode` (modo operativo de Rhizome)
```
"normal" | "conservative" | "alert"
```

#### `ActionType` (acciones que Rhizome puede decidir)
```
"WATER_A"       # regar parcela A
"WATER_B"       # regar parcela B
"WATER_BOTH"    # regar ambas (poco comun)
"SKIP"          # no regar, seguir observando
"DEFER"         # posponer decision N minutos
"ALERT"         # marcar alerta pero no actuar
"BLOCK"         # bloquear riego forzadamente
"SHUTDOWN"      # parada defensiva (depositos vacios, fallo grave)
```

#### `ContradictionType`
```
"sensor_vs_vision"      # humedad dice ok, camara ve estres
"policy_expired"        # politica activa ya caduco
"deposit_inconsistent"  # sensor nivel vs caudal historico no cuadran
"flow_vs_pump"          # bomba activa pero caudalimetro no registra
"weather_conflict"      # meteo nueva contradice politica vigente
"tank_underflow"        # deposito por debajo de minimo seguro
```

#### `Severity`
```
"info" | "warning" | "critical"
```

#### `WeatherProvenance`
```
"local_station"   # captura propia (ej: Ecowitt)
"ferried"         # Pollen la trajo de otra parcela
"forecast_api"    # API externa (cuando hay conectividad)
```

### 1.4 Reglas duras de parseo

- **Campo desconocido:** se ignora silenciosamente (forward compatibility). No se rechaza el mensaje.
- **Campo obligatorio ausente:** error de validacion. Se rechaza y se logea.
- **Campo de tipo incorrecto:** error de validacion. Se rechaza.
- **Enum con valor no listado:** error de validacion. Se rechaza.
- **Timestamp sin `Z` (zulu):** error de validacion. Todos los timestamps son UTC explicito.

---

## 2. Los 6 schemas

### 2.1 RhizomeSnapshot

**Proposito:** instantanea del estado del nodo Rhizome en un momento dado.

**Quien lo produce:** Rhizome (cada 60s por defecto, configurable).
**Quien lo consume:** Pollen (via `/snapshot` endpoint), Meristem (indirectamente via Pollen).
**Persistencia:** SQLite local en Rhizome (tabla `snapshots`, retencion configurable).

```json
{
  "schema_version": "1.0",
  "created_at": "2026-04-16T14:32:05Z",
  "origin_node_id": "rhizome_01",
  "signature": null,

  "snapshot_id": "snap_rhizome_01_20260416T143205_a3f2",
  "mode": "normal",

  "active_policy_id": "pkt_rhizome_01_20260416T083015_d5e7",
  "active_policy_expires_at": "2026-04-17T08:30:15Z",

  "sensors": {
    "soil_moisture_a_pct": 38.2,
    "soil_moisture_b_pct": 41.7,
    "tank_level_pct": 72.0,
    "flow_rate_lpm": 0.0,
    "last_reading_at": "2026-04-16T14:31:58Z"
  },

  "vision": {
    "last_capture_at": "2026-04-16T14:25:00Z",
    "parcel_a_status": "healthy",
    "parcel_b_status": "healthy",
    "visual_notes": "hojas firmes, color normal en ambas parcelas"
  },

  "health": {
    "cpu_temp_c": 58.4,
    "cpu_load_pct": 41.0,
    "ram_used_gb": 4.8,
    "ram_total_gb": 7.4,
    "esp32_heartbeat_ok": true,
    "last_esp32_ack_at": "2026-04-16T14:32:00Z"
  },

  "last_decision_id": "rec_rhizome_01_20260416T143000_91ba",
  "pending_contradictions": []
}
```

**Tabla de campos especificos:**

| Campo | Tipo | Obligatorio | Notas |
|-------|------|:-----------:|-------|
| `snapshot_id` | string | si | ID canonico |
| `mode` | `Mode` enum | si | Modo operativo actual |
| `active_policy_id` | string | si | ID de la `PolicyPacket` que se esta aplicando |
| `active_policy_expires_at` | ISO-8601 UTC | si | TTL de la politica activa |
| `sensors.soil_moisture_a_pct` | float 0-100 | si | Humedad suelo parcela A |
| `sensors.soil_moisture_b_pct` | float 0-100 | si | Humedad suelo parcela B |
| `sensors.tank_level_pct` | float 0-100 | si | Nivel deposito agua |
| `sensors.flow_rate_lpm` | float >=0 | si | Caudal instantaneo (L/min) |
| `sensors.last_reading_at` | ISO-8601 UTC | si | Timestamp de la lectura mas reciente |
| `vision.last_capture_at` | ISO-8601 UTC | no | `null` si todavia no hay captura |
| `vision.parcel_a_status` | string libre | no | Puede ser: `"healthy"`, `"mild_stress"`, `"severe_stress"`, `"unknown"` |
| `vision.parcel_b_status` | string libre | no | Idem |
| `vision.visual_notes` | string libre | no | Texto generado por el modelo, max 500 chars |
| `health.cpu_temp_c` | float | si | Temperatura Jetson |
| `health.cpu_load_pct` | float 0-100 | si | Carga CPU |
| `health.ram_used_gb` | float | si | RAM en uso |
| `health.ram_total_gb` | float | si | RAM total |
| `health.esp32_heartbeat_ok` | bool | si | Heartbeat con ESP32 OK |
| `health.last_esp32_ack_at` | ISO-8601 UTC | no | Ultimo ACK, `null` si ESP32 nunca respondio |
| `last_decision_id` | string | no | `null` si todavia no se ha tomado decision |
| `pending_contradictions` | array de `alert_id` | si | Puede ser `[]`, nunca `null` |

**Validaciones duras:**
- `soil_moisture_*_pct` y `tank_level_pct` deben estar en rango 0-100
- `cpu_temp_c` razonable: -20 a 120 (rechazo fuera de ese rango como error de sensor)
- `mode` solo uno de los 3 valores del enum

---

### 2.2 PolicyPacket

**Proposito:** la politica de riego vigente para un nodo. Es el documento que guia las decisiones.

**Quien lo produce:** Meristem (cuando emite una politica nueva). En bootstrap inicial, Rhizome puede crear una politica default.
**Quien lo consume:** Rhizome (la aplica), Pollen (la transporta).
**Persistencia:** Rhizome guarda la activa + historico en SQLite.

```json
{
  "schema_version": "1.0",
  "created_at": "2026-04-16T08:30:15Z",
  "origin_node_id": "meristem_01",
  "signature": null,

  "policy_id": "pkt_rhizome_01_20260416T083015_d5e7",
  "target_node_id": "rhizome_01",
  "valid_until": "2026-04-17T08:30:15Z",

  "version_chain": [
    "pkt_rhizome_01_20260415T083015_1234",
    "pkt_rhizome_01_20260416T083015_d5e7"
  ],

  "mode_default": "normal",

  "rules": {
    "watering_window": {
      "start_hour_local": 6,
      "end_hour_local": 9
    },
    "soil_moisture_thresholds": {
      "parcel_a": { "min_pct": 35.0, "target_pct": 55.0 },
      "parcel_b": { "min_pct": 30.0, "target_pct": 50.0 }
    },
    "max_watering_duration_s": 45,
    "daily_water_budget_liters": 8.0,
    "tank_minimum_pct": 15.0,
    "require_vision_confirmation": false,
    "conservative_triggers": [
      "tank_level_below_30",
      "no_pollen_visit_48h",
      "policy_expires_within_3h"
    ]
  },

  "rationale": "Post-lluvia del 15 abril. Humedad general alta. Subir umbrales parcela B que suele retener mas.",
  "notes": "Primera iteracion tras validacion semanal."
}
```

**Campos clave:**

| Campo | Tipo | Obligatorio | Notas |
|-------|------|:-----------:|-------|
| `policy_id` | string | si | ID canonico |
| `target_node_id` | string | si | Politica especifica para un Rhizome concreto |
| `valid_until` | ISO-8601 UTC | si | Caducidad dura. Pasada esta hora, Rhizome entra en modo `conservative` |
| `version_chain` | array de `policy_id` | si | Historia hasta este packet. El primero es el bootstrap |
| `mode_default` | `Mode` enum | si | Modo por defecto cuando la politica entra en vigor |
| `rules.watering_window.start_hour_local` | int 0-23 | si | Hora local de inicio ventana de riego |
| `rules.watering_window.end_hour_local` | int 0-23 | si | Hora local de fin |
| `rules.soil_moisture_thresholds.*` | objeto | si | Por parcela, con `min_pct` y `target_pct` |
| `rules.max_watering_duration_s` | int | si | Limite duro por accion de riego |
| `rules.daily_water_budget_liters` | float | si | Presupuesto diario total |
| `rules.tank_minimum_pct` | float 0-100 | si | Por debajo de esto, no se riega |
| `rules.require_vision_confirmation` | bool | si | Si `true`, decision requiere check visual reciente |
| `rules.conservative_triggers` | array de string | si | Condiciones que activan modo conservador |
| `rationale` | string | no | Por que esta politica es asi (texto libre humano) |
| `notes` | string | no | Notas adicionales |

**Validaciones duras:**
- `valid_until > created_at`
- `watering_window.end_hour_local > start_hour_local` (no soportamos ventanas que cruzan medianoche en v1.0)
- `tank_minimum_pct >= 10.0` (nunca permitimos vaciar el tanque por debajo del 10% por defecto)
- `max_watering_duration_s <= 120` (limite duro del schema; el firmware ESP32 lo valida tambien)

---

### 2.3 PolicyDelta

**Proposito:** cambio incremental sobre una `PolicyPacket` existente. Mas barato de transportar que reenviar la politica entera.

**Quien lo produce:** Meristem.
**Quien lo consume:** Rhizome (aplica el delta y genera un `PolicyPacket` nuevo).
**Persistencia:** Rhizome guarda el delta + el nuevo packet resultante.

```json
{
  "schema_version": "1.0",
  "created_at": "2026-04-16T15:00:00Z",
  "origin_node_id": "meristem_01",
  "signature": null,

  "delta_id": "delta_meristem_01_20260416T150000_c92d",
  "target_node_id": "rhizome_01",
  "base_policy_id": "pkt_rhizome_01_20260416T083015_d5e7",

  "patches": [
    {
      "op": "replace",
      "path": "rules.soil_moisture_thresholds.parcel_b.min_pct",
      "value": 32.0
    },
    {
      "op": "replace",
      "path": "rules.daily_water_budget_liters",
      "value": 10.0
    },
    {
      "op": "add",
      "path": "rules.conservative_triggers",
      "value": "humidity_below_25_forecast"
    }
  ],

  "rationale": "Forecast Pollen trae humedad baja esperada en 24h. Subir budget y anadir trigger.",
  "ttl_seconds": 86400,
  "priority": "normal"
}
```

**Campos clave:**

| Campo | Tipo | Obligatorio | Notas |
|-------|------|:-----------:|-------|
| `delta_id` | string | si | ID canonico |
| `target_node_id` | string | si | Rhizome al que se aplica |
| `base_policy_id` | string | si | Politica sobre la que se aplica. Si Rhizome tiene otra activa, rechaza el delta |
| `patches` | array de operacion | si | Estilo JSON Patch (RFC 6902 simplificado) |
| `patches[].op` | enum: `"replace"`, `"add"`, `"remove"` | si | Operacion |
| `patches[].path` | string | si | Ruta con puntos, ej: `rules.max_watering_duration_s` |
| `patches[].value` | any | depende | Requerido para `replace` y `add`, prohibido para `remove` |
| `rationale` | string | no | Explicacion humana del cambio |
| `ttl_seconds` | int | si | Caducidad del delta. Si llega tarde, Rhizome lo rechaza |
| `priority` | enum: `"low"`, `"normal"`, `"high"`, `"critical"` | si | Orden de aplicacion |

**Validaciones duras:**
- `base_policy_id` debe existir en el historico de Rhizome. Si no, rechazo.
- `patches[].path` debe referirse a un campo existente en el schema de `PolicyPacket`.
- Si tras aplicar todos los patches el `PolicyPacket` resultante viola sus propias validaciones (ej: `max_watering_duration_s=300`), se rechaza el delta entero.
- `ttl_seconds` entre 60 y 604800 (1 semana max).

---

### 2.4 WeatherPacket

**Proposito:** observacion meteorologica con provenance y TTL.

**Quien lo produce:** Rhizome (si tiene estacion local), Pollen (cuando trae de otra parcela o API externa).
**Quien lo consume:** Rhizome (para reinterpretar la politica), Meristem (para estrategia).
**Persistencia:** Rhizome guarda los ultimos N packets en ventana temporal.

```json
{
  "schema_version": "1.0",
  "created_at": "2026-04-16T12:15:00Z",
  "origin_node_id": "pollen_01",
  "signature": null,

  "packet_id": "pkt_weather_pollen_01_20260416T121500_e7a2",
  "observed_at": "2026-04-16T11:45:00Z",
  "observed_by_node_id": "rhizome_02",
  "provenance": "ferried",
  "valid_until": "2026-04-16T17:45:00Z",

  "location": {
    "lat": 42.1828,
    "lon": 1.9931,
    "altitude_m": 1100,
    "label": "Castellar de n'Hug, parcela A"
  },

  "measurements": {
    "temperature_c": 18.4,
    "humidity_rel_pct": 62.0,
    "pressure_hpa": 1013.5,
    "rain_last_1h_mm": 0.0,
    "rain_last_24h_mm": 2.4,
    "wind_speed_kmh": 8.2,
    "wind_direction_deg": 220,
    "solar_radiation_wm2": 485,
    "uv_index": 4.8
  },

  "confidence": 0.85,
  "notes": "Estacion WS90 en rhizome_02. Ultima calibracion hace 3 semanas."
}
```

**Campos clave:**

| Campo | Tipo | Obligatorio | Notas |
|-------|------|:-----------:|-------|
| `packet_id` | string | si | ID canonico |
| `observed_at` | ISO-8601 UTC | si | Cuando se hizo la observacion (no cuando llego) |
| `observed_by_node_id` | string | si | Quien la observo originalmente |
| `provenance` | `WeatherProvenance` enum | si | `local_station` / `ferried` / `forecast_api` |
| `valid_until` | ISO-8601 UTC | si | Cuando deja de ser util |
| `location.lat` | float -90 a 90 | si | Latitud WGS84 |
| `location.lon` | float -180 a 180 | si | Longitud WGS84 |
| `location.altitude_m` | float | no | Altitud metros |
| `location.label` | string | no | Etiqueta humana |
| `measurements.*` | todos opcionales | no | Al menos uno debe estar presente |
| `confidence` | float 0-1 | si | Confianza en la medicion |
| `notes` | string | no | Texto libre |

**Reglas de TTL recomendadas por medida (aplicadas por quien emite):**

| Medida | TTL recomendado |
|--------|-----------------|
| Temperatura | 3h |
| Humedad relativa | 3h |
| Presion | 6h |
| Lluvia ultima 1h | 2h |
| Lluvia ultimas 24h | 12h |
| Viento | 1h |
| Radiacion solar | 2h (solo diurno) |
| UV | 2h (solo diurno) |

Si un `WeatherPacket` incluye varias medidas, el `valid_until` es el **minimo** de las TTLs aplicables.

**Validaciones duras:**
- `observed_at <= created_at` (no se permite meteo del futuro)
- `valid_until > created_at`
- `confidence` en rango [0, 1]
- Si `provenance == "local_station"`, entonces `observed_by_node_id == origin_node_id`

---

### 2.5 ContradictionAlert

**Proposito:** registro de inconsistencia detectada. Disparador de modo conservador o alerta.

**Quien lo produce:** Rhizome (cuando sus propios sensores se contradicen) o Pollen (cuando lo que observa al pasar no cuadra con lo que el snapshot de Rhizome decia).
**Quien lo consume:** Rhizome (modula modo y decision), Meristem (aprende patrones).
**Persistencia:** Rhizome + historico en Meristem.

```json
{
  "schema_version": "1.0",
  "created_at": "2026-04-16T13:22:30Z",
  "origin_node_id": "pollen_01",
  "signature": null,

  "alert_id": "alert_pollen_01_20260416T132230_f108",
  "target_node_id": "rhizome_01",
  "contradiction_type": "sensor_vs_vision",
  "severity": "warning",

  "observed_at": "2026-04-16T13:20:00Z",
  "evidence": {
    "sensor_reading": {
      "source": "snap_rhizome_01_20260416T131800_4c5e",
      "soil_moisture_a_pct": 42.0
    },
    "vision_reading": {
      "source": "pollen_capture_20260416T132015",
      "assessment": "severe_stress",
      "notes": "Hojas claramente caidas en parcela A, decoloracion en los bordes."
    }
  },

  "recommended_action": "defer_and_review",
  "expires_at": "2026-04-16T19:22:30Z",
  "rationale": "Humedad 42% es razonable en estacion seca, pero el estado visual indica estres claro. Puede haber sensor mal calibrado o problema de raiz."
}
```

**Campos clave:**

| Campo | Tipo | Obligatorio | Notas |
|-------|------|:-----------:|-------|
| `alert_id` | string | si | ID canonico |
| `target_node_id` | string | si | Rhizome afectado |
| `contradiction_type` | `ContradictionType` enum | si | |
| `severity` | `Severity` enum | si | Define si bloquea o solo loggea |
| `observed_at` | ISO-8601 UTC | si | Cuando se detecto |
| `evidence` | objeto | si | Estructura depende del type. Ver tabla abajo. |
| `recommended_action` | string | no | Enum informal: `"defer_and_review"`, `"block_watering"`, `"request_policy_review"`, `"continue_with_caution"` |
| `expires_at` | ISO-8601 UTC | si | TTL de la alerta |
| `rationale` | string | no | Explicacion humana |

**Estructura de `evidence` por `contradiction_type`:**

| Type | Campos obligatorios de evidence |
|------|-------------------------------|
| `sensor_vs_vision` | `sensor_reading` + `vision_reading` |
| `policy_expired` | `policy_id`, `expired_at` |
| `deposit_inconsistent` | `tank_level_pct`, `flow_history_summary` |
| `flow_vs_pump` | `pump_active_from`, `flow_rate_observed` |
| `weather_conflict` | `active_policy_id`, `conflicting_weather_packet_id` |
| `tank_underflow` | `tank_level_pct`, `minimum_threshold_pct` |

**Validaciones duras:**
- Si `severity == "critical"`, entonces `recommended_action` debe ser uno de: `"block_watering"`, `"request_policy_review"`.
- `expires_at > created_at`

**Comportamiento inducido en Rhizome:**

| Severity | Efecto |
|----------|--------|
| `info` | Se registra. Ninguna accion inmediata. |
| `warning` | Se registra. Modo pasa a `conservative` mientras la alerta esta viva. |
| `critical` | Se registra. Modo pasa a `alert`. Siguiente accion bloqueada hasta resolucion. |

---

### 2.6 DecisionReceipt

**Proposito:** acta de cada decision importante. La pieza mas visible en el video y en el writeup.

**Quien lo produce:** Rhizome cada vez que su policy_engine produce una decision.
**Quien lo consume:** visualizacion (overlay), auditoria, Meristem (para analisis de calidad).
**Persistencia:** SQLite Rhizome. Retention minimo 30 dias.

```json
{
  "schema_version": "1.0",
  "created_at": "2026-04-16T14:30:10Z",
  "origin_node_id": "rhizome_01",
  "signature": null,

  "decision_id": "rec_rhizome_01_20260416T143010_91ba",
  "snapshot_id": "snap_rhizome_01_20260416T143005_a3f2",
  "active_policy_id": "pkt_rhizome_01_20260416T083015_d5e7",

  "action": "WATER_A",
  "action_params": {
    "duration_s": 30,
    "expected_liters": 1.5
  },

  "rationale_short": "Humedad A en 38%, por debajo del umbral 45%. Dentro de ventana de riego. Deposito al 72%.",
  "rationale_full": "El snapshot reciente muestra humedad parcela A al 38.2%, umbral minimo 45% segun politica vigente pkt_...d5e7. Hora local 08:32 dentro de ventana 06-09. Deposito al 72%, muy por encima del minimo 15%. Vision confirma planta sana (healthy). Sin alertas de contradiccion activas. Se autoriza riego parcela A por 30s, ~1.5L esperados.",

  "policy_refs": [
    "rules.soil_moisture_thresholds.parcel_a.min_pct",
    "rules.watering_window",
    "rules.tank_minimum_pct"
  ],

  "contradictions": [],
  "confidence": 0.87,

  "executed": true,
  "execution_details": {
    "sent_to_esp32_at": "2026-04-16T14:30:10Z",
    "esp32_ack_at": "2026-04-16T14:30:11Z",
    "esp32_ack_status": "OK",
    "actual_duration_s": 30.2,
    "flow_observed_lpm": 3.1,
    "estimated_liters_actual": 1.56
  },

  "blocked_reason": null
}
```

**Campos clave:**

| Campo | Tipo | Obligatorio | Notas |
|-------|------|:-----------:|-------|
| `decision_id` | string | si | ID canonico |
| `snapshot_id` | string | si | Snapshot que se uso como entrada |
| `active_policy_id` | string | si | Politica aplicada |
| `action` | `ActionType` enum | si | |
| `action_params` | objeto | si | Parametros especificos de la accion. Estructura por action. |
| `rationale_short` | string | si | **Max 180 chars.** Apto para overlay de video. Regla dura. |
| `rationale_full` | string | si | Razonamiento completo, max 2000 chars. |
| `policy_refs` | array de string | si | Rutas del `PolicyPacket` que se aplicaron |
| `contradictions` | array de `alert_id` | si | Vacio si no habia |
| `confidence` | float 0-1 | si | Confianza del modelo en la decision |
| `executed` | bool | si | Si llego a ejecutarse fisicamente |
| `execution_details` | objeto | no | Obligatorio si `executed==true`, prohibido si `executed==false` |
| `blocked_reason` | string | no | Obligatorio si `executed==false`, prohibido si `executed==true` |

**Estructura de `action_params` por `action`:**

| Action | Campos |
|--------|--------|
| `WATER_A`, `WATER_B`, `WATER_BOTH` | `duration_s` (int), `expected_liters` (float) |
| `SKIP` | `next_check_in_s` (int) |
| `DEFER` | `defer_until` (ISO-8601), `reason` (string) |
| `ALERT` | `alert_id` (string referenciando `ContradictionAlert`) |
| `BLOCK` | `blocked_action` (string), `reason` (string) |
| `SHUTDOWN` | `reason` (string), `recoverable` (bool) |

**Validaciones duras:**
- `len(rationale_short) <= 180`. **Regla no negociable.**
- `len(rationale_full) <= 2000`
- `confidence` en [0, 1]
- Si `executed==true`: `execution_details` requerido, `blocked_reason` debe ser `null`.
- Si `executed==false`: `blocked_reason` requerido (string no vacio), `execution_details` debe ser `null`.
- Si `action in [WATER_*]` y `executed==true`: `execution_details.actual_duration_s <= active_policy.rules.max_watering_duration_s`.

---

## 3. Flujos tipicos

### 3.1 Ciclo de decision local (solo Rhizome)

```
1. sensors_loop genera lecturas
2. Rhizome construye RhizomeSnapshot
3. policy_engine aplica PolicyPacket activa al snapshot
4. Produce DecisionReceipt (action, rationale, etc.)
5. safety_layer valida DecisionReceipt contra reglas duras
6. Si valido -> enviar a ESP32 -> esperar ACK -> completar execution_details
7. Persistir DecisionReceipt en SQLite
```

### 3.2 Visita de Pollen (sync completo)

```
1. Pollen llega y descubre via BLE el rhizome_01
2. WiFi Direct handshake, abre canal HTTP a FastAPI de Rhizome
3. Pollen -> GET /snapshot           (recibe RhizomeSnapshot)
4. Pollen -> GET /policy/active      (recibe PolicyPacket activa)
5. Pollen -> GET /receipts?since=... (recibe DecisionReceipt historicos)
6. Pollen observa en vivo con camara + modelo local
7. Si detecta inconsistencia:
     Pollen -> POST /alert/contradiction (envia ContradictionAlert)
8. Si Pollen trae nueva meteo prestada:
     Pollen -> POST /packet/weather (envia WeatherPacket)
9. Si Pollen trae delta de Meristem:
     Pollen -> POST /delta/apply (envia PolicyDelta)
10. Rhizome aplica el delta, genera nuevo PolicyPacket, responde con el policy_id
```

### 3.3 Meristem emite nueva politica

```
1. Meristem analiza datos agregados (snapshots, alerts, receipts)
2. Decide que una politica necesita cambio
3. Emite PolicyDelta
4. Delta se guarda en queue de Meristem para el target_node_id
5. Siguiente Pollen que vaya a Meristem lo recoge
6. Pollen lo transporta a Rhizome (seccion 3.2 paso 9)
```

---

## 4. Versionado y evolucion

### 4.1 Semver simplificado

- **Minor bump** (`1.0` -> `1.1`): anadir campo opcional. Compatible hacia atras.
- **Major bump** (`1.0` -> `2.0`): cambio incompatible (quitar campo, cambiar tipo, cambiar semantica).

### 4.2 Regla dura

Cualquier cambio al schema **requiere entrada en bitacora con**:
- Motivacion del cambio
- Version antes / despues
- Migration path para nodos con version antigua
- Firma de Cambium Y Bea

Los dev (Xilema, Floema) pueden **proponer** cambios en bitacora, pero no mergean cambios de schema sin revision.

### 4.3 Compatibilidad

- Forward compatibility: parsers ignoran campos desconocidos. Un nodo v1.0 puede leer un mensaje v1.1.
- Backward compatibility dentro del mismo major: garantizada.
- Entre majors: no garantizada. Migration explicita.

---

## 5. Implementacion

### 5.1 Python (fuente de verdad)

Codigo en `code/shared/schemas/`:

```
code/shared/schemas/
├── __init__.py
├── base.py                   # BaseSchema con campos comunes
├── rhizome_snapshot.py
├── policy_packet.py
├── policy_delta.py
├── weather_packet.py
├── contradiction_alert.py
├── decision_receipt.py
├── enums.py                  # NodeType, Mode, ActionType, etc.
├── id_generator.py           # helpers para generar IDs canonicos
└── tests/
    ├── test_roundtrip.py     # obligatorio: JSON <-> Pydantic <-> JSON identico
    ├── test_validation.py
    └── examples/             # los JSON de ejemplo de este documento
```

**Reglas de implementacion:**
- Pydantic v2.
- Todos los models heredan de `BaseSchema`.
- Enums con `enum.Enum` (no strings libres).
- Validators custom para reglas que Pydantic no expresa directamente (ej: `executed==true => execution_details != null`).
- `tests/examples/` debe contener un JSON por schema exactamente igual a los ejemplos de este documento.

### 5.2 Kotlin (Pollen)

Codigo en `code/pollen/src/main/kotlin/org/zigiella/sprout/schemas/`:

- `kotlinx.serialization` con `@Serializable`.
- Mismos nombres de clase, mismos nombres de campo (camelCase en Kotlin, serializador a snake_case si hiciera falta — en v1.0 los nombres JSON son snake_case).
- Tests de roundtrip obligatorios: el mismo JSON de ejemplo debe parsear igual en Python y en Kotlin.

### 5.3 Tests cruzados

Una vez cada pieza implementada, Xilema y Floema deben correr un test cruzado:

1. Python genera un `RhizomeSnapshot` valido y lo serializa a JSON.
2. Kotlin parsea ese JSON.
3. Kotlin lo vuelve a serializar.
4. Python parsea el JSON de Kotlin.
5. Los dos dicts deben ser iguales.

Este test es **condicion de merge** del PR que integre Python↔Kotlin.

---

## 6. Ejemplos canonicos

Los JSONs completos de esta seccion se guardan tambien en `code/shared/schemas/examples/` como archivos independientes para tests automaticos:

- `examples/rhizome_snapshot_01.json`
- `examples/policy_packet_01.json`
- `examples/policy_delta_01.json`
- `examples/weather_packet_01.json`
- `examples/contradiction_alert_01.json`
- `examples/decision_receipt_01.json`

Cada ejemplo debe validar correctamente al implementar los schemas. Son parte de la definicion del contrato.

---

## 7. Preguntas frecuentes anticipadas

### Por que JSON y no Protocol Buffers / MessagePack / ...

MVP primero. JSON es legible, debuggeable con `curl`, todas las librerias lo soportan. Cuando tengamos problema de ancho de banda (no lo tenemos), evaluamos. Si llega, seguramente saltamos directo a CBOR antes que a Protobuf.

### Por que signature es opcional

Porque crypto bien hecha no entra en el MVP. Pero el campo **ya existe en el schema** para que el dia que lo implementemos no haya que cambiar el contrato, solo dejar de aceptar `null`.

### Que pasa si Pollen trae un delta para una base_policy_id que Rhizome ya no tiene

Rhizome rechaza el delta con error `base_policy_not_found`. Pollen se lo devuelve a Meristem la siguiente vez, Meristem genera un `PolicyPacket` completo nuevo (no delta) para reinicializar.

### Por que rationale_short tiene limite de 180 chars

Porque se pinta como overlay en el video y en el simulador. Si cabe en ~3 lineas, el jurado lo lee. Si no cabe, el prompt del modelo esta mal diseñado. El limite es dureza de diseno, no limitacion tecnica.

### Que pasa si un DecisionReceipt tiene contradictions no vacio

No bloquea por si mismo. El flag que bloquea es `severity` de las alertas referenciadas. Una decision puede ejecutarse aun con contradictions `info` registradas (se documenta, no se frena).

---

## 8. Enlaces

- [docs/01_architecture.md](01_architecture.md) — arquitectura general
- [docs/10_rhizome_spec.md](10_rhizome_spec.md) — spec Rhizome (Xilema)
- [docs/11_pollen_spec.md](11_pollen_spec.md) — spec Pollen (Floema)
- [docs/12_meristem_spec.md](12_meristem_spec.md) — spec Meristem
- [bitacora/2026-04-15_respuesta-xilema-6-decisiones_cambium.md](../bitacora/2026-04-15_respuesta-xilema-6-decisiones_cambium.md) — la bitacora que fijaba estos schemas como prioridad 1

---

**Fin de v1.0.** Lo que hay aqui es lo que se implementa. Lo que falte aqui, no existe en el MVP.
