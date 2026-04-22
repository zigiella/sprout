# Rhizome benchmarks

Resultados versionados del harness de benchmark de `code/rhizome/bench/`.

## Naming

```
YYYY-MM-DD_<modelo>_<hardware>.json
```

Ejemplo:

```text
2026-04-18_gemma4-e4b_hp-probook-460-g11.json
```

## Tabla comparativa

| Fecha | Modelo | Hardware | Requests OK | p50 latencia ms | p95 latencia ms | tok/s avg | RAM peak GiB | Notas |
|------|--------|----------|------------:|----------------:|----------------:|----------:|-------------:|-------|
| 2026-04-18 | `gemma2:2b` | `hp-probook-460-g11` | 4/4 | 54232.529 | 67759.539 | 8.976 | 14.400 | smoke local CPU, proxy E2B |
| 2026-04-18 | `gemma2:9b` | `hp-probook-460-g11` | 1/1 | 222169.970 | 222169.970 | 2.325 | 15.464 | smoke local CPU, proxy E4B, 1 prompt |
| 2026-04-18 | `gemma4:e4b` | `hp-probook-460-g11` | 2/2 | 106211.690 | 117911.550 | 6.274 | 15.463 | smoke local CPU, valida harness con Gemma 4 |

## Lectura

- `demo-pass`: funciona una vez con salida coherente
- `engineering-pass`: repite sin fallos en frio/caliente
- `failed`: hubo errores, timeouts o inestabilidad en la corrida

## Alcance actual

Las corridas versionadas aqui son una validacion local del harness y de los prompts. No sustituyen el benchmark objetivo de `#5`, que sigue pendiente de repetirse en Jetson Orin Nano Super y de compararse contra `llama.cpp`.

## Analisis derivado

Para sintetizar ratios y una hipotesis provisional de arquitectura:

```bash
cd code/rhizome
make analyze-benchmarks
```

Salida actual: `2026-04-18_local-proxy-analysis.md`
