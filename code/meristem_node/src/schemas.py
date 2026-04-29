"""Pydantic models para Meristem-nodo.

Schemas mínimos para empezar el esqueleto día 14. Día 15-16 se
alinean con los contratos v2 de Floema en `docs/20_data_contracts.md`
y con las clases Kotlin reales de `feat/pollen-f5-rhizome` para
serialización compatible.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Bundle entrante (lo que Pollen trae de cada visita)
# ---------------------------------------------------------------------------


class Bundle(BaseModel):
    """Lo que Pollen entrega a Meristem-nodo en POST /visit.

    Composición mínima v0:
    - rhizome_snapshot: estado del nodo Rhizome al momento de la visita
    - decision_receipts: decisiones del Rhizome desde la visita anterior
    - weather_digest: opcional, digest meteorológico transportado
    - validation_stamps: opcional, sellos de validación cruzada
    - active_policy_id: la policy actualmente activa en Rhizome (para
      saber qué afinar)
    - source_pollen_id: id del Pollen que transporta (trazabilidad)
    """

    bundle_id: str = Field(default_factory=lambda: f"b_{int(datetime.utcnow().timestamp())}")
    received_at: datetime = Field(default_factory=datetime.utcnow)
    source_pollen_id: str
    target_rhizome_id: str
    active_policy_id: str
    rhizome_snapshot: dict[str, Any]
    decision_receipts: list[dict[str, Any]] = Field(default_factory=list)
    weather_digest: dict[str, Any] | None = None
    validation_stamps: list[dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# PolicyPacket emitido (lo que Meristem-nodo devuelve)
# ---------------------------------------------------------------------------

ModeDefault = Literal["normal", "conservative", "alert"]


class PolicyPacket(BaseModel):
    """PolicyPacket v0 mínimo viable para Sprout MVP.

    Día 15-16 se alinea exactamente con el schema Kotlin de
    `feat/pollen-f5-rhizome` (clase `PolicyPacket.kt`). Esto es
    placeholder para empezar a iterar.
    """

    schema_version: str = "1.0"
    policy_id: str
    target_node_id: str
    valid_until: datetime
    mode_default: ModeDefault = "normal"
    rules: dict[str, Any] = Field(default_factory=dict)
    rationale: str
    signature: str = "<placeholder-meristem-v0>"


# ---------------------------------------------------------------------------
# Envelope de respuesta /visit (sobre común consistente con Pollen+Rhizome)
# ---------------------------------------------------------------------------

EnvelopeStatus = Literal["ok", "need_clarification", "refuse"]


class VisitResponsePayload(BaseModel):
    """Payload del envelope cuando status=ok."""

    policy_packet: PolicyPacket
    rationale_for_operator: str = Field(
        ...,
        max_length=240,
        description=(
            "Prosa amable en castellano (máx 240 chars) que el operador "
            "ve en pantalla del portátil tras la sesión de descarga."
        ),
    )
    evidence_refs: list[str] = Field(
        default_factory=list,
        description="bundle_ids que justificaron esta policy.",
    )


class VisitResponse(BaseModel):
    """Sobre común de respuesta a POST /visit (mismo formato que Pollen+Rhizome)."""

    task: Literal["afinar_policy"] = "afinar_policy"
    status: EnvelopeStatus
    reason_code: str | None = None
    question_es: str | None = None
    payload: VisitResponsePayload | None = None
