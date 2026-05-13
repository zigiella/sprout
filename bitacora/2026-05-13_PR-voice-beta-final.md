# PR: feat/floema/voice-beta-final -> main

## Descripción
Este Pull Request consolida el trabajo de las últimas dos semanas en la app Pollen (Mobile), migrando el proyecto desde un estado de mock/prototipo a una aplicación completamente integrada con inferencia multimodal *on-device* mediante **LiteRT-LM** (Gemma 4 E4B).

Se introducen los `Build Flavors` (`demo` vs `device`) para poder seguir corriendo la app en entornos sin aceleración hardware, se incorpora la captura de voz nativa (`16kHz .wav`), y se migran los esquemas de datos al estándar V2 (`MissionPatch`, `WeatherDigest`, etc.).

## Cambios Principales
* **Voz a LLM (Multimodal):** Añadido `PollenVoiceInfra.kt` y `AudioClipRecorder` para grabar voz. Se envía crudo a `sendAudioFile()` de LiteRT-LM.
* **LiteRT-LM Engine:** Refactorización total de la inferencia en `LiteRtInfra.kt`. Se deja atrás el antiguo MediaPipe y se configura para cargar modelos `.litertlm`.
* **Build Flavors:** Separación en `demo` (mocks para simuladores) y `device` (acceso directo a NPUs/GPUs).
* **Nuevos Schemas V2:** Integrados `MissionPatch`, `ValidationStamp` y `WeatherDigest`. Lógica de `REFUSE_RETRY` y "nonsense" testeada en `MiniEvaluatorTest.kt`.
* **Persistencia y Red:** `PollenStore` implementado para guardar `RhizomeSnapshot` localmente y configuración de parámetros `?locale=en` en el cliente de red.

---

## 🛠️ Instrucciones de Pruebas (Para `SUBMISSION.md` / Jueces)

Para probar la versión real con aceleración por hardware (**Device Build**) y el modelo Gemma 4 E4B, siga estos pasos:

1. **Compilación / Instalación:** Asegúrese de instalar el APK del flavor `device` (por ejemplo, compilando la variante `deviceRelease`).
2. **Descarga del Modelo:** Descargue el modelo compatible con LiteRT-LM desde el repositorio oficial de Kaggle/HuggingFace (ej. `gemma-4-E4B-it.litertlm`).
3. **Empujar el Modelo vía ADB:**
   Conecte su dispositivo físico y envíe el modelo al almacenamiento temporal del móvil ejecutando en su terminal:
   ```bash
   adb push path/local/gemma-4-E4B-it.litertlm /data/local/tmp/gemma-4-E4B-it.litertlm
   ```
4. **Configuración en la App:** 
   Al abrir la app por primera vez, verá la pantalla de "Download Manager". Pulse en **"Saltar (Ya tengo el modelo en dispositivo)"**. Verifique que la ruta cargada es `/data/local/tmp/gemma-4-E4B-it.litertlm` (o cámbiela si lo subió a otro lado) y pulse "Confirmar".
5. **Permisos:** La app solicitará permiso de micrófono para procesar comandos de voz. Acéptelo para probar la integración audio-to-text nativa.
