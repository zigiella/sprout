"""Smoke parity test: mismo /api/chat contra local y cloud, headers uniformes.

Valida el contrato agnostico de backend de #46: el caller ve la misma shape
de headers y body sin branchear. Los numeros difieren (cada upstream reporta
sus propios contadores), pero:

- Las 7 claves `Sprout-Inference-*` estan presentes en ambos.
- Body es Ollama-shape (`message.content`, `done: true`).
- `Sprout-Inference-Backend` identifica el upstream (local-ollama vs cloud-gemini).
- `Sprout-Inference-Model` refleja el tag del caller, no el id interno de Gemini.

Asimetria documentada (punto 7): con `think=true`, local emite
`Thinking-Tokens=0` porque Ollama no desglosa, mientras cloud reporta el
`thoughts_token_count` real. Test dedicado lo fija como contrato.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import httpx
import respx
from fastapi.testclient import TestClient

from src.backends.cloud import CloudBackend
from src.backends.local import LocalBackend
from src.config import (
    DEFAULT_MODEL_ALIASES,
    PricingConfig,
    RetryConfig,
    Settings,
)
from src.headers import (
    ALL_METRIC_HEADERS,
    HEADER_BACKEND,
    HEADER_COST_EUR,
    HEADER_DURATION_MS,
    HEADER_MODEL,
    HEADER_THINKING_TOKENS,
    HEADER_TOKENS_IN,
    HEADER_TOKENS_OUT,
)
from src.main import create_app


UPSTREAM_OLLAMA = "http://localhost:11435"


# ---------------------------------------------------------------------------
# Helpers: settings base, instalador de backend, respuesta Ollama/Gemini canned.
# ---------------------------------------------------------------------------


def _base_settings() -> Settings:
    # backend="test" para que create_app no intente instanciar cloud/local con
    # credenciales reales; luego monkey-patch `app.state.backend` con la pieza
    # que queremos ejercitar.
    return Settings(
        backend="test",
        adapter_port=11434,
        ollama_upstream_host=UPSTREAM_OLLAMA,
        gemini_api_key="fake",
        gemini_default_model="gemma-4-26b-a4b",
        thinking_budget=4096,
        pricing=PricingConfig(0.0, 0.0, 0.0),
        retry=RetryConfig(max_attempts=3, backoff_ms=(1, 1, 1)),
        model_aliases=dict(DEFAULT_MODEL_ALIASES),
    )


def _install_backend(app, backend: Any, label: str) -> None:
    app.state.backend = backend
    app.state.backend_label = label


def _ollama_canned(
    *,
    content: str = "hola desde ollama",
    thinking: str | None = None,
    prompt_eval_count: int = 42,
    eval_count: int = 17,
) -> dict:
    message: dict = {"role": "assistant", "content": content}
    if thinking is not None:
        message["thinking"] = thinking
    return {
        "model": "gemma4:26b-moe",
        "created_at": "2026-04-21T12:00:00Z",
        "message": message,
        "done": True,
        "done_reason": "stop",
        "prompt_eval_count": prompt_eval_count,
        "prompt_eval_duration": 10_000_000,
        "eval_count": eval_count,
        "eval_duration": 100_000_000,
    }


class _FakeGenai:
    """Shape minima de `genai.Client` para inyectar via `client_factory`."""

    def __init__(self, response: Any) -> None:
        self._response = response
        self.aio = SimpleNamespace(
            models=SimpleNamespace(generate_content=self._gen)
        )

    async def _gen(self, *, model, contents, config):  # noqa: ARG002
        return self._response


def _gemini_canned(
    *,
    content_parts: list[tuple[str, bool]],
    prompt_tokens: int = 42,
    candidates_tokens: int = 17,
    thoughts_tokens: int = 0,
) -> SimpleNamespace:
    parts = [SimpleNamespace(text=t, thought=th) for t, th in content_parts]
    return SimpleNamespace(
        candidates=[SimpleNamespace(content=SimpleNamespace(parts=parts))],
        usage_metadata=SimpleNamespace(
            prompt_token_count=prompt_tokens,
            candidates_token_count=candidates_tokens,
            thoughts_token_count=thoughts_tokens,
        ),
    )


def _make_cloud_backend(fake_client: _FakeGenai) -> CloudBackend:
    return CloudBackend(
        api_key="fake",
        default_model="gemma-4-26b-a4b",
        model_aliases={"gemma4:26b-moe": "gemma-4-26b-a4b"},
        thinking_budget=4096,
        retry=RetryConfig(max_attempts=3, backoff_ms=(1, 1, 1)),
        pricing=PricingConfig(0.0, 0.0, 0.0),
        client_factory=lambda _api_key: fake_client,
    )


# ---------------------------------------------------------------------------
# Parity de shape: headers y body igual forma aunque upstreams distintos.
# ---------------------------------------------------------------------------


@respx.mock
def test_smoke_parity_headers_y_body_shape_uniformes_entre_local_y_cloud():
    # Mismo request para ambos backends.
    payload = {
        "model": "gemma4:26b-moe",
        "messages": [{"role": "user", "content": "hola"}],
    }

    # --- local (respx intercepta httpx a :11435) ---
    respx.post(f"{UPSTREAM_OLLAMA}/api/chat").mock(
        return_value=httpx.Response(
            200,
            json=_ollama_canned(prompt_eval_count=42, eval_count=17),
        )
    )
    app_local = create_app(_base_settings())
    _install_backend(
        app_local, LocalBackend(upstream_host=UPSTREAM_OLLAMA), "local-ollama"
    )
    with TestClient(app_local) as c:
        r_local = c.post("/api/chat", json=payload)

    # --- cloud (fake genai client) ---
    fake_client = _FakeGenai(
        _gemini_canned(
            content_parts=[("hola desde gemini", False)],
            prompt_tokens=42,
            candidates_tokens=17,
            thoughts_tokens=0,
        )
    )
    app_cloud = create_app(_base_settings())
    _install_backend(app_cloud, _make_cloud_backend(fake_client), "cloud-gemini")
    with TestClient(app_cloud) as c:
        r_cloud = c.post("/api/chat", json=payload)

    # --- parity assertions ---
    # Status uniforme.
    assert r_local.status_code == 200
    assert r_cloud.status_code == 200

    # Body shape Ollama-compatible en ambos.
    for resp in (r_local, r_cloud):
        b = resp.json()
        assert "message" in b, "ambos backends deben devolver `message`"
        assert b["message"]["role"] == "assistant"
        assert "content" in b["message"]
        assert b["done"] is True

    # Las 7 claves Sprout-Inference-* presentes en ambos.
    for h in ALL_METRIC_HEADERS:
        assert h in r_local.headers, f"local missing {h}"
        assert h in r_cloud.headers, f"cloud missing {h}"

    # Backend label diferencia los upstreams.
    assert r_local.headers[HEADER_BACKEND] == "local-ollama"
    assert r_cloud.headers[HEADER_BACKEND] == "cloud-gemini"

    # Model label refleja el tag del caller en AMBOS. Para cloud, el backend
    # resuelve el alias a `gemma-4-26b-a4b` para la llamada a Gemini pero
    # preserva el tag original en el body/headers (punto 9 de #46).
    assert r_local.headers[HEADER_MODEL] == "gemma4:26b-moe"
    assert r_cloud.headers[HEADER_MODEL] == "gemma4:26b-moe"

    # Contadores numericos: los upstreams stubeados reportaron el mismo valor,
    # asi que el header tambien. El test clave es que AMBOS emitieron un
    # numero parseable en la misma clave.
    assert r_local.headers[HEADER_TOKENS_IN] == "42"
    assert r_cloud.headers[HEADER_TOKENS_IN] == "42"
    assert r_local.headers[HEADER_TOKENS_OUT] == "17"
    assert r_cloud.headers[HEADER_TOKENS_OUT] == "17"
    # Thinking-Tokens=0 en ambos: local por contrato (punto 7), cloud porque
    # el request no pidio think y el upstream reporto thoughts_token_count=0.
    assert r_local.headers[HEADER_THINKING_TOKENS] == "0"
    assert r_cloud.headers[HEADER_THINKING_TOKENS] == "0"
    # Cost: pricing=0 en ambos → "0.000000" uniforme (6 decimales).
    assert r_local.headers[HEADER_COST_EUR] == "0.000000"
    assert r_cloud.headers[HEADER_COST_EUR] == "0.000000"
    # Duration-Ms: int>=1, mismo formato.
    assert int(r_local.headers[HEADER_DURATION_MS]) >= 1
    assert int(r_cloud.headers[HEADER_DURATION_MS]) >= 1


# ---------------------------------------------------------------------------
# Asimetria documentada (punto 7): thinking en local vs cloud.
# ---------------------------------------------------------------------------


@respx.mock
def test_smoke_parity_asimetria_thinking_local_siempre_cero_cloud_desglosa():
    """Con `think=true`, local emite Thinking-Tokens=0 (Ollama no desglosa) y
    Tokens-Out incluye thinking; cloud reporta Thinking-Tokens real y
    Tokens-Out sin thinking. Esto NO es parity — es el compromiso documentado
    que el harness (#45) debe saber via `Sprout-Inference-Backend`.
    """
    payload = {
        "model": "gemma4:26b-moe",
        "messages": [{"role": "user", "content": "hola"}],
        "think": True,
    }

    # Local: eval_count=50 incluye thinking segun contrato Ollama; el texto de
    # razonamiento llega en `message.thinking`.
    respx.post(f"{UPSTREAM_OLLAMA}/api/chat").mock(
        return_value=httpx.Response(
            200,
            json=_ollama_canned(
                content="respuesta",
                thinking="razonando",
                prompt_eval_count=10,
                eval_count=50,
            ),
        )
    )
    app_local = create_app(_base_settings())
    _install_backend(
        app_local, LocalBackend(upstream_host=UPSTREAM_OLLAMA), "local-ollama"
    )
    with TestClient(app_local) as c:
        r_local = c.post("/api/chat", json=payload)

    # Cloud: thoughts_token_count=30 explicito; candidates=20.
    fake_client = _FakeGenai(
        _gemini_canned(
            content_parts=[
                ("razonando", True),
                ("respuesta", False),
            ],
            prompt_tokens=10,
            candidates_tokens=20,
            thoughts_tokens=30,
        )
    )
    app_cloud = create_app(_base_settings())
    _install_backend(app_cloud, _make_cloud_backend(fake_client), "cloud-gemini")
    with TestClient(app_cloud) as c:
        r_cloud = c.post("/api/chat", json=payload)

    # Asimetria en HEADERS:
    # - local: Thinking-Tokens=0 (no desglosa), Tokens-Out=50 (incluye thinking).
    assert r_local.headers[HEADER_THINKING_TOKENS] == "0"
    assert r_local.headers[HEADER_TOKENS_OUT] == "50"
    # - cloud: desglose real.
    assert r_cloud.headers[HEADER_THINKING_TOKENS] == "30"
    assert r_cloud.headers[HEADER_TOKENS_OUT] == "20"

    # Tokens-In si es paritario (ambos upstreams reportan prompt tokens).
    assert r_local.headers[HEADER_TOKENS_IN] == "10"
    assert r_cloud.headers[HEADER_TOKENS_IN] == "10"

    # BODY: ambos preservan `message.thinking` como texto visible al caller.
    # Esta paridad si se mantiene — la asimetria vive solo en los contadores.
    assert r_local.json()["message"]["thinking"] == "razonando"
    assert r_cloud.json()["message"]["thinking"] == "razonando"

    # Y el `eval_count` del body ollama-shape sigue siendo la suma en ambos:
    # local: eval_count nativo Ollama = 50 (incluye thinking).
    # cloud: adapter compone eval_count = candidates + thoughts = 20+30 = 50.
    assert r_local.json()["eval_count"] == 50
    assert r_cloud.json()["eval_count"] == 50
