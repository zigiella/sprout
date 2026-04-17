"""Tests negativos de validacion para reglas duras de los schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from schemas import ContradictionAlert, DecisionReceipt, PolicyDelta, PolicyPacket, RhizomeSnapshot, WeatherPacket
from schemas.tests.factories import (
    contradiction_alert_example,
    decision_receipt_example,
    policy_delta_example,
    policy_packet_example,
    rhizome_snapshot_example,
    weather_packet_example,
)


def test_rhizome_snapshot_rejects_percent_out_of_range() -> None:
    payload = rhizome_snapshot_example()
    payload["sensors"]["soil_moisture_a_pct"] = 120.0

    with pytest.raises(ValidationError):
        RhizomeSnapshot.model_validate(payload)


def test_rhizome_snapshot_rejects_cpu_temp_out_of_range() -> None:
    payload = rhizome_snapshot_example()
    payload["health"]["cpu_temp_c"] = 140.0

    with pytest.raises(ValidationError):
        RhizomeSnapshot.model_validate(payload)


def test_policy_packet_rejects_invalid_window() -> None:
    payload = policy_packet_example()
    payload["rules"]["watering_window"]["end_hour_local"] = 5

    with pytest.raises(ValidationError):
        PolicyPacket.model_validate(payload)


def test_policy_packet_rejects_expired_policy() -> None:
    payload = policy_packet_example()
    payload["valid_until"] = "2026-04-16T08:00:00Z"

    with pytest.raises(ValidationError):
        PolicyPacket.model_validate(payload)


def test_policy_packet_rejects_tank_minimum_below_hard_floor() -> None:
    payload = policy_packet_example()
    payload["rules"]["tank_minimum_pct"] = 5.0

    with pytest.raises(ValidationError):
        PolicyPacket.model_validate(payload)


def test_policy_delta_requires_base_policy_id() -> None:
    payload = policy_delta_example()
    payload["base_policy_id"] = "   "

    with pytest.raises(ValidationError):
        PolicyDelta.model_validate(payload)


def test_policy_delta_rejects_unknown_path() -> None:
    payload = policy_delta_example()
    payload["patches"][0]["path"] = "rules.unknown_field"

    with pytest.raises(ValidationError):
        PolicyDelta.model_validate(payload)


def test_policy_delta_rejects_remove_with_value() -> None:
    payload = policy_delta_example()
    payload["patches"][0] = {"op": "remove", "path": "notes", "value": "sobrante"}

    with pytest.raises(ValidationError):
        PolicyDelta.model_validate(payload)


def test_weather_packet_provenance_is_strict_enum() -> None:
    payload = weather_packet_example()
    payload["provenance"] = "voice_note"

    with pytest.raises(ValidationError):
        WeatherPacket.model_validate(payload)


def test_weather_packet_requires_observed_not_future() -> None:
    payload = weather_packet_example()
    payload["observed_at"] = "2026-04-16T12:16:00Z"

    with pytest.raises(ValidationError):
        WeatherPacket.model_validate(payload)


def test_weather_packet_local_station_requires_matching_origin() -> None:
    payload = weather_packet_example()
    payload["provenance"] = "local_station"

    with pytest.raises(ValidationError):
        WeatherPacket.model_validate(payload)


def test_contradiction_alert_requires_evidence_shape() -> None:
    payload = contradiction_alert_example()
    del payload["evidence"]["vision_reading"]

    with pytest.raises(ValidationError):
        ContradictionAlert.model_validate(payload)


def test_contradiction_alert_critical_requires_blocking_action() -> None:
    payload = contradiction_alert_example()
    payload["severity"] = "critical"
    payload["recommended_action"] = "continue_with_caution"

    with pytest.raises(ValidationError):
        ContradictionAlert.model_validate(payload)


def test_contradiction_alert_requires_future_expiry() -> None:
    payload = contradiction_alert_example()
    payload["expires_at"] = "2026-04-16T13:00:00Z"

    with pytest.raises(ValidationError):
        ContradictionAlert.model_validate(payload)


def test_decision_receipt_rejects_long_rationale_short() -> None:
    payload = decision_receipt_example()
    payload["rationale_short"] = "x" * 181

    with pytest.raises(ValidationError):
        DecisionReceipt.model_validate(payload)


def test_decision_receipt_requires_execution_details_when_executed() -> None:
    payload = decision_receipt_example()
    payload["execution_details"] = None

    with pytest.raises(ValidationError):
        DecisionReceipt.model_validate(payload)


def test_decision_receipt_rejects_blocked_reason_when_executed() -> None:
    payload = decision_receipt_example()
    payload["blocked_reason"] = "no deberia existir"

    with pytest.raises(ValidationError):
        DecisionReceipt.model_validate(payload)


def test_decision_receipt_requires_blocked_reason_when_not_executed() -> None:
    payload = decision_receipt_example()
    payload["executed"] = False
    payload["execution_details"] = None
    payload["blocked_reason"] = ""

    with pytest.raises(ValidationError):
        DecisionReceipt.model_validate(payload)


def test_decision_receipt_requires_action_params_per_action() -> None:
    payload = decision_receipt_example()
    payload["action"] = "DEFER"
    payload["action_params"] = {"reason": "viento"}
    payload["executed"] = False
    payload["execution_details"] = None
    payload["blocked_reason"] = "deferred"

    with pytest.raises(ValidationError):
        DecisionReceipt.model_validate(payload)
