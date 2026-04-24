# Research Digest: Thinking Mode en Gemma 4 E4B (LiteRT-LM)
**Fecha:** 2026-04-24
**Fuentes:** `guia1-litertlm-gemma4-thinking.md`, `guia2-litertlm-gemma4-thinking.md`

## 1. El modelo tiene la capacidad, la API tiene la plomería
No existe un flag simple `think=True` en LiteRT-LM. En su lugar, el soporte de *Thinking* se articula mediante tres elementos:
1. **`extraContext`:** Inyectando `mapOf("enable_thinking" to true)` en el `ConversationConfig` para activar el flujo en la plantilla del modelo.
2. **`channels`:** LiteRT-LM soporta dividir la salida en canales (ej. el canal de respuesta principal y un canal paralelo de *thinking*).
3. **Filtros de KV Cache:** La opción `filter_channel_content_from_kv_cache=true` (disponible en la API de Python, pendiente de confirmación de exposición limpia en Android) permite que el razonamiento no contamine el historial de la conversación.

## 2. Situación de Hardware y Estabilidad
- **Gemma 4 E4B es pesado (3.65 GB).** Aunque el *model card* anuncia soporte hasta 32k tokens, la realidad comunitaria muestra fallos (*crashes* por OOM o *SIGSEGV*) en Android e iOS al superar los 4096 tokens o al usar delegados de GPU inmaduros.
- La recomendación oficial de Google para producción en Android con Gemma 4 pasa por **AICore / Gemini Nano**, no LiteRT-LM puro. Sin embargo, para portabilidad y control total (nuestro caso), LiteRT-LM sigue siendo el camino.
- **E2B vs E4B:** La comunidad reporta mucha mayor estabilidad con la versión pequeña (E2B). E4B castiga el *runtime* actual. 

## 3. Estrategia para Sprout (Fase 3)
Dado este panorama, la implementación más segura y controlada para Pollen será:
1. **System Prompt Dinámico:** Ya he creado el registro `SystemPrompts.kt` para poder conmutar e inyectar instrucciones maestras sin tocar el core.
2. **Activación de Thinking:** Empezaremos pasando el System Prompt y probaremos si inyectando `extraContext = mapOf("enable_thinking" to true)` en `ConversationConfig` logramos que la respuesta mejore, parseando la salida si fuera necesario.
3. **Fallback a Tool Use:** Si el canal de thinking nativo de LiteRT-LM resulta inestable en Kotlin, pasaremos a darle herramientas (Tools) como mecanismo alternativo de "razonamiento externo".
