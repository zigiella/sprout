"""Tests de los bloques few-shot añadidos en plan B día 26.

Smoke v4 mostró que gemma-4-E4B improvisa el formato de tool calling:
a veces emite `<|tool_call>call: name(args)` (rescatable vía plan A),
a veces narra en lenguaje natural ("voy a consultar el histórico…"
sin emitir tool call real). Para forzar formato determinista, añadimos
un ejemplo few-shot en ambos system prompts mostrando el formato
canónico `<tool_call>{"name": ..., "arguments": {...}}</tool_call>`.

Estos tests:
1. Blindan que el bloque few-shot está presente en ambos prompts.
2. **Cierran el bucle**: verifican que el formato exacto del ejemplo
   en el prompt es parseable por el parser tolerante (plan A). Si
   alguien edita el ejemplo del prompt y rompe el formato, este test
   falla antes de que se note en runtime.
"""
from __future__ import annotations

import json
import re

from src.prompts import MERISTEM_CHAT_SYSTEM_PROMPT_ES, MERISTEM_SYSTEM_PROMPT_ES
from src.inference import _parse_tool_call_from_text


# ---------------------------------------------------------------------------
# Presencia del bloque few-shot
# ---------------------------------------------------------------------------


def test_visit_prompt_contains_few_shot_block():
    """System prompt de /visit contiene el bloque de formato estricto."""
    assert "FORMATO ESTRICTO PARA INVOCAR UNA HERRAMIENTA" in MERISTEM_SYSTEM_PROMPT_ES
    assert "<tool_call>" in MERISTEM_SYSTEM_PROMPT_ES
    assert "</tool_call>" in MERISTEM_SYSTEM_PROMPT_ES


def test_chat_prompt_contains_few_shot_block():
    """System prompt de /chat contiene el bloque de formato estricto."""
    assert "FORMATO ESTRICTO PARA INVOCAR UNA HERRAMIENTA" in MERISTEM_CHAT_SYSTEM_PROMPT_ES
    assert "<tool_call>" in MERISTEM_CHAT_SYSTEM_PROMPT_ES
    assert "</tool_call>" in MERISTEM_CHAT_SYSTEM_PROMPT_ES


def test_visit_prompt_contains_anti_hallucination_rules():
    """Reglas absolutas anti-alucinación están presentes en /visit."""
    assert "REGLAS ABSOLUTAS DE TOOL CALLING" in MERISTEM_SYSTEM_PROMPT_ES
    assert "NO narres" in MERISTEM_SYSTEM_PROMPT_ES
    assert "NO inventes el resultado" in MERISTEM_SYSTEM_PROMPT_ES


def test_chat_prompt_contains_anti_hallucination_rules():
    """Reglas absolutas anti-alucinación están presentes en /chat."""
    assert "REGLAS ABSOLUTAS DE TOOL CALLING" in MERISTEM_CHAT_SYSTEM_PROMPT_ES
    assert "NO narres" in MERISTEM_CHAT_SYSTEM_PROMPT_ES
    assert "NO inventes el resultado" in MERISTEM_CHAT_SYSTEM_PROMPT_ES


# ---------------------------------------------------------------------------
# Bucle prompt → parser: el ejemplo del prompt es parseable
# ---------------------------------------------------------------------------


_TOOL_CALL_EXAMPLE_PATTERN = re.compile(
    r"<tool_call>(\{.*?\})</tool_call>",
    re.DOTALL,
)


def _extract_example_tool_call(prompt_text: str) -> str:
    """Extrae el primer ejemplo `<tool_call>{...}</tool_call>` del prompt."""
    m = _TOOL_CALL_EXAMPLE_PATTERN.search(prompt_text)
    assert m, "no se encontró un ejemplo <tool_call>...</tool_call> en el prompt"
    return m.group(0)


def test_visit_prompt_example_is_parseable_by_plan_a_parser():
    """El ejemplo del prompt de /visit debe ser parseable por el parser
    tolerante. Si alguien rompe el formato del ejemplo, esto falla aquí
    en lugar de en runtime."""
    example = _extract_example_tool_call(MERISTEM_SYSTEM_PROMPT_ES)
    out = _parse_tool_call_from_text(example)
    assert out is not None, f"el ejemplo del prompt no se parsea: {example!r}"
    assert len(out) == 1
    tc = out[0]
    assert isinstance(tc["function"]["name"], str)
    assert len(tc["function"]["name"]) > 0
    # arguments debe ser un JSON válido
    args = json.loads(tc["function"]["arguments"])
    assert isinstance(args, dict)


def test_chat_prompt_example_is_parseable_by_plan_a_parser():
    """Idem para el prompt de /chat."""
    example = _extract_example_tool_call(MERISTEM_CHAT_SYSTEM_PROMPT_ES)
    out = _parse_tool_call_from_text(example)
    assert out is not None, f"el ejemplo del prompt no se parsea: {example!r}"
    assert len(out) == 1
    args = json.loads(out[0]["function"]["arguments"])
    assert isinstance(args, dict)


def test_visit_prompt_example_uses_real_tool_name():
    """El ejemplo debe usar una tool real (no inventada). Si alguien
    cambia el ejemplo a una tool que no existe, esto avisa."""
    from src.prompts import TOOL_DEFINITIONS

    real_tool_names = {t["function"]["name"] for t in TOOL_DEFINITIONS}
    example = _extract_example_tool_call(MERISTEM_SYSTEM_PROMPT_ES)
    parsed = _parse_tool_call_from_text(example)
    assert parsed is not None
    name = parsed[0]["function"]["name"]
    assert name in real_tool_names, (
        f"el ejemplo del prompt usa tool {name!r}, pero las tools reales "
        f"son: {real_tool_names}"
    )


def test_chat_prompt_example_uses_real_tool_name():
    """Idem para el prompt de chat."""
    from src.prompts import TOOL_DEFINITIONS

    real_tool_names = {t["function"]["name"] for t in TOOL_DEFINITIONS}
    example = _extract_example_tool_call(MERISTEM_CHAT_SYSTEM_PROMPT_ES)
    parsed = _parse_tool_call_from_text(example)
    assert parsed is not None
    name = parsed[0]["function"]["name"]
    assert name in real_tool_names, (
        f"el ejemplo del prompt usa tool {name!r}, pero las tools reales "
        f"son: {real_tool_names}"
    )
