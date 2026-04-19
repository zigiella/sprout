# Xilema - harness E2E cross-node para #35

Fecha: 2026-04-19
Rama: `feat/simulator-cross-node-e2e-harness`
Issue principal: `#35`

## Que he hecho

- Monto un harness reproducible en `code/simulator/` para rehearsal local cross-node.
- El flujo actual encadena:
  - `Rhizome` mock
  - `Pollen` mock
  - `Meristem` real via `Ollama` local
- El harness genera artefactos versionados en `code/simulator/reports/`:
  - JSON completo
  - resumen Markdown
- Añado `Makefile`, tests y documentacion minima del simulator para que se pueda correr sin tocar codigo productivo de nodo.

## Decisiones de implementacion

1. **Vive en `code/simulator/`, no en `rhizome/` ni `meristem/`.**
   - Es infraestructura de rehearsal, no logica productiva de un nodo.

2. **Meristem corre real; Rhizome y Pollen van mockeados.**
   - Era la forma mas rapida de tener una medida E2E util sin esperar a hardware ni a `#28`.

3. **No obligo al LLM a emitir el `PolicyDelta` completo.**
   - El modelo devuelve una `advice` compacta.
   - El harness la materializa luego a `PolicyDelta` valido con `pydantic`.
   - Esto ha resultado mucho mas robusto que pedir el schema completo directo.

4. **Hard-limit de deposito fijado a 20%.**
   - Aunque el fixture canonico antiguo venia con 15, el harness ya trabaja con el limite fisico correcto.

## Verificacion

Desde `code/simulator/`:

- `python -m pytest tests`
- resultado: `5 passed`

Smoke real contra Ollama local:

- `python -m src.cross_node_e2e --model gemma4:e4b --scenario pollen_fresh_weather_review --timeout-sec 240 --num-predict 256 --hardware-label hp-probook-460-g11`

Artefactos generados:

- `code/simulator/reports/2026-04-19_gemma4-e4b_hp-probook-460-g11_cross-node-e2e.json`
- `code/simulator/reports/2026-04-19_gemma4-e4b_hp-probook-460-g11_cross-node-e2e.md`

## Lectura tecnica que me llevo

El harness funciona, pero deja una señal clara:

- `Rhizome export`: ~`0.08 ms`
- `Pollen relay`: ~`0.02 ms`
- `Meristem generate`: ~`123658 ms`
- `E2E total`: ~`123663 ms`
- `tokens/s`: ~`6.168`
- `first_token_latency`: ~`100066 ms`

Conclusion:

- el cuello de botella no esta en el encadenado entre nodos mockeados
- esta casi enteramente en `Meristem` local con `gemma4:e4b`
- para rehearsal, este harness ya nos sirve para detectar roturas de integracion
- pero tambien deja por escrito que el camino estrategico sincrono con `E4B` es demasiado lento si esperamos respuesta inmediata en una sola pasada interactiva

## Lo que queda

- abrir PR pequena que cierre `#35`
- cuando `#28` madure, cambiar el adapter de Meristem del harness para apuntar a endpoints reales (`/ingest`, `/deltas/...`) en vez de prompt directo
- ampliar con un segundo escenario versionado (`low_tank_blocked_reassessment`) cuando compense el coste de tiempo de corrida
