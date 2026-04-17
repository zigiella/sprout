"""Tests del stub de OllamaClient. Sin tocar red real."""

from __future__ import annotations

import httpx
import pytest

from src.llm_client import OllamaClient
from src.settings import Settings


def _settings() -> Settings:
    return Settings(
        ollama_host="http://localhost:11434",
        ollama_model="gemma4:e4b",
        meristem_port=7070,
        db_path=":memory:",
        shadow_enabled=False,
        gemini_api_key=None,
        shadow_model="gemma-4-31b-it",
    )


def test_ping_returns_true_on_200(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OllamaClient(_settings())

    def fake_get(self, url, *args, **kwargs):  # type: ignore[no-untyped-def]
        assert url == "/api/tags"
        return httpx.Response(200, json={"models": []})

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    try:
        assert client.ping() is True
    finally:
        client.close()


def test_ping_returns_false_on_connection_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = OllamaClient(_settings())

    def fake_get(self, url, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    try:
        assert client.ping() is False
    finally:
        client.close()


def test_model_exposed() -> None:
    client = OllamaClient(_settings())
    try:
        assert client.model == "gemma4:e4b"
    finally:
        client.close()
