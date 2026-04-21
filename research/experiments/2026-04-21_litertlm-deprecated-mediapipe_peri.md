# LiteRT-LM reemplaza a MediaPipe Tasks GenAI para Gemma 4

## 1. Ficha técnica del experimento original
- **URL:** [Primeros pasos con LiteRT-LM en Android](https://ai.google.dev/edge/litert-lm/android?hl=es-419)
- **Autor/a:** Google AI Edge
- **Fecha de publicación:** Documentación actual (Última actualización ~marzo 2026)
- **Claim central:** El estándar para ejecutar modelos grandes (Gemma) en dispositivos móviles abandona MediaPipe Tasks GenAI (`.bin` / `.task`) y pasa a usar el paquete nativo LiteRT-LM con formato `.litertlm`.

## 2. Método y resultados en nuestras palabras
Google ha deprecado las dependencias anteriores de MediaPipe para GenAI y ha consolidado la inferencia de LLMs en el edge bajo el framework **LiteRT-LM**. 
El cambio implica:
- Nuevo formato de modelo obligatorio: `.litertlm` (adiós a los `.bin` y `.task`).
- Nueva dependencia en Kotlin: `com.google.ai.edge.litertlm:litertlm-android`.
- Nuevo flujo de inferencia: uso de la clase `Engine` (y `Conversation`) en lugar de `LlmInference` de MediaPipe.

## 3. Reproducción propia
Floema chocó hoy con esta pared al intentar levantar el motor localmente en Pollen con Gemma 4. El stack de inferencia antiguo simplemente no es compatible o no carga los nuevos binarios correctamente. El paso a LiteRT-LM es un bloqueo duro; la trampa estaba en intentar mantener código legado de MediaPipe.

## 4. Transferibles a Sprout
🔴 **Cambio de diseño / arquitectura**
- **@floema:** Pollen necesita migrar a `litertlm-android`. Toda la orquestación actual de la inferencia en Kotlin debe reescribirse para inicializar el `Engine` de LiteRT-LM y manejar las corrutinas mediante su API `sendMessageAsync`.
- **@xilema:** Cuando generes o provisiones los binarios cuantizados de Gemma 4 E4B para la validación en hardware, asegúrate de utilizar el conversor a formato `.litertlm` (o descargarlos desde la comunidad LiteRT en HuggingFace). Los `.bin` ya no nos sirven en Pollen ni en la integración con MCU si usan las mismas herramientas genéricas, aunque Rhizome usará C++ (LiteRT).
- **@meristem:** Si el backend distribuye o hace tracking de los binarios, el nuevo formato estándar oficial en nuestro sistema pasa a ser `.litertlm`.

## 5. No-transferibles
- La configuración de `Backend.NPU` descrita en la documentación de Google requiere librerías compartidas pesadas y soporte específico. Por ahora, nos aseguramos de que corra en CPU/GPU sin bloquearnos intentando aprovechar la NPU hasta tener un perfilado estable del consumo en el Pixel.
- El apartado de herramientas OpenAPI (`OpenApiTool`) queda fuera de scope por ahora, dado que Pollen utilizará sus propios wrappers locales para decisión agronómica.
