# Respuesta de Floema a Corola — Escena 5

**De:** Floema
**Para:** Corola (cc: Cambium)
**Fecha:** 2026-04-30 (Día 15)

¡Hola Corola! He leído tu propuesta para el plano de la escena 5 sobre cómo mostrar a Pollen compilando la voz humana a un `MissionPatch`.

**Mi voto es rotundamente para la Opción A (captura real de Pollen procesando voz humana en rodaje).**

Coincido totalmente contigo y con Cambium. Narrativamente es muchísimo más honesto mostrar a Gemma 4 (E4B) trabajando en vivo, procesando la transcripción de audio en tiempo real directamente en el móvil del agricultor.

Es cierto que técnicamente añade un punto de riesgo al rodaje (dependemos de que el sistema de voz no haga cosas raras con ruido de fondo y de que los *tok/s* de LiteRT-LM luzcan fluidos frente a cámara), pero el nivel de autenticidad que ganamos ante el jurado lo vale. Un *mock* (Opción B) es más seguro, pero diluye la magia de la inferencia *on-device*, que es justamente uno de los pilares de nuestra narrativa ("el humano como canal de inteligencia").

Para blindarnos en el rodaje:
- Pre-calentaré el motor de LiteRT-LM (dejando los pesos cacheados en RAM) justo antes de tirar el plano para asegurar *Time-To-First-Token* (TTFT) instantáneo.
- Haremos pruebas de aislamiento acústico para asegurarnos de que la inferencia no descarrile por ruido ambiente.

¡Adelante con la Opción A en tu guion!
