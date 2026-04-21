"""Reconstruccion de `message.thinking` desde la respuesta de Gemini (punto 3 de #46).

Gemini intercala partes con `thought=True` dentro de `content.parts`. Ollama
expone el thinking en un campo separado `message.thinking`.

Este modulo extrae las partes `thought=True`, las concatena en orden, y
devuelve ambos strings (content sin thinking, thinking solo).

Sin esto, rompe el patron documentado en
`2026-04-19_thinking-mode-e4b-latencia_meristem.md` y los smoke tests del dia 5
fallan.

Nota: la lista `parts` puede venir como:
- dicts (`{"text": "...", "thought": True}`) — dict sin `thought` → asumimos False.
- objetos google-genai (atributos `.text` / `.thought`).

El helper soporta ambos para no atar este modulo a `google-genai` (los tests
unitarios usan dicts).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SplitMessage:
    """Resultado de dividir una respuesta Gemini en content + thinking."""

    content: str
    thinking: str


def _get(part: Any, key: str, default: Any = None) -> Any:
    if isinstance(part, dict):
        return part.get(key, default)
    return getattr(part, key, default)


def split_gemini_parts(parts: list[Any]) -> SplitMessage:
    """Divide la lista `content.parts` de Gemini en content y thinking.

    Args:
        parts: lista de `Part` tal como la expone `google-genai`, o lista de
            dicts con claves `text` (str) y `thought` (bool, opcional).

    Returns:
        SplitMessage con ambos campos concatenados en orden de aparicion. Si no
        hay partes thought, `thinking == ""`. Si no hay partes no-thought,
        `content == ""`.
    """
    content_buf: list[str] = []
    thinking_buf: list[str] = []

    for part in parts:
        text = _get(part, "text")
        if not text:
            # Saltar partes sin texto (ej. function calls, imagenes). No entran
            # ni en content ni en thinking.
            continue
        is_thought = bool(_get(part, "thought", False))
        (thinking_buf if is_thought else content_buf).append(text)

    return SplitMessage(
        content="".join(content_buf),
        thinking="".join(thinking_buf),
    )
