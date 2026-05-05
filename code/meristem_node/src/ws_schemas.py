"""Schemas WebSocket para protocolo Pollen ↔ Meristem (Variante D).

Implementa el protocolo v1.0 acordado con Floema en
`bitacora/2026-05-04_acepto-variante-d-websocket-protocolo_meristem-a-floema.md`
(PR #81 mergeado).

Convención uniforme de mensajes:
    {"event": "<event_name>", "payload": {...}, "timestamp": ISO8601, "trace_id": ...}

Endpoint: ws://<meristem-host>:13000/ws/pollen-sync
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Eventos del protocolo (v1.0)
# ---------------------------------------------------------------------------


class WSEvent(str, Enum):
    """Eventos del protocolo Pollen ↔ Meristem v1.0."""

    # Pollen → Meristem
    POLLEN_HELLO = "pollen_hello"
    BUNDLES_PUSHED = "bundles_pushed"
    POLICIES_PULLED = "policies_pulled"
    POLLEN_HEARTBEAT = "pollen_heartbeat"

    # Meristem → Pollen
    MERISTEM_READY = "meristem_ready"
    COMMAND = "command"
    PROGRESS = "progress"
    MERISTEM_HEARTBEAT_ACK = "meristem_heartbeat_ack"
    ERROR = "error"


# ---------------------------------------------------------------------------
# Envelope uniforme
# ---------------------------------------------------------------------------


class WSMessage(BaseModel):
    """Envelope uniforme de cualquier mensaje WebSocket Pollen ↔ Meristem.

    `trace_id` es opcional v1.0; recomendado para correlacionar request
    con response durante operaciones que generen progress events.
    """

    event: WSEvent
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    trace_id: str | None = None


# ---------------------------------------------------------------------------
# Payloads tipados (validación de campos por evento)
# ---------------------------------------------------------------------------


class PollenHelloPayload(BaseModel):
    """Payload del `pollen_hello` (al conectar)."""

    pollen_id: str
    app_version: str = "0.0.0"
    bundles_pending_count: int = 0
    policies_to_pickup_target_ids: list[str] = Field(default_factory=list)


class MeristemReadyPayload(BaseModel):
    """Payload del `meristem_ready` (respuesta a hello)."""

    meristem_id: str
    version: str = "0.1.0"
    policies_ready_for_pickup: list[dict[str, str]] = Field(
        default_factory=list,
        description="Lista de {target_node_id, policy_id} listos para retirar.",
    )


CommandName = Literal["push_bundles", "pull_policies"]


class CommandPayload(BaseModel):
    """Payload del `command` (Meristem → Pollen tras click agricultor)."""

    command: CommandName
    expected_count: int = 0


class BundlesPushedPayload(BaseModel):
    """Payload del `bundles_pushed` (Pollen tras terminar tanda HTTP)."""

    count: int
    bundle_ids: list[str] = Field(default_factory=list)


class PoliciesPulledPayload(BaseModel):
    """Payload del `policies_pulled` (Pollen tras retirar policies)."""

    count: int
    policy_ids: list[str] = Field(default_factory=list)


class ProgressPayload(BaseModel):
    """Payload del `progress` durante operaciones largas."""

    operation: CommandName
    processed: int
    total: int
    current_target_node_id: str | None = None
    current_status: Literal["ok", "refuse", "need_clarification"] | None = None


class HeartbeatAckPayload(BaseModel):
    """Payload de `meristem_heartbeat_ack`."""

    online: bool = True


class ErrorPayload(BaseModel):
    """Payload de `error` (cualquier dirección)."""

    code: str
    message_es: str
    details: str | None = None


# ---------------------------------------------------------------------------
# Helpers para construir envelopes
# ---------------------------------------------------------------------------


def build_message(
    event: WSEvent,
    payload: dict[str, Any] | BaseModel,
    trace_id: str | None = None,
) -> dict[str, Any]:
    """Construye un mensaje WS listo para `websocket.send_json(...)`.

    Acepta tanto dict como Pydantic model como payload.
    """
    if isinstance(payload, BaseModel):
        payload_dict = payload.model_dump(mode="json")
    else:
        payload_dict = payload
    return WSMessage(
        event=event,
        payload=payload_dict,
        trace_id=trace_id,
    ).model_dump(mode="json")
