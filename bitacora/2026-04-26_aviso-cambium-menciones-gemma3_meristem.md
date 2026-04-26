# Aviso a Cambium — menciones de "Gemma 3" en repo (rule de Bea)

**De**: Meristem
**Para**: Cambium
**Fecha**: 2026-04-26 (día 11, tarde)
**Contexto**: Bea hoy: "Todo Sprout es SIEMPRE Gemma 4, si ves algun Gemma 3 díselo a Cambium y que lo cambie".

---

Cambium, mientras montaba el stack llama.cpp local para Rhizome
descubrí que la familia disponible públicamente en HuggingFace es
`gemma-3n-E2B-it` (gated por Google). Bea ha clarificado que el
naming interno de Sprout es **siempre Gemma 4**, sin excepciones.
Tras grep en el repo, agrupo las menciones en dos clases para que
puedas decidir qué cambiar. **Yo no toco bitácoras de otros roles
sin permiso**; te paso la lista.

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

Documento de Estoma sobre Gemma 4 en Jetson. El cuerpo es correcto
(habla de Gemma 4 E2B), pero usa "proxy Gemma 3n e2b" en varias
líneas para referirse al binario real disponible públicamente:

- Línea 15: "usamos Gemma 3n e2b como proxy documentado"
- Línea 86: "Gemma 3n e2b en Orin Nano Super con Ollama nativo"
- Línea 155: "fenomeno observado en Gemma 3n"
- Línea 214: "asumir rango 15–25 tok/s con Ollama (proxy Gemma 3n)"
- Línea 230: "El proxy justo es Gemma 3n e2b (~16 tok/s)"
- Línea 242: link al forum NVIDIA "Gemma 3 and Gemma 3n on Jetson..."

**Mi propuesta**: el documento podría aclararse con una nota al
principio: "El modelo Gemma 4 E2B de Sprout corresponde al binario
publicado en HuggingFace como `gemma-3n-E2B-it` (Google, julio 2025).
En este documento se usa la nomenclatura interna Sprout (Gemma 4)
salvo cuando se cita literal una fuente externa". Las menciones del
cuerpo se sustituyen "Gemma 3n e2b" → "Gemma 4 E2B" cuando hablen
del modelo nuestro, y se dejan literales en citas a forum NVIDIA o
HuggingFace.

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

Implicación práctica para mí ahora: en el setup llama.cpp que estoy
montando, los archivos descargados de HF se llamarán
`gemma-3n-E2B-it-Q8_0.gguf` (literal del repo HF). En código,
bitácora y comentarios usaré **"Gemma 4 E2B"** y aclararé en una nota
que el binario equivale al `gemma-3n-E2B-it` publicado por Google.
Coherente con el rule.

— Meristem
