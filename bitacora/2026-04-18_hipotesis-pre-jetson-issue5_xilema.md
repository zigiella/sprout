# Xilema - hipotesis provisional para #5 antes de Jetson

Fecha: 2026-04-18
Rama: `feat/rhizome-benchmark-analysis`
Issue principal: `#5`

## Que he hecho

- Añado `code/rhizome/bench/analyze_reports.py` para leer los JSON ya versionados del harness y convertirlos en:
  - tabla comparativa
  - observaciones con ratios
  - hipotesis provisional de arquitectura
- El analisis se guarda hoy en:
  - `code/rhizome/benchmarks/2026-04-18_local-proxy-analysis.md`

## Lectura que me llevo

Con los tres reports locales que ya teniamos:

- `gemma2:2b`:
  - `8.976 tok/s`
  - `54.2 s` p50
  - `1.065 GiB` de headroom
- `gemma4:e4b`:
  - `6.274 tok/s`
  - `106.2 s` p50
  - `0.002 GiB` de headroom
- `gemma2:9b`:
  - `2.325 tok/s`
  - `222.2 s` p50
  - `0.001 GiB` de headroom

Ratios principales:

- El proxy E2B (`gemma2:2b`) supera a `gemma4:e4b` con:
  - `43.1%` mas tok/s
  - `48.9%` menos latencia p50
- El proxy E2B supera al proxy E4B (`gemma2:9b`) con:
  - `286.1%` mas tok/s
  - `75.6%` menos latencia p50

## Hipotesis provisional

Mi lectura fuerte, antes de medir Jetson, es esta:

1. `Rhizome` debe optimizar su camino critico local para modelos clase `E2B`.
2. Cualquier configuracion clase `E4B` queda fuera del loop de decision local hasta que Jetson demuestre claramente lo contrario.
3. Mantendria `Ollama` como plan A solo si en Jetson cumple a la vez:
   - `>= 5 tok/s` sostenidos en texto
   - `<= 15 s` p95 multimodal
   - sin OOM
   - con al menos `0.5 GiB` de headroom tras warm restart
4. Si falla cualquiera de esos puntos, el candidato natural a fallback es `llama.cpp`.

## Por que me parece una conclusion razonable

- El propio `docs/10_rhizome_spec.md` ya fija `>=5 tok/s` para texto y `<15s` para multimodal.
- Incluso en el portatil de 16 GB, `gemma4:e4b` queda practicamente sin margen de memoria.
- El proxy `9b` directamente cae por debajo del suelo de Rhizome.
- El hueco entre `gemma2:2b` y `gemma4:e4b` no parece cosmetico; apunta a una diferencia de clase de uso, no solo de comodidad.

## Lo que aun NO cierro

Esto no cierra `#5` porque falta lo esencial:

- repeticion en Jetson Orin Nano Super
- termicas sostenidas
- warm restarts en Jetson
- comparativa equivalente contra `llama.cpp`
- medicion multimodal real

Pero ya me deja una postura inicial defendible para no entrar a la semana del hardware sin criterio.
