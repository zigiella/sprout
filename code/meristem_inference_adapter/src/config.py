"""Configuracion del adapter.

Env vars + alias de modelos + pricing placeholders. No depende de FastAPI ni de
httpx; se puede importar en tests sin levantar el server.

PLACEHOLDER para el thinking budget se resuelve en #44 tras A/B.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal

BackendMode = Literal["cloud", "local", "test"]


# -----------------------------------------------------------------------------
# Placeholder — #44 fija el valor empirico tras A/B.
# No optimizar en base a este numero.
# -----------------------------------------------------------------------------
THINKING_BUDGET_TOKENS_PLACEHOLDER = 4096


# -----------------------------------------------------------------------------
# Alias de modelos (punto 9). Overridable por env via MODEL_ALIAS_<tag>=<cloud_id>
# (formato exacto a confirmar en implementacion).
# -----------------------------------------------------------------------------
DEFAULT_MODEL_ALIASES: dict[str, str] = {
    "gemma4:26b-moe": "gemma-4-26b-a4b",
    "gemma4:e4b": "gemma-4-e4b-it",
    "gemma4:31b": "gemma-4-31b-it",
}


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int
    backoff_ms: tuple[int, ...]


@dataclass(frozen=True)
class PricingConfig:
    in_eur_per_1k: float
    out_eur_per_1k: float
    thinking_eur_per_1k: float


@dataclass(frozen=True)
class Settings:
    backend: BackendMode
    adapter_port: int
    ollama_upstream_host: str
    gemini_api_key: str | None
    gemini_default_model: str
    thinking_budget: int
    pricing: PricingConfig
    retry: RetryConfig
    model_aliases: dict[str, str] = field(default_factory=dict)


def _get_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _get_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


def _get_backend(default: BackendMode = "test") -> BackendMode:
    raw = (os.environ.get("INFERENCE_BACKEND") or default).strip().lower()
    if raw not in ("cloud", "local", "test"):
        raise ValueError(
            f"INFERENCE_BACKEND invalido: {raw!r}. Valores validos: cloud | local | test"
        )
    return raw  # type: ignore[return-value]


def load_settings() -> Settings:
    """Construye Settings desde el entorno actual. Scaffold: stub sin validacion completa."""
    return Settings(
        backend=_get_backend(),
        adapter_port=_get_int("ADAPTER_PORT", 11434),
        ollama_upstream_host=os.environ.get(
            "OLLAMA_UPSTREAM_HOST", "http://localhost:11435"
        ),
        gemini_api_key=os.environ.get("GEMINI_API_KEY") or None,
        gemini_default_model=os.environ.get("GEMINI_DEFAULT_MODEL", "gemma-4-26b-a4b"),
        thinking_budget=_get_int(
            "MERISTEM_THINKING_BUDGET", THINKING_BUDGET_TOKENS_PLACEHOLDER
        ),
        pricing=PricingConfig(
            in_eur_per_1k=_get_float("GEMINI_PRICE_IN_EUR_PER_1K", 0.0),
            out_eur_per_1k=_get_float("GEMINI_PRICE_OUT_EUR_PER_1K", 0.0),
            thinking_eur_per_1k=_get_float("GEMINI_PRICE_THINKING_EUR_PER_1K", 0.0),
        ),
        retry=RetryConfig(
            max_attempts=_get_int("RETRY_MAX_ATTEMPTS", 3),
            backoff_ms=(
                _get_int("RETRY_BACKOFF_MS_1", 500),
                _get_int("RETRY_BACKOFF_MS_2", 2000),
                _get_int("RETRY_BACKOFF_MS_3", 8000),
            ),
        ),
        model_aliases=dict(DEFAULT_MODEL_ALIASES),
    )


def resolve_model(tag: str, aliases: dict[str, str]) -> str:
    """Mapea un tag tipo `gemma4:26b-moe` al id del backend cloud.

    Si el tag no esta en el dict, se devuelve tal cual (permite pasar ids nativos).
    """
    return aliases.get(tag, tag)
