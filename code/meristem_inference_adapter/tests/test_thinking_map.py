"""Tests de `thinking_map` — punto 2 de #46."""

from __future__ import annotations

import pytest

from src.thinking_map import GeminiThinkingConfig, map_think_to_gemini


def test_think_true_activa_con_budget():
    cfg = map_think_to_gemini(think=True, budget_when_on=4096)
    assert cfg == GeminiThinkingConfig(include_thoughts=True, thinking_budget=4096)


def test_think_false_desactiva_explicito():
    cfg = map_think_to_gemini(think=False, budget_when_on=4096)
    assert cfg == GeminiThinkingConfig(include_thoughts=False, thinking_budget=0)


def test_think_none_tratado_como_false():
    # Ausencia de `think` en el request Ollama no debe significar "default del
    # modelo"; debe significar "off explicito".
    cfg = map_think_to_gemini(think=None, budget_when_on=4096)
    assert cfg == GeminiThinkingConfig(include_thoughts=False, thinking_budget=0)


def test_think_true_con_budget_cero_levanta():
    # Si el caller pide thinking=True pero el budget es 0, mejor fallar ruidoso
    # que mandar "activa thinking con 0 tokens" (que ya es off).
    with pytest.raises(ValueError, match="budget_when_on=0"):
        map_think_to_gemini(think=True, budget_when_on=0)


def test_think_true_con_budget_negativo_levanta():
    with pytest.raises(ValueError):
        map_think_to_gemini(think=True, budget_when_on=-1)
