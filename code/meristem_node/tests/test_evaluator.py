"""Tests del Evaluator — las 4 reglas determinísticas + casos borde.

Cada test cubre un caso de la mini-batería v0 acordada con Xilema:
- M1: bundle limpio (camino feliz) → CONFIRM_POLICY
- M2: bundle con disputas → CONSERVATIVE_POLICY
- M3: bundle con emergencia → ALERT_POLICY
- M4: bundle con hard limit malicioso → REFUSE (HARD_LIMIT_DOMAIN)
- M5: bundle con jurisdicción Pollen → REFUSE (JURISDICTION_POLLEN)

Los bundles ejemplo viven en `code/meristem_node/examples/` y se usan
también para demo en directo y para el cenital cartoon de Corola.

Ejecutar:
    cd code/meristem_node
    pip install pytest
    python -m pytest tests/ -v
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.evaluator import (
    RC_HARD_LIMIT,
    RC_JURISDICTION_POLLEN,
    RC_LOW_CONFIDENCE,
    RC_PERSISTENT_EMERGENCY,
    RC_STABLE,
    evaluate,
)
from src.schemas import Action, Bundle


def _make_bundle(
    *,
    rhizome_snapshot: dict | None = None,
    decision_receipts: list[dict] | None = None,
    weather_digest: dict | None = None,
    validation_stamps: list[dict] | None = None,
) -> Bundle:
    """Helper para construir Bundle con defaults razonables."""
    return Bundle(
        source_pollen_id="pollen_test",
        target_rhizome_id="rhizome_01",
        active_policy_id="pkt_old",
        rhizome_snapshot=rhizome_snapshot or {
            "snapshot_id": "snap_test",
            "mode": "normal",
            "alert_latched": False,
            "pending_contradictions": [],
        },
        decision_receipts=decision_receipts or [],
        weather_digest=weather_digest,
        validation_stamps=validation_stamps or [],
    )


# ---------------------------------------------------------------------------
# M1: bundle limpio → CONFIRM_POLICY
# ---------------------------------------------------------------------------


def test_M1_bundle_limpio_camino_feliz() -> None:
    """Bundle sin emergencias, sin disputas, alta confianza → CONFIRM."""
    bundle = _make_bundle(
        decision_receipts=[
            {"action": "WATER_A", "confidence": 0.92},
            {"action": "WATER_B", "confidence": 0.88},
            {"action": "SKIP", "confidence": 0.95},
        ],
        weather_digest={"isStale": False, "summary": "soleado moderado"},
    )

    result = evaluate(bundle)

    assert result.action == Action.CONFIRM_POLICY
    assert result.reason_code == RC_STABLE
    assert result.suggested_mode == "normal"
    assert "limpio" in result.rationale_seed.lower() or "estable" in result.rationale_seed.lower()


# ---------------------------------------------------------------------------
# M2: bundle con disputas → CONSERVATIVE_POLICY
# ---------------------------------------------------------------------------


def test_M2_validation_stamp_disputed() -> None:
    """ValidationStamp con status=disputed → CONSERVATIVE."""
    bundle = _make_bundle(
        decision_receipts=[
            {"action": "WATER_A", "confidence": 0.85},
        ],
        validation_stamps=[
            {
                "status": "disputed",
                "subject": "plot:A",
                "basis": ["sensor 26%", "operador parcela seca"],
            },
        ],
    )

    result = evaluate(bundle)

    assert result.action == Action.CONSERVATIVE_POLICY
    assert result.reason_code == RC_LOW_CONFIDENCE
    assert result.suggested_mode == "conservative"
    assert "soil_dry_threshold_pct_bump" in result.suggested_rules


def test_M2_bis_avg_confidence_baja() -> None:
    """Confianza media < 0.7 → CONSERVATIVE."""
    bundle = _make_bundle(
        decision_receipts=[
            {"action": "WATER_A", "confidence": 0.5},
            {"action": "WATER_B", "confidence": 0.55},
            {"action": "SKIP", "confidence": 0.6},
        ],
    )

    result = evaluate(bundle)

    assert result.action == Action.CONSERVATIVE_POLICY
    assert result.reason_code == RC_LOW_CONFIDENCE


def test_M2_ter_pending_contradictions() -> None:
    """snapshot.pending_contradictions no vacío → CONSERVATIVE."""
    bundle = _make_bundle(
        rhizome_snapshot={
            "snapshot_id": "snap_test",
            "mode": "normal",
            "alert_latched": False,
            "pending_contradictions": ["sensor_vs_vision"],
        },
        decision_receipts=[{"action": "WATER_A", "confidence": 0.9}],
    )

    result = evaluate(bundle)

    assert result.action == Action.CONSERVATIVE_POLICY


# ---------------------------------------------------------------------------
# M3: bundle con emergencia → ALERT_POLICY
# ---------------------------------------------------------------------------


def test_M3_alert_latched() -> None:
    """snapshot.mode=alert + alert_latched=True → ALERT_POLICY."""
    bundle = _make_bundle(
        rhizome_snapshot={
            "snapshot_id": "snap_alert",
            "mode": "alert",
            "alert_latched": True,
            "pending_contradictions": [],
        },
        decision_receipts=[
            {"action": "BLOCK", "confidence": 1.0, "blocked_reason": "TANK_LOW"},
        ],
    )

    result = evaluate(bundle)

    assert result.action == Action.ALERT_POLICY
    assert result.reason_code == RC_PERSISTENT_EMERGENCY
    assert result.suggested_mode == "alert"
    assert result.suggested_rules.get("alert_until_human_review") is True


def test_M3_bis_blocks_consecutivos() -> None:
    """N receipts BLOCK consecutivos → ALERT_POLICY (sin alert_latched)."""
    bundle = _make_bundle(
        rhizome_snapshot={
            "snapshot_id": "snap_test",
            "mode": "normal",
            "alert_latched": False,
            "pending_contradictions": [],
        },
        decision_receipts=[
            {"action": "BLOCK", "confidence": 1.0, "blocked_reason": "JETSON_HEARTBEAT_LOST"},
            {"action": "BLOCK", "confidence": 1.0, "blocked_reason": "JETSON_HEARTBEAT_LOST"},
            {"action": "BLOCK", "confidence": 1.0, "blocked_reason": "TANK_LOW"},
        ],
    )

    result = evaluate(bundle)

    assert result.action == Action.ALERT_POLICY


# ---------------------------------------------------------------------------
# M4: bundle con hard limit malicioso → REFUSE (HARD_LIMIT_DOMAIN)
# ---------------------------------------------------------------------------


def test_M4_hard_limit_relax_via_visit_amendment() -> None:
    """validation_stamp.visit_amendment intenta bajar tank_minimum_pct."""
    bundle = _make_bundle(
        validation_stamps=[
            {
                "status": "confirmed",
                "subject": "plot:A",
                "visit_amendment": {
                    "policy_override": "tank_minimum_pct=10",
                    "duration_h": 6,
                },
            },
        ],
    )

    result = evaluate(bundle)

    assert result.action == Action.REFUSE
    assert result.reason_code == RC_HARD_LIMIT
    assert "hard limit" in result.rationale_seed.lower() or "frontera fisica" in result.rationale_seed.lower()


def test_M4_bis_hard_limit_via_camelCase() -> None:
    """Verifica que también detectamos camelCase (visitAmendment / policyOverride)."""
    bundle = _make_bundle(
        validation_stamps=[
            {
                "status": "confirmed",
                "visitAmendment": {
                    "policyOverride": "tank_minimum_pct=5",
                    "durationH": 6,
                },
            },
        ],
    )

    result = evaluate(bundle)

    assert result.action == Action.REFUSE
    assert result.reason_code == RC_HARD_LIMIT


def test_M4_ter_max_seconds_intent_increase() -> None:
    """Intentar SUBIR max_seconds_per_event > 180 también es relax."""
    bundle = _make_bundle(
        validation_stamps=[
            {
                "status": "confirmed",
                "visit_amendment": {"policy_override": "max_seconds_per_event=300"},
            },
        ],
    )

    result = evaluate(bundle)

    assert result.action == Action.REFUSE
    assert result.reason_code == RC_HARD_LIMIT


# ---------------------------------------------------------------------------
# M5: bundle con jurisdicción Pollen → REFUSE (JURISDICTION_POLLEN)
# ---------------------------------------------------------------------------


def test_M5_operator_request_en_snapshot() -> None:
    """snapshot incluye operator_request → es jurisdicción Pollen vía MissionPatch."""
    bundle = _make_bundle(
        rhizome_snapshot={
            "snapshot_id": "snap_test",
            "mode": "normal",
            "alert_latched": False,
            "pending_contradictions": [],
            "operator_request": "regar 30s extra hoy plot A",
        },
    )

    result = evaluate(bundle)

    assert result.action == Action.REFUSE
    assert result.reason_code == RC_JURISDICTION_POLLEN
    assert "pollen" in result.rationale_seed.lower()


def test_M5_bis_decision_receipt_con_tag_operator_override() -> None:
    """receipt con tag operator_override → idem JURISDICTION_POLLEN."""
    bundle = _make_bundle(
        decision_receipts=[
            {"action": "WATER_A", "confidence": 0.9, "tags": ["operator_override"]},
        ],
    )

    result = evaluate(bundle)

    assert result.action == Action.REFUSE
    assert result.reason_code == RC_JURISDICTION_POLLEN


# ---------------------------------------------------------------------------
# Casos borde — precedencia de reglas
# ---------------------------------------------------------------------------


def test_precedencia_REFUSE_corta_antes_de_ALERT() -> None:
    """Si hay alert_latched + hard_limit_relax, REFUSE corta primero."""
    bundle = _make_bundle(
        rhizome_snapshot={
            "snapshot_id": "snap_alert",
            "mode": "alert",
            "alert_latched": True,
            "pending_contradictions": [],
        },
        validation_stamps=[
            {
                "status": "confirmed",
                "visit_amendment": {"policy_override": "tank_minimum_pct=10"},
            },
        ],
    )

    result = evaluate(bundle)

    # REFUSE tiene prioridad sobre ALERT
    assert result.action == Action.REFUSE
    assert result.reason_code == RC_HARD_LIMIT


def test_precedencia_ALERT_corta_antes_de_CONSERVATIVE() -> None:
    """Emergencia + disputas → ALERT (no CONSERVATIVE)."""
    bundle = _make_bundle(
        rhizome_snapshot={
            "snapshot_id": "snap_alert",
            "mode": "alert",
            "alert_latched": True,
            "pending_contradictions": ["sensor_vs_vision"],  # también disputaría
        },
        validation_stamps=[{"status": "disputed", "basis": ["..."]}],
    )

    result = evaluate(bundle)

    assert result.action == Action.ALERT_POLICY
    assert result.reason_code == RC_PERSISTENT_EMERGENCY
