# Pollen — Spec tecnica del MVP

> Pollen es el nodo itinerante. No es un sincronizador con camara. Es **un segundo par de ojos con criterio propio** que desafia o confirma el belief de Rhizome en vivo.

---

## 1. Rol en el sistema

Pollen cumple cuatro funciones, las cuatro con Gemma 4 E2B on-device:

1. **Ferry meteorologico.** Lleva weather_packets desde parcelas con estacion hacia parcelas sin estacion.
2. **Auditor in situ.** Compara el belief de Rhizome con lo que Pollen observa al pasar (camara + sensores del telefono).
3. **Corrector temporal.** Si detecta contradiccion fuerte o meteo fresca incompatible con la politica vigente, propone un ajuste con TTL corto.
4. **Distribuidor de criterio.** Transporta policy_deltas y evidencia comparativa entre Rhizome y Meristem.

## 2. Hardware y stack

### 2.1 Dispositivo
- **Pixel 10 Pro de Bea** (Tensor G5, 16 GB RAM)

### 2.2 Stack de inferencia (plan A)
- **Google AI Edge LiteRT** como runtime on-device
- **MediaPipe LLM Inference API** para serving
- **Gemma 4 E2B** (texto + vision) cuantizado para movil

### 2.3 Plan B (fallback si LiteRT no madura a tiempo)
- **llama.cpp** compilado para Android (ARM64)
- Inicialmente via Termux para prototipado, luego binario nativo
- Perdemos el track LiteRT pero conservamos inferencia real on-device

### 2.4 Comunicacion con Rhizome
- **BLE** para handshake y descubrimiento
- **WiFi Direct** para transferencia de payloads (fotos, snapshots, policy deltas)
- Protocolo JSON sobre socket TCP, schemas en `code/shared/schemas/`
- Target: sync completo en menos de 30 segundos

### 2.5 UI
- **Jetpack Compose**
- Minimalista: estado del nodo, boton de sync, vista de audit, cola de deltas
- Indicador persistente "Offline" en verde cuando no hay conectividad externa

## 3. Flujo canonico del MVP (el momento WOW del video)

Este es el flujo que aparece en el video de 3 minutos, en orden exacto:

### Paso 1: Aproximacion (0-3s en video)
Bea sube a la terraza con el Pixel 10 Pro. Abre la app Sprout Pollen.

### Paso 2: Sync local (3-6s)
El telefono descubre Rhizome via BLE y establece WiFi Direct. Rhizome comparte:
- Ultimos snapshots de las dos parcelas logicas
- Belief actual: "Parcela A hidratacion OK, Parcela B hidratacion OK, politica conservador_v3, ultima foto hace 2h"
- Receipts de las ultimas 3 decisiones
- Depositos y caudal actual

### Paso 3: Audit en vivo (6-16s) — **ESTE ES EL MOMENTO WOW**
Bea apunta la camara a la Parcela B en vivo. Gemma 4 E2B on-device analiza el video stream:

- Detecta curling leve en hojas del margen superior
- Detecta tono amarillento que no aparece en la foto que Rhizome tomo hace 2h
- **Genera contradiction_alert:** "Inconsistencia entre vision_rhizome (t-2h) y vision_pollen (t-0). Estres visual emergente no registrado."

La pantalla del Pixel muestra en splitscreen:
- Arriba: la foto de Rhizome de hace 2h
- Abajo: lo que ve Pollen en vivo
- Overlay con el razonamiento de Gemma 4 E2B

### Paso 4: Nota de voz contextual (16-22s)
Bea dice: "Manana hace sol fuerte y hay mucho viento seco."
El telefono transcribe on-device y empaqueta un **weather_packet** con TTL 18h, origen manual, confianza media.

### Paso 5: Policy delta propuesto (22-28s)
Pollen consolida:
- contradiction_alert del audit
- weather_packet de la voz
- Observacion de nivel bajo de deposito desde Rhizome

Y genera un **policy_delta** propuesto: "subir prudencia temporal, ventana de riego corta, inspeccion visual en 6h". Lo muestra en UI, Bea confirma.

### Paso 6: Firmado y persistencia (28-30s)
El delta se firma y se guarda en Pollen con ruta prevista: "entregar a Meristem cuando haya sync".

### Paso 7: Viaje y entrega (aparece como "time-lapse" en el video)
Bea baja al pueblo. Sin internet el delta viaja con ella. Al llegar al bar del pueblo donde hay WiFi publico, Pollen sincroniza con Meristem.

### Paso 8: Retorno con politica revisada (proxima visita)
En la siguiente visita, Pollen trae una policy revisada desde Meristem y se la entrega a Rhizome.

### Paso 9: Caso de caducidad (el momento Safety)
En otra toma del video: Pollen trae un weather_packet con TTL vencido. Rhizome lo rechaza explicitamente con un mensaje visible: "contexto caducado, no aplicado".

## 4. Contratos de datos relevantes

Schemas completos en `code/shared/schemas/`. Resumen:

### weather_packet
```json
{
  "type": "weather_packet",
  "id": "wp_2026-04-15T17:12_pollen_pixel10",
  "origin": "pollen:voice" | "rhizome:station" | "external",
  "observed_at": "2026-04-15T17:12:00Z",
  "ttl_h": 18,
  "confidence": 0.65,
  "content": {
    "sun": "strong",
    "wind": "dry_moderate",
    "rain_prob_24h": 0.0
  }
}
```

### contradiction_alert
```json
{
  "type": "contradiction_alert",
  "id": "ca_...",
  "source": "pollen",
  "rhizome_belief_ts": "2026-04-15T15:10:00Z",
  "pollen_observation_ts": "2026-04-15T17:12:00Z",
  "subject": "parcela_b",
  "evidence": {
    "rhizome_vision_summary": "hojas sanas, color uniforme",
    "pollen_vision_summary": "curling leve margen superior, tono amarillento",
    "severity": "medium"
  }
}
```

### policy_delta
```json
{
  "type": "policy_delta",
  "id": "pd_...",
  "target_rhizome": "rhizome_02",
  "proposed_at": "2026-04-15T17:15:00Z",
  "ttl_h": 12,
  "changes": {
    "mode": "conservador+",
    "watering_window_h": 0.5,
    "visual_inspection_due_h": 6
  },
  "requires_meristem_validation": true
}
```

## 5. Que demostrar en video

- [ ] Gemma 4 corriendo en el movil (icono o overlay visible)
- [ ] "Offline" en verde durante toda la secuencia
- [ ] Splitscreen foto-de-Rhizome vs video-de-Pollen
- [ ] Razonamiento de Gemma 4 en pantalla (overlay de texto)
- [ ] Policy delta generandose on-device
- [ ] Caso de caducidad: delta/packet rechazado

## 6. Criterios de exito para el MVP

- Sync Rhizome-Pollen en <30s
- Inferencia on-device de E2B en <10s para audit visual
- Contradiction alert generada correctamente en al menos 1 escenario controlado
- Policy delta sintacticamente valido (pasa validacion de schema)
- El telefono NUNCA hace peticion a internet durante el flujo (salvo el paso de sync con Meristem al final, que se hace via WiFi local si esta disponible)

## 7. Fuera de alcance para el MVP

- Inferencia de audio ambiente (rain/wind detection): en roadmap v2
- Sincronizacion con otros Pollen (multi-phone): v2
- Notificaciones push desde Meristem: v2
- Modo "historial visual" con timeline de visitas: v2

## 8. Referencias

- [Google AI Edge LiteRT docs](https://ai.google.dev/edge/litert)
- [MediaPipe LLM Inference Android](https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference/android)
- [GEMMA4-SKILL.md](../GEMMA4-SKILL.md) seccion 4.5 (MLX y moviles)
- Hackathon Cactus track (routing entre modelos) y LiteRT track
