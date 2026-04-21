"""Backend `local` — reverse-proxy transparente a Ollama real en :11435 (punto 6).

Meristem habla a :11434 (el adapter). Ollama real corre en :11435
(`ollama serve --port 11435`). El adapter reenvia sin modificar request ni
response, solo extrae contadores nativos para emitir los headers
`Sprout-Inference-*`.

## Contadores

Ollama devuelve en la respuesta:
- `prompt_eval_count` (tokens del prompt)
- `eval_count` (tokens generados; INCLUYE thinking si think=true)
- `prompt_eval_duration` y `eval_duration` (en ns)

Nota importante (punto 7): en local, `Sprout-Inference-Thinking-Tokens` se
emite como `0` porque Ollama no desglosa thinking de generacion en los
contadores — el campo `message.thinking` llega como texto, no como contador
separado. Consecuencia: `Sprout-Inference-Tokens-Out` en local equivale a
`eval_count` tal cual (incluye thinking).

Esto significa que la paridad local vs cloud NO es exacta en el header
`Tokens-Out` cuando thinking esta activo. El caller debe saberlo via
`Sprout-Inference-Backend`: en `cloud-gemini` el desglose es real, en
`local-ollama` `Thinking-Tokens=0` y `Tokens-Out` puede incluir thinking.

El harness #45 documenta esta asimetria al comparar.

## Streaming (punto 8)

Si el caller envia `stream=true`, el adapter lo fuerza a `false` hacia el
upstream. Ollama devuelve un unico JSON y el adapter lo relay tal cual.
Streaming real es iteracion posterior solo si #43 lo requiere.

## Errores

Fallos de conexion (Ollama upstream caido) se propagan como `httpx.HTTPError`.
`main.py` no los captura; FastAPI devuelve 500. Es el comportamiento deseado:
en local mode un upstream muerto es un bug del dev, no un escenario operativo.
"""

from __future__ import annotations

import copy
import time
from typing import Any

import httpx

from ..headers import InferenceMetrics


class LocalBackend:
    """Reverse-proxy a Ollama real en `:11435` (o lo que diga `upstream_host`)."""

    def __init__(
        self,
        upstream_host: str,
        *,
        timeout_s: float = 600.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        """Construye el backend.

        Args:
            upstream_host: URL base de Ollama real. Ej. `http://localhost:11435`.
            timeout_s: timeout total de la llamada. 600s por defecto porque
                generaciones largas con 26B pueden pasar de 2 minutos en CPU.
            client: `httpx.AsyncClient` inyectable para tests (respx).
        """
        self._upstream_host = upstream_host.rstrip("/")
        self._timeout = httpx.Timeout(timeout_s)
        self._external_client = client

    def _client(self) -> httpx.AsyncClient:
        if self._external_client is not None:
            return self._external_client
        return httpx.AsyncClient(
            base_url=self._upstream_host, timeout=self._timeout
        )

    async def _forward(
        self, path: str, request: dict[str, Any]
    ) -> tuple[dict[str, Any], InferenceMetrics]:
        # Forzamos stream=false al upstream: el adapter siempre devuelve un
        # unico JSON (punto 8). El caller puede mandar stream=true y recibira
        # el chunk completo en la respuesta sintetica.
        body = copy.deepcopy(request)
        body["stream"] = False

        t0 = time.perf_counter_ns()
        if self._external_client is not None:
            client = self._external_client
            owns_client = False
        else:
            client = httpx.AsyncClient(
                base_url=self._upstream_host, timeout=self._timeout
            )
            owns_client = True
        try:
            response = await client.post(path, json=body)
            response.raise_for_status()
            data = response.json()
        finally:
            if owns_client:
                await client.aclose()
        t1 = time.perf_counter_ns()

        # Contadores nativos de Ollama. Todos opcionales: si el upstream no los
        # devuelve (ej. error parcial), se asumen 0.
        tokens_in = int(data.get("prompt_eval_count") or 0)
        tokens_out = int(data.get("eval_count") or 0)
        model = str(data.get("model") or request.get("model") or "")
        duration_ms = max((t1 - t0) // 1_000_000, 1)

        metrics = InferenceMetrics(
            backend="local-ollama",
            model=model,
            tokens_in=tokens_in,
            # En local no podemos desglosar thinking; Tokens-Out incluye
            # thinking si think=true. Thinking-Tokens=0 explicito por contrato.
            tokens_out=tokens_out,
            thinking_tokens=0,
            duration_ms=duration_ms,
            cost_eur=0.0,
        )
        return data, metrics

    async def chat(
        self, request: dict[str, Any]
    ) -> tuple[dict[str, Any], InferenceMetrics]:
        return await self._forward("/api/chat", request)

    async def generate(
        self, request: dict[str, Any]
    ) -> tuple[dict[str, Any], InferenceMetrics]:
        return await self._forward("/api/generate", request)
