"""Tests del backend `cloud` (Gemini API).

Usamos un `client_factory` inyectado que devuelve un cliente fake con la misma
shape que `genai.Client`: un atributo `.aio.models.generate_content` async.
Los tipos `types.Content`, `types.Part`, `types.GenerateContentConfig` SI son
los reales (no queremos divergencia con la API de produccion).

Cubre, en orden de riesgo tecnico del comentario de #46:

- Punto 1: si request trae `format={schema}`, se pasa por flatten antes de ir
  a Gemini como `response_schema`. El config capturado no contiene `$ref`.
- Punto 2: `think=true` pone `thinking_config.include_thoughts=True` y
  `thinking_budget=<budget>`; `think=false` pone `include_thoughts=False` y
  `thinking_budget=0`.
- Punto 3: partes `thought=True` se separan en `message.thinking`;
  `message.content` solo lleva lo no-thought.
- Punto 4: `eval_count == candidates_token_count + thoughts_token_count`.
  Headers desglosan.
- Punto 5: 2x 429 + exito al 3er intento → respuesta normal. 3x 429 →
  UpstreamRateLimited.
- Punto 9: `gemma4:26b-moe` del caller se resuelve a `gemma-4-26b-a4b` en la
  llamada a Gemini, pero el body devuelto conserva el tag original.
- system role del caller se extrae a `system_instruction` y NO va en contents.
- `options.num_ctx` se ignora (no propagable a Gemini).
- Cost calculado desde pricing.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from google.genai import errors as genai_errors

from src.backends.cloud import CloudBackend
from src.config import PricingConfig, RetryConfig
from src.retry import UpstreamRateLimited


# ---------------------------------------------------------------------------
# Helpers: fake client y respuesta
# ---------------------------------------------------------------------------


def _fake_response(
    *,
    parts_specs: list[tuple[str, bool]],  # [(text, is_thought), ...]
    prompt_tokens: int = 10,
    candidates_tokens: int = 5,
    thoughts_tokens: int = 0,
) -> SimpleNamespace:
    parts = [SimpleNamespace(text=t, thought=th) for t, th in parts_specs]
    return SimpleNamespace(
        candidates=[SimpleNamespace(content=SimpleNamespace(parts=parts))],
        usage_metadata=SimpleNamespace(
            prompt_token_count=prompt_tokens,
            candidates_token_count=candidates_tokens,
            thoughts_token_count=thoughts_tokens,
        ),
    )


class _FakeGenaiClient:
    """Minima shape de `genai.Client` para tests.

    Registra los argumentos de cada llamada en `self.calls` y deja que el test
    defina la respuesta (o excepcion) con `set_response` / `set_error_sequence`.
    """

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self._response: Any = None
        self._error_sequence: list[BaseException] = []
        self._final_response_after_errors: Any = None
        self.aio = SimpleNamespace(
            models=SimpleNamespace(generate_content=self._generate_content)
        )

    def set_response(self, response: Any) -> None:
        self._response = response

    def set_error_sequence(
        self, errors: list[BaseException], final_response: Any
    ) -> None:
        self._error_sequence = list(errors)
        self._final_response_after_errors = final_response

    async def _generate_content(
        self, *, model: str, contents: Any, config: Any
    ) -> Any:
        self.calls.append({"model": model, "contents": contents, "config": config})
        if self._error_sequence:
            exc = self._error_sequence.pop(0)
            raise exc
        if self._final_response_after_errors is not None:
            resp = self._final_response_after_errors
            self._final_response_after_errors = None
            return resp
        if self._response is None:
            raise AssertionError("test no fijo response")
        return self._response


def _make_backend(
    *,
    client: _FakeGenaiClient,
    pricing: PricingConfig | None = None,
    retry: RetryConfig | None = None,
    thinking_budget: int = 4096,
    aliases: dict[str, str] | None = None,
) -> CloudBackend:
    return CloudBackend(
        api_key="fake-key",
        default_model="gemma-4-26b-a4b",
        model_aliases=aliases or {"gemma4:26b-moe": "gemma-4-26b-a4b"},
        thinking_budget=thinking_budget,
        retry=retry or RetryConfig(max_attempts=3, backoff_ms=(1, 1, 1)),
        pricing=pricing or PricingConfig(0.0, 0.0, 0.0),
        client_factory=lambda api_key: client,
    )


def _make_429() -> genai_errors.APIError:
    # Construye un APIError con code=429 sin tocar response/details reales.
    exc = genai_errors.APIError.__new__(genai_errors.APIError)
    exc.code = 429
    exc.status = "RESOURCE_EXHAUSTED"
    exc.message = "rate limited"
    exc.details = {}
    exc.response = None
    BaseException.__init__(exc, "429 RESOURCE_EXHAUSTED")
    return exc


# ---------------------------------------------------------------------------
# Chat basico + headers + alias
# ---------------------------------------------------------------------------


async def test_chat_basico_devuelve_body_ollama_y_metrics():
    client = _FakeGenaiClient()
    client.set_response(
        _fake_response(
            parts_specs=[("hola desde Gemini", False)],
            prompt_tokens=42,
            candidates_tokens=17,
            thoughts_tokens=0,
        )
    )
    backend = _make_backend(client=client)
    body, metrics = await backend.chat(
        {
            "model": "gemma4:26b-moe",
            "messages": [{"role": "user", "content": "hola"}],
        }
    )
    # Body shape
    assert body["message"]["role"] == "assistant"
    assert body["message"]["content"] == "hola desde Gemini"
    assert body["message"]["thinking"] == ""
    assert body["done"] is True
    assert body["prompt_eval_count"] == 42
    assert body["eval_count"] == 17  # sin thinking → == candidates
    assert body["model"] == "gemma4:26b-moe"  # tag original preservado
    # Metrics
    assert metrics.backend == "cloud-gemini"
    assert metrics.model == "gemma4:26b-moe"
    assert metrics.tokens_in == 42
    assert metrics.tokens_out == 17
    assert metrics.thinking_tokens == 0
    assert metrics.duration_ms >= 1


async def test_alias_gemma4_26b_moe_se_resuelve_al_id_gemini():
    client = _FakeGenaiClient()
    client.set_response(_fake_response(parts_specs=[("x", False)]))
    backend = _make_backend(client=client)
    await backend.chat({"model": "gemma4:26b-moe", "messages": []})
    assert len(client.calls) == 1
    # El id que llega a Gemini es el resuelto, no el alias Ollama.
    assert client.calls[0]["model"] == "gemma-4-26b-a4b"


async def test_tag_sin_alias_se_pasa_tal_cual():
    client = _FakeGenaiClient()
    client.set_response(_fake_response(parts_specs=[("x", False)]))
    backend = _make_backend(client=client)
    await backend.chat({"model": "gemma-4-e4b-it", "messages": []})
    assert client.calls[0]["model"] == "gemma-4-e4b-it"


async def test_sin_model_usa_default():
    client = _FakeGenaiClient()
    client.set_response(_fake_response(parts_specs=[("x", False)]))
    backend = _make_backend(client=client)
    body, metrics = await backend.chat({"messages": []})
    assert body["model"] == "gemma-4-26b-a4b"
    assert metrics.model == "gemma-4-26b-a4b"


# ---------------------------------------------------------------------------
# Punto 3: thinking parts → message.thinking
# ---------------------------------------------------------------------------


async def test_thinking_parts_se_separan_en_message_thinking():
    client = _FakeGenaiClient()
    client.set_response(
        _fake_response(
            parts_specs=[
                ("razonamiento interno. ", True),
                ("respuesta visible ", False),
                ("mas razonamiento. ", True),
                ("final.", False),
            ],
            prompt_tokens=100,
            candidates_tokens=20,
            thoughts_tokens=50,
        )
    )
    backend = _make_backend(client=client)
    body, metrics = await backend.chat(
        {"model": "gemma4:26b-moe", "messages": [], "think": True}
    )
    assert body["message"]["content"] == "respuesta visible final."
    assert body["message"]["thinking"] == "razonamiento interno. mas razonamiento. "
    # Punto 4: eval_count = candidates + thoughts = 20 + 50 = 70
    assert body["eval_count"] == 70
    # Headers desglosan
    assert metrics.tokens_out == 20
    assert metrics.thinking_tokens == 50


# ---------------------------------------------------------------------------
# Punto 2: thinking map
# ---------------------------------------------------------------------------


async def test_think_true_configura_thinking_include_thoughts_y_budget():
    client = _FakeGenaiClient()
    client.set_response(_fake_response(parts_specs=[("x", False)]))
    backend = _make_backend(client=client, thinking_budget=4096)
    await backend.chat(
        {"model": "gemma4:26b-moe", "messages": [], "think": True}
    )
    cfg = client.calls[0]["config"]
    assert cfg.thinking_config.include_thoughts is True
    assert cfg.thinking_config.thinking_budget == 4096


async def test_think_false_desactiva_con_budget_cero():
    client = _FakeGenaiClient()
    client.set_response(_fake_response(parts_specs=[("x", False)]))
    backend = _make_backend(client=client)
    await backend.chat(
        {"model": "gemma4:26b-moe", "messages": [], "think": False}
    )
    cfg = client.calls[0]["config"]
    assert cfg.thinking_config.include_thoughts is False
    assert cfg.thinking_config.thinking_budget == 0


async def test_think_ausente_tratado_como_false():
    client = _FakeGenaiClient()
    client.set_response(_fake_response(parts_specs=[("x", False)]))
    backend = _make_backend(client=client)
    await backend.chat({"model": "gemma4:26b-moe", "messages": []})
    cfg = client.calls[0]["config"]
    assert cfg.thinking_config.include_thoughts is False
    assert cfg.thinking_config.thinking_budget == 0


# ---------------------------------------------------------------------------
# Punto 1: flatten de schema
# ---------------------------------------------------------------------------


async def test_format_schema_se_aplana_antes_de_enviar_a_gemini():
    client = _FakeGenaiClient()
    client.set_response(_fake_response(parts_specs=[('{"a": 1}', False)]))
    backend = _make_backend(client=client)

    schema_con_refs = {
        "$defs": {"Foo": {"type": "string"}},
        "type": "object",
        "properties": {"foo": {"$ref": "#/$defs/Foo"}},
    }
    await backend.chat(
        {"model": "gemma4:26b-moe", "messages": [], "format": schema_con_refs}
    )
    cfg = client.calls[0]["config"]
    # response_mime_type fijado
    assert cfg.response_mime_type == "application/json"
    # response_schema aplanado: no hay $ref ni $defs
    flat = cfg.response_schema
    import json as _json

    serialized = _json.dumps(flat)
    assert "$ref" not in serialized
    assert "$defs" not in serialized
    # Y `foo` expandido in-place.
    assert flat["properties"]["foo"] == {"type": "string"}


async def test_format_json_string_sin_schema():
    # Ollama permite `format: "json"` sin schema; mapeamos solo el mime-type.
    client = _FakeGenaiClient()
    client.set_response(_fake_response(parts_specs=[("{}", False)]))
    backend = _make_backend(client=client)
    await backend.chat(
        {"model": "gemma4:26b-moe", "messages": [], "format": "json"}
    )
    cfg = client.calls[0]["config"]
    assert cfg.response_mime_type == "application/json"
    assert cfg.response_schema is None  # no schema explicito


# ---------------------------------------------------------------------------
# options: temperature, num_predict, num_ctx
# ---------------------------------------------------------------------------


async def test_options_temperature_y_num_predict_se_propagan():
    client = _FakeGenaiClient()
    client.set_response(_fake_response(parts_specs=[("x", False)]))
    backend = _make_backend(client=client)
    await backend.chat(
        {
            "model": "gemma4:26b-moe",
            "messages": [],
            "options": {"temperature": 0.3, "num_predict": 256},
        }
    )
    cfg = client.calls[0]["config"]
    assert cfg.temperature == 0.3
    assert cfg.max_output_tokens == 256


async def test_options_num_ctx_se_ignora_en_cloud(caplog):
    # Gemini no tiene equivalente directo. Verificamos que NO se propaga y que
    # se loguea un info para trazabilidad.
    import logging

    client = _FakeGenaiClient()
    client.set_response(_fake_response(parts_specs=[("x", False)]))
    backend = _make_backend(client=client)
    with caplog.at_level(logging.INFO, logger="src.backends.cloud"):
        await backend.chat(
            {
                "model": "gemma4:26b-moe",
                "messages": [],
                "options": {"num_ctx": 65536},
            }
        )
    # Config no lleva atributo derivado de num_ctx.
    cfg = client.calls[0]["config"]
    assert not hasattr(cfg, "num_ctx")
    # Log registrado.
    assert any("num_ctx" in rec.message for rec in caplog.records)


# ---------------------------------------------------------------------------
# system role → system_instruction (no va en contents)
# ---------------------------------------------------------------------------


async def test_role_system_se_extrae_a_system_instruction():
    client = _FakeGenaiClient()
    client.set_response(_fake_response(parts_specs=[("x", False)]))
    backend = _make_backend(client=client)
    await backend.chat(
        {
            "model": "gemma4:26b-moe",
            "messages": [
                {"role": "system", "content": "Se breve y preciso."},
                {"role": "user", "content": "hola"},
            ],
        }
    )
    call = client.calls[0]
    cfg = call["config"]
    assert cfg.system_instruction == "Se breve y preciso."
    # contents solo lleva el mensaje user (1 item).
    assert len(call["contents"]) == 1
    assert call["contents"][0].role == "user"


async def test_role_assistant_se_mapea_a_model():
    client = _FakeGenaiClient()
    client.set_response(_fake_response(parts_specs=[("x", False)]))
    backend = _make_backend(client=client)
    await backend.chat(
        {
            "model": "gemma4:26b-moe",
            "messages": [
                {"role": "user", "content": "hi"},
                {"role": "assistant", "content": "hello"},
                {"role": "user", "content": "follow up"},
            ],
        }
    )
    contents = client.calls[0]["contents"]
    assert [c.role for c in contents] == ["user", "model", "user"]


# ---------------------------------------------------------------------------
# Punto 5: retry 429
# ---------------------------------------------------------------------------


async def test_dos_429_luego_exito_devuelve_respuesta_normal():
    client = _FakeGenaiClient()
    client.set_error_sequence(
        errors=[_make_429(), _make_429()],
        final_response=_fake_response(
            parts_specs=[("recuperado", False)],
            prompt_tokens=3,
            candidates_tokens=1,
        ),
    )
    backend = _make_backend(
        client=client,
        retry=RetryConfig(max_attempts=3, backoff_ms=(1, 1, 1)),
    )
    body, metrics = await backend.chat(
        {"model": "gemma4:26b-moe", "messages": []}
    )
    assert body["message"]["content"] == "recuperado"
    # 3 llamadas al upstream: 2 que fallaron + 1 que tuvo exito.
    assert len(client.calls) == 3


async def test_tres_429_levanta_upstream_rate_limited():
    client = _FakeGenaiClient()
    client.set_error_sequence(
        errors=[_make_429(), _make_429(), _make_429()],
        final_response=None,
    )
    backend = _make_backend(
        client=client,
        retry=RetryConfig(max_attempts=3, backoff_ms=(1, 1, 1)),
    )
    with pytest.raises(UpstreamRateLimited) as ei:
        await backend.chat({"model": "gemma4:26b-moe", "messages": []})
    assert ei.value.attempts == 3
    assert len(client.calls) == 3


# ---------------------------------------------------------------------------
# Cost
# ---------------------------------------------------------------------------


async def test_cost_calculado_desde_pricing():
    client = _FakeGenaiClient()
    client.set_response(
        _fake_response(
            parts_specs=[("x", False)],
            prompt_tokens=1000,
            candidates_tokens=500,
            thoughts_tokens=200,
        )
    )
    pricing = PricingConfig(
        in_eur_per_1k=0.10,  # 0.10 EUR/1K in
        out_eur_per_1k=0.40,  # 0.40 EUR/1K out
        thinking_eur_per_1k=0.20,  # 0.20 EUR/1K thinking
    )
    backend = _make_backend(client=client, pricing=pricing)
    _, metrics = await backend.chat({"model": "gemma4:26b-moe", "messages": []})
    # 1000/1000 * 0.10 + 500/1000 * 0.40 + 200/1000 * 0.20
    # = 0.10 + 0.20 + 0.04 = 0.34
    assert metrics.cost_eur == pytest.approx(0.34)


# ---------------------------------------------------------------------------
# /api/generate
# ---------------------------------------------------------------------------


async def test_generate_usa_response_y_unico_mensaje_user():
    client = _FakeGenaiClient()
    client.set_response(_fake_response(parts_specs=[("salida", False)]))
    backend = _make_backend(client=client)
    body, _ = await backend.generate(
        {"model": "gemma4:e4b", "prompt": "hola", "system": "Se conciso."}
    )
    # Shape
    assert "response" in body
    assert "message" not in body
    assert body["response"] == "salida"
    # Contents: 1 mensaje user; system_instruction aparte.
    call = client.calls[0]
    assert len(call["contents"]) == 1
    assert call["contents"][0].role == "user"
    assert call["config"].system_instruction == "Se conciso."


# ---------------------------------------------------------------------------
# Robustez: respuesta sin candidates
# ---------------------------------------------------------------------------


async def test_respuesta_sin_candidates_levanta_runtime_error():
    client = _FakeGenaiClient()
    client.set_response(SimpleNamespace(candidates=[], usage_metadata=None))
    backend = _make_backend(client=client)
    with pytest.raises(RuntimeError, match="sin candidates"):
        await backend.chat({"model": "gemma4:26b-moe", "messages": []})
