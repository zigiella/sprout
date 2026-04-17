"""Tests de settings: defaults seguros y lectura de entorno."""

from __future__ import annotations

import pytest

from src.settings import load_settings


def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "OLLAMA_HOST",
        "OLLAMA_MODEL",
        "MERISTEM_PORT",
        "DB_PATH",
        "SHADOW_ENABLED",
        "GEMINI_API_KEY",
        "SHADOW_MODEL",
    ):
        monkeypatch.delenv(name, raising=False)


def test_defaults_are_safe(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)
    settings = load_settings()
    # Por defecto, shadow OFF. Es la regla dura del spec 12 §2.4.
    assert settings.shadow_enabled is False
    assert settings.gemini_api_key is None
    assert settings.ollama_host == "http://localhost:11434"
    assert settings.ollama_model == "gemma4:e4b"
    assert settings.meristem_port == 7070
    assert settings.db_path == "./meristem.db"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("true", True),
        ("True", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("false", False),
        ("0", False),
        ("no", False),
        ("", False),
        ("garbage", False),
    ],
)
def test_shadow_flag_parsing(
    monkeypatch: pytest.MonkeyPatch, raw: str, expected: bool
) -> None:
    _clear_env(monkeypatch)
    monkeypatch.setenv("SHADOW_ENABLED", raw)
    assert load_settings().shadow_enabled is expected


def test_port_parses_int(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_env(monkeypatch)
    monkeypatch.setenv("MERISTEM_PORT", "8080")
    assert load_settings().meristem_port == 8080
