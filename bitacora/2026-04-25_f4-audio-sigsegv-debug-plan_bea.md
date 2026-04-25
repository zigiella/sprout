# Plan de Debugging para SIGSEGV en Audio Nativo (Fase 4)
**Autor:** Bea
**Fecha:** 25 de Abril de 2026
**Contexto:** La integración de `Content.AudioFile` en LiteRT-LM (Gemma 4 E4B) lanza un `SIGSEGV` al procesar el archivo. Queda pausado para el MVP (se usa ASR de Android en la demo), pero este es el plan de asalto para aislar el bug cuando retomemos la funcionalidad.

---

## 1. Probar con un WAV “canónico” generado, no grabado
El objetivo es aislar si el fallo viene de la captura de Android (cabeceras mal cerradas, etc.) o del parser de LiteRT-LM.

**Generar WAV PCM16 (2s):**
```bash
ffmpeg -y -f lavfi -i sine=frequency=1000:sample_rate=16000 -t 2 -ac 1 -c:a pcm_s16le test_tone_16k_mono_pcm16.wav
```
**Generar WAV Float32 (2s):**
```bash
ffmpeg -y -f lavfi -i sine=frequency=1000:sample_rate=16000 -t 2 -ac 1 -c:a pcm_f32le test_tone_16k_mono_f32.wav
```

## 2. Normalizar el WAV real de Pollen
Si los audios generados funcionan, normalizaremos el audio capturado por Android.
```bash
ffmpeg -y -i input.wav -t 10 -ac 1 -ar 16000 -c:a pcm_s16le normalized_10s_16k_mono_pcm16.wav
```
Si LiteRT-LM acepta un WAV normalizado en PC pero no el grabado en caliente, el problema reside en la escritura de la cabecera en `PollenVoiceInfra`.

## 3. Matriz de Aislamiento por Capas
Tabla de progresión estricta para acorralar el fallo:

| Prueba | Modelo | Input | Backend | Resultado esperado |
| --- | --- | --- | --- | --- |
| Texto simple | E4B | texto | CPU | no crash |
| Texto simple | E4B | texto | GPU/NPU | no crash |
| Audio oficial | E4B | WAV Google | CPU | transcribe o falla controlado |
| Audio oficial | E4B | WAV Google | GPU/NPU | transcribe o falla controlado |
| Audio normalizado | E4B | WAV propio | CPU | transcribe o falla controlado |
| Audio normalizado | E2B | mismo WAV | CPU | comparar (E4B puede tener OOM) |
| Audio generado | E4B | tono/silencio | CPU | no crash |

*Nota:* Si E2B procesa audio y E4B crashea, el grabador queda absuelto y el problema es de memoria o lazy loading en el modelo de 3.65 GB.

## 4. Revisión de Rutas y Memoria
- **Fichero Cerrado:** Asegurar `outputStream.flush()`, `fileDescriptor.sync()`, `outputStream.close()` antes de pasar la ruta.
- **Rutas Absolutas:** Usar siempre `context.cacheDir.absolutePath`. Nada de `content://` URIs.
- **Backend CPU:** Probar siempre en CPU primero, ya que GPU/NPU suelen ser inestables con tipos multimodales en versiones alpha.
- **Ciclo de Vida (Engine):** Verificar si el crash ocurre al abrir el modelo, al crear conversación, o en el decode de audio.

## 5. Captura de Logs
Para abrir el Issue en `google-ai-edge/LiteRT-LM` (si resulta ser su bug), ejecutar:
```bash
adb logcat -c
adb logcat | grep -iE "litert|litertlm|jni|sigsegv|tombstone|miniaudio|audio|gemma|xnnpack|gpu|npu"
```
Guardar variables de entorno (Modelo E4B, SHA256, versión LiteRT, dispositivo, SoC, duración, etc.).
