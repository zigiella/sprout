"""Settings de Meristem.

Lee variables de entorno (o .env cargado por el runner) y expone un objeto
inmutable. No usa `pydantic-settings` para no anadir dependencia — os.environ
con defaults es suficiente en este scope.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _get_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    ollama_host: str
    ollama_model: str
    meristem_port: int
    db_path: str
    shadow_enabled: bool
    gemini_api_key: str | None
    shadow_model: str


def load_settings() -> Settings:
    """Construye Settings desde el entorno actual."""
    return Settings(
        ollama_host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
        ollama_model=os.environ.get("OLLAMA_MODEL", "gemma4:e4b"),
        meristem_port=int(os.environ.get("MERISTEM_PORT", "7070")),
        db_path=os.environ.get("DB_PATH", "./meristem.db"),
        shadow_enabled=_get_bool("SHADOW_ENABLED", False),
        gemini_api_key=os.environ.get("GEMINI_API_KEY") or None,
        shadow_model=os.environ.get("SHADOW_MODEL", "gemma-4-31b-it"),
    )
