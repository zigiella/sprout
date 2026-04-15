# pollen/

Aplicacion Android para el Pixel 10 Pro. Es el nodo itinerante.

## Rol

- Sync local con Rhizome via BLE + WiFi Direct
- Inferencia on-device con Gemma 4 E2B via LiteRT (plan A) o llama.cpp (plan B)
- Audit visual en vivo comparando belief de Rhizome vs observacion directa
- Generacion de weather_packets, contradiction_alerts y policy_deltas
- Transporte fisico de contexto hacia Meristem

Detalle completo en [`docs/11_pollen_spec.md`](../../docs/11_pollen_spec.md).

## Stack

- Kotlin + Jetpack Compose
- Google AI Edge LiteRT / MediaPipe LLM Inference API
- Android BLE + WiFi P2P APIs
- `kotlinx.serialization` para schemas JSON (mismos que `shared/schemas/`)

## Estructura (a construir)

```
pollen/
├── README.md
├── app/
│   ├── build.gradle.kts
│   ├── src/main/
│   │   ├── kotlin/net/sprout/pollen/
│   │   │   ├── MainActivity.kt
│   │   │   ├── inference/         # Gemma 4 via LiteRT
│   │   │   ├── sync/              # BLE + WiFi Direct
│   │   │   ├── schemas/           # weather_packet, etc
│   │   │   ├── ui/                # Compose screens
│   │   │   └── viewmodel/
│   │   └── res/
│   └── src/test/
├── build.gradle.kts
└── settings.gradle.kts
```

## Pendiente

- Validacion temprana: Gemma 4 E2B corre en Pixel 10 Pro via LiteRT
- Si falla LiteRT, pivotamos a llama.cpp Android en semana 1
