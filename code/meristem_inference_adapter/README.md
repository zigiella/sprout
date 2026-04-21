# meristem_inference_adapter/

Proxy local Ollama-compatible que expone `localhost:11434` con la API de Ollama
(`/api/chat`, `/api/generate`) y reenvia:

- a Gemini API cuando `INFERENCE_BACKEND=cloud` (demo via nube con Gemma 26B MoE)
- a Ollama real en `:11435` cuando `INFERENCE_BACKEND=local` (reverse-proxy transparente)
- a un backend `test` con respuestas canneadas cuando `INFERENCE_BACKEND=test` (CI sin Gemini ni Ollama)

Meristem (el consumidor) habla siempre a `:11434` con contrato Ollama nativo y
no distingue el backend. El switch es del adapter.

Contexto: D2/D3 de `bitacora/2026-04-20_meristem-reframe-modelo-objetivo_cambium.md`
y los 11 criterios tecnicos convergidos en el comentario de #46.

## Estado

Implementado en `feat/meristem-inference-adapter-46`. Los 11 criterios técnicos
del comentario de Cambium en #46 están cubiertos. 88 tests verdes, ninguno
requiere Gemini ni Ollama real (contrato punto 11).

Pendiente de ejecución (no bloquea merge): verificación en vivo de la
semántica de `thoughts_token_count` contra Gemini API real — ver sección
correspondiente abajo.

## Estructura

```
meristem_inference_adapter/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py                # FastAPI app en :11434, /api/chat + /api/generate
│   ├── config.py              # env vars, aliases de modelos, pricing
│   ├── schema_flatten.py      # inline de $ref / poda de $defs (punto 1)
│   ├── thinking_map.py        # Ollama think <-> Gemini thinking_config (punto 2)
│   ├── reconstruct.py         # extrae partes thought=true a message.thinking (punto 3)
│   ├── headers.py             # emite Sprout-Inference-* uniformes (punto 7)
│   ├── retry.py               # backoff 500ms/2s/8s para 429 Gemini (punto 5)
│   └── backends/
│       ├── __init__.py
│       ├── base.py            # Protocol InferenceBackend
│       ├── local.py           # reverse-proxy transparente a :11435
│       ├── cloud.py           # Gemini API (google-genai)
│       └── test.py            # mock con canned responses (punto 11)
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_scaffold.py        # config + health + protocolo
    ├── test_schema_flatten.py  # punto 1
    ├── test_thinking_map.py    # punto 2
    ├── test_reconstruct.py     # punto 3
    ├── test_headers.py         # puntos 4 y 7
    ├── test_retry.py           # punto 5
    ├── test_backend_test.py    # punto 11
    ├── test_backend_local.py   # reverse-proxy con respx
    ├── test_backend_cloud.py   # Gemini API con genai client fake
    ├── test_main.py            # integracion FastAPI + error handling
    └── test_smoke_parity.py    # mismo prompt local vs cloud, headers uniformes
```

## Port layout (punto 6)

| Quien | Puerto | Nota |
|---|---|---|
| Meristem | cliente | habla a `http://localhost:11434` |
| adapter | `11434` | escucha SIEMPRE aqui |
| Ollama real | `11435` | solo en modo `local`; arrancar con `ollama serve --port 11435` |
| Gemini API | remoto | backend `cloud` |

## Variables de entorno

Ver `.env.example`. Claves:

| Var | Default | Nota |
|---|---|---|
| `INFERENCE_BACKEND` | `test` | `cloud` \| `local` \| `test` |
| `ADAPTER_PORT` | `11434` | puerto del adapter |
| `OLLAMA_UPSTREAM_HOST` | `http://localhost:11435` | solo usado en `local` |
| `GEMINI_API_KEY` | (vacio) | requerido si `cloud` |
| `GEMINI_DEFAULT_MODEL` | `gemma-4-26b-a4b` | modelo cloud por defecto |
| `MERISTEM_THINKING_BUDGET` | `4096` | placeholder, #44 lo fija empiricamente |
| `GEMINI_PRICE_IN_EUR_PER_1K` | `0.0` | configurable, no hardcoded |
| `GEMINI_PRICE_OUT_EUR_PER_1K` | `0.0` | |
| `GEMINI_PRICE_THINKING_EUR_PER_1K` | `0.0` | |
| `RETRY_MAX_ATTEMPTS` | `3` | |
| `RETRY_BACKOFF_MS_1/2/3` | `500` / `2000` / `8000` | |

## Alias de modelos (punto 9)

```python
DEFAULT_MODEL_ALIASES = {
    "gemma4:26b-moe": "gemma-4-26b-a4b",
    "gemma4:e4b":     "gemma-4-e4b-it",
    "gemma4:31b":     "gemma-4-31b-it",
}
```

Overridable por env (pendiente de definir formato exacto en implementacion).

## Headers `Sprout-Inference-*` (puntos 4 y 7)

Adapter emite el set completo en **ambos** modos. En modo local los campos de
coste son `0.0`.

```
Sprout-Inference-Backend:         cloud-gemini | local-ollama | test
Sprout-Inference-Model:           gemma-4-26b-a4b | gemma-4-e4b-it | ...
Sprout-Inference-Tokens-In:       <int>    = prompt_token_count
Sprout-Inference-Tokens-Out:      <int>    = candidates_token_count (sin thinking)
Sprout-Inference-Thinking-Tokens: <int>    = thoughts_token_count (0 explicito si thinking off)
Sprout-Inference-Duration-Ms:     <int>    = wallclock total adapter
Sprout-Inference-Cost-EUR:        <float>  = 0.0 en local/test
```

### Nota sobre `tok/s` derivado (punto 4, docstring explicito pedido por Cambium)

`eval_count` en la respuesta Ollama-format que el adapter devuelve se calcula como
`candidates_token_count + thoughts_token_count`. Eso significa que cualquier
`tok/s` derivado como `eval_count / eval_duration` **incluye tokens de thinking**
cuando thinking esta activo.

El numero defendible (tok/s de generacion visible al usuario) sale de los
headers desglosados: `Sprout-Inference-Tokens-Out / Sprout-Inference-Duration-Ms`.

Harness (#45), writeup y cualquier grafica comparativa DEBEN usar los headers
desglosados, no el `eval_count` agregado.

## Placeholder thinking budget (punto 2)

```python
# PLACEHOLDER — default empirico se fija en #44 tras A/B.
# No optimizar en base a este numero.
THINKING_BUDGET_TOKENS_PLACEHOLDER = 4096
```

Cuando #44 cierre, la constante se sustituye por el valor medido y el
comentario referencia el run.

## Semantica de `thoughts_token_count` (verificacion diferida)

Pregunta abierta: cuando Gemini responde con `include_thoughts=true`, los
`thoughts_token_count` ¿consumen del pool de la ventana de contexto (como
`prompt_token_count + candidates_token_count`) o son output-only?

La respuesta no cambia el contrato del adapter — los 3 contadores se emiten
siempre, desglosados, en los headers `Sprout-Inference-*`. Solo afecta al
**scope de #47** (sweep de ventana de contexto): si consumen, el sweep tiene
que presupuestarlos contra el `num_ctx` nominal.

Protocolo ejecutable + decision rule + estado actual:
`bitacora/2026-04-21_thoughts-token-count-verificacion-pendiente_meristem.md`.

TL;DR del estado: **diferido**. La verificacion queda bloqueada a disponer de
`GEMINI_API_KEY`; es reproducible en ~3 minutos con el script documentado en la
bitacora. No bloquea el merge de #46.

## Streaming (punto 8)

`stream=true` en el request se acepta pero el adapter bufferea la respuesta
completa de Gemini/Ollama y devuelve un unico chunk Ollama-format. Streaming
real es iteracion posterior solo si #43 lo requiere.

## Coexistencia con Ollama real (punto 6)

Si se quiere correr Ollama real y el adapter a la vez, Ollama debe ir a `:11435`:

```bash
OLLAMA_HOST=0.0.0.0:11435 ollama serve
# o
ollama serve --port 11435
```

El adapter en modo `local` reenvia transparentemente a `$OLLAMA_UPSTREAM_HOST`.

## Como correr

```bash
cd code/meristem_inference_adapter
pip install -r requirements.txt
cp .env.example .env
# por defecto arranca con INFERENCE_BACKEND=test (no necesita Gemini ni Ollama)
python -m src.main
```

## Tests

```bash
cd code/meristem_inference_adapter
python -m pytest tests -v                    # suite completa (sin Gemini ni Ollama real)
python -m pytest -m gemini tests -v          # solo si GEMINI_API_KEY esta exportada
python -m pytest -m ollama tests -v          # solo si hay daemon Ollama en :11435
```

CI verde sin upstreams reales gracias al backend `test` (punto 11 de Cambium) y
a `respx` + fake `genai.Client` para los backends `local` y `cloud`. 88 tests
cubren los 11 criterios técnicos + smoke parity local-vs-cloud via headers
(`test_smoke_parity.py`).

## Troubleshooting

### 429 desde Gemini durante sweep de contexto (#47)

Esperado. El adapter reintenta (3 intentos por defecto, backoff
`500ms / 2s / 8s` configurable). Si el ultimo intento sigue dando 429, responde
503 con `Sprout-Inference-Error: upstream_rate_limited`. Caller (harness)
decide si descartar el punto del sweep o esperar.

### Puerto `:11434` ocupado

Otro Ollama corriendo. Matar ese daemon o cambiar `ADAPTER_PORT`.

### `thinking` vacio con backend cloud pese a `think=true`

Verificar `MERISTEM_THINKING_BUDGET` > 0 y que el modelo cloud soporte thinking
(26B MoE si; E4B-cloud, verificar).

## Referencias

- `bitacora/2026-04-20_meristem-reframe-modelo-objetivo_cambium.md` (D3)
- `bitacora/2026-04-19_thinking-mode-e4b-latencia_meristem.md`
- `bitacora/2026-04-21_thoughts-token-count-verificacion-pendiente_meristem.md`
- #46 (este PR) — comentarios con los 11 criterios
- #42 (quick-win `/api/chat`) — precede
- #44 (thinking mode A/B) — consume el adapter, fija `THINKING_BUDGET_TOKENS_PLACEHOLDER`
- #45 (harness completo) — consume el adapter
- #47 (sweep ventana de contexto) — consume el adapter
