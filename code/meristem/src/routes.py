"""Endpoints HTTP de Meristem.

Montados sobre un APIRouter que `main.create_app` incluye. La config
(db_path principalmente) se lee desde `request.app.state.settings`.

Endpoints:

- POST /ingest             — Pollen empuja evidencia (snapshot/receipt/weather/alert).
- GET  /policies/{target}  — lee la policy activa del target (o 404).
- GET  /deltas/pending/{target} — lista deltas en estado `pending`.
- POST /deltas/propose     — Pollen propone un delta; Meristem lo valida
                             contra §30 y lo persiste como validated/rejected.
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, ValidationError
from schemas import (
    ContradictionAlert,
    DecisionReceipt,
    PolicyDelta,
    PolicyPacket,
    RhizomeSnapshot,
    WeatherPacket,
)

from . import persistence, safety_rules

router = APIRouter()


# Mapeo `kind` → modelo pydantic. Controla el discriminador de /ingest y la
# lista de tipos de evidencia que Meristem acepta consumir.
INGEST_KINDS: dict[str, type] = {
    "rhizome_snapshot": RhizomeSnapshot,
    "decision_receipt": DecisionReceipt,
    "weather_packet": WeatherPacket,
    "contradiction_alert": ContradictionAlert,
}


class IngestEnvelope(BaseModel):
    """Envoltorio minimo para /ingest: `kind` + `payload` crudo.

    El payload se valida contra el modelo correspondiente a `kind` dentro
    del handler; aqui solo tipamos el envelope.
    """

    kind: Literal[
        "rhizome_snapshot",
        "decision_receipt",
        "weather_packet",
        "contradiction_alert",
    ]
    payload: dict[str, Any]


class IngestResponse(BaseModel):
    stored_id: int
    kind: str


def _db_path(request: Request) -> str:
    return request.app.state.settings.db_path


# ---------------------------------------------------------------------------
# POST /ingest
# ---------------------------------------------------------------------------

@router.post(
    "/ingest",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=IngestResponse,
)
def ingest(envelope: IngestEnvelope, request: Request) -> IngestResponse:
    model_cls = INGEST_KINDS[envelope.kind]
    try:
        parsed = model_cls.model_validate(envelope.payload)
    except ValidationError as exc:
        # Reemitimos como 422 con los errores pydantic, sin exponer stacktrace.
        raise HTTPException(
            status_code=422,  # Unprocessable Content. Constante renombrada en Starlette nuevo; usamos literal para evitar DeprecationWarning cross-version.
            detail={"kind": envelope.kind, "errors": exc.errors()},
        )

    canonical = parsed.model_dump(mode="json")
    stored_id = persistence.insert_evidence(
        _db_path(request),
        kind=envelope.kind,
        origin_node_id=canonical["origin_node_id"],
        payload=canonical,
    )
    return IngestResponse(stored_id=stored_id, kind=envelope.kind)


# ---------------------------------------------------------------------------
# GET /policies/{rhizome_id}
# ---------------------------------------------------------------------------

@router.get("/policies/{rhizome_id}")
def get_policy(rhizome_id: str, request: Request) -> dict[str, Any]:
    policy = persistence.get_active_policy(_db_path(request), rhizome_id)
    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"rhizome_id": rhizome_id, "reason": "no_active_policy"},
        )
    return policy


# ---------------------------------------------------------------------------
# GET /deltas/pending/{rhizome_id}
# ---------------------------------------------------------------------------

@router.get("/deltas/pending/{rhizome_id}")
def list_pending_deltas(
    rhizome_id: str, request: Request
) -> dict[str, Any]:
    deltas = persistence.list_deltas(
        _db_path(request), rhizome_id, persistence.DELTA_STATUS_PENDING
    )
    return {"rhizome_id": rhizome_id, "deltas": deltas, "count": len(deltas)}


# ---------------------------------------------------------------------------
# POST /deltas/propose
# ---------------------------------------------------------------------------

class DeltaProposeResponse(BaseModel):
    delta_id: str
    status: str
    reason: str | None = None
    violations: list[dict[str, Any]] | None = None


@router.post("/deltas/propose", status_code=status.HTTP_201_CREATED)
def propose_delta(
    payload: dict[str, Any], request: Request
) -> DeltaProposeResponse:
    # Paso 1: validar schema del delta.
    try:
        delta = PolicyDelta.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,  # Unprocessable Content. Constante renombrada en Starlette nuevo; usamos literal para evitar DeprecationWarning cross-version.
            detail={"kind": "policy_delta", "errors": exc.errors()},
        )

    db = _db_path(request)

    # Paso 2: la policy base debe existir y no haber expirado. Sin base no se
    # puede proyectar el delta, asi que no se puede evaluar §30.
    active = persistence.get_active_policy(db, delta.target_node_id)
    if active is None or active["policy_id"] != delta.base_policy_id:
        detail = {
            "delta_id": delta.delta_id,
            "reason": "base_policy_not_active",
            "base_policy_id": delta.base_policy_id,
            "active_policy_id": active["policy_id"] if active else None,
        }
        # Persistimos como rejected para auditoria antes de devolver error.
        persistence.insert_delta(
            db,
            delta=delta.model_dump(mode="json"),
            status=persistence.DELTA_STATUS_REJECTED,
            reason="base_policy_not_active",
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=detail
        )

    # Paso 3: proyectar delta sobre base y validar §30.
    try:
        base_packet = PolicyPacket.model_validate(active)
        violations = safety_rules.check_delta_against_base(
            delta, base_packet
        )
    except ValidationError as exc:
        # Proyeccion invalida a nivel de schema (ej: target_pct < min_pct tras
        # el patch). Tratamos como violacion "suave" del contrato.
        persistence.insert_delta(
            db,
            delta=delta.model_dump(mode="json"),
            status=persistence.DELTA_STATUS_REJECTED,
            reason="projection_invalid_schema",
        )
        raise HTTPException(
            status_code=422,  # Unprocessable Content. Constante renombrada en Starlette nuevo; usamos literal para evitar DeprecationWarning cross-version.
            detail={
                "delta_id": delta.delta_id,
                "reason": "projection_invalid_schema",
                "errors": exc.errors(),
            },
        )

    if violations:
        violation_dicts = [v.to_dict() for v in violations]
        persistence.insert_delta(
            db,
            delta=delta.model_dump(mode="json"),
            status=persistence.DELTA_STATUS_REJECTED,
            reason=safety_rules.REASON_VIOLATES_SAFETY_RULE,
        )
        # Rastro auditable del intento (Gap 4: no usamos ContradictionAlert).
        persistence.append_decision_log(
            db,
            origin_node_id=delta.origin_node_id,
            action="blocked_by_safety",
            payload={
                "attempted_delta": delta.model_dump(mode="json"),
                "violations": violation_dicts,
            },
        )
        raise HTTPException(
            status_code=422,  # Unprocessable Content. Constante renombrada en Starlette nuevo; usamos literal para evitar DeprecationWarning cross-version.
            detail={
                "delta_id": delta.delta_id,
                "reason": safety_rules.REASON_VIOLATES_SAFETY_RULE,
                "violations": violation_dicts,
            },
        )

    # Paso 4: delta valido. Persistimos como validated.
    persistence.insert_delta(
        db,
        delta=delta.model_dump(mode="json"),
        status=persistence.DELTA_STATUS_VALIDATED,
        reason=None,
    )
    return DeltaProposeResponse(
        delta_id=delta.delta_id,
        status=persistence.DELTA_STATUS_VALIDATED,
    )
