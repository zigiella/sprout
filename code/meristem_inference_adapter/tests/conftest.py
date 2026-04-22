"""Config de pytest para meristem_inference_adapter.

Anade la raiz del paquete al sys.path (para `from src... import ...`) y
`code/shared` (para reusar los schemas canonicos en tests de flatten).

Fixtures compartidos:
- `adapter_settings()`  → `Settings` con backend=test, valores deterministicos.
- `adapter_app()`       → `FastAPI` construida sobre esos settings.
- `adapter_client()`    → `TestClient` sobre la app.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_THIS = Path(__file__).resolve()
_ADAPTER_ROOT = _THIS.parents[1]
_CODE_ROOT = _ADAPTER_ROOT.parent
_SHARED = _CODE_ROOT / "shared"

for path in (_ADAPTER_ROOT, _SHARED):
    path_str = str(path)
    if path.exists() and path_str not in sys.path:
        sys.path.insert(0, path_str)

# Imports que dependen de sys.path se hacen dentro de las fixtures para que
# `collect` no falle si uno de los modulos aun no existe durante el scaffold.


def _make_settings():
    from src.config import (
        DEFAULT_MODEL_ALIASES,
        PricingConfig,
        RetryConfig,
        Settings,
    )

    return Settings(
        backend="test",
        adapter_port=11434,
        ollama_upstream_host="http://localhost:11435",
        gemini_api_key=None,
        gemini_default_model="gemma-4-26b-a4b",
        thinking_budget=4096,
        pricing=PricingConfig(
            in_eur_per_1k=0.0,
            out_eur_per_1k=0.0,
            thinking_eur_per_1k=0.0,
        ),
        retry=RetryConfig(max_attempts=3, backoff_ms=(500, 2000, 8000)),
        model_aliases=dict(DEFAULT_MODEL_ALIASES),
    )


@pytest.fixture
def adapter_settings():
    return _make_settings()


@pytest.fixture
def adapter_app(adapter_settings):
    from src.main import create_app

    return create_app(adapter_settings)


@pytest.fixture
def adapter_client(adapter_app):
    from fastapi.testclient import TestClient

    with TestClient(adapter_app) as client:
        yield client
