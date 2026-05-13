"""Tests del parser tolerante de tool calls inline (día 26 plan A).

Gemma 4 a veces emite tool calls como texto inline en lugar del formato
Ollama-estructurado. Estas pruebas blindan que el rescate funciona para
los formatos observados en runtime sin romper el camino feliz (cuando
sí viene estructurado).

Caso real visto en smoke_d26_v3 (chat_alert):
    answer_es: "<|tool_call>call: get_recent_history(target_node_id=\"rhizome_01\", last_n=5)"

con tool_calls=[] en la respuesta del adapter.
"""
from __future__ import annotations

import json

import pytest

from src.inference import (
    _parse_kwargs_string,
    _parse_tool_call_from_text,
    _strip_inline_tool_call,
)


# ---------------------------------------------------------------------------
# _parse_kwargs_string
# ---------------------------------------------------------------------------


def test_kwargs_string_double_quoted_string():
    out = _parse_kwargs_string('target_node_id="rhizome_01"')
    assert out == {"target_node_id": "rhizome_01"}


def test_kwargs_string_single_quoted_string():
    out = _parse_kwargs_string("name='value'")
    assert out == {"name": "value"}


def test_kwargs_string_int():
    out = _parse_kwargs_string("last_n=5")
    assert out == {"last_n": 5}


def test_kwargs_string_negative_int():
    out = _parse_kwargs_string("offset=-3")
    assert out == {"offset": -3}


def test_kwargs_string_float():
    out = _parse_kwargs_string("ratio=0.75")
    assert out == {"ratio": 0.75}


def test_kwargs_string_bool_true():
    out = _parse_kwargs_string("enabled=true")
    assert out == {"enabled": True}


def test_kwargs_string_bool_false_capital():
    out = _parse_kwargs_string("flag=False")
    assert out == {"flag": False}


def test_kwargs_string_null():
    out = _parse_kwargs_string("optional=null")
    assert out == {"optional": None}


def test_kwargs_string_mixed():
    """El caso real del chat_alert d26v3."""
    out = _parse_kwargs_string('target_node_id="rhizome_01", last_n=5')
    assert out == {"target_node_id": "rhizome_01", "last_n": 5}


def test_kwargs_string_multiple_mixed_types():
    out = _parse_kwargs_string('a="x", b=5, c=true, d=0.5')
    assert out == {"a": "x", "b": 5, "c": True, "d": 0.5}


def test_kwargs_string_empty():
    assert _parse_kwargs_string("") == {}
    assert _parse_kwargs_string("   ") == {}


def test_kwargs_string_none_input():
    assert _parse_kwargs_string(None) is None  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# _parse_tool_call_from_text — formato kwargs (caso runtime real)
# ---------------------------------------------------------------------------


def test_parse_inline_kwargs_real_case():
    """Caso exacto observado en smoke_d26_v3 chat_alert."""
    text = '<|tool_call>call: get_recent_history(target_node_id="rhizome_01", last_n=5)'
    out = _parse_tool_call_from_text(text)
    assert out is not None
    assert len(out) == 1
    tc = out[0]
    assert tc["function"]["name"] == "get_recent_history"
    # type: "function" requerido por llama-server (smoke v5 falló sin esto)
    assert tc["type"] == "function"
    args = json.loads(tc["function"]["arguments"])
    assert args == {"target_node_id": "rhizome_01", "last_n": 5}


def test_parse_inline_kwargs_includes_openai_type_field():
    """llama-server (OpenAI-compat) requiere `type: function` en cada
    tool_call. Sin él, devuelve 500 'Missing tool call type' al reenviar
    el assistant_msg en la 2ª iteración del loop. Esto blinda contra esa
    regresión específica observada en smoke_d26_v5."""
    text = '<|tool_call>call: compare_targets(target_a="a", target_b="b")'
    out = _parse_tool_call_from_text(text)
    assert out is not None
    assert all(tc.get("type") == "function" for tc in out), (
        "todos los tool_calls rescatados deben tener type='function'"
    )


def test_parse_inline_kwargs_compare_targets():
    text = '<|tool_call>call: compare_targets(target_a="rhizome_01", target_b="rhizome_02")'
    out = _parse_tool_call_from_text(text)
    assert out is not None
    assert out[0]["function"]["name"] == "compare_targets"
    args = json.loads(out[0]["function"]["arguments"])
    assert args == {"target_a": "rhizome_01", "target_b": "rhizome_02"}


def test_parse_inline_kwargs_variant_with_closing_pipe():
    """Variante <|tool_call|> con barra de cierre."""
    text = '<|tool_call|>call: get_weather_history(plot_id="plot_A")'
    out = _parse_tool_call_from_text(text)
    assert out is not None
    assert out[0]["function"]["name"] == "get_weather_history"


def test_parse_inline_kwargs_no_call_prefix():
    """Variante sin 'call:' inicial."""
    text = '<|tool_call>get_recent_history(last_n=3)'
    out = _parse_tool_call_from_text(text)
    assert out is not None
    assert out[0]["function"]["name"] == "get_recent_history"


def test_parse_inline_kwargs_embedded_in_text():
    """Tool call rodeada de otro texto (común en thinking)."""
    text = (
        "Para responder necesito histórico. "
        '<|tool_call>call: get_recent_history(target_node_id="rhizome_01", last_n=5)'
        " Tras recibir resultados procederé a comparar."
    )
    out = _parse_tool_call_from_text(text)
    assert out is not None
    assert out[0]["function"]["name"] == "get_recent_history"


# ---------------------------------------------------------------------------
# _parse_tool_call_from_text — formato JSON wrappeado (defensivo)
# ---------------------------------------------------------------------------


def test_parse_inline_json_format():
    text = '<|tool_call>{"name": "compare_targets", "arguments": {"target_a": "rhizome_01", "target_b": "rhizome_02"}}'
    out = _parse_tool_call_from_text(text)
    assert out is not None
    assert out[0]["function"]["name"] == "compare_targets"
    assert out[0]["type"] == "function"
    args = json.loads(out[0]["function"]["arguments"])
    assert args == {"target_a": "rhizome_01", "target_b": "rhizome_02"}


def test_parse_inline_json_with_closing_tag():
    text = '<tool_call>{"name": "get_recent_history", "arguments": {"last_n": 3}}</tool_call>'
    out = _parse_tool_call_from_text(text)
    assert out is not None
    assert out[0]["function"]["name"] == "get_recent_history"


def test_parse_inline_json_arguments_as_string():
    """Variante donde arguments viene como string JSON (no dict)."""
    text = '<|tool_call>{"name": "x", "arguments": "{\\"a\\": 1}"}'
    out = _parse_tool_call_from_text(text)
    assert out is not None
    args = json.loads(out[0]["function"]["arguments"])
    assert args == {"a": 1}


# ---------------------------------------------------------------------------
# _parse_tool_call_from_text — casos negativos
# ---------------------------------------------------------------------------


def test_parse_empty_text():
    assert _parse_tool_call_from_text("") is None
    assert _parse_tool_call_from_text(None) is None  # type: ignore[arg-type]


def test_parse_plain_text_no_tool_call():
    """Respuesta normal del LLM (no tool call) no debe disparar rescate."""
    text = "La parcela rhizome_01 está estable. No requiere acción."
    assert _parse_tool_call_from_text(text) is None


def test_parse_json_rationale_no_tool_call():
    """JSON de rationale (normal en /visit) no es tool call."""
    text = '{"rationale_tecnico": "test", "rationale_para_operador": "ok"}'
    assert _parse_tool_call_from_text(text) is None


# ---------------------------------------------------------------------------
# _strip_inline_tool_call
# ---------------------------------------------------------------------------


def test_strip_removes_kwargs_format():
    text = (
        'Voy a consultar el histórico. '
        '<|tool_call>call: get_recent_history(target_node_id="rhizome_01", last_n=5)'
    )
    cleaned = _strip_inline_tool_call(text)
    assert "<|tool_call>" not in cleaned
    assert "get_recent_history" not in cleaned
    assert "Voy a consultar el histórico." in cleaned


def test_strip_removes_json_format():
    text = 'Llamando: <tool_call>{"name": "x", "arguments": {}}</tool_call> ok'
    cleaned = _strip_inline_tool_call(text)
    assert "<tool_call>" not in cleaned
    assert "Llamando:" in cleaned
    assert "ok" in cleaned


def test_strip_preserves_plain_text():
    text = "Sin tool call. Sólo texto normal."
    assert _strip_inline_tool_call(text) == text


def test_strip_empty_input():
    assert _strip_inline_tool_call("") == ""


# ---------------------------------------------------------------------------
# Integración: compose_chat_response rescata tool_call inline y ejecuta tool
# ---------------------------------------------------------------------------


def test_compose_chat_response_recovers_inline_tool_call(monkeypatch):
    """E2E del rescate: caso real chat_alert d26v3.

    Iteración 0: adapter devuelve content con `<|tool_call>call: ...` y
                 tool_calls=[]. Rescate detecta, ejecuta call_tool stub.
    Iteración 1: adapter devuelve respuesta natural en castellano.

    Verifica:
      - tool_calls_log contiene la tool invocada (no vacía)
      - tool_calls_recovered_from_text == 1
      - answer_es es la respuesta natural, no el <|tool_call>...
    """
    from src import inference

    responses = iter([
        # Iter 0: emite tool call inline (formato gemma observado en runtime)
        {
            "message": {
                "content": (
                    '<|tool_call>call: get_recent_history('
                    'target_node_id="rhizome_01", last_n=5)'
                ),
                "thinking": "",
            },
            "done_reason": "stop",
            "prompt_eval_count": 683,
            "eval_count": 50,
        },
        # Iter 1: tras recibir tool_result, redacta respuesta natural
        {
            "message": {
                "content": (
                    "El histórico de rhizome_01 muestra alerta persistente "
                    "desde ayer. La policy activa pkt_meristem_abcd1234 "
                    "mantiene modo alerta y bloquea riegos automáticos."
                ),
                "thinking": "",
            },
            "done_reason": "stop",
            "prompt_eval_count": 800,
            "eval_count": 80,
        },
    ])

    def fake_post_chat(*args, **kwargs):
        return next(responses)

    # Stub determinista del call_tool para no acoplar el test al contenido
    # exacto del histórico (cualquier string sirve para cerrar el loop).
    def fake_call_tool(name, args):
        assert name == "get_recent_history"
        assert args["target_node_id"] == "rhizome_01"
        assert args["last_n"] == 5
        return "Alerta TANK_LOW persistente desde ayer 14:00."

    monkeypatch.setattr(inference, "_post_chat", fake_post_chat)
    # call_tool se importa dentro de la función vía `from .prompts import call_tool`
    # → parchear en el módulo `src.prompts`.
    from src import prompts
    monkeypatch.setattr(prompts, "call_tool", fake_call_tool)

    answer, metrics = inference.compose_chat_response(
        operator_message="¿Por qué está rhizome_01 en alerta hoy?",
    )

    assert metrics["tool_calls_recovered_from_text"] == 1
    assert len(metrics["tool_calls_log"]) == 1
    assert metrics["tool_calls_log"][0]["name"] == "get_recent_history"
    assert metrics["tool_calls_log"][0]["args"] == {
        "target_node_id": "rhizome_01", "last_n": 5,
    }
    # Respuesta natural (la segunda iter), no el <|tool_call>
    assert "<|tool_call>" not in answer
    assert "rhizome_01" in answer
    assert "pkt_meristem_abcd1234" in answer


def test_compose_chat_response_no_rescue_when_structured_tool_calls_present(monkeypatch):
    """Camino feliz: si el adapter devuelve tool_calls estructuradas,
    no se debe disparar el rescate (no marcar recovered_from_text)."""
    from src import inference

    responses = iter([
        # Iter 0: tool_calls bien estructuradas (no rescate necesario)
        {
            "message": {
                "content": "",
                "thinking": "",
                "tool_calls": [{
                    "id": "tc_1",
                    "function": {
                        "name": "get_recent_history",
                        "arguments": '{"target_node_id": "rhizome_01", "last_n": 3}',
                    },
                }],
            },
            "done_reason": "stop",
            "prompt_eval_count": 600,
            "eval_count": 40,
        },
        # Iter 1: respuesta final
        {
            "message": {
                "content": "Histórico sin novedades. Todo estable.",
                "thinking": "",
            },
            "done_reason": "stop",
            "prompt_eval_count": 700,
            "eval_count": 30,
        },
    ])

    def fake_post_chat(*args, **kwargs):
        return next(responses)

    def fake_call_tool(name, args):
        return "ok"

    monkeypatch.setattr(inference, "_post_chat", fake_post_chat)
    from src import prompts
    monkeypatch.setattr(prompts, "call_tool", fake_call_tool)

    answer, metrics = inference.compose_chat_response(
        operator_message="¿Estado?",
    )

    # NO debe haber rescate marcado
    assert "tool_calls_recovered_from_text" not in metrics
    # Pero sí debe haber ejecutado la tool estructurada
    assert len(metrics["tool_calls_log"]) == 1
    assert metrics["tool_calls_log"][0]["name"] == "get_recent_history"
    assert "Histórico sin novedades" in answer
