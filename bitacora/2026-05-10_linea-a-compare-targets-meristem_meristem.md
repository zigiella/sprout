# Línea A día 24 — tool `compare_targets` + bundle M7 demo

**Autora**: Meristem
**Fecha**: 2026-05-10 (día 24)
**Antecede**: `bitacora/2026-05-10_lineas-cd-resultados-meristem_meristem.md`
(C+D del mismo día)
**Material destino**: writeup §3 (LLM eleva señal con incertidumbre
explícita) + §6 (visión post-MVP / fase 2 plan IA)

---

## TL;DR

- **Tool `compare_targets(target_a, target_b, last_n=5)`** añadida a
  `prompts.py`: stub determinista con datos plausibles que cuentan
  historia clara (rhizome_01 degradado vs rhizome_02 estable).
- **Bundle M7** demo creado (`bundle_M7_compare_targets_demo.json`):
  ALERT en rhizome_01 con hint multi-Rhizome para invitar al modelo
  a llamar la tool y emitir hipótesis tipo *"problema local en
  rhizome_01, no global"* con marcador de confianza explícito.
- **Default `num_predict=256`** aplicado en `inference.py` (cambio
  derivado del experimento de línea C, día 24). Reduce latencia
  ~53% en producción.
- **Tests**: 36/36 PASS post-cambios.
- **Smoke con LLM real PENDIENTE** por OOM del portátil en este
  momento (modelo necesita 9.8 GB, disponibles 5.9 GB). El stub
  está validado, la integración tool→inference→main está cubierta
  por tests existentes. Smoke con LLM real cuando haya RAM.

---

## Lo que entrego

### 1. Tool `compare_targets`

**Definición** (en `TOOL_DEFINITIONS`):

```python
{
  "name": "compare_targets",
  "description": "Compara comportamiento entre dos Rhizomes en
    el mismo periodo (modos, reason_codes, tank/soil promedios) +
    resaltado de diferencias destacadas. Usar solo cuando la
    decisión actual sea CONSERVATIVE o ALERT y el agricultor
    gestiona varios Rhizomes (al menos dos conocidos). Permite
    emitir hipótesis 'es problema local del Rhizome, no global',
    siempre con marcador de confianza explícito.",
  "parameters": {
    "target_a": str,
    "target_b": str,
    "last_n": int (default 5)
  }
}
```

**Stub determinista**: rhizome_01 degradado (4 ALERT en 5 visitas,
tank avg 22%, soil avg 23%) vs rhizome_02 estable (5 STABLE_BUNDLE,
tank avg 76%). Diff highlights cuentan la historia clara:

```json
[
  "rhizome_01 en alerta persistente (3 de últimas 5 visitas), rhizome_02 estable.",
  "Depósito de rhizome_01 muy bajo (avg 22%) frente a rhizome_02 saludable (avg 76%).",
  "Patrón sugiere problema local del rhizome_01 (suministro/sensor), no condición global compartida."
]
```

### 2. Principio de incertidumbre explícito en system prompt

Añadido al system prompt:

> *"PRINCIPIO IMPORTANTE para tool calling: las hipótesis que emitas
> basadas en tools deben llevar marcador de confianza explícito
> ('posible', 'sospecho', 'indica') y citar el dato concreto que la
> sustenta. NO afirmes diagnósticos cerrados que el agricultor no
> pueda verificar."*

Esto es **fase 2 del plan IA** (día 19) operacionalizada al fin: el
LLM no afirma diagnósticos cerrados, eleva señal con incertidumbre.
**Material para writeup §3 y §5** sobre Safety & Trust.

### 3. Bundle M7 demo

`bundle_M7_compare_targets_demo.json` con:
- `target_rhizome_id="rhizome_01"`
- mode=alert + alert_latched=true + tank_pct=14
- 3 BLOCK consecutivos (DEPOSITO_BAJO + ALERTA_LATCHED)
- Campo `_demo_hint` en snapshot que sugiere contexto multi-Rhizome
- weather_digest presente (a diferencia de M6 que lo deja null)
- Diseñado para que el modelo decida `compare_targets` espontáneamente
  porque ya tiene weather y necesita perspectiva cross-target

### 4. Default `num_predict=256` aplicado

Cambio derivado de línea C (mismo día):

```python
# inference.py
DEFAULT_NUM_CTX = 4096
# num_predict reducido de 1024 -> 256 tras mini-experimento dia 24
# (linea C). Reduce latencia ~53% sin perder validez del rationale.
DEFAULT_NUM_PREDICT = 256
```

Header `X-Meristem-Num-Predict` permite override puntual si una
alerta específica necesita más detalle.

---

## Lo que NO entrego (apuntado como pendiente)

### Smoke con LLM real bloqueado por OOM

Levanté stack completo (llama-server :8080 + adapter :11434 +
meristem :13000). Hice POST de un bundle estable a `rhizome_02`
(seeding) y después M7 a `rhizome_01`. Ambos cayeron al **stub
fallback** con error 500 del adapter.

Diagnóstico final: **OOM del modelo en este momento**. Curl directo
al adapter devolvió:

```json
{"error":"model requires more system memory (9.8 GiB) than is
available (5.9 GiB)"}
```

**No es bug** ni del tool nuevo ni del code path. Es constraint de
RAM del portátil ahora (otros procesos compitiendo). Apuntado para
re-correr cuando haya hueco de RAM.

**Lo que SÍ está validado**:

1. Tests existentes 36/36 PASS — la integración
   `tool definition → call_tool → inference loop` está cubierta
2. Stub determinista produce JSON correcto (verificado vía Python)
3. Tool registrada en `TOOL_DEFINITIONS` y system prompt actualizado
4. Bundle M7 carga válido como Pydantic Bundle
5. Path completo desde `/visit` → `_compose_rationale` → propagación
   de num_predict ya validado en líneas C+D

**Pendiente cuando haya RAM**: smoke en directo del bundle M7 con
LLM real para verificar que el modelo invoca `compare_targets`
espontáneamente y emite rationale con marcador de confianza
explícito. Esto irá en una bitácora corta de seguimiento, no
bloquea este PR.

---

## Implicaciones arquitectónicas

### Para writeup §3 (Arquitectura)

Frase candidata:

> *"En Meristem, el LLM puede llamar tools en runtime para enriquecer
> el rationale: clima histórico, diff de policy anterior, secuencia
> temporal del Rhizome, comparación cross-target. Estas tools devuelven
> datos agregados que el modelo no sabe — y el modelo decide cuándo
> pedirlos. La novedad arquitectónica no es el tool calling per se,
> sino que **las tools se usan exclusivamente para enriquecer el
> rationale, no para mover la decisión**. La acción la firma el
> Evaluator antes de que el LLM intervenga."*

### Para writeup §5 (Safety & Trust)

Frase candidata:

> *"El system prompt instruye al modelo a emitir hipótesis con
> marcador de confianza explícito ('posible', 'sospecho') y a citar
> el dato concreto que las sustenta. El LLM eleva señal pero no
> cierra el bucle: el operador decide si actúa, y la verificación
> queda trazada en `decisions.llm_metrics.tool_calls_log` — auditable
> por inferencia."*

---

## Estado al cerrar

- ✅ Tool registrada + stub determinista
- ✅ Bundle M7 demo + README actualizado
- ✅ Default `num_predict=256` aplicado
- ✅ Tests 36/36 PASS
- ⏭️ Smoke LLM real → pendiente por OOM (apuntado)
- 🛑 Stack apagado + BBDD limpia

## Archivos modificados / creados

- `code/meristem_node/src/prompts.py` — tool def + stub
  `compare_targets` + principio de incertidumbre en system prompt
- `code/meristem_node/src/inference.py` — default `num_predict=256`
  con justificación inline
- `code/meristem_node/examples/bundle_M7_compare_targets_demo.json`
  — bundle nuevo
- `code/meristem_node/examples/README.md` — fila M7 añadida
- `bitacora/2026-05-10_linea-a-compare-targets-meristem_meristem.md`
  — esta bitácora

---

— Meristem
