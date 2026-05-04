# Mini-experimento contexto Meristem-nodo — protocolo + script

**Autora**: Meristem
**Fecha**: 2026-05-04 (día 19)
**Estado**: protocolo + script entregados; ejecución pendiente de
ventana confirmada con Bea (portátil libre de demo activa).
**Antecede**: `bitacora/2026-05-04_plan-ia-meristem-fases-arquitectura_meristem.md`
(principio "memoria por tools, no por stuffing")
**Material destino**: writeup §3 (Arquitectura).

---

## TL;DR

- **No ejecuto las corridas reales ahora** — el portátil está en uso
  para video y otras pruebas. Bloquearlo 25-90 min con stack levantado
  no es prioritario hoy.
- **Sí entrego el cómo**: script automatizado
  (`code/meristem_node/scripts/mini_exp_context.py`) + bitácora con
  protocolo, qué medir, criterios de éxito.
- **Cuando haya ventana**, ejecutar el script con un comando da
  ~25 min de gráfica para writeup §3 + datos persistidos en JSON
  para el equipo.
- **Pre-requisito menor**: `inference.py` necesita ~10 líneas de
  cambio para que `num_ctx` sea configurable. Lo abro como sub-tarea
  separada cuando se ejecute (no urgente).

---

## Pregunta de investigación

> ¿Cómo se comporta Gemma 4 E4B Q4_K_M en CPU Alder Lake variando
> `num_ctx`, en términos de latencia y calidad de rationale?

**Hipótesis (a validar)**:
1. Latencia crece **superlineal** con `num_ctx`. Doblar de 4k a 8k
   no dobla la latencia; la triplica o más.
2. Calidad del rationale **no mejora monotónicamente** con `num_ctx`
   más alto. Hay un punto de meseta (probable: 4k-8k).
3. El **rationale_chars output** es estable (~150-240) sin importar
   num_ctx, porque la regla de brevedad de Xilema actúa.

Si las hipótesis se confirman, el principio arquitectónico "memoria
por tools, no por stuffing" tiene evidencia empírica defendible.

## Diseño experimental

### Matriz de corridas

- **Bundles**: `M1` (clean), `M3` (emergency), `M6` (tool calling demo).
  Selección deliberada de los 3 reason_codes principales (CONFIRM,
  ALERT, ALERT con tool calling forzado).
- **`num_ctx` valores**:
  - **Versión LIGHT** (recomendada): `[2048, 4096, 8192, 16384]` — 4 puntos.
  - **Versión FULL**: `[1024, 2048, 4096, 8192, 16384, 32768]` — 6 puntos.
- **Repeticiones**: 1 por celda en LIGHT (12 corridas total), 2 en
  FULL (36 corridas) para promediar variabilidad.

### Tiempo estimado

- LIGHT: 12 corridas × ~2 min/corrida = **~25 min**
- FULL: 36 corridas × ~2 min/corrida = **~75 min**

Más warmup inicial del LLM (~30-60s) y carga modelo (~30s).

### Métricas a recoger por corrida

| Métrica | Origen | Para qué sirve |
|---|---|---|
| `latency_ms` | medido en cliente | Eje Y de gráfica latencia vs num_ctx |
| `prompt_tokens` (`tokens_in_iter_0`) | `decisions.llm_metrics` | Verificar que aprovechamos num_ctx |
| `output_tokens` (`tokens_out_iter_0`) | idem | Confirmar regla de brevedad |
| `tool_iterations` | idem | M6 idealmente ≥1, M1/M3 = 0 |
| `parsed_ok` | idem | Sanity: el JSON sigue válido en num_ctx altos |
| `thinking_chars_iter_0` | idem | ¿El thinking se infla con más contexto? |
| `rationale_for_operator` (chars) | response payload | ¿Sigue ≤240 chars? |

### Criterios de éxito del experimento (no del sistema)

- [ ] 12 (LIGHT) o 36 (FULL) corridas completan sin error 5xx
- [ ] Tabla CSV/JSON exportable
- [ ] Gráfica latencia vs num_ctx con 3 líneas (una por bundle)
- [ ] Si M6 dispara tool calling al menos 1 vez en algún num_ctx,
      validamos visualmente la capacidad
- [ ] `rationale_for_operator` ≤ 240 chars en todas las corridas

## Pre-requisito: hacer `num_ctx` configurable

Actualmente `code/meristem_node/src/inference.py` tiene `num_ctx=4096`
hardcodeado en `_post_chat`. Para el experimento, hay que hacer una
de dos:

### Opción A — env var (preferida, ~5 min de trabajo)

```python
NUM_CTX_DEFAULT = int(os.environ.get("MERISTEM_NUM_CTX", "4096"))
NUM_PREDICT_DEFAULT = int(os.environ.get("MERISTEM_NUM_PREDICT", "1024"))
```

Y exportar antes de cada corrida del experimento:
```bash
MERISTEM_NUM_CTX=8192 python -m src.main
```

Pero esto requiere reiniciar `meristem-node` entre corridas (lento).

### Opción B — header request (recomendada, ~10 min de trabajo)

```python
def _post_chat(adapter_url, messages, tools, num_ctx_override=None):
    payload["options"]["num_ctx"] = num_ctx_override or NUM_CTX_DEFAULT
```

Y leer en el endpoint `/visit` un header `X-Meristem-Num-Ctx` opcional.
Esto permite cambiar `num_ctx` por petición sin reiniciar el servicio.
**Mejor para el experimento**.

### Decisión

Opción B. Cuando ejecutemos el experimento, abro PR pequeño con la
modificación (~10 líneas). El script ya envía el header.

## Ejecución cuando haya ventana

```bash
# 1. Levantar stack
llama-server -m models/gemma-4-E4B-it-Q4_K_M.gguf -c 32768 --port 8080
python -m meristem_inference_adapter.main  # :12000
cd code/meristem_node
MERISTEM_USE_LLM=true python -m src.main  # :13000

# 2. Verificar
curl -s http://localhost:13000/health  # llm_mode=real

# 3. Ejecutar experimento (versión LIGHT)
python scripts/mini_exp_context.py --light --output-json results_d19.json

# 4. Generar gráfica (post-experimento, en notebook o python ad-hoc)
python -c "
import json, matplotlib.pyplot as plt
data = json.load(open('results_d19.json'))
for bundle in {r['bundle'] for r in data}:
    pts = [(r['num_ctx'], r['latency_ms']) for r in data if r['bundle']==bundle]
    plt.plot(*zip(*sorted(pts)), label=bundle, marker='o')
plt.xscale('log'); plt.xlabel('num_ctx'); plt.ylabel('latency_ms')
plt.legend(); plt.title('Latencia vs num_ctx — Meristem E4B Q4_K_M CPU')
plt.savefig('latency_vs_ctx.png', dpi=120)
"
```

## Material para writeup §3

Cuando tengamos los datos, el párrafo §3 puede incluir:

> **Latencia y contexto en CPU doméstica** (datos empíricos):
> medimos Gemma 4 E4B Q4_K_M en CPU Alder Lake variando `num_ctx`
> sobre 3 bundles representativos (M1 clean, M3 emergency, M6 con
> tool calling forzado). La latencia crece superlineal: doblar
> `num_ctx` triplica el tiempo de inferencia. Por debajo de 8k
> tokens el rationale es indistinguible en calidad respecto a 16k+.
> Esta evidencia justifica el principio de "memoria por tools, no
> por stuffing": el modelo solo carga histórico cuando lo pide
> explícitamente, y el contexto operativo (`num_ctx=4096`) cabe
> con margen para system prompt + bundle + 1-2 tool results.

(Se ajustará con los números reales cuando se ejecute.)

## Out of scope del experimento (deuda explícita)

- **Calidad cualitativa del rationale**: no medimos automáticamente.
  Para fase posterior con escala 1-5 humana sobre subset reducido.
- **Comparación E2B vs E4B vs 12B**: solo medimos E4B (modelo
  productivo de Meristem). Pollen/Rhizome miden por separado en sus
  experimentos respectivos.
- **GPU vs CPU**: hardware contrastante a cargo de Endodermis (RD04).
- **Modelos no-Gemma**: out of scope absoluto del proyecto.
- **Carga concurrente** (N requests simultáneos): no aplica al slow
  brain doméstico v0.

## Coordinación

**Con Bea**: confirmar ventana de portátil libre (preferible noche
o mañana temprano cuando Corola/video no usan).

**Con Cambium**: cuando salgan los datos, los integro al §3 en formato
literal listo para pegar (mismo patrón que la bitácora RD04 día 19).

**Con Endodermis**: si tiene curiosidad por replicar en Jetson,
cambiando el endpoint URL del script. Su hallazgo RD04 (deriva
semántica GPU vs CPU) es complementario; este experimento mide
latencia/contexto, no deriva semántica.

---

## Cierre

El protocolo está listo. El script está committeado. La modificación
de `inference.py` para `num_ctx` configurable es trivial cuando toque.
Cuando Bea me dé "go con ventana de 25 min", ejecutamos.

— Meristem
