"""Tests minimos de scaffold.

No tocan logica real (los stubs levantan NotImplementedError). Solo verifican:

- que el paquete es importable
- que Settings carga con defaults y backend=test
- que /health responde en la app construida

Tests de logica vienen en las siguientes tandas (tasks 2-7).
"""

from __future__ import annotations


def test_config_loads_with_defaults(monkeypatch):
    # limpiar env para que coja defaults
    for k in (
        "INFERENCE_BACKEND",
        "ADAPTER_PORT",
        "MERISTEM_THINKING_BUDGET",
        "GEMINI_API_KEY",
    ):
        monkeypatch.delenv(k, raising=False)

    from src.config import load_settings

    settings = load_settings()
    assert settings.backend == "test"
    assert settings.adapter_port == 11434
    assert settings.thinking_budget == 4096
    assert settings.gemini_api_key is None
    assert settings.retry.max_attempts == 3
    assert settings.retry.backoff_ms == (500, 2000, 8000)
    assert settings.model_aliases["gemma4:26b-moe"] == "gemma-4-26b-a4b"


def test_config_rejects_invalid_backend(monkeypatch):
    monkeypatch.setenv("INFERENCE_BACKEND", "bogus")

    from src.config import load_settings

    import pytest

    with pytest.raises(ValueError, match="INFERENCE_BACKEND invalido"):
        load_settings()


def test_resolve_model_fallback():
    from src.config import resolve_model

    aliases = {"gemma4:26b-moe": "gemma-4-26b-a4b"}
    assert resolve_model("gemma4:26b-moe", aliases) == "gemma-4-26b-a4b"
    # tag no aliased se devuelve tal cual
    assert resolve_model("unknown:model", aliases) == "unknown:model"


def test_health_endpoint(adapter_client):
    r = adapter_client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["backend"] == "test"
    assert body["adapter_port"] == 11434


def test_backend_is_test_protocol_compatible(adapter_app):
    from src.backends.base import InferenceBackend

    backend = adapter_app.state.backend
    # runtime_checkable Protocol: verifica que existen chat() y generate()
    assert isinstance(backend, InferenceBackend)
