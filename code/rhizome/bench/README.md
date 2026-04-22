# Rhizome benchmark harness

Harness reproducible para medir inferencia local con el mismo protocolo en portatil y en Jetson.

## Objetivo

- congelar el `prompt_set.jsonl`
- medir latencia, tok/s y memoria con formato estable
- guardar resultados comparables en `../benchmarks/`
- cambiar solo el target del runner cuando llegue el Jetson

## Archivos

- `build_prompt_set.py` genera `prompt_set.jsonl` desde los schemas canonicos de `code/shared/`
- `run_ollama_benchmark.py` ejecuta el set contra la API local de Ollama
- `prompt_set.jsonl` es la fuente canonica de prompts para comparacion

## Comandos

Desde `code/rhizome/`:

```bash
make generate-prompts
make check-prompts
make analyze-benchmarks
python -m bench.run_ollama_benchmark --model gemma4:e4b --hardware-label hp-probook-460-g11
```

## Notas

- El harness soporta `image_paths`, aunque la primera version del prompt set es texto puro.
- `power_watts_avg` queda en `null` cuando el host no expone una lectura portable.
- En Jetson el runner se reutiliza sin cambiar el formato de salida; solo cambia el modelo y, si hace falta, el endpoint.
- `analyze_reports.py` convierte los JSON comprometidos en una hipotesis provisional de arquitectura para `#5`.
