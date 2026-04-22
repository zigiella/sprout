# Rhizome — especificación v2

## 1. Rol

Rhizome es el nodo autónomo de parcela.

Su trabajo es responder esta pregunta:

> **¿Debo regar aquí y ahora, dentro de mi sobre seguro?**

## 2. Hardware y software

- Jetson Orin Nano Super 8 GB
- JetPack 6.x + MAXN SUPER + NVMe SSD + swap
- Gemma 4 E2B via **llama.cpp** (no Ollama; Ollama en Jetson no tiene mmap loading y E2B queda al limite de memoria)
- servicio local del agente Rhizome
- SQLite
- enlace serie con ESP32
- acceso a meteo local si existe
- API local para Pollen

Detalle operativo de la ruta llama.cpp en `docs/51_rhizome_gemma4_e2b_jetson_guide.md`.

## 3. Qué hace

- recibe telemetría del ESP32,
- mantiene estado materializado por parcela,
- interpreta política vigente,
- decide `WATER`, `DEFER`, `SKIP`, `BLOCK`,
- envía comandos al ESP32,
- registra `DecisionReceipt`,
- sirve bundles locales a Pollen.

## 4. Qué no hace

- no redefine estrategia de largo plazo,
- no depende de internet,
- no conduce actuadores directamente,
- no habla con otros Rhizome salvo a través de Pollen.

## 5. Entradas

### Del ESP32
- humedad A/B,
- nivel de depósito,
- caudal,
- heartbeat,
- alertas físicas.

### De su propia capa local
- política activa,
- historial de decisiones,
- weather cache,
- health local del Jetson,
- in/outbox.

### De Pollen
- `MissionPatch`,
- `WeatherDigest`,
- `ValidationStamp`,
- `VisitAmendment`,
- `PolicyPacket`.

## 6. Cálculos

### 6.1 Estado materializado
Por parcela:
- `soil_now_pct`
- `tank_now_pct`
- `flow_ok`
- `last_watered_at`
- `policy_age_h`
- `weather_age_h`

### 6.2 Scores
- `need_score`
- `risk_score`
- `belief_age_score`
- `action_envelope`

### 6.3 Modos
- `normal`
- `conservative`
- `alert`

## 7. Decisiones permitidas

- `WATER(plot, seconds)`
- `DEFER(minutes)`
- `SKIP`
- `BLOCK`
- `ALERT`

Toda acción física debe ir encapsulada y validada por el ESP32.

## 8. Uso de Gemma 4 E2B

Gemma no está en el loop para todo.
Solo entra cuando hay arbitraje o explicación.

### Casos donde sí entra
- señales contradictorias,
- misión humana nueva,
- weather digest que cambia el contexto,
- necesidad de explicar una decisión,
- relectura de política en modo prudente.

### Casos donde no entra
- depósito vacío,
- tiempo máximo excedido,
- stop de emergencia,
- heartbeat perdido,
- fallo físico claro.

## 9. Salidas

- `RhizomeSnapshot`
- `DecisionReceipt`
- `AlertEvent`
- comando serie a ESP32
- bundle para Pollen

## 10. API local para Pollen

### Lectura
- `GET /status`
- `GET /snapshot/latest`
- `GET /receipts?since=...`
- `GET /outbox`
- `GET /explain/decision/{id}`

### Escritura
- `POST /mission_patch`
- `POST /weather_digest`
- `POST /validation_stamp`
- `POST /visit_amendment`
- `POST /policy_packet`

## 11. Capa de datos de Rhizome

### SQLite
- `sensor_samples`
- `plot_state`
- `policy_active`
- `policy_history`
- `decision_receipts`
- `alerts`
- `weather_cache`
- `inbox_packets`
- `outbox_packets`
- `sync_sessions`

### Retención sugerida
- crudo de sensores: 7 días
- estado materializado: 30 días
- receipts y alertas: 90 días
- bundles enviados: hasta ACK de Pollen + 30 días

## 12. Definición de hecho

Rhizome está listo cuando puede:

1. decidir sobre dos parcelas lógicas sin internet,
2. recibir telemetría del ESP32,
3. mandar una orden y recibir ACK,
4. producir `DecisionReceipt` legible,
5. aceptar un `MissionPatch` o rechazarlo por caducidad o seguridad,
6. explicar a Pollen por qué decidió lo que decidió.
