# Xilema - benchmark multimodal y fases cold/warm para #5

Fecha: 2026-04-18
Rama de trabajo inicial: `feat/rhizome-multimodal-benchmark-prep`
Issue principal: `#5`
Issue de apoyo: `#33`

## Que he hecho

- Preparo una extension del harness de `code/rhizome/bench/` para cubrir dos huecos que nos faltaban antes del Jetson:
  - prompts multimodales controlados
  - separacion explicita de fases `cold`, `warm` y `repeat`
- Añado `bench/render_synthetic_images.py` para generar PNGs sinteticos deterministas en `bench/assets/`.
- Extiendo `bench/build_prompt_set.py` con 5 prompts multimodales nuevos:
  - `vision_parcel_a_dry_decision`
  - `vision_parcel_b_dry_decision`
  - `vision_tank_low_guardrail`
  - `vision_sensor_vs_snapshot_contradiction`
  - `vision_incoming_rain_mode_shift`
- Extiendo `bench/run_ollama_benchmark.py` para soportar:
  - modo clasico como hasta ahora
  - modo por fases con `--phases cold,warm,repeat`
  - reseteo del modelo antes de `cold` y `warm`
  - warmup previo a `warm`
  - resumen agregado por fase, por modalidad y por fase+modalidad
- Actualizo tests y documentacion de uso (`Makefile`, `bench/README.md`, `rhizome/README.md`).

## Decisiones que he tomado

1. **Las imagenes del benchmark no son "mockups bonitos" ni fotos.**
   - Son tarjetas visuales sinteticas y controladas.
   - Priorizo repetibilidad, trazabilidad y ligereza del repo frente a realismo.

2. **`cold` no significa solo "primer prompt".**
   - El runner fuerza descarga del modelo antes de la fase y usa `keep_alive=0`.
   - Asi la fase `cold` mide arranque real request a request.

3. **`warm` y `repeat` se separan.**
   - `warm` hace reset + warmup y luego una pasada con modelo ya cargado.
   - `repeat` mide varias pasadas consecutivas para ver estabilidad y degradacion.

4. **Cada prompt declara `modality`.**
   - Esto nos deja medir `p95` multimodal sin mezclarlo con el camino texto puro.

## Verificacion hecha

Desde `code/rhizome/`:

- `python -m bench.render_synthetic_images --check`
- `python -m bench.build_prompt_set --check`
- `python -m pytest tests`

Resultado: `13 passed`.

## Riesgo / nota operativa

- La rama local donde he construido esto esta apilada encima de `feat/rhizome-benchmark-analysis` (`PR #32`, aun abierto), no directamente sobre `main`.
- Antes de abrir PR de `#33`, conviene sacar estos cambios a una rama limpia basada en `main` para que la revision salga pequena y no mezcle el analisis previo con esta pieza nueva.

## Lo que queda

- Rehacer la rama sobre `main` y abrir PR pequeno que cierre `#33`.
- Cuando llegue el Jetson:
  - correr el mismo prompt set con `--phases cold,warm,repeat`
  - comparar `Ollama` vs `llama.cpp`
  - validar si el umbral multimodal `<15s p95` es realista o no
