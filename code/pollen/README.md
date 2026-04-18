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

## Build local

Requisitos: **Android SDK 34**, **JDK 17**, **Gradle 8.6+**.

```bash
cd code/pollen
gradle wrapper --gradle-version 8.6   # genera ./gradlew si no existe
./gradlew assembleDebug                # compila APK debug
./gradlew testDebugUnitTest            # corre tests unitarios JVM
```

Si no tienes Android SDK local (entorno sin soporte para herramientas Android): **usa el CI**. Cada push a rama `feat/pollen-*` dispara [el workflow de CI](../../.github/workflows/pollen-ci.yml) que compila y corre tests en un runner con SDK. Los resultados aparecen en el PR.

## CI

Workflow: [`.github/workflows/pollen-ci.yml`](../../.github/workflows/pollen-ci.yml).

Se dispara en:
- `push` a ramas `feat/pollen-**`
- `pull_request` a `main` cuando toca `code/pollen/**`

Ejecuta:
- `gradle assembleDebug` — compila APK debug
- `gradle testDebugUnitTest` — tests unitarios JVM

Los reportes de test se suben como artifact (`pollen-test-reports`) para inspeccion post-failure.

**Regla dura:** PR con CI en rojo no se mergea. Documentado en CONTRIBUTING §9.

## Pendiente

- Validacion temprana: Gemma 4 E2B corre en Pixel 10 Pro via LiteRT
- Si falla LiteRT, pivotamos a llama.cpp Android en semana 1
- Screenshot tests / instrumented tests en emulador (issue aparte si llega a hacer falta)
