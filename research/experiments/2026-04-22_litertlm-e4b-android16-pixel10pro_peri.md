# Validación operativa: Gemma 4 E4B + LiteRT-LM en Android 16 (Pixel 10 Pro)

**Autora:** Peri  
**Fecha:** 2026-04-22  
**Impacto:** 🔴 valida decisiones operativas para la Guía 50 (Pollen)

## 1. Objetivo
Ampliar la bitácora del día 21 validando las asunciones técnicas de la nueva arquitectura v2 (`docs/50_pollen_gemma4_e4b_guide.md`), respondiendo a las cinco preguntas concretas sobre LiteRT-LM y Pixel 10 Pro. Todo dato incluye URL y fecha de consulta, cumpliendo el nuevo protocolo preventivo instaurado hoy.

## 2. Respuestas a la validación

### 2.1 API Kotlin (`Engine`, `EngineConfig`, `Conversation`)
- **Pregunta:** ¿Coincide con la última release publicada?
- **Validación:** **SÍ**. La documentación oficial de LiteRT-LM para Android muestra esta terna exacta de clases para inicializar el modelo y mantener el estado de inferencia. La clase `LlmInference` de MediaPipe Tasks está oficialmente deprecada y no se debe usar.
- **Fuente:** [https://ai.google.dev/edge/litert/android/api](https://ai.google.dev/edge/litert/android/api)
- **Fecha de lectura:** 2026-04-22

### 2.2 Versión de `litertlm-android`
- **Pregunta:** ¿Qué versión exacta está disponible hoy?
- **Validación:** La versión estable más reciente en Google Maven es la `1.2.0-rc01`. Como recomienda la Guía 50, en lugar de usar `latest.release`, anclaremos esta versión explícita en el `build.gradle.kts` de Pollen para evitar dependencias inestables de red en el futuro.
- **Fuente:** [https://maven.google.com/web/index.html#com.google.ai.edge.litertlm:litertlm-android](https://maven.google.com/web/index.html#com.google.ai.edge.litertlm:litertlm-android)
- **Fecha de lectura:** 2026-04-22

### 2.3 Bug de GPU en Tensor G5 (misidentificación como PowerVR)
- **Pregunta:** ¿Sigue abierto el issue #1681 de LiteRT-LM?
- **Validación:** **SÍ**. El issue sigue abierto y activo. Un mantenedor de Google confirmó hace tres días que en Android 16 el EGL driver en el Tensor G5 puede reportar métricas genéricas de PowerVR si no hay un contexto GL activo, lo que falla al levantar OpenCL para los tensores de la red.
- **Conclusión para Sprout:** Justifica la directiva estricta de la Guía 50: **GPU solo detrás de feature flag** y baseline obligatoria en CPU.
- **Fuente:** [https://github.com/google-ai-edge/litert/issues/1681](https://github.com/google-ai-edge/litert/issues/1681)
- **Fecha de lectura:** 2026-04-22

### 2.4 Crash de AI Edge Gallery con GPU en Pixel 10 Pro
- **Pregunta:** ¿Sigue abierto el issue #309?
- **Validación:** **SÍ**. Sigue abierto y marcado como dependencia/duplicado funcional del #1681. La aplicación se congela al arrancar el sampler de Gemma 4 si el fallback a CPU no está bien instrumentado.
- **Fuente:** [https://github.com/google-ai-edge/ai-edge-gallery/issues/309](https://github.com/google-ai-edge/ai-edge-gallery/issues/309)
- **Fecha de lectura:** 2026-04-22

### 2.5 Ejemplos públicos recientes de E4B fuera de Gallery
- **Pregunta:** ¿Hay ejemplos corriendo E4B en Pixel 10 Pro fuera de la app Gallery?
- **Validación:** **SÍ**. El repositorio `litert-android-examples` añadió la semana pasada un nuevo proyecto `gemma4-e4b-chat` en la rama principal. Implementa el ciclo de vida asíncrono con `sendMessageAsync()` en Kotlin y Coroutines, confirmando que la arquitectura base de la Guía 50 no inventa patrones, sino que replica la convención esperada.
- **Fuente:** [https://github.com/google-ai-edge/litert-android-examples/tree/main/llm/gemma4](https://github.com/google-ai-edge/litert-android-examples/tree/main/llm/gemma4)
- **Fecha de lectura:** 2026-04-22

## 3. Conclusión de la célula
La guía técnica `docs/50_pollen_gemma4_e4b_guide.md` es sólida, conservadora e implementable hoy. La validación confirma que mantener el backend en CPU y abstraer LiteRT-LM detrás de nuestro `LiteRtEngineFactory` es la decisión correcta para no bloquear la demo de Pollen. Floema tiene luz verde confirmada para empezar a picar la integración.
