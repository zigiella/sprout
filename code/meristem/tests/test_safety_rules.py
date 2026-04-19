"""Unit tests del validador pre-emit de §30.

Cada test crea un PolicyPacket via el builder canonico y muta el campo bajo
test. Mantener el builder como baseline evita divergencia con los fixtures.
"""

from __future__ import annotations

from copy import deepcopy

import pytest
from schemas import PolicyDelta, PolicyPacket
from schemas.examples.builders import (
    policy_delta_example,
    policy_packet_example,
)

from src import safety_rules
from src.safety_rules import (
    FIRMWARE_MAX_WATERING_DURATION_S,
    FIRMWARE_TANK_MINIMUM_PCT,
    REASON_VIOLATES_SAFETY_RULE,
)


def _packet(overrides_rules: dict | None = None) -> PolicyPacket:
    data = deepcopy(policy_packet_example())
    if overrides_rules:
        data["rules"].update(overrides_rules)
    return PolicyPacket.model_validate(data)


def test_canonical_packet_passes() -> None:
    """El fixture canonico debe pasar §30 tras el fix de Gap 1 (fixture a 20%)."""
    violations = safety_rules.check_policy_packet(_packet())
    assert violations == []


def test_firmware_limits_are_documented() -> None:
    """Sanity: las constantes espejo de §30 no se mueven sin intencion."""
    assert FIRMWARE_MAX_WATERING_DURATION_S == 60
    assert FIRMWARE_TANK_MINIMUM_PCT == 20.0
    assert REASON_VIOLATES_SAFETY_RULE == "violates_safety_rule"


def test_duration_over_60_blocks() -> None:
    packet = _packet({"max_watering_duration_s": 120})
    violations = safety_rules.check_policy_packet(packet)
    assert len(violations) == 1
    v = violations[0]
    assert v.rule == "rules.max_watering_duration_s"
    assert v.proposed_value == 120
    assert v.firmware_limit == 60


def test_duration_exactly_60_passes() -> None:
    # §30.1: "Duracion maxima: 60 s". Es inclusivo.
    packet = _packet({"max_watering_duration_s": 60})
    assert safety_rules.check_policy_packet(packet) == []


def test_tank_below_20_blocks() -> None:
    packet = _packet({"tank_minimum_pct": 15.0})
    violations = safety_rules.check_policy_packet(packet)
    assert len(violations) == 1
    assert violations[0].rule == "rules.tank_minimum_pct"
    assert violations[0].proposed_value == 15.0
    assert violations[0].firmware_limit == 20.0


def test_tank_exactly_20_passes() -> None:
    packet = _packet({"tank_minimum_pct": 20.0})
    assert safety_rules.check_policy_packet(packet) == []


def test_multiple_violations_reported_together() -> None:
    packet = _packet(
        {"max_watering_duration_s": 90, "tank_minimum_pct": 10.0}
    )
    violations = safety_rules.check_policy_packet(packet)
    rules = {v.rule for v in violations}
    assert rules == {
        "rules.max_watering_duration_s",
        "rules.tank_minimum_pct",
    }


def test_project_delta_applies_replace() -> None:
    base = _packet()
    delta_data = deepcopy(policy_delta_example())
    delta_data["base_policy_id"] = base.policy_id
    delta = PolicyDelta.model_validate(delta_data)

    projected = safety_rules.project_delta(delta, base)
    # El fixture replace parcel_b.min_pct a 32.0 y budget a 10.0.
    assert projected.rules.soil_moisture_thresholds.parcel_b.min_pct == 32.0
    assert projected.rules.daily_water_budget_liters == 10.0
    # Y base no se muta.
    assert base.rules.daily_water_budget_liters == 8.0


def test_project_delta_add_appends_to_list() -> None:
    base = _packet()
    delta_data = deepcopy(policy_delta_example())
    delta_data["base_policy_id"] = base.policy_id
    delta = PolicyDelta.model_validate(delta_data)

    projected = safety_rules.project_delta(delta, base)
    triggers = projected.rules.conservative_triggers
    # El fixture add anade "humidity_below_25_forecast" a la lista existente.
    assert "humidity_below_25_forecast" in triggers
    # Y los anteriores siguen ahi.
    assert "tank_level_below_30" in triggers


def test_delta_that_would_violate_30_is_caught() -> None:
    """Criterio de aceptacion #28: delta con max_watering_duration_s=120
    debe detectarse via check_delta_against_base."""
    base = _packet()
    delta_data = deepcopy(policy_delta_example())
    delta_data["base_policy_id"] = base.policy_id
    delta_data["patches"] = [
        {
            "op": "replace",
            "path": "rules.max_watering_duration_s",
            "value": 120,
        }
    ]
    delta = PolicyDelta.model_validate(delta_data)

    violations = safety_rules.check_delta_against_base(delta, base)
    assert len(violations) == 1
    assert violations[0].rule == "rules.max_watering_duration_s"
    assert violations[0].proposed_value == 120


def test_delta_that_brings_tank_below_20_is_caught() -> None:
    base = _packet()
    delta_data = deepcopy(policy_delta_example())
    delta_data["base_policy_id"] = base.policy_id
    delta_data["patches"] = [
        {"op": "replace", "path": "rules.tank_minimum_pct", "value": 12.0}
    ]
    delta = PolicyDelta.model_validate(delta_data)

    violations = safety_rules.check_delta_against_base(delta, base)
    assert len(violations) == 1
    assert violations[0].rule == "rules.tank_minimum_pct"


def test_delta_remove_on_scalar_clears_via_model_revalidation() -> None:
    """Un `remove` sobre un campo requerido rompe el schema al re-validar.

    Esto es esperable: project_delta re-valida la proyeccion con pydantic,
    asi que un remove mal intencionado levanta ValidationError antes incluso
    de llegar al validador §30.
    """
    from pydantic import ValidationError

    base = _packet()
    delta_data = deepcopy(policy_delta_example())
    delta_data["base_policy_id"] = base.policy_id
    delta_data["patches"] = [
        {"op": "remove", "path": "rules.max_watering_duration_s"}
    ]
    delta = PolicyDelta.model_validate(delta_data)

    with pytest.raises(ValidationError):
        safety_rules.project_delta(delta, base)
