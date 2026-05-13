"""Tests del endpoint /health."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.settings import Settings


def _settings(tmp_path: Path, shadow: bool = False) -> Settings:
    return Settings(
        ollama_host="http://localhost:11434",
        ollama_model="gemma4:e4b",
        meristem_port=7070,
        db_path=str(tmp_path / "meristem.db"),
        shadow_enabled=shadow,
        gemini_api_key=None,
        shadow_model="gemma-4-31b-it",
    )


def test_health_ok(tmp_path: Path) -> None:
    app = create_app(_settings(tmp_path))
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model"] == "gemma4:e4b"
    assert body["shadow_enabled"] is False
    assert "version" in body


def test_create_app_creates_sqlite_schema(tmp_path: Path) -> None:
    import sqlite3

    db_path = tmp_path / "meristem.db"
    create_app(_settings(tmp_path))
    assert db_path.exists(), "create_app debe inicializar SQLite"
    with sqlite3.connect(str(db_path)) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    expected = {
        "evidence",
        "policies",
        "deltas",
        "decisions_log",
        "shadow_comparisons",
    }
    assert expected.issubset(tables), tables


def test_create_app_shadow_on_without_genai_raises(tmp_path: Path) -> None:
    """Si SHADOW_ENABLED pero google-genai no esta instalada, debe fallar al
    importar. Esto hace explicito el contrato: flag on => dependencia opcional
    presente."""
    import importlib.util

    # `find_spec` puede lanzar `ModuleNotFoundError` si el paquete padre
    # `google` no existe en absoluto (no solo si falta el sub-paquete
    # `genai`). Envolvemos para tratar ambos casos como "no instalado".
    try:
        has_genai = importlib.util.find_spec("google.genai") is not None
    except ModuleNotFoundError:
        has_genai = False

    if has_genai:
        pytest.skip("google-genai instalada; test no aplica en este entorno.")
    # `ImportError` es la superclase de `ModuleNotFoundError`. Python 3.13
    # levanta `ImportError: cannot import name 'genai' from 'google'`
    # cuando el paquete namespace `google` existe (p.ej. por grpcio) pero
    # no contiene `genai`. Cubrimos ambos.
    with pytest.raises(ImportError):
        create_app(_settings(tmp_path, shadow=True))
