"""Protocolo comun a todos los backends.

Un backend recibe un request Ollama-format y devuelve (respuesta Ollama-format,
InferenceMetrics para los headers Sprout-Inference-*).

El adapter (main.py) orquesta: selecciona backend segun Settings, invoca,
envuelve la respuesta con los headers y la devuelve al caller.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from ..headers import InferenceMetrics


@runtime_checkable
class InferenceBackend(Protocol):
    """Contrato minimo que cualquier backend debe cumplir.

    Los metodos son asyncronos porque cloud y local hacen I/O de red; test puede
    implementarlos como `async def` triviales.
    """

    async def chat(
        self, request: dict[str, Any]
    ) -> tuple[dict[str, Any], InferenceMetrics]:
        """Implementa `/api/chat`.

        Args:
            request: body del request Ollama-format (dict parseado de JSON).

        Returns:
            Tupla `(response_body, metrics)`. `response_body` es el dict que el
            adapter serializara como JSON de respuesta. `metrics` alimenta los
            headers Sprout-Inference-*.
        """
        ...

    async def generate(
        self, request: dict[str, Any]
    ) -> tuple[dict[str, Any], InferenceMetrics]:
        """Implementa `/api/generate`. Mismo contrato que `chat`."""
        ...
