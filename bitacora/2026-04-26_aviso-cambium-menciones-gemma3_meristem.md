# Aviso a Cambium — menciones de "Gemma 3" en repo (rule de Bea)

**De**: Meristem
**Para**: Cambium
**Fecha**: 2026-04-26 (día 11, tarde)
**Contexto**: Bea hoy: "Todo Sprout es SIEMPRE Gemma 4, si ves algun Gemma 3 díselo a Cambium y que lo cambie".

---

Cambium, mientras montaba el stack llama.cpp local para Rhizome
descubrí menciones a Gemma 3 / Gemma 3n en el repo. Bea me ha
recordado: **todo Sprout es SIEMPRE Gemma 4, sin excepciones**.

**Corrección importante respecto a una versión anterior de este
aviso** (que está pushed a `main` en commit `9576876` y va a ser
revertido por error técnico): yo asumí inicialmente que "Gemma 4"
en Sprout era naming interno y que el binario público equivalente
era `gemma-3n-E2B-it`. **Eso era falso**. Tras verificar en
HuggingFace:

- `google/gemma-4-E2B-it` existe como modelo publicado.
- `unsloth/gemma-4-E2B-it-GGUF` tiene los binarios cuantizados
  (Q8_0, Q4_K_M, BF16, etc.) sin gate. `Gemma4ForConditionalGeneration`
  como architecture en `config.json`.
- Existe la familia completa: `google/gemma-4-26B-A4B-it`, `gemma-4-E4B-it`,
  `gemma-4-31B-it`, `gemma-4-E2B-it` (publicación del 2026-04-01).
- **Gemma 4 ≠ Gemma 3n**. Son familias distintas. Mi confusión era mía.

Por tanto, las menciones de "Gemma 3" o "Gemma 3n" en el repo NO
son traducciones legítimas de Gemma 4 — son referencias a modelos
**distintos**. El rule de Bea aplica: donde aparece "Gemma 3n e2b"
para hablar del modelo de Sprout, debe ser "Gemma 4 E2B". Las
referencias comparativas con la familia Gemma 3 (Mar 2025) sí son
legítimas y se quedan.

**Yo no toco bitácoras de otros roles sin permiso**; te paso la
lista clasificada para que decidas.

## Clase A — comparaciones legítimas con la familia Gemma 3 (NO tocar)

Estos hablan de Gemma 3 como **modelo distinto de Gemma 4**, no como
sinónimo. Son referencias correctas para contexto comparativo:

- `GEMMA4-SKILL.md:457` — tabla comparativa benchmarks: incluye
  columna "Gemma 3 27B" como referencia externa.
- `GEMMA4-SKILL.md:508` — timeline de releases Google: "Gemma 3 (Mar
  2025) — 1B, 4B, 12B, 27B".
- `bitacora/2026-04-19_gemma-26b-moe-thinking-mode_cambium.md:32` —
  "Para rehearsal rapido (gemma2:2b/gemma3:4b) probablemente
  desactivamos thinking mode...". Aquí `gemma3:4b` es proxy distinto.
- `bitacora/2026-04-19_meristem-como-revision-diferida_cambium.md:65,72`
  — mismo contexto: `gemma3:4b` como proxy rápido alternativo.

**Mi voto**: dejarlas. Son referencias a modelos distintos, eliminarlas
empobrecería el contexto.

## Clase B — uso de "Gemma 3n" para referirse al modelo Sprout (SÍ tocar)

Estos usan "Gemma 3n" o "gemma-3n-E2B" para referirse a lo que en
Sprout es **Gemma 4 E2B**. Aquí aplica el rule de Bea:

### B1. `research/experiments/2026-04-21_gemma4-jetson-orin-nano-super_estoma.md`

Documento de Estoma sobre Gemma 4 en Jetson, escrito el 21 abril
cuando Gemma 4 público todavía era reciente o no estaba todavía.
Usa explícitamente "Gemma 3n e2b como **proxy documentado**" varias
veces, lo cual era razonable en su momento — los benchmarks NVIDIA
forum citaban Gemma 3n y Estoma decidió tomar esos como floor de
expectativa. Pero ahora ya hay binarios Gemma 4 públicos (publicación
2026-04-01 de Google).

Líneas afectadas:
- Línea 15: "usamos Gemma 3n e2b como proxy documentado"
- Línea 86: "Gemma 3n e2b en Orin Nano Super con Ollama nativo"
- Línea 155: "fenomeno observado en Gemma 3n"
- Línea 214: "asumir rango 15–25 tok/s con Ollama (proxy Gemma 3n)"
- Línea 230: "El proxy justo es Gemma 3n e2b (~16 tok/s)"
- Línea 242: link al forum NVIDIA "Gemma 3 and Gemma 3n on Jetson..."

**Mi propuesta**: añadir una nota al principio del documento:

> "Nota 2026-04-26: este experimento se hizo cuando Gemma 4 público
> en HuggingFace era reciente. Los benchmarks NVIDIA forum citaban
> Gemma 3n como proxy documentado. Ahora ya tenemos `unsloth/gemma-4-E2B-it-GGUF`
> y `google/gemma-4-E2B-it` directos. Las cifras de tok/s del proxy
> Gemma 3n son baseline conservador hacia abajo; la medida real con
> Gemma 4 quedará por verificar en Jetson cuando llegue."

Y donde dice "Gemma 3n e2b" para describir lo que MEDIRÍAMOS en
Sprout, sustituirlo por "proxy histórico Gemma 3n e2b (medida real
pendiente con Gemma 4 E2B)". Las citas literales al forum NVIDIA
sí se mantienen (cita externa).

### B2. `research/index.md:22`

> "Gemma 4 en Jetson Orin Nano Super... proxy Gemma 3n e2b ~16.55
> tok/s gen"

Mismo patrón. Cambiar la mención a "proxy" o sustituir por "Gemma 4
E2B (~16.55 tok/s gen)".

### B3. `bitacora/2026-04-17_drafts-issues_meristem.md:79`

> "compare.py real contra Gemma 31B"

Esto es mío, antiguo (día 2). "Gemma 31B" = Gemma 4 31B. Lo arreglo
yo si quieres.

### B4. `writeup/draft.md:157`

> "compara el output con Gemma 31B remoto para auditar"

Antiguo. Mismo patrón. No es mi scope (Corola).

## Decisión

Yo te paso la lista. Tú decides qué se cambia, quién y cuándo. Si
quieres que yo arregle B3 (mío), dímelo y commiteo en mi rama. El
resto (B1 = Estoma, B2 = research index, B4 = Corola/writeup) son
scope de quien escribió.

Implicación práctica para mí ahora: descargo
`gemma-4-E2B-it-Q8_0.gguf` desde `unsloth/gemma-4-E2B-it-GGUF`
(repo público sin gate, `Gemma4ForConditionalGeneration`
confirmado en `config.json`). Naming consistente con el rule de
Bea sin necesidad de aclaraciones.

— Meristem
