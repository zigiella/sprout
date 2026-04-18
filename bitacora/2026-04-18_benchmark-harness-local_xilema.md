# Xilema - benchmark harness local para #5

Fecha: 2026-04-18
Rama: `feat/rhizome-benchmark-harness`
Issue: `#5`

## Objetivo de esta pieza

Preparar desde ya el harness reproducible del benchmark de Rhizome para que, cuando llegue el Jetson, solo cambie el target del runner y no el protocolo de medida.

## Lo que he implementado

- `code/rhizome/bench/` como harness de benchmark.
- `build_prompt_set.py` genera `prompt_set.jsonl` a partir de ejemplos canonicos de `code/shared/schemas/examples/`.
- `prompt_set.jsonl` queda congelado con 25 prompts representativos de:
  - decision local
  - auditoria de `PolicyDelta`
  - receipts
  - weather / TTL
  - safety / handoff
- `run_ollama_benchmark.py` ejecuta el set contra Ollama local y guarda JSON estable en `code/rhizome/benchmarks/`.
- El runner captura:
  - latencia wall-clock
  - first-token latency aproximada (`load_duration + prompt_eval_duration`)
  - tok/s (`eval_count / eval_duration`)
  - pico de memoria del sistema
  - metadata de host, runtime y modelo
- `Makefile` y tests minimos para verificar que el prompt set y los agregados no se rompen.

## Validacion tecnica

En `code/rhizome/`:

```bash
python -m bench.build_prompt_set --check
python -m pytest tests
```

Resultado: `7 passed`.

## Corridas locales guardadas

Host local:
- `HP ProBook 460 16 inch G11`
- `Windows 11`
- `16 GB RAM`
- `ollama 0.21.0`

Resultados guardados en `code/rhizome/benchmarks/`:

- `2026-04-18_gemma2-2b_hp-probook-460-g11_smoke.json`
  - 4/4 prompts OK
  - p50 latencia: `54.2 s`
  - tok/s avg: `8.976`
  - RAM peak: `14.4 GiB`
- `2026-04-18_gemma2-9b_hp-probook-460-g11_smoke.json`
  - 1/1 prompt OK
  - latencia: `222.2 s`
  - tok/s avg: `2.325`
  - RAM peak: `15.464 GiB`
- `2026-04-18_gemma4-e4b_hp-probook-460-g11_smoke.json`
  - 2/2 prompts OK
  - p50 latencia: `106.2 s`
  - tok/s avg: `6.274`
  - RAM peak: `15.463 GiB`

## Lectura honesta

- El harness ya sirve y deja resultados comparables.
- `gemma2:2b` local es usable como proxy rapido para validar prompts y runner.
- `gemma2:9b` en este host va muy lento y cerca del techo de memoria; sirve como referencia de peor caso, no como entorno de trabajo agradable.
- Estos numeros **no cierran #5**. Falta:
  - repetir en Jetson Orin Nano Super
  - medir termicas sostenidas
  - comparar contra `llama.cpp`
  - proponer umbrales de fallback en `docs/10_rhizome_spec.md`

## Nota de metodo

Las corridas comprometidas hoy son `smoke`, no la matriz final completa. Las he usado para validar:

1. que el prompt set congela bien el tipo de carga
2. que el runner mide lo que necesitamos
3. que los proxies `gemma2:2b` y `gemma2:9b` ya pueden correrse localmente

Cuando llegue el Jetson, la siguiente pasada deberia reutilizar el mismo `prompt_set.jsonl` y el mismo formato de salida JSON.
