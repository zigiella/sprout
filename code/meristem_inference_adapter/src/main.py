"""FastAPI app del adapter.

Expone `/api/chat` y `/api/generate` en `:11434` (por defecto) con contrato
Ollama-nativo. Selecciona backend segun `INFERENCE_BACKEND` y delega.

Manejo de errores (punto 5 de #46): `UpstreamRateLimited` se traduce a 503 con
el header `Sprout-Inference-Error: upstream_rate_limited`. El caller (harness,
policy_engine) decide si descartar el punto o esperar.

Streaming (punto 8): `stream=true` se acepta pero el adapter bufferea la
respuesta completa y devuelve un unico chunk. Streaming real es iteracion
posterior solo si #43 lo requiere.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import FastAPI, Request, Response

from .backends.base import InferenceBackend
from .config import Settings, load_settings
from .headers import (
    HEADER_BACKEND,
    HEADER_ERROR,
    HEADER_MODEL,
    build_sprout_headers,
)
from .retry import UpstreamRateLimited

logger = logging.getLogger(__name__)


def _build_backend(settings: Settings) -> InferenceBackend:
    """Selecciona el backend segun `settings.backend`.

    Import local de cada backend para que `INFERENCE_BACKEND=test` no exija
    `google-genai` ni el upstream de Ollama.
    """
    if settings.backend == "cloud":
        from .backends.cloud import CloudBackend

        if not settings.gemini_api_key:
            raise RuntimeError(
                "INFERENCE_BACKEND=cloud pero GEMINI_API_KEY no esta definida."
            )
        return CloudBackend(
            api_key=settings.gemini_api_key,
            default_model=settings.gemini_default_model,
            model_aliases=settings.model_aliases,
            thinking_budget=settings.thinking_budget,
            retry=settings.retry,
            pricing=settings.pricing,
        )
    if settings.backend == "local":
        from .backends.local import LocalBackend

        return LocalBackend(upstream_host=settings.ollama_upstream_host)
    if settings.backend == "llamacpp":
        from .backends.llamacpp import LlamaCppBackend

        return LlamaCppBackend(server_url=settings.llamacpp_server_url)
    # backend == "test"
    from .backends.test import TestBackend

    return TestBackend()


def _json_dumps(obj: Any) -> str:
    # Helper separado para que los tests puedan stubbearlo si quisieran validar
    # que las duraciones se emiten como int, no float.
    return json.dumps(obj, ensure_ascii=False)


def _rate_limit_response(body: dict[str, Any], backend_label: str) -> Response:
    """Construye la respuesta 503 cuando el upstream agoto los reintentos."""
    # Preservamos backend/model del request para que el caller pueda correlar
    # el error con el punto del sweep que lo provoco, pero no emitimos
    # contadores (no hubo llamada exitosa).
    model = body.get("model", "")
    headers = {
        HEADER_BACKEND: backend_label,
        HEADER_MODEL: model,
        HEADER_ERROR: "upstream_rate_limited",
    }
    payload = {
        "error": "upstream_rate_limited",
        "detail": "Upstream agoto los reintentos tras los backoffs configurados.",
    }
    return Response(
        content=_json_dumps(payload),
        media_type="application/json",
        status_code=503,
        headers=headers,
    )


def _backend_label(settings: Settings) -> str:
    mapping = {
        "cloud": "cloud-gemini",
        "local": "local-ollama",
        "llamacpp": "local-llamacpp",
        "test": "test",
    }
    return mapping[settings.backend]


def create_app(settings: Settings | None = None) -> FastAPI:
    """Construye la FastAPI app. Factory permite inyectar settings en tests."""
    settings = settings or load_settings()
    backend = _build_backend(settings)
    label = _backend_label(settings)

    app = FastAPI(
        title="meristem_inference_adapter",
        version="0.1.0",
        description=(
            "Proxy Ollama-compatible. Backend: "
            f"{settings.backend}. Ver README.md."
        ),
    )
    app.state.settings = settings
    app.state.backend = backend
    app.state.backend_label = label

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "backend": settings.backend,
            "adapter_port": settings.adapter_port,
            "version": "0.1.0",
        }

    @app.post("/api/chat")
    async def chat(request: Request) -> Response:
        body = await request.json()
        # Leemos backend_label en cada request (no en closure) para que los
        # tests puedan inyectar un backend distinto via state monkey-patch.
        current_label = request.app.state.backend_label
        current_backend = request.app.state.backend
        try:
            response_body, metrics = await current_backend.chat(body)
        except UpstreamRateLimited as exc:
            logger.warning("chat rate-limited: %s", exc)
            return _rate_limit_response(body, current_label)
        headers = build_sprout_headers(metrics)
        return Response(
            content=_json_dumps(response_body),
            media_type="application/json",
            headers=headers,
        )

    @app.post("/api/generate")
    async def generate(request: Request) -> Response:
        body = await request.json()
        current_label = request.app.state.backend_label
        current_backend = request.app.state.backend
        try:
            response_body, metrics = await current_backend.generate(body)
        except UpstreamRateLimited as exc:
            logger.warning("generate rate-limited: %s", exc)
            return _rate_limit_response(body, current_label)
        headers = build_sprout_headers(metrics)
        return Response(
            content=_json_dumps(response_body),
            media_type="application/json",
            headers=headers,
        )

    return app


app = create_app()


def main() -> None:
    """Entrypoint CLI. `python -m src.main` levanta uvicorn."""
    import uvicorn

    settings = load_settings()
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.adapter_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
