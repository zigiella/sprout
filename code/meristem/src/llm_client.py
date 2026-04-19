"""Cliente Ollama para el modelo local (Gemma 4 E4B).

Dos operaciones:
- `ping()`: chequeo de salud contra `/api/tags`. Usado por el smoke test.
- `generate_json(system, user, schema)`: llamada a `/api/generate` con
  structured output. Ollama (>=0.1.30) acepta `format` como JSON schema dict
  y garantiza salida parseable. El modulo no asume `pydantic` aqui — devuelve
  el dict y deja que el caller valide con su schema.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from .settings import Settings


class OllamaClient:
    """Wrapper minimo sobre el endpoint HTTP de Ollama."""

    def __init__(self, settings: Settings, timeout_s: float = 120.0) -> None:
        # timeout alto por defecto porque /api/generate con structured output
        # sobre E4B tipicamente tarda 20-40s en hardware modesto. El ping
        # usa su propio timeout corto sobre el mismo cliente.
        self._host = settings.ollama_host.rstrip("/")
        self._model = settings.ollama_model
        self._client = httpx.Client(base_url=self._host, timeout=timeout_s)

    @property
    def model(self) -> str:
        return self._model

    def ping(self, timeout_s: float = 2.0) -> bool:
        """Consulta `/api/tags`. Devuelve True si Ollama responde 200."""
        try:
            response = self._client.get("/api/tags", timeout=timeout_s)
        except httpx.HTTPError:
            return False
        return response.status_code == 200

    def generate_json(
        self,
        system: str,
        user: str,
        schema: dict[str, Any] | None = None,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        """Invoca `/api/generate` pidiendo JSON como salida.

        Si `schema` es un JSON Schema, Ollama fuerza el formato contra el.
        Si es None, se pide solo `format="json"` (valido pero sin garantia
        de estructura).

        Levanta:
        - httpx.HTTPError si el daemon no responde o devuelve != 2xx.
        - ValueError si la respuesta no es JSON parseable.
        """
        payload: dict[str, Any] = {
            "model": self._model,
            "system": system,
            "prompt": user,
            "stream": False,
            "options": {"temperature": temperature},
        }
        payload["format"] = schema if schema is not None else "json"

        response = self._client.post("/api/generate", json=payload)
        response.raise_for_status()
        body = response.json()
        raw = body.get("response", "")
        if not raw:
            raise ValueError("Ollama devolvio respuesta vacia")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Ollama no devolvio JSON parseable: {raw[:200]}"
            ) from exc

    def close(self) -> None:
        self._client.close()
