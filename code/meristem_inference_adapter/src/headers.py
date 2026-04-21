"""Emision uniforme de headers `Sprout-Inference-*` (puntos 4 y 7 de #46).

Caller (`policy_engine`) lee estos headers y persiste sin branchear por backend.
En modo local/test los campos de coste son `0.0`.

Semantica exacta (punto 7, fijada en el comentario tecnico de #46):

    Sprout-Inference-Backend:         cloud-gemini | local-ollama | test
    Sprout-Inference-Model:           gemma-4-26b-a4b | gemma-4-e4b-it | ...
    Sprout-Inference-Tokens-In:       = prompt_token_count
    Sprout-Inference-Tokens-Out:      = candidates_token_count (SIN thinking)
    Sprout-Inference-Thinking-Tokens: = thoughts_token_count (0 explicito si off)
    Sprout-Inference-Duration-Ms:     = wallclock total adapter
    Sprout-Inference-Cost-EUR:        = 0.0 en local/test

PUNTO 4 — docstring explicito pedido por Cambium:
El `eval_count` que el adapter devuelve en la respuesta Ollama-format se
calcula como `candidates_token_count + thoughts_token_count`. Cualquier `tok/s`
derivado como `eval_count / eval_duration` **incluye tokens de thinking**. El
numero defendible sale de los headers desglosados: `Tokens-Out / Duration-Ms`.
Harness (#45) y writeup DEBEN usar los desglosados.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

BackendLabel = Literal["cloud-gemini", "local-ollama", "test"]

HEADER_BACKEND = "Sprout-Inference-Backend"
HEADER_MODEL = "Sprout-Inference-Model"
HEADER_TOKENS_IN = "Sprout-Inference-Tokens-In"
HEADER_TOKENS_OUT = "Sprout-Inference-Tokens-Out"
HEADER_THINKING_TOKENS = "Sprout-Inference-Thinking-Tokens"
HEADER_DURATION_MS = "Sprout-Inference-Duration-Ms"
HEADER_COST_EUR = "Sprout-Inference-Cost-EUR"
HEADER_ERROR = "Sprout-Inference-Error"

ALL_METRIC_HEADERS = (
    HEADER_BACKEND,
    HEADER_MODEL,
    HEADER_TOKENS_IN,
    HEADER_TOKENS_OUT,
    HEADER_THINKING_TOKENS,
    HEADER_DURATION_MS,
    HEADER_COST_EUR,
)


@dataclass(frozen=True)
class InferenceMetrics:
    """Contadores uniformes que el backend devuelve al adapter.

    Todos los campos son obligatorios, explicitos. `thinking_tokens=0` cuando
    thinking esta off (no omitir el header). `cost_eur=0.0` en local/test.
    """

    backend: BackendLabel
    model: str
    tokens_in: int
    tokens_out: int  # SIN thinking
    thinking_tokens: int  # 0 explicito si thinking off
    duration_ms: int
    cost_eur: float  # 0.0 en local/test

    def __post_init__(self) -> None:
        for name, value in (
            ("tokens_in", self.tokens_in),
            ("tokens_out", self.tokens_out),
            ("thinking_tokens", self.thinking_tokens),
            ("duration_ms", self.duration_ms),
        ):
            if value < 0:
                raise ValueError(f"{name} no puede ser negativo: {value}")
        if self.cost_eur < 0.0:
            raise ValueError(f"cost_eur no puede ser negativo: {self.cost_eur}")


def build_sprout_headers(metrics: InferenceMetrics) -> dict[str, str]:
    """Construye el dict de headers `Sprout-Inference-*` para la respuesta HTTP.

    Todos los valores son str (requisito de FastAPI `Response.headers`). El
    caller convierte de vuelta a int/float si necesita.

    Args:
        metrics: metricas uniformes del backend.

    Returns:
        Dict con las 7 claves `Sprout-Inference-*`. Nunca omite claves.
    """
    return {
        HEADER_BACKEND: metrics.backend,
        HEADER_MODEL: metrics.model,
        HEADER_TOKENS_IN: str(metrics.tokens_in),
        HEADER_TOKENS_OUT: str(metrics.tokens_out),
        HEADER_THINKING_TOKENS: str(metrics.thinking_tokens),
        HEADER_DURATION_MS: str(metrics.duration_ms),
        # cost_eur con 6 decimales para no perder precision en costes bajos
        # (una decision Meristem cuesta ~centimos). Formato decimal fijo para
        # que el parsing del caller sea estable.
        HEADER_COST_EUR: f"{metrics.cost_eur:.6f}",
    }
