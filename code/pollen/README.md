# pollen/

**Abstract:**
Pollen is the mobile edge-node of the Sprout agricultural ecosystem, built as an Android application for Pixel 10 Pro. It operates as the "roaming brain" of the farm, acting as an offline bridge between the central Meristem server and the remote Rhizome micro-controllers. Pollen handles synchronous data transport via local HTTP APIs and relies entirely on on-device LLM inference using the cutting-edge Gemma 4 E4B model. By integrating native `16kHz .wav` audio capturing with Google's `LiteRT-LM` framework, Pollen enables multi-modal, natural language interactions with farm operators directly in the field, with zero reliance on cloud connectivity. It validates agricultural policies, records field observations, and evaluates complex voice commands deterministically before syncing back to the base station.

**Build Flavors:**
- **`demo` flavor:** Uses a deterministic mock evaluator to simulate model decisions instantly. Ideal for UI testing, fast iteration, and simulator deployments without requiring heavy model downloads or specific hardware.
- **`device` flavor:** The production-ready hardware path. Integrates the real `LiteRT-LM` pipeline bound to an on-device Gemma 4 E4B model. Requires Android 12+ (API 31+) and a device with NPU/GPU capabilities for interactive generation speeds.

---

Aplicación Android para el Pixel 10 Pro. Es el **nodo itinerante** del sistema Sprout.

## Rol

- Sync local con Rhizome vía **HTTP polling** sobre WiFi (Rhizome expone fachada HTTP de lectura en el Jetson).
- Inferencia on-device con **Gemma 4 E4B vía LiteRT-LM** (Google AI Edge), con **audio multimodal nativo**: la app graba `.wav` 16 kHz desde el micrófono y lo inyecta directamente al modelo sin pipeline STT separado.
- Compilación de la intención humana en un `MissionPatch` estructurado con caducidad.
- Validación cruzada (`ValidationStamp`) del estado de Rhizome contra la observación directa del operario.
- Transporte físico de contexto (`WeatherDigest`, `MissionPatch`) hacia Meristem entre visitas.

Detalle completo en [`docs/11_pollen_spec.md`](../../docs/11_pollen_spec.md).

## Stack

- **Kotlin** + Jetpack Compose para UI.
- **LiteRT-LM Android** (`com.google.ai.edge.litertlm:litertlm-android`) para inferencia Gemma 4 E4B con audio multimodal.
- **`kotlinx.serialization`** para los schemas JSON (compartidos con `code/shared/schemas/`).
- **Ktor / OkHttp** para HTTP polling contra Rhizome y Meristem.

## Build flavors

La app se construye en dos flavors distintos:

| Flavor | Para qué | Inferencia | Modelo requerido | APK |
|--------|----------|------------|------------------|-----|
| **`demo`** | Emulador, dispositivos sin recursos, walkthrough de la UI sin modelo | Mock LiteRT determinista | Ninguno | [`demo/pollen-demo.apk`](../../demo/pollen-demo.apk) (~39 MB) |
| **`device`** | Pixel 10 Pro u otro Android 12+ real, con Gemma 4 E4B local | LiteRT-LM real | `gemma-4-E4B-it.litertlm` (3,6 GB) side-loaded vía ADB | Build local |

La separación vive en `app/src/demo/.../llm/LiteRtInfra.kt` (mock) vs `app/src/device/.../llm/LiteRtInfra.kt` (real LiteRT-LM con `sendAudioFile()`).

## Cómo probar el device build con Gemma 4 E4B real

1. **Compilar** el variant `deviceRelease` desde `code/pollen/`:
   ```bash
   ./gradlew assembleDeviceRelease
   ```
2. **Descargar el modelo** compatible con LiteRT-LM (`gemma-4-E4B-it.litertlm`) desde Kaggle o HuggingFace.
3. **Side-loadear el modelo** vía ADB:
   ```bash
   adb push gemma-4-E4B-it.litertlm /data/local/tmp/gemma-4-E4B-it.litertlm
   ```
4. **Instalar el APK** y abrir la app. En el primer arranque, en la pantalla **"Download Manager"**:
   - Pulsa **"Saltar (ya tengo el modelo en dispositivo)"**.
   - Confirma la ruta `/data/local/tmp/gemma-4-E4B-it.litertlm` (o cámbiala si lo subiste a otro lado).
   - Pulsa **"Confirmar"**.
5. **Permisos**: la app solicitará permiso de micrófono para procesar comandos de voz. Acéptalo para probar el flujo audio → `MissionPatch`.

Requisitos del dispositivo:
- Android 12 / API 31+
- 12 GB RAM recomendado, 16 GB ideal
- Al menos 6 GB libres en almacenamiento
- CPU runtime es la ruta estable; el rendimiento GPU/NPU varía por dispositivo

## Structure (real, post-day-27)

```
pollen/
├── README.md
├── build.gradle.kts
├── settings.gradle.kts
├── gradlew + gradle/wrapper/   # Gradle 9.3.1 vía wrapper
└── app/
    ├── build.gradle.kts        # flavors demo + device
    └── src/
        ├── main/kotlin/net/sprout/pollen/
        │   ├── MainActivity.kt
        │   ├── voice/          # PollenVoiceInfra.kt + AudioClipRecorder.kt
        │   ├── llm/            # SystemPrompts (real engines viven en flavors)
        │   ├── inference/      # MiniEvaluator (deterministic guard rails)
        │   ├── schemas/        # MissionPatch, WeatherDigest, ValidationStamp, FieldVisit, etc.
        │   ├── sync/           # RhizomeMockClient + real HTTP clients
        │   └── ui/             # HomeScreen, VisitarRhizomeScreen, VisitarMeristemScreen, VoiceBetaPanel, ChatFeature
        ├── demo/kotlin/net/sprout/pollen/llm/LiteRtInfra.kt    # mock determinista
        ├── device/kotlin/net/sprout/pollen/llm/LiteRtInfra.kt  # real LiteRT-LM
        └── test/kotlin/net/sprout/pollen/
            ├── inference/MiniEvaluatorTest.kt   # REFUSE_RETRY, REFUSE_HARD, APPLY_AS_IS, APPLY_CONSERVATIVE
            └── schemas/RoundTripTest.kt          # validación JSON ↔ Kotlin
```

## Build local

Requisitos: **Android SDK 34**, **JDK 17**, **Gradle 9.3.1+** (incluido en el wrapper).

```bash
cd code/pollen
./gradlew assembleDebug            # APK debug (flavor demo por defecto)
./gradlew assembleDeviceRelease    # APK device flavor (LiteRT-LM real)
./gradlew testDebugUnitTest        # tests unitarios JVM
```

Si no tienes Android SDK local: **usa el CI**. Cada PR contra `main` que toque `code/pollen/**` dispara [el workflow](../../.github/workflows/pollen-ci.yml) que compila y corre tests en un runner Ubuntu con SDK.

## CI

Workflow: [`.github/workflows/pollen-ci.yml`](../../.github/workflows/pollen-ci.yml).

Se dispara en:
- `push` a ramas `feat/pollen-**`
- `pull_request` a `main` cuando toca `code/pollen/**` o el propio workflow

Ejecuta (usando el wrapper local, garantizando Gradle 9.3.1):
- `./gradlew assembleDebug` — compila APK debug
- `./gradlew testDebugUnitTest` — tests unitarios JVM

Los reportes de test se suben como artifact (`pollen-test-reports`) para inspección post-failure.

**Regla dura:** PR con CI en rojo no se mergea. Documentado en CONTRIBUTING §9.

## Lógica anti-nonsense (Mini Evaluator)

`MiniEvaluator.kt` aplica cuatro chequeos deterministas antes de aplicar cualquier `MissionPatch` propuesto por el LLM:

1. **Schema validation** — el JSON emitido debe casar con el contrato `MissionPatch`.
2. **No conflict with hard limits** — la política propuesta no puede violar el sobre de seguridad del firmware.
3. **Syntactic-semantic match** — al menos un keyword o número del transcript debe aparecer en el rationale o en los campos del patch.
4. **Explicit model confidence** — si LiteRT-LM expone `logprobs`, el umbral es 0,7.

Si cualquiera falla, Pollen responde con `REFUSE_RETRY` o `REFUSE_HARD` (cuatro casos cubiertos en `MiniEvaluatorTest.kt`). **La negativa es una feature del producto, no un fallo.**

## Bitácora

Material de bitácora relevante:
- `bitacora/2026-04-27_draft-issue-litertlm-thinking_floema.md` — primer intento LiteRT-LM, problemas iniciales.
- `bitacora/2026-05-01_litertlm-pixel10pro-compatibility_floema.md` — validación Pixel 10 Pro.
- `bitacora/2026-05-12_PR-voice-beta-final_floema.md` — descripción consolidada del PR voice-beta-final.
- `research/04_litertlm_thinking_pt1.md`, `pt2`, `digest` — investigación comparativa LiteRT-LM vs MediaPipe.


---

## Note on language

The English **Abstract** at the top of this file is the canonical public summary. The body below is in Spanish — it is the working language of the team and the place where decisions, trade-offs and trace get written. The contracts, code and tests are inspectable without Spanish context. See [Language note in the root README](../../README.md#language-note) for the project-wide policy.
