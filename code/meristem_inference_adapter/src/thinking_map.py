"""Mapeo del parametro `think` entre Ollama y Gemini (punto 2 de #46).

Ollama: `think: true | false`, binario, budget libre.
Gemini: `thinking_config={include_thoughts: bool, thinking_budget: int}`, explicito.

Reglas acordadas en el comentario tecnico de #46:

- `think=true`  desde caller → `include_thoughts=True`  + `thinking_budget=<budget_when_on>`
- `think=false` o ausente    → `include_thoughts=False` + `thinking_budget=0`
  (desactivado explicito, no default del modelo)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GeminiThinkingConfig:
    include_thoughts: bool
    thinking_budget: int


def map_think_to_gemini(
    think: bool | None,
    budget_when_on: int,
) -> GeminiThinkingConfig:
    """Traduce el flag `think` de Ollama al `thinking_config` de Gemini.

    Args:
        think: valor del campo `think` del request Ollama. `None` se trata como
            `False` (ausencia = desactivado explicito, no default del modelo).
        budget_when_on: presupuesto de thinking a aplicar cuando `think=True`.
            Viene de `Settings.thinking_budget` (env `MERISTEM_THINKING_BUDGET`).

    Returns:
        GeminiThinkingConfig listo para pasar a `google-genai`.

    Raises:
        ValueError: si `think=True` pero `budget_when_on <= 0`.
    """
    if think:
        if budget_when_on <= 0:
            raise ValueError(
                f"think=True pero budget_when_on={budget_when_on}. "
                "Si se quiere desactivar thinking, pasar think=False."
            )
        return GeminiThinkingConfig(
            include_thoughts=True,
            thinking_budget=budget_when_on,
        )
    return GeminiThinkingConfig(include_thoughts=False, thinking_budget=0)
