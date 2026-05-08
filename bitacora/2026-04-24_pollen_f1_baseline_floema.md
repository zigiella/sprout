# Bitácora Pollen: F1 & F2 (LiteRT-LM Baseline)
**Fecha:** 2026-04-24
**Autor:** Floema & Bea

## Contexto
Transición desde MediaPipe Tasks GenAI hacia Google LiteRT-LM para la inferencia de Gemma 4 E4B en dispositivos móviles (Pixel 10 Pro), estableciendo el CPU como baseline inicial.

## Hitos Logrados
1. **Infraestructura LiteRT-LM (F1):**
   - Integración de `litertlm-android` en la aplicación.
   - Refactorización del código de inferencia usando las clases `Engine` y `Conversation`.
   - Inicialización bloqueante en `Dispatchers.IO` para asegurar que el modelo (3.4GB) cargue de forma síncrona en memoria antes de permitir iteraciones, evitando crasheos.
2. **Telemetría y Diagnóstico:**
   - Incorporación de `GenerationMetrics` para medir *Init Time*, *Time To First Token* (TTFT) y *Total Generation Time*. Esto es crítico para futuras pruebas con NPU.
3. **Gestión de Memoria y Límites (F2):**
   - Configurado `EngineConfig(maxNumTokens = 4096)` para evitar que las respuestas se trunquen prematuramente.
   - Refactorizado `LiteRtChatService` para mantener vivo el objeto `Conversation` entre envíos, dotando a Gemma de persistencia de memoria durante la sesión.

## Retos Técnicos Superados
- **Compatibilidad Kotlin/Compose:** Hubo que migrar todo el ecosistema de Compose a Kotlin 2.2.10 usando el nuevo plugin nativo `org.jetbrains.kotlin.plugin.compose` para que los metadatos más recientes de LiteRT no colisionasen con el compilador.
- **Desensamblado de API:** Dado que `sendMessageAsync` retorna un flujo de objetos de tipo `Message` (y no Strings puros como en MediaPipe), se realizó ingeniería inversa a las clases internas del AAR para extraer la estructura exacta: `chunk.contents.contents.filterIsInstance<Content.Text>().joinToString("") { it.text }`.

## Siguientes Pasos
- **F3 (Thinking):** Implementar la capacidad del modelo para auto-razonar o invocar herramientas antes de dar la respuesta final al usuario (uso del *system instruction* o tags de thinking si el modelo lo soporta nativamente).
- **F4 (Voz):** Explorar la integración de síntesis y reconocimiento de voz para convertir el chat en una interfaz puramente conversacional en tiempo real.
