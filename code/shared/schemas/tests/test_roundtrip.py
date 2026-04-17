"""Tests de round-trip para los schemas compartidos."""

from __future__ import annotations

import pytest

from schemas import (
    ContradictionAlert,
    DecisionReceipt,
    PolicyDelta,
    PolicyPacket,
    RhizomeSnapshot,
    WeatherPacket,
)
from schemas.tests.factories import canonical_examples

MODEL_BY_NAME = {
    "rhizome_snapshot": RhizomeSnapshot,
    "policy_packet": PolicyPacket,
    "policy_delta": PolicyDelta,
    "weather_packet": WeatherPacket,
    "contradiction_alert": ContradictionAlert,
    "decision_receipt": DecisionReceipt,
}


@pytest.mark.parametrize("name", sorted(MODEL_BY_NAME))
def test_canonical_examples_roundtrip(name: str) -> None:
    model_cls = MODEL_BY_NAME[name]
    payload = canonical_examples()[name]

    parsed = model_cls.model_validate(payload)
    dumped = parsed.model_dump(mode="json")
    reparsed = model_cls.model_validate(dumped)

    assert reparsed.model_dump(mode="json") == dumped
