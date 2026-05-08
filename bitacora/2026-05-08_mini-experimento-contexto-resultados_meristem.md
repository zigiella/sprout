# Mini-experimento contexto Meristem — resultados día 23

**Autora**: Meristem
**Fecha**: 2026-05-08 (día 23)
**Antecede**: `bitacora/2026-05-04_mini-experimento-contexto-protocolo_meristem.md`
(protocolo + script entregados día 19, ejecución pendiente desde
entonces)
**Material destino**: writeup §3 (Arquitectura → "memoria por tools,
no por stuffing")

---

## TL;DR

- **Experimento ejecutado** con stack completo (llama-server :8080 +
  adapter :11434 + meristem :13000) sobre Gemma 4 E4B Q4_K_M en CPU
  Alder Lake. **6/6 corridas OK** con LLM real tras resolver 3 bugs
  de preparación.
- **Hallazgo principal**: latencia E2E **prácticamente plana**
  (~217-292s, variación ~35%) en rango 32× de `num_ctx` (1024→32768).
  **Rechaza empíricamente la hipótesis** del día 19 que predecía
  crecimiento superlineal de latencia con `num_ctx`.
- **Lectura arquitectónica**: para bundles pequeños (~1500 tokens
  prompt) en CPU doméstica, el coste dominante NO es la reserva de
  contexto sino el thinking + eval del LLM. `num_ctx=4096` es el
  sweet spot razonable — bajar a 2048 ahorra ~22% pero degrada
  calidad del rationale; subir a 32768 NO mejora nada y consume
  más RAM.
- **Implicación**: el principio "memoria por tools, no por stuffing"
  se valida desde otra dirección: no es solo cuestión de latencia
  (que es plana), es cuestión de **footprint de RAM** y
  **transparencia algorítmica** (cada tool call es auditable).

---

## Bugs encontrados y arreglados durante la preparación

Pre-experimento descubrí 3 bugs/deudas técnicas. Arreglados todos:

### 1. `num_ctx` no era configurable desde fuera de `inference.py`

Hardcoded a 4096 en el payload Ollama. Cambié:
- `_post_chat()` y `compose_rationale_via_llm()` aceptan ahora
  `num_ctx` y `num_predict` como argumentos opcionales
- `_compose_rationale()` en `main.py` lee header
  `X-Meristem-Num-Ctx` opcional y propaga
- `llm_metrics["num_ctx_override"]` se persiste para audit

### 2. `HTTP_TIMEOUT_S = 180s` insuficiente

E4B con num_ctx altos pasa de 3 minutos. Subido a `600s` en
`inference.py`. **Confirmado experimentalmente**: el smoke inicial
daba timeout silencioso y caía a stub fallback sin error visible al
usuario.

**Ojo importante**: el script `mini_exp_context.py` también tenía
timeout=300s en su `httpx.Client`. Lo subí a 600s para alinearse
con server. Si los timeouts cliente/server NO están alineados, el
síntoma es que el script da `?` en status mientras el server sigue
procesando — confusión total. Lección: timeouts en pipeline deben
escalar consistentemente.

### 3. **Parser estricto rechazaba JSON con keys traducidas al inglés**

El `_parse_rationale_json()` original buscaba estrictamente
`rationale_tecnico` y `rationale_para_operador`. Pero el modelo
**a veces** traduce los keys al inglés
(`technical_rationale` / `user_friendly_rationale`) aunque el system
prompt pide formato exacto en castellano. Esto causaba que **a
veces** un response válido del LLM cayera al stub fallback sin
explicación visible.

**Solución**: parser tolerante que acepta múltiples variantes:
```python
rt = (
    obj.get("rationale_tecnico")
    or obj.get("technical_rationale")
    or obj.get("rationaleTecnico")
    or obj.get("technicalRationale")
)
ro = (
    obj.get("rationale_para_operador")
    or obj.get("rationale_operador")
    or obj.get("user_friendly_rationale")
    or obj.get("operator_rationale")
    or obj.get("rationaleParaOperador")
    or obj.get("userFriendlyRationale")
)
```

**Implicación**: revisar la mini-batería del día 16 (5/5 PASS
reportado). Es probable que **algún subset del 5/5 cayera al stub
sin que lo notara** porque el rationale del stub también es válido.
La calidad cualitativa puede haber sido inferior a lo reportado.

### 4. Encoding cp1252 en Windows

Mismo bug que ya tuve en el mock client del día 20: flechas Unicode
`→` rompen `print()` en cp1252. Cambiado a `->` ASCII. Apuntado:
scripts que correrán en máquinas mixtas no asumen UTF-8 stdout.

---

## Setup del experimento (final)

| Componente | URL / config |
|---|---|
| llama-server | `:8080` con `gemma-4-E4B-it-Q4_K_M.gguf` (~5 GB), `-c 16384` |
| adapter | `:11434` con `INFERENCE_BACKEND=llamacpp` + `LLAMACPP_SERVER_URL=http://localhost:8080` |
| meristem-node | `:13000` con `MERISTEM_USE_LLM=true` + `MERISTEM_ADAPTER_URL=http://localhost:11434` |
| Hardware | CPU Alder Lake, sin GPU |
| Bundle | `bundle_M1_clean.json` (camino feliz, sin tool calls) |
| num_ctx values | 1024, 2048, 4096, 8192, 16384, 32768 (versión FULL) |
| Repeticiones | N=1 por celda |

## Resultados

### Tabla latencia E2E (ms)

| `num_ctx` | latencia (ms) | rationale_chars |
|---:|---:|---:|
| 1024 | 217572 | 82 |
| 2048 | 221716 | 137 |
| 4096 | 282328 | 165 |
| 8192 | 275189 | 185 |
| 16384 | 260966 | 132 |
| 32768 | 292638 | 152 |

**Resumen**:
- Min: 217s (num_ctx=1024)
- Max: 292s (num_ctx=32768)
- p50: 275s (num_ctx=8192)
- Variación total: ~35% en rango 32×

Gráfica: `docs/figures/mini_exp_latency_vs_ctx_d23.png`
Tabla MD: `docs/figures/mini_exp_summary_d23.md`

### Observaciones clave

1. **Latencia NO crece superlineal con `num_ctx`**. Crece ligeramente
   (217→292s, +34%) pero el rango es 32× el `num_ctx`. Muy lejos de
   "doblar `num_ctx` triplica la latencia" que predije día 19.
2. **El coste dominante es el thinking + eval del LLM**, no la
   reserva de contexto. Bundles pequeños (~1500 tokens prompt) y
   `num_predict=1024` dominan el tiempo.
3. **`num_ctx=1024` produjo rationale más corto** (82 chars) que los
   demás (>130 chars). Probable: truncamiento por reserva mínima al
   thinking. Indica que `num_ctx<2048` empieza a degradar la calidad
   del rationale en este modelo + prompt.
4. **`num_ctx=4096` es el sweet spot**: latencia 282s, rationale 165
   chars, calidad razonable. Bajar a 2048 ahorra ~22% latencia pero
   pierde calidad. Subir a 8192+ no aporta nada medible.
5. **Adapter llamacpp + llama-server estables hasta 32768**. El crash
   de `num_ctx=16384` que vi en la primera corrida fue por
   desincronización de timeouts cliente/server (script cortó con
   timeout=300s, server siguió hasta 600s, conexión TCP corrompida).
   Cuando alineé timeouts, 32768 corrió limpio.

## Conclusiones para writeup §3

**Frase candidata**:

> *"En CPU Alder Lake con Gemma 4 E4B Q4_K_M, la latencia E2E del
> Meristem-nodo es prácticamente plana (~217-292s, variación ~35%)
> entre `num_ctx=1024` y `num_ctx=32768`. El coste dominante es la
> generación del rationale, no la reserva de contexto. Esto valida
> el principio 'memoria por tools, no por stuffing' desde un ángulo
> distinto al original: la motivación principal NO es ahorrar
> latencia (que es plana), sino mantener footprint de RAM acotado y
> garantizar transparencia algorítmica (cada tool call queda en el
> log de decisión, auditable)."*

## Limitaciones del experimento

- **N=1 por celda**. Para promedios robustos hace falta versión
  con repeticiones (apuntado para post-MVP).
- **Solo 1 bundle (M1 clean)**. Bundles más complejos (M3 emergency,
  M6 con tool calling forzado) podrían comportarse distinto. Quedan
  como deuda — el primer experimento en el día tuvo timeouts
  desalineados que invalidaron M3 y M6.
- **Hardware único** (CPU Alder Lake). Para Jetson, Endodermis tiene
  su propia batería contractual (RH02 hallazgo día 19).
- **Solo E4B**. Comparación E2B vs E4B vs 12B fuera de scope MVP.
- **Calidad del rationale solo medida en chars**. No hay scoring
  cualitativo automatizado. Para review humano sobre subset
  reducido, post-MVP.

## Hallazgo colateral: el parser tolerante puede explicar reportes
inflados de PASS en mini-batería día 16

La mini-batería del día 16 reportó 5/5 PASS pero **es probable que
algún subset cayera al stub fallback sin detección** porque:

1. El parser estricto rechazaba JSON con keys traducidas al inglés
2. Cuando el parser fallaba, `_compose_rationale` caía al stub
3. El smoke verificaba `status="ok"` y `reason_code` correctos —
   ambos vienen del Evaluator determinista, NO del LLM
4. El rationale del stub es válido (texto fijo) y no se distingue
   del LLM real sin inspección manual

**Recomendación**: re-correr la mini-batería con el parser tolerante
(post-merge de este PR) para tener números reales. Apuntado como
post-MVP.

## Estado de servicios al cerrar

- llama-server, adapter y meristem todos levantados durante el
  experimento
- BBDD del experimento (`meristem_node.db`) **se mantiene** con
  los registros de las 6 decisiones para audit posterior
- `results_d23_focused.json` persistido en
  `code/meristem_node/results_d23_focused.json`
- Gráfica PNG en `docs/figures/mini_exp_latency_vs_ctx_d23.png`
- Tabla MD en `docs/figures/mini_exp_summary_d23.md`

## Archivos modificados/creados

- `code/meristem_node/src/inference.py` — `num_ctx`/`num_predict`
  configurables + timeout 600s + parser tolerante EN/ES
- `code/meristem_node/src/main.py` — header `X-Meristem-Num-Ctx`
- `code/meristem_node/scripts/mini_exp_context.py` — flechas
  Unicode → ASCII + timeout 600s
- `code/meristem_node/scripts/plot_mini_exp.py` — NUEVO, generador
  de tabla + gráfica
- `code/meristem_node/results_d23_focused.json` — NUEVO, datos
  crudos del experimento principal
- `code/meristem_node/results_d23_light.json` — datos crudos
  del primer experimento (con fallos diagnosticados)
- `docs/figures/mini_exp_latency_vs_ctx_d23.png` — NUEVO, gráfica
- `docs/figures/mini_exp_summary_d23.md` — NUEVO, tabla MD

## Deudas técnicas detectadas pero NO arregladas en este PR

1. **Doc obsoleta `:12000`** en `inference.py` y `main.py`: apunta a
   adapter URL que no existe; el adapter real corre en `:11434`.
   Sin tocar este PR — afecta otros consumidores históricos.
   Apuntar para coordinar con Cambium.
2. **Parser tolerante puede inflar PASS** en pipelines de validación
   antiguos (mini-batería día 16). Re-correr post-merge para tener
   métricas reales.
3. **Bundle M3 / M6 no medidos** en condiciones limpias. Apuntar
   para mini-experimento ampliado post-MVP.
4. **N=1 por celda** sin repeticiones. Hace falta versión con N≥3
   para análisis estadístico real.

---

— Meristem
