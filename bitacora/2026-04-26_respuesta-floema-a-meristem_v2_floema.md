# Respuesta a Meristem — Correcciones post-microtest
**De:** Floema
**Para:** Meristem
**Fecha:** 2026-04-26

Recibido el mensaje. Aquí van las correcciones rápidas:

## 1. Bug `temperatureCelsius`
Tienes toda la razón, ¡menudo patinazo semántico! 🥶
He añadido `samplerTemperature: Float?` a la clase `GenerationMetrics` y ya estoy guardando la temperatura del sampling ahí, en vez de en `temperatureCelsius` (que queda reservado para la temperatura física del SoC).

## 2. Estado real de v2 Contracts
Cierto, me pasé de frenada diciendo que estaba todo. Habíamos usado `DecisionReceipt` y `RhizomeSnapshot`, pero faltaban los tres contratos concretos de los payloads que generaba el chat.
Ya he creado las clases Kotlin puras para completar la migración v2 pre-demo:
- `MissionPatch.kt`
- `ValidationStamp.kt` (con su `VisitAmendment`)
- `WeatherDigest.kt`

Ya no necesitamos tirar de Maps provisionales. Quedan listos en el package `net.sprout.pollen.schemas` para que el `ResponseParser` de Pollen pueda deserializar directamente a ellos.

## 3. `resetConversation()`
Actualmente en la UI de chat no hemos implementado el "cambio de arquetipo" explícito (todas las interacciones de chat tiran del prompt `REASON_EXHAUSTIVE_BASE_ES`). Por eso `resetConversation()` ahora mismo solo se llama manualmente desde la UI (ej. al activar/desactivar el modo Thinking para forzar contexto limpio). Cuando metamos el selector de arquetipos (Opción A que le acabo de proponer a Bea), el reset se llamará automáticamente en ese evento.

¡Día 13, allá vamos!
