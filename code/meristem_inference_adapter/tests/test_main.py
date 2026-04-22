"""Integration tests de main.py (/api/chat, /api/generate) con el backend test.

Cubre:
- Header `Sprout-Inference-*` completo en la respuesta HTTP (las 7 claves).
- Body Ollama-shaped (`message` en chat, `response` en generate).
- Seleccion de fixture via `options.test_fixture`.
- Traduccion de `UpstreamRateLimited` a 503 con `Sprout-Inference-Error`.
- /health expone el backend configurado.
- Coexistencia del adapter con `ollama serve` (port layout punto 6) validada
  a nivel de contrato — no se arranca ollama real en CI.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.backends.test import CannedResponse, TestBackend
from src.config import (
    DEFAULT_MODEL_ALIASES,
    PricingConfig,
    RetryConfig,
    Settings,
)
from src.headers import (
    HEADER_BACKEND,
    HEADER_COST_EUR,
    HEADER_DURATION_MS,
    HEADER_ERROR,
    HEADER_MODEL,
    HEADER_THINKING_TOKENS,
    HEADER_TOKENS_IN,
    HEADER_TOKENS_OUT,
)
from src.main import create_app
from src.retry import UpstreamRateLimited


def _make_test_settings() -> Settings:
    return Settings(
        backend="test",
        adapter_port=11434,
        ollama_upstream_host="http://localhost:11435",
        gemini_api_key=None,
        gemini_default_model="gemma-4-26b-a4b",
        thinking_budget=4096,
        pricing=PricingConfig(0.0, 0.0, 0.0),
        retry=RetryConfig(max_attempts=3, backoff_ms=(500, 2000, 8000)),
        model_aliases=dict(DEFAULT_MODEL_ALIASES),
    )


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------


def test_health_reporta_backend():
    app = create_app(_make_test_settings())
    with TestClient(app) as client:
        r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["backend"] == "test"
    assert body["adapter_port"] == 11434


# ---------------------------------------------------------------------------
# /api/chat
# ---------------------------------------------------------------------------


def test_chat_body_ollama_shape_y_headers_completos():
    app = create_app(_make_test_settings())
    with TestClient(app) as client:
        r = client.post(
            "/api/chat",
            json={
                "model": "gemma4:26b-moe",
                "messages": [{"role": "user", "content": "hola"}],
            },
        )
    assert r.status_code == 200
    body = r.json()
    # Body Ollama-shape: /api/chat devuelve `message`.
    assert body["message"]["role"] == "assistant"
    assert "content" in body["message"]
    assert "thinking" in body["message"]
    assert body["done"] is True
    assert body["prompt_eval_count"] >= 0
    assert body["eval_count"] >= 0
    # Headers Sprout-Inference-*: las 7 claves presentes.
    assert r.headers[HEADER_BACKEND] == "test"
    assert r.headers[HEADER_MODEL] == "gemma4:26b-moe"
    assert int(r.headers[HEADER_TOKENS_IN]) >= 0
    assert int(r.headers[HEADER_TOKENS_OUT]) >= 0
    assert int(r.headers[HEADER_THINKING_TOKENS]) >= 0
    assert int(r.headers[HEADER_DURATION_MS]) >= 1
    assert float(r.headers[HEADER_COST_EUR]) == 0.0


def test_chat_selecciona_fixture_via_options():
    app = create_app(_make_test_settings())
    with TestClient(app) as client:
        r = client.post(
            "/api/chat",
            json={
                "model": "gemma4:26b-moe",
                "messages": [],
                "options": {"test_fixture": "with_thinking"},
            },
        )
    assert r.status_code == 200
    body = r.json()
    assert body["message"]["content"] == "respuesta final"
    assert body["message"]["thinking"].startswith("razonando")
    # Headers deben reflejar el canned `with_thinking`: tokens_out=5, thinking=15.
    assert r.headers[HEADER_TOKENS_OUT] == "5"
    assert r.headers[HEADER_THINKING_TOKENS] == "15"


def test_chat_thinking_cero_se_emite_explicito():
    # Punto 7: thinking_tokens=0 explicito, no header ausente.
    app = create_app(_make_test_settings())
    with TestClient(app) as client:
        r = client.post(
            "/api/chat",
            json={"model": "x", "messages": []},  # canned default → thinking=0
        )
    assert HEADER_THINKING_TOKENS in r.headers
    assert r.headers[HEADER_THINKING_TOKENS] == "0"


# ---------------------------------------------------------------------------
# /api/generate
# ---------------------------------------------------------------------------


def test_generate_body_shape_y_headers():
    app = create_app(_make_test_settings())
    with TestClient(app) as client:
        r = client.post(
            "/api/generate",
            json={"model": "gemma4:e4b", "prompt": "hola"},
        )
    assert r.status_code == 200
    body = r.json()
    # /api/generate usa `response`, no `message`.
    assert "response" in body
    assert "message" not in body
    assert body["done"] is True
    # Headers idem que chat.
    assert r.headers[HEADER_BACKEND] == "test"
    assert r.headers[HEADER_MODEL] == "gemma4:e4b"


# ---------------------------------------------------------------------------
# Error: UpstreamRateLimited → 503 + Sprout-Inference-Error
# ---------------------------------------------------------------------------


class _AlwaysRateLimitBackend:
    """Backend que siempre levanta UpstreamRateLimited. Para test del handler."""

    __test__ = False

    async def chat(self, request):
        raise UpstreamRateLimited(attempts=3, last_error=RuntimeError("429"))

    async def generate(self, request):
        raise UpstreamRateLimited(attempts=3, last_error=RuntimeError("429"))


def _make_app_with_backend(backend, label: str = "cloud-gemini"):
    # Construye app con un backend inyectado via monkey-patch del state.
    settings = _make_test_settings()
    app = create_app(settings)
    app.state.backend = backend
    app.state.backend_label = label
    return app


def test_chat_rate_limit_devuelve_503_con_header_de_error():
    app = _make_app_with_backend(_AlwaysRateLimitBackend(), label="cloud-gemini")
    with TestClient(app) as client:
        r = client.post(
            "/api/chat",
            json={"model": "gemma4:26b-moe", "messages": []},
        )
    assert r.status_code == 503
    assert r.headers[HEADER_ERROR] == "upstream_rate_limited"
    # Preservamos backend/model para que el caller pueda correlar el error.
    assert r.headers[HEADER_BACKEND] == "cloud-gemini"
    assert r.headers[HEADER_MODEL] == "gemma4:26b-moe"
    # Pero NO emitimos contadores (no hubo llamada exitosa).
    assert HEADER_TOKENS_IN not in r.headers
    assert HEADER_TOKENS_OUT not in r.headers


def test_generate_rate_limit_devuelve_503_con_header_de_error():
    app = _make_app_with_backend(_AlwaysRateLimitBackend())
    with TestClient(app) as client:
        r = client.post(
            "/api/generate",
            json={"model": "gemma4:e4b", "prompt": "x"},
        )
    assert r.status_code == 503
    assert r.headers[HEADER_ERROR] == "upstream_rate_limited"


# ---------------------------------------------------------------------------
# Custom canned: permite inyectar fixtures desde tests.
# ---------------------------------------------------------------------------


def test_custom_canned_se_propaga_a_la_app():
    custom = {
        "default": CannedResponse(
            model="gemma-4-26b-a4b",
            content="canned!",
            tokens_in=7,
            tokens_out=3,
            thinking_tokens=0,
        ),
    }
    backend = TestBackend(canned=custom)
    app = _make_app_with_backend(backend, label="test")
    with TestClient(app) as client:
        r = client.post("/api/chat", json={"model": "m", "messages": []})
    assert r.status_code == 200
    body = r.json()
    assert body["message"]["content"] == "canned!"
    assert r.headers[HEADER_TOKENS_IN] == "7"
    assert r.headers[HEADER_TOKENS_OUT] == "3"


# ---------------------------------------------------------------------------
# Contrato: /api/chat y /api/generate devuelven Content-Type application/json
# ---------------------------------------------------------------------------


def test_content_type_json_en_ambos_endpoints():
    app = create_app(_make_test_settings())
    with TestClient(app) as client:
        for path, payload in (
            ("/api/chat", {"model": "m", "messages": []}),
            ("/api/generate", {"model": "m", "prompt": "x"}),
        ):
            r = client.post(path, json=payload)
            assert r.headers["content-type"].startswith("application/json"), path
