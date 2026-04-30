"""Executable checks for Xilema's Rhizome->Meristem MVP handoff fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient
from schemas import DecisionReceipt, PolicyDelta, PolicyPacket, RhizomeSnapshot

from src import persistence, safety_rules

_EXAMPLES_DIR = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "rhizome_minimal_handoff"
)


def _load_json(name: str) -> dict:
    return json.loads((_EXAMPLES_DIR / name).read_text(encoding="utf-8"))


def test_handoff_fixtures_validate_against_current_schemas() -> None:
    policy = PolicyPacket.model_validate(_load_json("active_policy_seed.json"))
    snapshot_envelope = _load_json("ingest_rhizome_snapshot_tank_low.json")
    receipt_envelope = _load_json("ingest_decision_receipt_tank_low.json")
    delta = PolicyDelta.model_validate(
        _load_json("ra04_safety_downgrade_delta.json")
    )

    RhizomeSnapshot.model_validate(snapshot_envelope["payload"])
    DecisionReceipt.model_validate(receipt_envelope["payload"])

    assert policy.rules.tank_minimum_pct == 20.0
    assert delta.patches[0].path == "rules.tank_minimum_pct"
    assert delta.patches[0].value == 15.0


def test_ra04_handoff_delta_is_rejected_by_safety_rules() -> None:
    policy = PolicyPacket.model_validate(_load_json("active_policy_seed.json"))
    delta = PolicyDelta.model_validate(
        _load_json("ra04_safety_downgrade_delta.json")
    )

    violations = safety_rules.check_delta_against_base(delta, policy)

    assert len(violations) == 1
    assert violations[0].rule == "rules.tank_minimum_pct"
    assert violations[0].proposed_value == 15.0
    assert violations[0].firmware_limit == 20.0


def test_handoff_flow_against_meristem_http_api(
    meristem_client: TestClient, meristem_settings
) -> None:
    policy = _load_json("active_policy_seed.json")
    persistence.upsert_policy(meristem_settings.db_path, policy)

    for filename in (
        "ingest_rhizome_snapshot_tank_low.json",
        "ingest_decision_receipt_tank_low.json",
    ):
        response = meristem_client.post("/ingest", json=_load_json(filename))
        assert response.status_code == 202, response.text

    response = meristem_client.post(
        "/deltas/propose",
        json=_load_json("ra04_safety_downgrade_delta.json"),
    )

    assert response.status_code == 422, response.text
    detail = response.json()["detail"]
    assert detail["reason"] == "violates_safety_rule"
    assert detail["violations"][0]["rule"] == "rules.tank_minimum_pct"
