# Local proxy analysis for Rhizome

Generated at: `2026-04-18T13:35:14Z`

## Thresholds carried into #5

- Rhizome text floor from `docs/10_rhizome_spec.md`: `>= 5.0` tok/s.
- Rhizome multimodal ceiling from `docs/10_rhizome_spec.md`: `<= 15` s.
- Provisional memory headroom guardrail for warm restarts: `>= 0.5` GiB free after peak.

## Reports

| Model | Host | Requests OK | p50 ms | p95 ms | tok/s avg | RAM peak GiB | Headroom GiB | Text floor |
|------|------|------------:|-------:|-------:|----------:|-------------:|-------------:|-----------|
| `gemma4:e4b` | `hp-probook-460-g11` | 2/2 | 106211.69 | 117911.55 | 6.274 | 15.463 | 0.002 | yes |
| `gemma2:2b` | `hp-probook-460-g11` | 4/4 | 54232.529 | 67759.539 | 8.976 | 14.4 | 1.065 | yes |
| `gemma2:9b` | `hp-probook-460-g11` | 1/1 | 222169.97 | 222169.97 | 2.325 | 15.464 | 0.001 | no |

## Observations

- En `hp-probook-460-g11`, el proxy E2B (`gemma2:2b`) supera a `gemma4:e4b` con 43.1% mas tok/s y 48.9% menos latencia p50.
- En `hp-probook-460-g11`, el proxy E2B (`gemma2:2b`) supera al proxy E4B (`gemma2:9b`) con 286.1% mas tok/s y 75.6% menos latencia p50.
- `gemma2:9b` cae por debajo del minimo de Rhizome (`5.0` tok/s) con `2.325` tok/s.
- `gemma4:e4b` deja solo `0.002` GiB de headroom en `hp-probook-460-g11`, por debajo del margen prudente de `0.5` GiB.

## Provisional architecture hypothesis

- Hipotesis provisional: Rhizome debe optimizar el loop local de decision para modelos clase E2B; cualquier E4B queda fuera del camino critico hasta que Jetson demuestre lo contrario.
- Umbral provisional para mantener Ollama como primario en Jetson: >=`5.0` tok/s en texto sostenido, p95 multimodal <=`15` s, sin OOM y con al menos `0.5` GiB de headroom tras warm restart.
- Candidato a fallback `llama.cpp`: cualquier configuracion de Ollama que no cargue, caiga por debajo del umbral de tok/s, supere el p95 multimodal o pierda estabilidad entre corridas calientes.

