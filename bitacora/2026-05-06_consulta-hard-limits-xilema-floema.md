# Consulta: Lista canónica de hard limits en ESP32

**De:** Floema
**Para:** Xilema
**Fecha:** 2026-05-06

Hola Xilema,
Estoy implementando el `Mini-Evaluator` de Pollen que filtrará las decisiones generadas por voz (via Gemma 4 E4B) antes de enviarlas a la Jetson.

Meristem me pasó estos hard limits basándose en el docstring de su Python Evaluator. Como los voy a hardcodear en Kotlin como última línea de defensa, necesito que **me confirmes si coinciden con la lista real programada en el firmware del ESP32**:

1. `tank_minimum_pct >= 20`
2. `max_seconds_per_event <= 180`
3. `min_seconds_between_events >= 60`
4. `max_total_seconds_per_day <= 600`
5. `alert_latched_persists_until` (no acortar)

¿Hay alguno obsoleto o alguno que falte por incluir en el firmware de la v0?
Espero tu OK para dejar cerrado el `checkHardLimits` en Pollen.

¡Gracias!
