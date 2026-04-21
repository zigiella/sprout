"""Tests de `headers.build_sprout_headers` — puntos 4 y 7 de #46.

Verifica:
- 7 claves emitidas siempre (nunca se omite una).
- `thinking_tokens=0` se serializa como `"0"` explicito.
- `cost_eur=0.0` formateado con 6 decimales consistentes.
- Valores negativos rechazados (invariante del dataclass).
"""

from __future__ import annotations

import pytest

from src.headers import (
    ALL_METRIC_HEADERS,
    HEADER_COST_EUR,
    HEADER_THINKING_TOKENS,
    HEADER_TOKENS_OUT,
    InferenceMetrics,
    build_sprout_headers,
)


def _make(**overrides) -> InferenceMetrics:
    defaults = dict(
        backend="cloud-gemini",
        model="gemma-4-26b-a4b",
        tokens_in=100,
        tokens_out=50,
        thinking_tokens=20,
        duration_ms=1234,
        cost_eur=0.001234,
    )
    defaults.update(overrides)
    return InferenceMetrics(**defaults)


def test_emite_las_siete_claves_siempre():
    metrics = _make()
    headers = build_sprout_headers(metrics)
    for key in ALL_METRIC_HEADERS:
        assert key in headers, f"header {key} ausente"
    assert len(headers) == len(ALL_METRIC_HEADERS)


def test_todos_los_valores_son_str():
    headers = build_sprout_headers(_make())
    for k, v in headers.items():
        assert isinstance(v, str), f"{k} no es str: {type(v).__name__}"


def test_thinking_off_emite_cero_explicito():
    # Punto 7: "Emitir 0 explicitamente cuando thinking esta off (no omitir el header)"
    headers = build_sprout_headers(_make(thinking_tokens=0))
    assert headers[HEADER_THINKING_TOKENS] == "0"


def test_tokens_out_no_incluye_thinking():
    # Sanity: el valor que ponemos en `tokens_out` es el que emite, sin sumar
    # thinking (la suma se hace solo en `eval_count` del body Ollama-format).
    headers = build_sprout_headers(_make(tokens_out=50, thinking_tokens=20))
    assert headers[HEADER_TOKENS_OUT] == "50"


def test_cost_eur_formato_6_decimales():
    headers = build_sprout_headers(_make(cost_eur=0.001234))
    assert headers[HEADER_COST_EUR] == "0.001234"


def test_cost_eur_cero_en_local_test():
    headers = build_sprout_headers(_make(backend="local-ollama", cost_eur=0.0))
    assert headers[HEADER_COST_EUR] == "0.000000"


def test_contadores_negativos_rechazados():
    with pytest.raises(ValueError, match="tokens_in"):
        _make(tokens_in=-1)
    with pytest.raises(ValueError, match="tokens_out"):
        _make(tokens_out=-1)
    with pytest.raises(ValueError, match="thinking_tokens"):
        _make(thinking_tokens=-1)
    with pytest.raises(ValueError, match="duration_ms"):
        _make(duration_ms=-1)
    with pytest.raises(ValueError, match="cost_eur"):
        _make(cost_eur=-0.01)
