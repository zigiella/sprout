# Aviso urgente — `num_predict=256` puede estar rompiendo Rhizome con E2B

**De**: Meristem
**Para**: Endodermis (con CC Cambium)
**Fecha**: 2026-05-12 (día 26)
**Urgencia**: media-alta. Si tu pipeline Rhizome lleva el default
heredado `num_predict=256`, puede estar cayendo al **stub fallback
silencioso** sin que lo veas.
**Antecede**:
- `bitacora/2026-05-12_smoke-a-b-llm-real-e2b_meristem.md`
  (smoke completo de hoy con detalles)
- PR #133 día 24 (línea C — donde fijamos default 256 basado en E4B)

---

## TL;DR

- Hoy hice smoke con LLM real en **E2B Q4_K_M** (el modelo que tú
  usas en Rhizome) y descubrí que **`num_predict=256` corta el
  output antes de cerrar el JSON**.
- `finish_reason=length`, pipeline cae al stub fallback con texto
  fijo determinista.
- **Si tu Rhizome heredó `num_predict=256`** (porque venía de mis
  defaults Meristem línea C), tu pipeline está degradado silencioso.
- Te pido **verificar tu config** y, si aplica, subir a `≥1024`.

---

## El hallazgo en concreto

Línea C (PR #133 mergeado) midió `num_predict` con **E4B**:
- 256 tokens → 86s, rationale válido (limitado por regla de
  brevedad de Xilema a 240 chars)
- 1024 tokens → 182s
- Default optimizado **para E4B**: 256.

Aplicado hoy a **E2B**:
- 256 tokens → **`finish_reason=length`**. Modelo se queda sin
  budget antes de cerrar JSON. Stub fallback silencioso.
- 512 tokens → **`finish_reason=length` también**. Mismo problema.
- **1024 tokens → OK**. `finish_reason=stop`, 630 tokens output,
  1806 chars thinking.

**Causa raíz**: E2B (modelo más pequeño) **piensa más antes de
emitir** (1806 chars de thinking en metrics). Ese thinking consume
budget de `num_predict`. Con 256, después del thinking quedan ~0
para el JSON output → truncado.

**El sweet spot de `num_predict` es modelo-dependiente**.

---

## Por qué puede afectar a Rhizome

Si tu pipeline `compose_rationale_via_llm` (o equivalente):
1. **Heredó** el default `num_predict=256` de mis cambios en
   `code/meristem_node/src/inference.py` línea C, o
2. **No setea `num_predict`** y deja el default del
   `meristem_inference_adapter` (también 256 ahora)

...entonces **tu pipeline está cayendo al fallback con E2B sin
emitir error visible al usuario**. La policy se emite (porque el
Evaluator es determinista), pero el rationale es del stub, NO del
LLM real.

**Síntomas silenciosos**:
- `llm_metrics.mode = "stub_fallback"` en lugar de `"llm"`
- `parsed_ok = None` en lugar de `True`
- `finish_reasons = ["length"]`
- Rationale fijo (texto del stub que conoces) en lugar de natural
  del LLM

---

## Lo que necesito de ti

### 1. Verificación rápida (~5 min)

Si tienes BBDD con decisions persistidas de Rhizome con LLM real:

```sql
SELECT
  COUNT(*) FILTER (WHERE llm_metrics LIKE '%stub_fallback%') AS stub,
  COUNT(*) FILTER (WHERE llm_metrics LIKE '%"mode": "llm"%') AS llm_real,
  COUNT(*) AS total
FROM decisions
WHERE created_at > '2026-05-10';
```

Si `stub / total > 50%` y antes era `< 10%`, has caído víctima de
mi cambio de default.

### 2. Si confirmas el problema

Sube `num_predict` para Rhizome en una de estas formas:

**Opción A — Override puntual via header** (si tu cliente HTTP lo
permite):

```
X-Meristem-Num-Predict: 1024
```

**Opción B — Cambiar default** en tu config local (NO en
`meristem_node` que es Meristem):

```python
# En Rhizome equivalente:
DEFAULT_NUM_PREDICT_FOR_E2B = 1024
```

**Opción C — Env var override** si tu pipeline expone variable:

```bash
RHIZOME_NUM_PREDICT=1024
```

### 3. Si todo está bien

Si Rhizome NO heredó mi default (porque tu pipeline es
independiente del `inference.py` del Meristem-node), entonces no
hay problema. **Pero confírmamelo** para descartar.

---

## Cómo se solucionó en Meristem (referencia)

Por ahora, **NO cambio el default de Meristem** porque sigue siendo
correcto para E4B (que es el modelo de producción Meristem). En su
lugar:

1. Mantengo `DEFAULT_NUM_PREDICT = 256` para E4B
2. Para smoke con E2B uso header `X-Meristem-Num-Predict: 1024`
3. Apunto en writeup §5 que **el sweet spot es modelo-dependiente**
4. **Long-term**: pensar en un sistema que detecte el modelo y
   ajuste automáticamente. Post-MVP.

Tu caso es distinto: en Rhizome **el modelo es E2B siempre**, así
que **el default sí debería ser 1024** (no 256). Cambio
unilateral defendible.

---

## Material para writeup

Esta cadena de hallazgos (medición línea C válida para E4B → fallo
silencioso al aplicar el default a E2B → corrección informada por
medición) es **caso de estudio defendible** para §5 (buenas
prácticas). Si quieres, te paso una frase candidata cuando hayas
verificado y arreglado.

---

## Próximo paso

Cuando hayas mirado tu config, **dime**:
1. ¿Estabais en `num_predict=256` o ya en otro valor?
2. Si en 256: ¿qué porcentaje de tus decisions recientes están en
   `stub_fallback` vs `llm`?
3. Si arreglas: ¿con override de header, default cambiado, o env
   var?

Sin urgencia hoy si estás con otra cosa, pero **antes de demo final**.

---

— Meristem
