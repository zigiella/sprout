"""Backend `cloud` — Gemini API via `google-genai`.

Compone las cinco utilidades de la task 2:

1. Si el request trae `format=<schema>`, pasar por `schema_flatten` (Gemini
   rechaza `$ref`/`$defs`).
2. Mapear `think` con `thinking_map.map_think_to_gemini`.
3. Ejecutar la llamada a Gemini dentro de `retry.with_retry` para 429s
   (backoff 500ms/2s/8s, 3 intentos por defecto).
4. Dividir `candidate.content.parts` en content + thinking con
   `reconstruct.split_gemini_parts`.
5. Construir respuesta Ollama-format y emitir `InferenceMetrics` con el
   desglose real de tokens.

## Traduccion Ollama → Gemini

### `/api/chat`

Ollama `messages: [{"role": "user"|"assistant"|"system", "content": "..."}]`
se mapea a:
- `role=system` → `config.system_instruction` (NO va en `contents`).
- `role=user` → `Content(role="user", parts=[Part.from_text("...")])`.
- `role=assistant` → `Content(role="model", parts=[Part.from_text("...")])`.

### `/api/generate`

Ollama `{"prompt": "...", "system": "..."?}` se mapea a un unico mensaje user
mas un `system_instruction` opcional.

### `options`

- `options.temperature` → `config.temperature`
- `options.num_predict` → `config.max_output_tokens` (si > 0).
- `options.num_ctx` → **NO propagable a Gemini**. Gemini no expone ventana por
  llamada; el limite efectivo lo fija el modelo. Se ignora silenciosamente con
  un warning en log. Ver bitacora del sweep de #47.

## Contadores y eval_count

Ollama `eval_count` = `candidates_token_count + thoughts_token_count`. Los
headers `Sprout-Inference-*` desglosan (ver `headers.py` punto 4).

## Cost

`cost_eur = (tokens_in/1000)*price_in + (tokens_out/1000)*price_out
          + (thinking/1000)*price_thinking`.

Los tres precios vienen de env (`GEMINI_PRICE_*_EUR_PER_1K`), default `0.0` —
no se hardcodea el pricing vigente. Si el caller no configura, el header sale
`0.000000` y el harness documenta que el coste real hay que calcularlo fuera.

## thoughts_token_count: ventana o output-only

Pendiente verificar empiricamente (ver task 8). El adapter emite los 3
contadores por separado; si thoughts descuenta de la ventana total, eso afecta
al scope del sweep de #47, no al adapter.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable

from ..config import PricingConfig, RetryConfig, resolve_model
from ..headers import InferenceMetrics
from ..reconstruct import split_gemini_parts
from ..retry import with_retry
from ..schema_flatten import flatten_json_schema
from ..thinking_map import map_think_to_gemini

logger = logging.getLogger(__name__)

# Importacion perezosa del SDK para que `INFERENCE_BACKEND=test` no exija
# `google-genai` instalado.
_GENAI_MODULE = None
_GENAI_TYPES = None
_GENAI_ERRORS = None


def _load_genai() -> tuple[Any, Any, Any]:
    """Carga google-genai on-demand. Cachea el resultado."""
    global _GENAI_MODULE, _GENAI_TYPES, _GENAI_ERRORS
    if _GENAI_MODULE is None:
        from google import genai as _genai  # type: ignore[import-untyped]
        from google.genai import errors as _errors, types as _types

        _GENAI_MODULE = _genai
        _GENAI_TYPES = _types
        _GENAI_ERRORS = _errors
    return _GENAI_MODULE, _GENAI_TYPES, _GENAI_ERRORS


def _is_rate_limit_error(exc: BaseException) -> bool:
    """Predicado para `with_retry`: True si la excepcion es un 429 de Gemini."""
    _, _, errors_mod = _load_genai()
    if not isinstance(exc, errors_mod.APIError):
        return False
    return getattr(exc, "code", None) == 429


def _translate_chat_request(request: dict[str, Any]) -> tuple[list, str | None]:
    """Traduce `messages` Ollama → (contents Gemini, system_instruction)."""
    _, types, _ = _load_genai()
    system_instruction: str | None = None
    contents: list = []
    for msg in request.get("messages", []):
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "system":
            # Gemini permite un unico system_instruction. Si hay varios msgs
            # system, se concatenan con un blank line entre ellos — esto es
            # poco comun pero el contrato Ollama lo permite.
            system_instruction = (
                content
                if system_instruction is None
                else f"{system_instruction}\n\n{content}"
            )
            continue
        gemini_role = "model" if role == "assistant" else "user"
        contents.append(
            types.Content(
                role=gemini_role,
                parts=[types.Part.from_text(text=content)],
            )
        )
    return contents, system_instruction


def _translate_generate_request(request: dict[str, Any]) -> tuple[list, str | None]:
    """Traduce `prompt` Ollama → (contents Gemini, system_instruction)."""
    _, types, _ = _load_genai()
    prompt = request.get("prompt", "")
    system_instruction = request.get("system") or None
    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    ]
    return contents, system_instruction


def _build_config(
    request: dict[str, Any],
    *,
    thinking_budget: int,
    system_instruction: str | None,
) -> Any:
    """Construye GenerateContentConfig desde options + format + think."""
    _, types, _ = _load_genai()
    options = request.get("options") or {}

    kwargs: dict[str, Any] = {}
    if system_instruction is not None:
        kwargs["system_instruction"] = system_instruction

    # temperature
    if "temperature" in options:
        kwargs["temperature"] = float(options["temperature"])
    # num_predict → max_output_tokens
    if "num_predict" in options:
        n = int(options["num_predict"])
        if n > 0:
            kwargs["max_output_tokens"] = n
    # num_ctx: Gemini no lo soporta por llamada.
    if "num_ctx" in options:
        logger.info(
            "cloud: num_ctx=%s ignorado (Gemini no expone ventana por llamada).",
            options["num_ctx"],
        )

    # format=<schema>: estructura JSON-structured-output.
    fmt = request.get("format")
    if isinstance(fmt, dict):
        flat = flatten_json_schema(fmt)
        kwargs["response_mime_type"] = "application/json"
        kwargs["response_schema"] = flat
    elif fmt == "json":
        # Ollama permite `format: "json"` sin schema. Gemini necesita
        # response_mime_type; lo fijamos igual sin schema.
        kwargs["response_mime_type"] = "application/json"

    # thinking
    think_flag = request.get("think")
    thinking_cfg = map_think_to_gemini(
        think=think_flag, budget_when_on=thinking_budget
    )
    kwargs["thinking_config"] = types.ThinkingConfig(
        include_thoughts=thinking_cfg.include_thoughts,
        thinking_budget=thinking_cfg.thinking_budget,
    )

    return types.GenerateContentConfig(**kwargs)


def _compute_cost(
    *,
    tokens_in: int,
    tokens_out: int,
    thinking_tokens: int,
    pricing: PricingConfig,
) -> float:
    return (
        (tokens_in / 1000.0) * pricing.in_eur_per_1k
        + (tokens_out / 1000.0) * pricing.out_eur_per_1k
        + (thinking_tokens / 1000.0) * pricing.thinking_eur_per_1k
    )


class CloudBackend:
    """Backend Gemini API."""

    def __init__(
        self,
        *,
        api_key: str,
        default_model: str,
        model_aliases: dict[str, str],
        thinking_budget: int,
        retry: RetryConfig,
        pricing: PricingConfig,
        client_factory: Callable[[str], Any] | None = None,
    ) -> None:
        """Construye el backend cloud.

        Args:
            api_key: GEMINI_API_KEY.
            default_model: id de modelo Gemini a usar si el caller no manda uno.
            model_aliases: dict `{"gemma4:26b-moe": "gemma-4-26b-a4b", ...}`.
            thinking_budget: presupuesto de thinking cuando `think=true`.
            retry: politica de reintentos para 429s.
            pricing: pricing por 1K tokens para los 3 tipos de contador.
            client_factory: callable que recibe `api_key` y devuelve un cliente
                al estilo `genai.Client` (con `.aio.models.generate_content`).
                Inyectable para tests.
        """
        self._api_key = api_key
        self._default_model = default_model
        self._aliases = dict(model_aliases)
        self._thinking_budget = thinking_budget
        self._retry = retry
        self._pricing = pricing
        self._client_factory = client_factory
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            if self._client_factory is not None:
                self._client = self._client_factory(self._api_key)
            else:
                genai, _, _ = _load_genai()
                self._client = genai.Client(api_key=self._api_key)
        return self._client

    def _resolve_model(self, request: dict[str, Any]) -> str:
        tag = request.get("model") or self._default_model
        return resolve_model(tag, self._aliases)

    async def _call_gemini(
        self, *, model_id: str, contents: list, config: Any
    ) -> Any:
        client = self._get_client()

        async def _op() -> Any:
            return await client.aio.models.generate_content(
                model=model_id, contents=contents, config=config
            )

        return await with_retry(
            _op,
            max_attempts=self._retry.max_attempts,
            backoff_ms=self._retry.backoff_ms,
            is_rate_limit=_is_rate_limit_error,
        )

    def _build_metrics_and_body_common(
        self,
        *,
        response: Any,
        request_model_tag: str,
        duration_ns: int,
    ) -> tuple[str, str, int, int, int, int]:
        """Extrae campos comunes de la respuesta Gemini.

        Returns:
            (content, thinking, tokens_in, tokens_out, thinking_tokens, duration_ms)
        """
        candidates = getattr(response, "candidates", None) or []
        if not candidates:
            raise RuntimeError(
                "Gemini respondio sin candidates — posible filtro de seguridad."
            )
        parts = getattr(candidates[0].content, "parts", None) or []
        split = split_gemini_parts(parts)

        usage = getattr(response, "usage_metadata", None)
        tokens_in = int(getattr(usage, "prompt_token_count", 0) or 0)
        tokens_out = int(getattr(usage, "candidates_token_count", 0) or 0)
        thinking_tokens = int(getattr(usage, "thoughts_token_count", 0) or 0)
        duration_ms = max(duration_ns // 1_000_000, 1)

        return (
            split.content,
            split.thinking,
            tokens_in,
            tokens_out,
            thinking_tokens,
            duration_ms,
        )

    def _split_duration_ns(
        self, total_ns: int, tokens_in: int, tokens_out_plus_thinking: int
    ) -> tuple[int, int]:
        """Proporcional a tokens; mitad-mitad si ambos son 0."""
        total = tokens_in + tokens_out_plus_thinking
        if total == 0:
            half = total_ns // 2
            return half, total_ns - half
        prompt_ns = (total_ns * tokens_in) // total
        return prompt_ns, total_ns - prompt_ns

    async def chat(
        self, request: dict[str, Any]
    ) -> tuple[dict[str, Any], InferenceMetrics]:
        request_model_tag = request.get("model", self._default_model)
        model_id = self._resolve_model(request)
        contents, system_instruction = _translate_chat_request(request)
        config = _build_config(
            request,
            thinking_budget=self._thinking_budget,
            system_instruction=system_instruction,
        )

        t0 = time.perf_counter_ns()
        response = await self._call_gemini(
            model_id=model_id, contents=contents, config=config
        )
        t1 = time.perf_counter_ns()
        total_ns = max(t1 - t0, 1_000)

        content, thinking, tokens_in, tokens_out, thinking_tokens, duration_ms = (
            self._build_metrics_and_body_common(
                response=response,
                request_model_tag=request_model_tag,
                duration_ns=total_ns,
            )
        )

        prompt_ns, eval_ns = self._split_duration_ns(
            total_ns, tokens_in, tokens_out + thinking_tokens
        )

        body = {
            "model": request_model_tag,  # preservamos el tag que el caller envio
            "created_at": "1970-01-01T00:00:00Z",  # deterministico
            "message": {
                "role": "assistant",
                "content": content,
                "thinking": thinking,
            },
            "done": True,
            "done_reason": "stop",
            "prompt_eval_count": tokens_in,
            # Contrato Ollama: eval_count incluye thinking.
            "eval_count": tokens_out + thinking_tokens,
            "prompt_eval_duration": prompt_ns,
            "eval_duration": eval_ns,
            "total_duration": total_ns,
        }
        metrics = InferenceMetrics(
            backend="cloud-gemini",
            model=request_model_tag,
            tokens_in=tokens_in,
            tokens_out=tokens_out,  # SIN thinking
            thinking_tokens=thinking_tokens,
            duration_ms=duration_ms,
            cost_eur=_compute_cost(
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                thinking_tokens=thinking_tokens,
                pricing=self._pricing,
            ),
        )
        return body, metrics

    async def generate(
        self, request: dict[str, Any]
    ) -> tuple[dict[str, Any], InferenceMetrics]:
        request_model_tag = request.get("model", self._default_model)
        model_id = self._resolve_model(request)
        contents, system_instruction = _translate_generate_request(request)
        config = _build_config(
            request,
            thinking_budget=self._thinking_budget,
            system_instruction=system_instruction,
        )

        t0 = time.perf_counter_ns()
        response = await self._call_gemini(
            model_id=model_id, contents=contents, config=config
        )
        t1 = time.perf_counter_ns()
        total_ns = max(t1 - t0, 1_000)

        content, thinking, tokens_in, tokens_out, thinking_tokens, duration_ms = (
            self._build_metrics_and_body_common(
                response=response,
                request_model_tag=request_model_tag,
                duration_ns=total_ns,
            )
        )

        prompt_ns, eval_ns = self._split_duration_ns(
            total_ns, tokens_in, tokens_out + thinking_tokens
        )

        body = {
            "model": request_model_tag,
            "created_at": "1970-01-01T00:00:00Z",
            # /api/generate usa `response` en vez de `message`.
            "response": content,
            "thinking": thinking,
            "done": True,
            "done_reason": "stop",
            "prompt_eval_count": tokens_in,
            "eval_count": tokens_out + thinking_tokens,
            "prompt_eval_duration": prompt_ns,
            "eval_duration": eval_ns,
            "total_duration": total_ns,
        }
        metrics = InferenceMetrics(
            backend="cloud-gemini",
            model=request_model_tag,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            thinking_tokens=thinking_tokens,
            duration_ms=duration_ms,
            cost_eur=_compute_cost(
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                thinking_tokens=thinking_tokens,
                pricing=self._pricing,
            ),
        )
        return body, metrics
