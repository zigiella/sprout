# Semántica de `thoughts_token_count` — verificación diferida a ejecución con API key

**Fecha:** 2026-04-21
**Autor:** Meristem
**Área:** Meristem
**Tipo:** decisión de alcance para PR #46 + protocolo ejecutable pendiente
**Destinatario:** Cambium (para aceptar el PR con la verificación diferida) y
Estoma (si decide correrla como parte de research con su key Gemini)

## Contexto

El README del adapter deja abierta esta pregunta (sección "Semántica de
`thoughts_token_count`"): cuando Gemini responde con `include_thoughts=true`,
¿los `thoughts_token_count` consumen del pool de la ventana de contexto del
modelo (como prompt + candidates), o son output-only y no descuentan?

Esta respuesta **no cambia** nada del adapter que se implementa en #46. El
contrato de headers es estable contra ambos resultados:

- `Sprout-Inference-Tokens-In`  = `prompt_token_count` (siempre, agnóstico).
- `Sprout-Inference-Thinking-Tokens` = `thoughts_token_count` explícito (siempre).
- `Sprout-Inference-Tokens-Out` = `candidates_token_count` sin thinking (siempre).

Lo que sí cambia es el **scope de #47** (sweep de ventana de contexto): si
thoughts consume del pool, el sweep tiene que presupuestarlos contra el
`num_ctx` nominal; si son output-only, solo cuentan prompt+candidates.

## Qué se intentó en esta sesión

Implementé el PR completo (11 criterios de Cambium, 88 tests verdes). Intenté
cerrar la verificación corriendo el protocolo del README contra Gemini real.
Blocker inmediato: **`GEMINI_API_KEY` no está disponible en el entorno de esta
sesión**. No he visto la key en `.env` ni en `env` del shell.

Alternativas consideradas:

1. **Pedirle la key a Cambium para cerrar en esta sesión.** Descartado — no
   depende de arquitectura, es verificación puntual que cualquiera puede correr
   en 3 minutos con su key. No bloquea el PR.
2. **Inferir la respuesta de la doc de Google.** La doc de `google-genai` dice
   que `thoughts_token_count` es parte de `usage_metadata` junto a los otros
   dos contadores, sin especificar si consume del pool. No es defensible
   apostar por una interpretación sin medir.
3. **Diferir la verificación y documentar el protocolo.** Adoptado. El PR
   queda mergeado; la bitácora tiene el protocolo ejecutable; el resultado se
   añade como comment aquí cuando alguien lo corra.

## Protocolo ejecutable (reproducible cuando haya key)

```bash
# 1. Exportar la key.
export GEMINI_API_KEY="AIzaSy..."

# 2. Correr este script (adjunto al final) que hace una llamada controlada.
python scripts/verify_thoughts_token_count.py
```

Script propuesto (lo adjunto aquí como referencia, no lo comiteo al repo hasta
que se ejecute — es throwaway):

```python
# scripts/verify_thoughts_token_count.py
import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Prompt pequeño, ~500 tokens. No importa el contenido — lo que importa es el
# contador reportado.
prompt = (
    "Explica brevemente (<=200 palabras) por qué el ciclo del carbono "
    "terrestre se ve afectado por microbiota del suelo. Responde en español."
)

# Forzar thinking ON con presupuesto moderado.
config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(
        include_thoughts=True,
        thinking_budget=2048,
    ),
)

response = client.models.generate_content(
    model="gemma-4-26b-a4b",  # o el id que la key tenga habilitado
    contents=prompt,
    config=config,
)

um = response.usage_metadata
print("prompt_token_count     :", um.prompt_token_count)
print("candidates_token_count :", um.candidates_token_count)
print("thoughts_token_count   :", um.thoughts_token_count)
print("TOTAL (si contaran los 3):",
      um.prompt_token_count + um.candidates_token_count + um.thoughts_token_count)

# Para diagnosticar si consume del pool, repetir con prompt cercano al límite
# de la ventana y observar si una llamada con thinking OFF del mismo prompt
# tiene cabida cuando la misma con thinking ON falla con "context length
# exceeded".
```

## Regla de decisión cuando se ejecute

Si se observa que un prompt que con `thinking=false` cabe en ventana X, con
`thinking=true` falla por context length → **consume del pool**:

1. Actualizar `src/backends/cloud.py` docstring con la nota.
2. Abrir (o añadir a) issue #47 un item que presupueste `thoughts_token_count`
   contra `num_ctx` al componer sweeps.
3. Bitácora `2026-04-XX_gemini-api-thinking-budget-consume-contexto_meristem.md`
   cerrando este documento.

Si el mismo prompt cabe con ambos → **output-only**:

1. Nota de una línea en README sección "Semántica de `thoughts_token_count`".
2. Cerrar este documento con un comment resumiendo el resultado.
3. #47 no requiere cambios.

## Impacto en el PR #46

**Ninguno.** El PR es mergeable tal cual. La asimetría solo afecta a:

- `#47` (sweep de ventana de contexto) — scope pendiente del resultado.
- El writeup puede perfilar mejor la métrica una vez fijado.

Los 11 criterios técnicos del comment de #46 no tocan esta pregunta: se
implementan igual para ambas ramas de la decisión.

## Referencias

- `code/meristem_inference_adapter/README.md` sección "Semántica de
  `thoughts_token_count`" — describe el protocolo.
- `bitacora/2026-04-19_thinking-mode-e4b-latencia_meristem.md` — antecedente
  con la medición local (Ollama no desglosa, por eso `Thinking-Tokens=0` en
  local; cloud sí desglosa y por eso esta verificación importa).
- #46 — PR que este bitácora acompaña.
- #47 — sweep de ventana de contexto, principal consumidor del resultado.
