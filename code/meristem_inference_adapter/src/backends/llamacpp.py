"""Backend `llamacpp` — reverse-proxy + converter a `llama-server` local.

Sirve para tuning Rhizome: Gemma 4 E2B sobre llama.cpp local imita el
runtime real del Jetson Orin Nano Super (mismo binario, mismo modelo,
misma cuantizacion Q4_K_M; unica diferencia es CPU x86 vs GPU NVIDIA
Tegra). Ver `bitacora/2026-04-27_setup-llama-cpp-local-rhizome_meristem.md`.

## Traduccion Ollama -> llama-server (OpenAI-format)

llama-server expone `/v1/chat/completions` y `/v1/completions` con
contrato OpenAI. El adapter recibe Ollama-format en `/api/chat` y
`/api/generate`, y aqui hacemos la conversion.

### `/api/chat`

Ollama:
```json
{
  "model": "gemma4:e2b",
  "messages": [{"role":"system|user|assistant","content":"..."}],
  "options": {"temperature":0.3,"num_predict":2048,"num_ctx":4096},
  "think": true|false,
  "stream": false
}
```

OpenAI:
```json
{
  "model": "gemma-4-E2B-it",
  "messages": [{"role":"system|user|assistant","content":"..."}],
  "temperature": 0.3,
  "max_tokens": 2048,
  "stream": false
}
```

`num_ctx` no es propagable por turno en llama-server (el contexto se fija
al arrancar el server con `-c`). Se ignora silenciosamente con un warning,
analogo a como hace el backend cloud con Gemini.

`think` no se propaga: el modelo Gemma 4 emite thinking inline siempre
que su chat template lo permite. Para apagar thinking habria que usar un
template distinto al arrancar `llama-server`. Por ahora (decision A de
R7-bis para multi-turn de Pollen), el caller decide a nivel de prompt si
quiere o no thinking.

### `/api/generate`

Mismo patron pero con un solo mensaje. Ollama `{"prompt":"..."}` se mapea
a `messages: [{"role":"user","content":"..."}]`.

## Reconstruccion de respuesta Ollama-format

llama-server devuelve:
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "<respuesta visible o vacio si thinking activo>",
      "reasoning_content": "<razonamiento si el modelo pensaba>"
    },
    "finish_reason": "stop|length|..."
  }],
  "usage": {"prompt_tokens": N, "completion_tokens": N, ...},
  "timings": {"prompt_ms": ..., "predicted_ms": ..., ...}
}
```

Convertimos a Ollama:
```json
{
  "model": "...",
  "created_at": "...",
  "message": {
    "role": "assistant",
    "content": "<content>",
    "thinking": "<reasoning_content si lo hay>"
  },
  "done": true,
  "done_reason": "<finish_reason>",
  "prompt_eval_count": <prompt_tokens>,
  "eval_count": <completion_tokens>,
  "total_duration": <ns>,
  "prompt_eval_duration": <ns>,
  "eval_duration": <ns>
}
```

El campo `thinking` aqui hace de paralelo al campo de Ollama nativo, asi
el harness/cliente puede acceder al razonamiento si lo necesita.

## Headers Sprout-Inference-*

`tokens_in` = `usage.prompt_tokens`
`tokens_out` = `usage.completion_tokens` (incluye thinking si el modelo
   lo emitio en `reasoning_content`)
`thinking_tokens` = no desglosable separadamente desde `usage.*` actual
   de llama-server. Marcamos 0 por contrato (analogo a backend `local`),
   y los tokens de razonamiento se cuentan en `tokens_out`. Documentamos
   la asimetria.
`duration_ms` = wallclock del adapter
`cost_eur` = 0.0 (modelo local)

## Errores

- 404 / connection refused: caller probablemente no arrancó `llama-server`.
  Se propaga como `httpx.HTTPError` (FastAPI -> 500).
- Timeout: igual.
- Status no 200 del server: se propaga.
"""

from __future__ import annotations

import copy
import logging
import time
from typing import Any

import httpx

from ..headers import InferenceMetrics

logger = logging.getLogger(__name__)


class LlamaCppBackend:
    """Reverse-proxy + converter a `llama-server` local (OpenAI-compatible)."""

    def __init__(
        self,
        server_url: str,
        *,
        timeout_s: float = 600.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        """Construye el backend.

        Args:
            server_url: URL base de `llama-server`. Ej. `http://localhost:8080`.
            timeout_s: timeout total. 600s por defecto (generaciones largas
                en CPU pueden pasar de 2 minutos).
            client: `httpx.AsyncClient` inyectable para tests.
        """
        self._server_url = server_url.rstrip("/")
        self._timeout = httpx.Timeout(timeout_s)
        self._external_client = client

    def _client(self) -> tuple[httpx.AsyncClient, bool]:
        """Devuelve (client, owns) — owns=True si el caller debe cerrarlo."""
        if self._external_client is not None:
            return self._external_client, False
        return (
            httpx.AsyncClient(base_url=self._server_url, timeout=self._timeout),
            True,
        )

    @staticmethod
    def _ollama_chat_to_openai(request: dict[str, Any]) -> dict[str, Any]:
        """Convierte request Ollama `/api/chat` a OpenAI `/v1/chat/completions`.

        - `messages` se pasa tal cual (mismo schema role/content).
        - `options.temperature` -> `temperature`.
        - `options.num_predict` -> `max_tokens` (si > 0).
        - `options.num_ctx` se ignora con warning (no propagable por turno).
        - `think` se ignora (controlado por chat template del server).
        - `stream` siempre `false` (el adapter no soporta streaming todavia).
        """
        messages = request.get("messages") or []
        options = request.get("options") or {}

        oai: dict[str, Any] = {
            "messages": messages,
            "stream": False,
        }

        # model name: el caller pone el alias Ollama (ej. gemma4:e2b);
        # el server llama.cpp tiene el modelo cargado fijo, asi que el
        # campo 'model' en OpenAI es informativo. Lo dejamos como esta.
        if "model" in request:
            oai["model"] = request["model"]

        if "temperature" in options:
            oai["temperature"] = options["temperature"]

        num_predict = options.get("num_predict")
        if num_predict is not None and num_predict > 0:
            oai["max_tokens"] = num_predict

        if "num_ctx" in options:
            logger.warning(
                "llamacpp backend: options.num_ctx=%s no es propagable por turno; "
                "el contexto se fija al arrancar llama-server con -c. Ignorado.",
                options["num_ctx"],
            )

        if request.get("think"):
            logger.debug(
                "llamacpp backend: think=true ignorado; el modelo Gemma 4 emite "
                "thinking segun su chat template (decision a nivel de prompt)."
            )

        return oai

    @staticmethod
    def _ollama_generate_to_openai(request: dict[str, Any]) -> dict[str, Any]:
        """Convierte request Ollama `/api/generate` a OpenAI."""
        messages: list[dict[str, str]] = []
        if request.get("system"):
            messages.append({"role": "system", "content": request["system"]})
        if request.get("prompt"):
            messages.append({"role": "user", "content": request["prompt"]})

        synth = dict(request)
        synth["messages"] = messages
        return LlamaCppBackend._ollama_chat_to_openai(synth)

    @staticmethod
    def _openai_to_ollama(
        oai_resp: dict[str, Any],
        request_model: str,
        elapsed_ns: int,
    ) -> dict[str, Any]:
        """Convierte response OpenAI a Ollama-format.

        - `content` puede venir vacio si el modelo emitio todo en
          `reasoning_content` (caso comun cuando thinking template activo).
        - Preservamos ambos: `content` -> `message.content`,
          `reasoning_content` -> `message.thinking` (analogo a Ollama nativo).
        """
        choices = oai_resp.get("choices") or []
        msg: dict[str, Any] = {}
        finish_reason = "stop"
        if choices:
            choice = choices[0]
            raw_msg = choice.get("message") or {}
            msg["role"] = raw_msg.get("role") or "assistant"
            msg["content"] = raw_msg.get("content") or ""
            reasoning = raw_msg.get("reasoning_content")
            if reasoning:
                msg["thinking"] = reasoning
            finish_reason = choice.get("finish_reason") or "stop"
        else:
            msg = {"role": "assistant", "content": ""}

        usage = oai_resp.get("usage") or {}
        timings = oai_resp.get("timings") or {}
        prompt_ms = float(timings.get("prompt_ms") or 0.0)
        predicted_ms = float(timings.get("predicted_ms") or 0.0)

        return {
            "model": oai_resp.get("model") or request_model,
            "created_at": oai_resp.get("created"),  # int unix; Ollama suele iso
            "message": msg,
            "done": True,
            "done_reason": finish_reason,
            "prompt_eval_count": int(usage.get("prompt_tokens") or 0),
            "eval_count": int(usage.get("completion_tokens") or 0),
            "total_duration": int(elapsed_ns),
            "prompt_eval_duration": int(prompt_ms * 1_000_000),
            "eval_duration": int(predicted_ms * 1_000_000),
        }

    async def _forward(
        self, request: dict[str, Any], path: str = "/v1/chat/completions",
        *, is_generate: bool = False,
    ) -> tuple[dict[str, Any], InferenceMetrics]:
        """POST a llama-server y devuelve (Ollama-response, metrics)."""
        if is_generate:
            oai_req = self._ollama_generate_to_openai(request)
        else:
            oai_req = self._ollama_chat_to_openai(request)

        request_model = str(request.get("model") or "")

        t0 = time.perf_counter_ns()
        client, owns_client = self._client()
        try:
            response = await client.post(path, json=oai_req)
            response.raise_for_status()
            oai_data = response.json()
        finally:
            if owns_client:
                await client.aclose()
        t1 = time.perf_counter_ns()
        elapsed_ns = t1 - t0
        elapsed_ms = max(elapsed_ns // 1_000_000, 1)

        ollama_resp = self._openai_to_ollama(
            oai_data, request_model=request_model, elapsed_ns=elapsed_ns
        )

        usage = oai_data.get("usage") or {}
        tokens_in = int(usage.get("prompt_tokens") or 0)
        tokens_out = int(usage.get("completion_tokens") or 0)
        # llama-server en `usage` no separa thinking de content. El
        # `reasoning_content` viene como string en `message`, no se cuenta
        # aparte. Marcamos thinking_tokens=0 por contrato (el caller sabe
        # que tokens_out incluye thinking si lo hubo, igual que en local).
        metrics = InferenceMetrics(
            backend="local-llamacpp",
            model=ollama_resp["model"] or request_model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            thinking_tokens=0,
            duration_ms=elapsed_ms,
            cost_eur=0.0,
        )
        return ollama_resp, metrics

    async def chat(
        self, request: dict[str, Any]
    ) -> tuple[dict[str, Any], InferenceMetrics]:
        return await self._forward(request, "/v1/chat/completions", is_generate=False)

    async def generate(
        self, request: dict[str, Any]
    ) -> tuple[dict[str, Any], InferenceMetrics]:
        return await self._forward(request, "/v1/chat/completions", is_generate=True)
