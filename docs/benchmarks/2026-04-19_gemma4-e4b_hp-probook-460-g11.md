# Benchmark note — 2026-04-19 — gemma4:e4b en hp-probook-460-g11

## Contexto

Corrida smoke del harness `code/simulator/src/cross_node_e2e.py` con:

- escenario: `pollen_fresh_weather_review`
- runtime: `Ollama`
- modelo: `gemma4:e4b`
- host: `hp-probook-460-g11`

Objetivo de la corrida: comprobar que el rehearsal local `Rhizome mock -> Pollen mock -> Meristem real`
funciona de extremo a extremo y deja una medida honesta del coste estrategico.

## Resultado

La corrida fue **valida** y produjo un `PolicyDelta` materializado correctamente.

Metricas principales:

- `Rhizome export`: `0.081 ms`
- `Pollen relay`: `0.024 ms`
- `Meristem generate`: `123658.642 ms`
- `E2E total`: `123663.258 ms`
- `first_token_latency`: `100066.766 ms`
- `tokens_per_second`: `6.168`

## Hallazgo

El encadenado entre nodos mockeados no es el problema.

El cuello de botella esta casi enteramente en `Meristem` local con `gemma4:e4b`.
Esto refuerza la decision de tratar a `Meristem` como **revision diferida** y no
como capa sincronica dentro del mismo gesto interactivo de `Pollen`.

## Consecuencia practica

- El harness E2E ya sirve para rehearsal e integracion.
- La capa estrategica local con `E4B` sigue siendo util, pero no debe presentarse
  como respuesta instantanea en el mismo ciclo temporal que `Rhizome` o `Pollen`.
- Futuras comparativas deben repetir esta misma corrida en:
  - `gemma2:2b` o `gemma3:4b` como modo rehearsal
  - `Jetson Orin Nano Super 8 GB` cuando llegue el hardware
