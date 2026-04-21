"""Tests del backend `test` (punto 11 de Cambium).

Verifica:
- Implementa el Protocol InferenceBackend (runtime check).
- chat() y generate() devuelven respuesta Ollama-shaped + InferenceMetrics.
- Selector `options.test_fixture` pica el canned correcto; default si no se pasa.
- Selector desconocido levanta KeyError (ruidoso, no silente).
- El modelo del request sobreescribe el del canned (pasa tal cual).
- eval_count incluye thinking (contrato Ollama); headers los separan.
- last_chat_request / last_generate_request se guardan para inspeccion.
- Canned custom sin 'default' rechazado en init.
"""

from __future__ import annotations

import pytest

from src.backends.base import InferenceBackend
from src.backends.test import (
    DEFAULT_CANNED,
    CannedResponse,
    TestBackend,
)


def test_implementa_protocol():
    backend = TestBackend()
    assert isinstance(backend, InferenceBackend)


async def test_chat_shape_ollama_default():
    backend = TestBackend()
    body, metrics = await backend.chat({"model": "gemma4:26b-moe", "messages": []})
    # Shape /api/chat
    assert body["done"] is True
    assert body["message"]["role"] == "assistant"
    assert body["message"]["content"] == "ok"
    assert body["message"]["thinking"] == ""
    # Contadores
    assert body["prompt_eval_count"] == 10
    assert body["eval_count"] == 2  # tokens_out + thinking_tokens = 2 + 0
    assert body["prompt_eval_duration"] > 0
    assert body["eval_duration"] > 0
    # Model se propaga desde el request, no del canned
    assert body["model"] == "gemma4:26b-moe"


async def test_generate_shape_ollama_default():
    backend = TestBackend()
    body, metrics = await backend.generate(
        {"model": "gemma4:e4b", "prompt": "hola"}
    )
    # Shape /api/generate (response en vez de message)
    assert "response" in body
    assert body["response"] == "ok"
    assert "message" not in body  # sanity: no mezcla shapes
    assert body["thinking"] == ""
    assert body["model"] == "gemma4:e4b"


async def test_chat_with_thinking_fixture():
    backend = TestBackend()
    body, metrics = await backend.chat(
        {
            "model": "gemma-4-26b-a4b",
            "messages": [],
            "options": {"test_fixture": "with_thinking"},
        }
    )
    assert body["message"]["content"] == "respuesta final"
    assert body["message"]["thinking"].startswith("razonando")
    # eval_count = tokens_out (5) + thinking_tokens (15) = 20
    assert body["eval_count"] == 20
    # Headers separan: tokens_out=5, thinking_tokens=15, tokens_in=20
    assert metrics.tokens_out == 5
    assert metrics.thinking_tokens == 15
    assert metrics.tokens_in == 20


async def test_selector_desconocido_levanta_keyerror():
    backend = TestBackend()
    with pytest.raises(KeyError, match="no_existe"):
        await backend.chat(
            {"model": "foo", "options": {"test_fixture": "no_existe"}}
        )


async def test_canned_custom_sin_default_rechazado():
    with pytest.raises(ValueError, match="default"):
        TestBackend(
            canned={"custom": CannedResponse(model="x", content="y")}
        )


async def test_canned_custom_acepta_si_tiene_default():
    custom = {
        "default": CannedResponse(model="x", content="y", tokens_in=1, tokens_out=1),
        "my_fixture": CannedResponse(
            model="x", content="custom!", tokens_in=3, tokens_out=4
        ),
    }
    backend = TestBackend(canned=custom)
    body, _ = await backend.chat(
        {"model": "x", "options": {"test_fixture": "my_fixture"}}
    )
    assert body["message"]["content"] == "custom!"
    assert body["eval_count"] == 4


async def test_metrics_backend_es_test_y_cost_cero():
    backend = TestBackend()
    _, metrics = await backend.chat({"model": "foo"})
    assert metrics.backend == "test"
    assert metrics.cost_eur == 0.0
    assert metrics.duration_ms >= 1  # suelo


async def test_last_request_se_guarda():
    backend = TestBackend()
    req = {"model": "foo", "messages": [{"role": "user", "content": "hi"}]}
    await backend.chat(req)
    assert backend.last_chat_request is req
    # generate aun no invocado
    assert backend.last_generate_request is None

    gen_req = {"model": "bar", "prompt": "g"}
    await backend.generate(gen_req)
    assert backend.last_generate_request is gen_req


async def test_eval_count_incluye_thinking_contrato_ollama():
    # Punto 4: eval_count = tokens_out + thinking_tokens. Los headers los separan.
    backend = TestBackend()
    body, metrics = await backend.chat(
        {"model": "m", "options": {"test_fixture": "with_thinking"}}
    )
    assert body["eval_count"] == metrics.tokens_out + metrics.thinking_tokens


async def test_empty_fixture_no_divide_por_cero():
    # tokens_in=0 y tokens_out=0: el splitter no debe dividir por cero.
    backend = TestBackend()
    body, metrics = await backend.chat(
        {"model": "m", "options": {"test_fixture": "empty"}}
    )
    assert body["prompt_eval_duration"] >= 0
    assert body["eval_duration"] >= 0
    assert (
        body["prompt_eval_duration"] + body["eval_duration"]
        == body["total_duration"]
    )
