# Tarea: Batería de Pruebas A/B Thinking vs No-Thinking
**Asignado a:** Meristem
**Prioridad:** Media (Preparación para F3)

## Objetivo
Evaluar rigurosamente la diferencia de latencia, calidad y estructura de las respuestas del modelo Gemma 4 E4B (LiteRT-LM) bajo distintas configuraciones de System Prompts y activación de Thinking Mode.

## Entorno de Pruebas
- Simulador local (o dispositivo de testeo con métricas monitorizadas).
- Pollen App (rama `feat/pollen-f2-memory` o equivalente).

## Casos de Prueba (A/B Testing)
1. **Baseline (Sin Thinking):**
   - Config: `enable_thinking = false`
   - Prompt de Sistema: `SystemPrompts.AUDITOR_BASELINE`
2. **Thinking Nativo (Sin System Prompt Especial):**
   - Config: `enable_thinking = true`
   - Prompt de Sistema: Vacio o Baseline.
3. **Thinking Guiado (Con System Prompt Especial):**
   - Config: `enable_thinking = true`
   - Prompt de Sistema: `SystemPrompts.AUDITOR_THINKING_A`

## Batería de Prompts Similares a Producción
1. "Tengo este fragmento de código con un bug en SQLite. ¿Cuál es el problema?"
2. "Calcula el impacto en memoria de usar List vs Sequence en Kotlin para 1000 iteraciones."
3. "Resume el historial de nuestra conversación y dime de qué temas hemos hablado hoy."
4. "¿Cuáles son los riesgos de usar un delegado NPU inestable?"

## Entregables
- Archivo CSV o log de telemetría recogiendo `Init Time`, `TTFT`, `Total Time`, y `Output Tokens` por cada caso de uso.
- Análisis cualitativo sobre si la activación de *thinking* aporta una precisión que justifique el aumento de latencia.
- Recomendación de configuración óptima para despliegue en Pixel 10 Pro.
