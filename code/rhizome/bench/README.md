# Rhizome benchmark harness

Harness reproducible para medir inferencia local con el mismo protocolo en portatil y en Jetson.

## Objetivo

- congelar el `prompt_set.jsonl`
- congelar tambien un set pequeno de imagenes sinteticas controladas
- medir latencia, tok/s y memoria con formato estable
- separar `cold`, `warm` y `repeat` para distinguir arranque, modelo ya cargado y estabilidad
- guardar resultados comparables en `../benchmarks/`
- cambiar solo el target del runner cuando llegue el Jetson

## Archivos

- `render_synthetic_images.py` genera PNGs sinteticos deterministas en `assets/`
- `build_prompt_set.py` genera `prompt_set.jsonl` desde los schemas canonicos de `code/shared/`
- `run_ollama_benchmark.py` ejecuta el set contra la API local de Ollama
- `prompt_set.jsonl` es la fuente canonica de prompts para comparacion
- `assets/*.png` son inputs visuales controlados para el camino multimodal

## Comandos

Desde `code/rhizome/`:

```bash
make generate-images
make generate-prompts
make check-images
make check-prompts
make analyze-benchmarks
python -m bench.run_ollama_benchmark --model gemma4:e4b --hardware-label hp-probook-460-g11
python -m bench.run_ollama_benchmark --model gemma4:e4b --hardware-label hp-probook-460-g11 --phases cold,warm,repeat --repeat 3
```

## Notas

- El prompt set mezcla prompts texto puro y multimodales, y cada record declara `modality`.
- En modo `cold,warm,repeat`, `cold` fuerza descarga del modelo, `warm` hace precarga y `repeat` mide varias pasadas seguidas.
- `power_watts_avg` queda en `null` cuando el host no expone una lectura portable.
- En Jetson el runner se reutiliza sin cambiar el formato de salida; solo cambia el modelo y, si hace falta, el endpoint.
- `analyze_reports.py` convierte los JSON comprometidos en una hipotesis provisional de arquitectura para `#5`.
- Las imagenes sinteticas no intentan ser "fotos realistas"; son tarjetas visuales controladas para comparar runtimes con el mismo input.
