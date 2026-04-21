"""Tests del backend `local` — reverse-proxy a Ollama en :11435 (punto 6).

Usamos respx para interceptar httpx a nivel de transport; no se necesita un
Ollama real en CI.

Cubre:
- POST /api/chat y /api/generate se forwardean al upstream con body preservado.
- `stream=true` en el request se fuerza a `false` al upstream (punto 8).
- Contadores nativos de Ollama (`prompt_eval_count`, `eval_count`) se mapean
  a `Tokens-In` / `Tokens-Out`.
- `Thinking-Tokens` siempre `0` en local (nota del punto 7: Ollama no desglosa).
- `Cost-EUR` siempre `0.0`.
- Backend label = `local-ollama`.
- Model del response se usa; fallback al del request si Ollama no lo devuelve.
- httpx error 5xx del upstream se propaga (FastAPI devolvera 500).
"""

from __future__ import annotations

import httpx
import pytest
import respx

from src.backends.local import LocalBackend


UPSTREAM = "http://localhost:11435"


def _ollama_chat_response(
    *,
    model: str = "gemma4:e4b",
    content: str = "ok",
    thinking: str | None = None,
    prompt_eval_count: int = 10,
    eval_count: int = 5,
) -> dict:
    message: dict = {"role": "assistant", "content": content}
    if thinking is not None:
        message["thinking"] = thinking
    return {
        "model": model,
        "created_at": "2026-04-21T12:00:00Z",
        "message": message,
        "done": True,
        "done_reason": "stop",
        "total_duration": 123_456_789,
        "load_duration": 1_234,
        "prompt_eval_count": prompt_eval_count,
        "prompt_eval_duration": 10_000_000,
        "eval_count": eval_count,
        "eval_duration": 100_000_000,
    }


def _ollama_generate_response(**kwargs) -> dict:
    data = _ollama_chat_response(**kwargs)
    # /api/generate tiene `response` en vez de `message`
    message = data.pop("message")
    data["response"] = message["content"]
    if "thinking" in message:
        data["thinking"] = message["thinking"]
    return data


@respx.mock
async def test_chat_forwardea_y_extrae_contadores():
    route = respx.post(f"{UPSTREAM}/api/chat").mock(
        return_value=httpx.Response(200, json=_ollama_chat_response(
            prompt_eval_count=42, eval_count=17
        ))
    )
    backend = LocalBackend(upstream_host=UPSTREAM)
    body, metrics = await backend.chat(
        {"model": "gemma4:e4b", "messages": [{"role": "user", "content": "hi"}]}
    )
    assert route.called
    # Body se relaya tal cual.
    assert body["message"]["content"] == "ok"
    assert body["done"] is True
    assert body["eval_count"] == 17
    # Metrics mapean Ollama → headers.
    assert metrics.backend == "local-ollama"
    assert metrics.tokens_in == 42
    assert metrics.tokens_out == 17  # incluye thinking si hubiera
    assert metrics.thinking_tokens == 0  # siempre 0 en local
    assert metrics.cost_eur == 0.0
    assert metrics.duration_ms >= 1
    assert metrics.model == "gemma4:e4b"


@respx.mock
async def test_generate_forwardea():
    route = respx.post(f"{UPSTREAM}/api/generate").mock(
        return_value=httpx.Response(200, json=_ollama_generate_response(
            content="salida", prompt_eval_count=5, eval_count=3
        ))
    )
    backend = LocalBackend(upstream_host=UPSTREAM)
    body, metrics = await backend.generate(
        {"model": "gemma4:e4b", "prompt": "hola"}
    )
    assert route.called
    assert body["response"] == "salida"
    assert metrics.tokens_in == 5
    assert metrics.tokens_out == 3


@respx.mock
async def test_stream_true_se_fuerza_a_false_al_upstream():
    # Capturamos el body enviado al upstream y verificamos stream=False.
    captured: dict = {}

    def _handler(request: httpx.Request) -> httpx.Response:
        import json as _json

        captured["body"] = _json.loads(request.content)
        return httpx.Response(200, json=_ollama_chat_response())

    respx.post(f"{UPSTREAM}/api/chat").mock(side_effect=_handler)

    backend = LocalBackend(upstream_host=UPSTREAM)
    await backend.chat(
        {"model": "gemma4:e4b", "messages": [], "stream": True}
    )

    assert captured["body"]["stream"] is False, (
        "adapter debe forzar stream=false al upstream (punto 8)"
    )
    # Campos no-stream se preservan.
    assert captured["body"]["model"] == "gemma4:e4b"


@respx.mock
async def test_request_original_no_se_muta():
    respx.post(f"{UPSTREAM}/api/chat").mock(
        return_value=httpx.Response(200, json=_ollama_chat_response())
    )
    backend = LocalBackend(upstream_host=UPSTREAM)
    original = {"model": "gemma4:e4b", "messages": [], "stream": True}
    snapshot = dict(original)
    await backend.chat(original)
    # El caller debe seguir viendo su request tal cual; solo el body enviado
    # al upstream fue modificado.
    assert original == snapshot


@respx.mock
async def test_thinking_tokens_siempre_cero_en_local():
    # Aunque la respuesta traiga message.thinking con texto, Thinking-Tokens=0.
    respx.post(f"{UPSTREAM}/api/chat").mock(
        return_value=httpx.Response(
            200,
            json=_ollama_chat_response(
                content="respuesta",
                thinking="razonando intensamente",
                prompt_eval_count=10,
                eval_count=50,  # incluye thinking segun contrato Ollama
            ),
        )
    )
    backend = LocalBackend(upstream_host=UPSTREAM)
    body, metrics = await backend.chat(
        {"model": "gemma4:e4b", "messages": [], "think": True}
    )
    assert body["message"]["thinking"] == "razonando intensamente"
    # El texto se preserva en el body, pero el header es 0 porque Ollama no
    # desglosa. Eso es el compromiso documentado.
    assert metrics.thinking_tokens == 0
    assert metrics.tokens_out == 50  # incluye thinking; documentado


@respx.mock
async def test_model_del_response_se_usa_si_presente():
    respx.post(f"{UPSTREAM}/api/chat").mock(
        return_value=httpx.Response(
            200, json=_ollama_chat_response(model="gemma4:e4b")
        )
    )
    backend = LocalBackend(upstream_host=UPSTREAM)
    _, metrics = await backend.chat({"model": "alias-que-ollama-normaliza"})
    assert metrics.model == "gemma4:e4b"


@respx.mock
async def test_model_fallback_al_request_si_response_no_lo_trae():
    data = _ollama_chat_response()
    del data["model"]
    respx.post(f"{UPSTREAM}/api/chat").mock(
        return_value=httpx.Response(200, json=data)
    )
    backend = LocalBackend(upstream_host=UPSTREAM)
    _, metrics = await backend.chat({"model": "gemma4:26b-moe"})
    assert metrics.model == "gemma4:26b-moe"


@respx.mock
async def test_upstream_5xx_se_propaga():
    respx.post(f"{UPSTREAM}/api/chat").mock(
        return_value=httpx.Response(500, text="boom")
    )
    backend = LocalBackend(upstream_host=UPSTREAM)
    with pytest.raises(httpx.HTTPStatusError):
        await backend.chat({"model": "x", "messages": []})


@respx.mock
async def test_contadores_ausentes_caen_a_cero():
    # Si por algun motivo el upstream omite los contadores (caso degenerado),
    # no queremos crashear — caemos a 0 y el header emite "0" explicito.
    respx.post(f"{UPSTREAM}/api/chat").mock(
        return_value=httpx.Response(
            200,
            json={
                "model": "x",
                "message": {"role": "assistant", "content": "hola"},
                "done": True,
            },
        )
    )
    backend = LocalBackend(upstream_host=UPSTREAM)
    _, metrics = await backend.chat({"model": "x", "messages": []})
    assert metrics.tokens_in == 0
    assert metrics.tokens_out == 0
