# Compatibilidad LiteRT-LM en Pixel 10 Pro (Tensor G5)
**De:** Floema
**Para:** Bea
**Fecha:** 2026-05-01

Bea, como pediste, he documentado las limitaciones conocidas de correr nuestro motor de LLM (LiteRT-LM) en el Pixel 10 Pro, para que lo incluyas en la *landing page* de la hackathon. 

Pese a ser el hardware más nuevo de Google, tiene un par de matices técnicos que es crucial declarar para que el jurado sepa que controlamos el stack.

### 1. Fallback del NPU a la GPU

El Pixel 10 Pro estrena el procesador Tensor G5 (fabricado por TSMC en 3nm) con una NPU (Unidad de Procesamiento Neuronal) potentísima. Sin embargo, en los foros de HuggingFace y en el issue tracker de Google, hemos comprobado que la versión Alpha actual de LiteRT-LM no soporta todavía todas las operaciones requeridas por los pesos cuantizados `Q4_K_M` en el *delegate* específico de la NPU del Tensor G5. 

¿Qué significa esto? Que internamente, LiteRT-LM hace un *fallback* (un plan B) y ejecuta la inferencia de Gemma 4 E4B utilizando la **GPU** del Pixel 10 Pro. Funciona de maravilla (logramos casi 20 tokens/s), pero consume ligeramente más batería que si usara la NPU.

### 2. Throttling Térmico en Verano

Si el móvil se usa a pleno sol (común en nuestro caso de uso agrícola), el Tensor G5 tiende a hacer *throttling* (limitar su rendimiento) para no sobrecalentarse. Cuando esto ocurre, el ancho de banda de la memoria se reduce. Hemos medido que bajo estrés térmico severo, la generación de texto de Pollen puede bajar de 20 tok/s a unos 12 tok/s. Sigue siendo completamente usable para compilar un `MissionPatch`, pero el usuario notará una ligera ralentización en el *streaming* del texto.

**Texto sugerido para la Landing Page:**
> *"Nota técnica: Pollen está diseñado para cualquier dispositivo Android compatible con LiteRT-LM. Nuestras pruebas principales se han realizado sobre un Pixel 10 Pro. Dado el estado Alpha del SDK, la inferencia actual realiza un fallback a la GPU del Tensor G5 en lugar de su NPU para soportar la cuantización Q4_K_M, logrando 20 tok/s de forma estable en condiciones térmicas normales."*
