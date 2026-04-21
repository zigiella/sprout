"""Tests de `reconstruct.split_gemini_parts` — punto 3 de #46.

Cubre el caso critico del comentario tecnico: partes `thought=True` y
`thought=False` intercaladas.
"""

from __future__ import annotations

from types import SimpleNamespace

from src.reconstruct import SplitMessage, split_gemini_parts


def test_partes_intercaladas_dict():
    parts = [
        {"text": "Let me think. ", "thought": True},
        {"text": "The answer is ", "thought": False},
        {"text": "Actually wait. ", "thought": True},
        {"text": "42.", "thought": False},
    ]
    out = split_gemini_parts(parts)
    assert out.content == "The answer is 42."
    assert out.thinking == "Let me think. Actually wait. "


def test_solo_content_sin_thinking():
    parts = [{"text": "hola", "thought": False}]
    out = split_gemini_parts(parts)
    assert out == SplitMessage(content="hola", thinking="")


def test_solo_thinking_sin_content():
    parts = [{"text": "pensando", "thought": True}]
    out = split_gemini_parts(parts)
    assert out == SplitMessage(content="", thinking="pensando")


def test_thought_ausente_es_false():
    # Una parte sin el campo `thought` se trata como content normal.
    parts = [{"text": "hola"}]
    out = split_gemini_parts(parts)
    assert out.content == "hola"
    assert out.thinking == ""


def test_parts_como_objetos_con_atributos():
    # google-genai devuelve objetos con .text / .thought, no dicts.
    parts = [
        SimpleNamespace(text="think ", thought=True),
        SimpleNamespace(text="answer", thought=False),
    ]
    out = split_gemini_parts(parts)
    assert out.content == "answer"
    assert out.thinking == "think "


def test_partes_sin_texto_se_saltan():
    # Function calls / imagenes sin .text no entran en ninguna cadena.
    parts = [
        {"text": "hello", "thought": False},
        {"function_call": {"name": "fn"}},  # sin text
        {"text": None, "thought": False},
        {"text": "", "thought": False},
        {"text": " world", "thought": False},
    ]
    out = split_gemini_parts(parts)
    assert out.content == "hello world"
    assert out.thinking == ""


def test_lista_vacia():
    out = split_gemini_parts([])
    assert out == SplitMessage(content="", thinking="")
