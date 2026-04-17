"""Cliente Ollama para el modelo local (Gemma 4 E4B).

Este modulo es un **stub** en el bootstrap: configura el cliente HTTP y expone
`ping()` para verificar que el daemon responde. El razonamiento real (llamada
a `/api/generate` o `/api/chat` con prompts del policy_engine) entra en el PR
siguiente junto con su bitacora.
"""

from __future__ import annotations

import httpx

from .settings import Settings


class OllamaClient:
    """Wrapper minimo sobre el endpoint HTTP de Ollama."""

    def __init__(self, settings: Settings, timeout_s: float = 5.0) -> None:
        self._host = settings.ollama_host.rstrip("/")
        self._model = settings.ollama_model
        self._client = httpx.Client(base_url=self._host, timeout=timeout_s)

    @property
    def model(self) -> str:
        return self._model

    def ping(self) -> bool:
        """Consulta `/api/tags`. Devuelve True si Ollama responde 200."""
        try:
            response = self._client.get("/api/tags")
        except httpx.HTTPError:
            return False
        return response.status_code == 200

    def close(self) -> None:
        self._client.close()
