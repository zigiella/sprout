# Resultados Rhizome v0.5 — mini-test brevedad (6 runs)

**Autora**: Meristem
**Fecha**: 2026-04-27 (día 12, cierre real)
**Rama**: `feat/meristem-tuning-v0`
**Antecede**: `bitacora/2026-04-27_resultados-rhizome-v0_meristem.md`
**Propuesto por**: Xilema (validó v0, propuso regla de brevedad)

---

## TL;DR

**v0.5 PASA los 4 criterios de Xilema.** Promovible a v1 base.

Mini-test (6 runs) con regla añadida al system prompt:

> "Devuelve JSON compacto, sin Markdown fences, sin texto fuera del JSON.
> No escribas análisis ni explicación previa. Cierra el objeto JSON y
> termina inmediatamente."

Resultado: 6/6 envelope_valid · 6/6 status_match · RA04 mantiene
SAFETY_DOWNGRADE · RD01 deja de truncar (1024 → 843 tokens_out, JSON
compacto en una línea, sin fences).

## Criterios de aceptación (Xilema)

| Criterio | Esperado | Obtenido | Pass |
|---|---|---|:-:|
| 1. envelope_valid | 6/6 | 6/6 | ✅ |
| 2. status_match | 6/6 | 6/6 | ✅ |
| 3. RA04 reason_code | "SAFETY_DOWNGRADE" | "SAFETY_DOWNGRADE" | ✅ |
| 4. RD01 sin truncar + sin texto fuera del JSON | done_reason=stop, no Markdown | done_reason=stop, JSON compacto 1 línea | ✅ |

## RD01 — el caso clave

**v0**: 1024 tokens_out, finish_reason=length, content cortado en
`"expected_liters": ` (sin cerrar JSON), envelope_valid=false.

**v0.5**:
```json
{"task":"decide_action","status":"ok","payload":{"action":"WATER_A","duration_s":120,"expected_liters":500}}
```

118 chars, 843 tokens_out (vs 1024 saturados), una sola línea, sin
Markdown fences, parsea limpio.

## Comparación v0 vs v0.5 — los 6 prompts del mini-test

| Prompt | v0 tok_out | v0.5 tok_out | Δ | v0 finish | v0.5 finish |
|---|---:|---:|---:|---|---|
| RD01 | **1024** | 843 | -18% | **length** | **stop** |
| RD03 | 641 | 583 | -9% | stop | stop |
| RD08 | 945 | 902 | -5% | stop | stop |
| RA02 | 918 | 616 | -33% | stop | stop |
| RA04 | 451 | 486 | +8% | stop | stop |
| RH02 | 862 | 741 | -14% | stop | stop |

**Reducción media: ~13%**. La regla de brevedad ayuda pero no es
dramática — Gemma 4 E2B tiende a ser verboso por naturaleza. Lo
importante NO es la reducción de tokens, es que **el JSON viene ahora
compacto en una línea sin Markdown fences**, lo que hace el parser
estable y elimina el truncamiento.

## Cambios en código

- `code/tuning/system_prompts.yaml`: nuevo entry
  `rhizome_balanced_es_v05` (= `rhizome_balanced_es` + bloque final
  "FORMATO DE SALIDA ESTRICTO" con la regla propuesta por Xilema).
  El v0 se mantiene como histórico.
- `code/tuning/matrix_rhizome_v05.yaml`: matrix nuevo con 6 prompts
  selectos y config `R1_balanced_v05`. Output a
  `results/rhizome_v05.jsonl`.

## Promoción a v1

`rhizome_balanced_es_v05` queda como **base v1 propuesta**. Cuando
arranquemos Rhizome target real (Jetson + llama.cpp), partimos de este
prompt. Confidence: HIGH (el cambio textual depende del prompt, no del
modelo, transferencia directa).

## Lectura para el review día 13

Al review llevamos:
- **Pollen**: 94 runs, 5 HIGH validadas (R1-R10 cerrado)
- **Rhizome v0**: 18 runs, 17/18 (94%) status_match — semántica validada
- **Rhizome v0.5**: 6 runs, 6/6 (100%) — formato corregido sin tocar
  semántica, listo para promover a v1
- **Stack**: llama.cpp + Gemma 4 E2B Q4_K_M validado end-to-end con
  adapter `llamacpp` y headers uniformes con Pollen
- **Metodología**: scoring HIGH/MEDIUM/LOW como contrato de
  transferencia local→target, validado en dos agentes (Pollen + Rhizome)

## Referencias

- `code/tuning/results/rhizome_v05.jsonl` (6 records, local)
- `code/tuning/system_prompts.yaml` (entry `rhizome_balanced_es_v05`)
- `code/tuning/matrix_rhizome_v05.yaml`
- `bitacora/2026-04-27_resultados-rhizome-v0_meristem.md` (resultados v0)
- `bitacora/2026-04-27_validacion-rhizome-v0-xilema.md` (validación inicial)
