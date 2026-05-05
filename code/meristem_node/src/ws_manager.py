"""PollenConnectionManager — estado de la conexión WebSocket activa.

Singleton que mantiene la **única** conexión WebSocket esperada en MVP
(un Pollen por Meristem-nodo). Si llega un segundo cliente, se rechaza.

Estado:
- pollen_id, app_version desde el primer `pollen_hello`
- last_heartbeat para detectar timeouts
- connected_at para metadata
- websocket_ref para enviar mensajes desde el state manager

Uso desde `main.py`:
    from .ws_manager import manager
    await manager.connect(websocket, hello_payload)
    ...
    await manager.disconnect()
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import WebSocket

from .ws_schemas import WSEvent, build_message


logger = logging.getLogger(__name__)


HEARTBEAT_TIMEOUT_S = 30.0  # Si no llega heartbeat en 30s, asumimos desconexión


class PollenConnectionManager:
    """Gestiona la conexión WebSocket Pollen ↔ Meristem.

    En MVP solo permitimos un Pollen conectado a la vez. Si llega un
    segundo intento, lo rechazamos con un error.
    """

    def __init__(self) -> None:
        self._websocket: WebSocket | None = None
        self._pollen_id: str | None = None
        self._app_version: str | None = None
        self._connected_at: datetime | None = None
        self._last_heartbeat: datetime | None = None

    @property
    def is_connected(self) -> bool:
        return self._websocket is not None

    @property
    def pollen_id(self) -> str | None:
        return self._pollen_id

    @property
    def is_alive(self) -> bool:
        """True si hay conexión y heartbeat reciente (< HEARTBEAT_TIMEOUT_S)."""
        if not self.is_connected or self._last_heartbeat is None:
            return False
        elapsed = datetime.utcnow() - self._last_heartbeat
        return elapsed < timedelta(seconds=HEARTBEAT_TIMEOUT_S)

    def state_snapshot(self) -> dict[str, Any]:
        """Snapshot serializable para `/health` y `/sync-state` endpoints."""
        return {
            "connected": self.is_connected,
            "alive": self.is_alive,
            "pollen_id": self._pollen_id,
            "app_version": self._app_version,
            "connected_at": (
                self._connected_at.isoformat() if self._connected_at else None
            ),
            "last_heartbeat": (
                self._last_heartbeat.isoformat() if self._last_heartbeat else None
            ),
        }

    async def accept_or_reject(self, websocket: WebSocket) -> bool:
        """Acepta el WebSocket si no hay otro conectado.

        Returns True si se aceptó, False si se rechazó.
        """
        if self._websocket is not None:
            # Ya hay un Pollen conectado; rechazamos.
            logger.warning(
                "Rechazada conexión WS: ya hay Pollen conectado (%s).",
                self._pollen_id,
            )
            await websocket.accept()
            await websocket.send_json(build_message(
                WSEvent.ERROR,
                {
                    "code": "ALREADY_CONNECTED",
                    "message_es": "Ya hay un Pollen conectado a este Meristem.",
                    "details": f"existing_pollen_id={self._pollen_id}",
                },
            ))
            await websocket.close(code=1008)  # Policy Violation
            return False
        await websocket.accept()
        self._websocket = websocket
        self._connected_at = datetime.utcnow()
        self._last_heartbeat = self._connected_at
        return True

    def register_hello(self, pollen_id: str, app_version: str) -> None:
        """Registra metadata del Pollen tras recibir `pollen_hello`."""
        self._pollen_id = pollen_id
        self._app_version = app_version
        self._last_heartbeat = datetime.utcnow()

    def heartbeat(self) -> None:
        """Refresca el last_heartbeat. Llamado en cada mensaje recibido."""
        self._last_heartbeat = datetime.utcnow()

    async def disconnect(self) -> None:
        """Limpia el estado tras desconexión (esperada o no)."""
        if self._websocket is not None:
            try:
                await self._websocket.close()
            except Exception:
                pass  # Ya cerrada
        self._websocket = None
        self._pollen_id = None
        self._app_version = None
        self._connected_at = None
        self._last_heartbeat = None

    async def send(
        self,
        event: WSEvent,
        payload: dict[str, Any],
        trace_id: str | None = None,
    ) -> bool:
        """Envía un mensaje al cliente Pollen conectado.

        Returns True si se envió, False si no hay conexión activa.
        """
        if self._websocket is None:
            logger.warning("send() sin conexión WS activa (event=%s)", event)
            return False
        try:
            await self._websocket.send_json(
                build_message(event, payload, trace_id=trace_id)
            )
            return True
        except Exception as e:
            logger.error("Error enviando WS event=%s: %s", event, e)
            await self.disconnect()
            return False


# Singleton global (un Pollen por Meristem-nodo en MVP)
manager = PollenConnectionManager()
