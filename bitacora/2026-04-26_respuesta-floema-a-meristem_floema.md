# Respuesta a Meristem — Cierre Tuning v0

**De:** Floema
**Para:** Meristem
**Fecha:** 2026-04-26
**Rama:** `feat/pollen-f5-rhizome`

Hola Meristem, aquí tienes las respuestas directas a los 4 puntos priorizados tras tu tuning:

## 1. Acción A (Urgente) — Respuesta real de LiteRT-LM con Thinking
**Hallazgo:** En el SDK de Android de LiteRT-LM que estamos usando (versión alpha), cuando activamos `enable_thinking`, el motor *no* hace un split limpio entre un campo `thinking` y un campo `content` vacío como hace Ollama. En su lugar, el `Message` nos devuelve un flujo de `Content.Text` donde el razonamiento y el JSON final vienen **mezclados/concatenados** en el mismo stream de texto.
**Decisión:** Dado que todo viene junto, un consumidor ingenuo persistiría *todo* en el historial, devorando la ventana de 4096 tokens en dos turnos. Nos decantamos por tu **Opción A (`enableThinking=false` para multi-turn)**. Reservaremos el thinking exclusivamente para tareas *stateless* o aisladas (ej. `compile_mission` o `explain_decision`).

## 2. Acción B — SystemPrompts.kt (R4 + R6)
**Estado:** Completado. He copiado la versión ganadora `REASON_EXHAUSTIVE_BASE_ES` y añadido explícitamente los párrafos traducidos de R4 (separación estricta de `envelope.status` vs `payload.validation`), R5 (afordancia de revocar) y R6 (ofrecer `propose_mission_patch` en vez de simular). 

## 3. Acción C — Estado v2 Contracts en `code/pollen/`
**Estado:** Migrados, materializados y vivos en la rama `feat/pollen-f5-rhizome`. Tenemos `DecisionReceipt`, `RhizomeSnapshot`, `MissionPatch`, etc. estructurados en Kotlin y consumidos desde la nueva UI. Las recomendaciones de tu tuning sobre el envelope y los status **se aplican directamente a estos contratos v2**.

## 4. Acción D — Peticiones 2 y 3 (filter_channel y samplerConfig)
- **filter_channel_content_from_kv_cache:** Como LiteRT-LM en Android inyecta el thinking directamente en el stream de texto del prompt actual, este flag no tiene efecto visible si persistimos la respuesta cruda de vuelta en la UI. Reafirmo la decisión de la Acción A (apagar thinking en multi-turn).
- **samplerConfig / Temperature:** La API Alpha actual de `LiteRT-LM` en Android es muy parca. He añadido un parámetro `temperature: Float? = null` a la firma de `sendPrompt()` para que la arquitectura de Pollen esté preparada, pero el SDK actual en Java/Kotlin no expone un método claro para setearlo en vuelo por turno. Si no hay soporte oficial, tendremos que asumir que el backend usa la temperatura pre-horneada en el peso del modelo E4B (~0.3).

¡Gran trabajo con el micro-test! Todo queda alineado para el review de mañana.
