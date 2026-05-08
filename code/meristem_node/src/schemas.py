"""Pydantic models para Meristem-nodo.

Schemas mínimos para empezar el esqueleto día 14. Día 15-16 se
alinean con los contratos v2 de Floema en `docs/20_data_contracts.md`
y con las clases Kotlin reales de `feat/pollen-f5-rhizome` para
serialización compatible.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
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

    bundle_id: str = Field(default_factory=lambda: f"b_{uuid.uuid4().hex[:12]}")
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
PolicyOrigin = Literal["meristem-durable", "pollen-visit"]
PolicyScope = Literal["durable", "transient"]


class PolicyPacket(BaseModel):
    """PolicyPacket v0 mínimo viable para Sprout MVP.

    Día 15-16 se alinea exactamente con el schema Kotlin de
    `feat/pollen-f5-rhizome` (clase `PolicyPacket.kt`). Esto es
    placeholder para empezar a iterar.

    Día 23 (sub-PR aditivo): añadidos `policy_origin` y `policy_scope`
    opcionales para distinguir policies durables (Meristem) de las
    transitorias (Pollen via visita) según spec Mini-Evaluator
    (PR #92 mergeado). Defaults preservan retrocompatibilidad: bundles
    antiguos sin estos campos siguen interpretándose como
    meristem-durable + durable.
    """

    schema_version: str = "1.0"
    policy_id: str
    target_node_id: str
    valid_until: datetime
    mode_default: ModeDefault = "normal"
    rules: dict[str, Any] = Field(default_factory=dict)
    rationale: str
    signature: str = "<placeholder-meristem-v0>"

    # Forward-compat con feature beta voz→política (PR #92 spec):
    policy_origin: PolicyOrigin = Field(
        default="meristem-durable",
        description=(
            "Quién emitió esta policy. 'meristem-durable' es la durable "
            "del slow brain doméstico. 'pollen-visit' es transitoria de "
            "una visita Pollen con Mini-Evaluator (feature beta)."
        ),
    )
    policy_scope: PolicyScope = Field(
        default="durable",
        description=(
            "Alcance temporal. 'durable' = TTL ~7 días, autoridad "
            "completa salvo hard limits. 'transient' = TTL ~12h, "
            "autoridad limitada (alerta durable siempre gana)."
        ),
    )


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


# ---------------------------------------------------------------------------
# Evaluator output (interno, no se serializa al cliente)
# ---------------------------------------------------------------------------


class Action(str, Enum):
    """Acción que el Evaluator decide tomar tras leer el bundle.

    Las 4 reglas determinísticas de Meristem-nodo emiten una de estas:
    - CONFIRM_POLICY: bundle limpio, extiende valid_until +7d (camino feliz)
    - CONSERVATIVE_POLICY: disputas/baja confianza/contradicciones,
      mode=conservative, thresholds más estrictos
    - ALERT_POLICY: emergencia persistente (DEPOSITO_BAJO repetido,
      HEARTBEAT_PERDIDO recurrente, ALERTA_LATCHED activa), mode=alert
    - REFUSE: el bundle pide algo que viola la jurisdicción de Meristem
      (HARD_LIMIT_DOMAIN, JURISDICTION_POLLEN)
    """

    CONFIRM_POLICY = "confirm_policy"
    CONSERVATIVE_POLICY = "conservative_policy"
    ALERT_POLICY = "alert_policy"
    REFUSE = "refuse"


class EvaluationResult(BaseModel):
    """Output del Evaluator. Decisión + trazabilidad + sugerencia para LLM."""

    action: Action
    reason_code: str
    evidence_refs: list[str] = Field(default_factory=list)
    suggested_mode: ModeDefault = "normal"
    suggested_rules: dict[str, Any] = Field(default_factory=dict)
    rationale_seed: str = Field(
        default="",
        description=(
            "Hechos concretos del bundle que justifican la action. El LLM "
            "los toma como base para escribir el rationale técnico y la "
            "prosa amable al operador. NO inventa, solo redacta."
        ),
    )


# ---------------------------------------------------------------------------
# Records persistidos (SQLite layer)
# ---------------------------------------------------------------------------


class BundleRecord(BaseModel):
    """Lo que se persiste en tabla bundles."""

    bundle_id: str
    received_at: datetime
    source_pollen_id: str
    target_rhizome_id: str
    active_policy_id: str
    raw_json: str  # bundle completo serializado para inspección post-mortem


class PolicyRecord(BaseModel):
    """Lo que se persiste en tabla policies."""

    policy_id: str
    emitted_at: datetime
    target_node_id: str
    raw_json: str  # PolicyPacket completo serializado
    evidence_refs: list[str]  # bundle_ids que justificaron


class DecisionRecord(BaseModel):
    """Lo que se persiste en tabla decisions (trazabilidad fuerte)."""

    decision_id: str
    bundle_id: str
    policy_id: str
    rule_applied: Action  # qué regla disparó
    reason_code: str
    llm_metrics: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Headers Sprout-Inference-* + finish_reason + tool_calls (si los "
            "hubo). Para análisis post-mortem y para mostrar al jurado en "
            "demo si pregunta por trazabilidad."
        ),
    )


# ---------------------------------------------------------------------------
# Status por target (vista consolidada multi-Rhizome — para /status en demo)
# ---------------------------------------------------------------------------


class TargetStatus(BaseModel):
    """Resumen del estado de Meristem para un Rhizome concreto.

    Usado en el endpoint `GET /status`. Pensado para que la demo MVP
    muestre en una pantalla cómo Meristem está gestionando 2 Rhizomes
    simultáneos en el mismo hardware (rhizome_01 + rhizome_02).

    Día 23: añadido desglose `policies_durable_count` +
    `policies_transient_count` para visibilidad de la distribución
    durable vs transitoria por target.
    """

    target_node_id: str
    bundles_received: int = 0
    last_bundle_at: datetime | None = None
    policies_emitted: int = 0
    policies_durable_count: int = 0
    policies_transient_count: int = 0
    latest_policy_id: str | None = None
    latest_policy_emitted_at: datetime | None = None
    latest_policy_mode: ModeDefault | None = None
    latest_policy_valid_until: datetime | None = None
    latest_policy_origin: PolicyOrigin | None = None
    latest_policy_scope: PolicyScope | None = None
    latest_reason_code: str | None = None
    latest_rule_applied: str | None = None


class StatusResponse(BaseModel):
    """Envelope de `GET /status` — vista consolidada multi-Rhizome."""

    targets_known: list[str] = Field(
        default_factory=list,
        description=(
            "IDs de todos los Rhizomes que han enviado bundles (incluye "
            "los que solo recibieron REFUSE). Ordenado alfabéticamente."
        ),
    )
    targets: list[TargetStatus] = Field(
        default_factory=list,
        description="Resumen por target. Mismo orden que `targets_known`.",
    )
