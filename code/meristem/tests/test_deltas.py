"""Tests de /deltas/pending y /deltas/propose."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from src import persistence


def _future_zulu(hours: int = 6) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def _install_active_policy(db_path: str, canonical_examples) -> dict:
    packet = deepcopy(canonical_examples()["policy_packet"])
    packet["valid_until"] = _future_zulu()
    persistence.upsert_policy(db_path, packet)
    return packet


def _delta_for(canonical_examples, base_policy_id: str) -> dict:
    delta = deepcopy(canonical_examples()["policy_delta"])
    delta["base_policy_id"] = base_policy_id
    return delta


def test_pending_empty_by_default(meristem_client: TestClient) -> None:
    response = meristem_client.get("/deltas/pending/rhizome_01")
    assert response.status_code == 200
    body = response.json()
    assert body == {"rhizome_id": "rhizome_01", "deltas": [], "count": 0}


def test_pending_lists_only_pending(
    meristem_client: TestClient, meristem_settings, canonical_examples
) -> None:
    """Sembramos tres deltas con status distinto y solo uno pending debe salir."""
    db = meristem_settings.db_path
    delta = deepcopy(canonical_examples()["policy_delta"])

    for idx, status in enumerate(
        [
            persistence.DELTA_STATUS_PENDING,
            persistence.DELTA_STATUS_VALIDATED,
            persistence.DELTA_STATUS_REJECTED,
        ]
    ):
        d = deepcopy(delta)
        d["delta_id"] = f"delta_test_{idx}"
        persistence.insert_delta(db, d, status=status)

    response = meristem_client.get("/deltas/pending/rhizome_01")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["deltas"][0]["delta_id"] == "delta_test_0"


def test_propose_validates_and_persists(
    meristem_client: TestClient, meristem_settings, canonical_examples
) -> None:
    active = _install_active_policy(meristem_settings.db_path, canonical_examples)
    delta = _delta_for(canonical_examples, active["policy_id"])

    response = meristem_client.post("/deltas/propose", json=delta)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["delta_id"] == delta["delta_id"]
    assert body["status"] == persistence.DELTA_STATUS_VALIDATED
    assert body["reason"] is None


def test_propose_rejects_when_base_policy_missing(
    meristem_client: TestClient, canonical_examples
) -> None:
    delta = _delta_for(canonical_examples, "pkt_does_not_exist_1234")

    response = meristem_client.post("/deltas/propose", json=delta)
    assert response.status_code == 409
    assert response.json()["detail"]["reason"] == "base_policy_not_active"


def test_propose_rejects_when_delta_violates_30(
    meristem_client: TestClient, meristem_settings, canonical_examples
) -> None:
    """Criterio #28: delta con max_watering_duration_s=120 => 422 con
    reason=violates_safety_rule."""
    active = _install_active_policy(meristem_settings.db_path, canonical_examples)
    delta = _delta_for(canonical_examples, active["policy_id"])
    delta["patches"] = [
        {
            "op": "replace",
            "path": "rules.max_watering_duration_s",
            "value": 120,
        }
    ]

    response = meristem_client.post("/deltas/propose", json=delta)
    assert response.status_code == 422, response.text
    detail = response.json()["detail"]
    assert detail["reason"] == "violates_safety_rule"
    assert len(detail["violations"]) == 1
    assert detail["violations"][0]["rule"] == "rules.max_watering_duration_s"
    assert detail["violations"][0]["proposed_value"] == 120
    assert detail["violations"][0]["firmware_limit"] == 60


def test_propose_rejects_delta_that_brings_tank_below_20(
    meristem_client: TestClient, meristem_settings, canonical_examples
) -> None:
    active = _install_active_policy(meristem_settings.db_path, canonical_examples)
    delta = _delta_for(canonical_examples, active["policy_id"])
    delta["patches"] = [
        {"op": "replace", "path": "rules.tank_minimum_pct", "value": 15.0}
    ]

    response = meristem_client.post("/deltas/propose", json=delta)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["reason"] == "violates_safety_rule"
    assert detail["violations"][0]["rule"] == "rules.tank_minimum_pct"


def test_rejected_delta_is_persisted_with_reason(
    meristem_client: TestClient, meristem_settings, canonical_examples
) -> None:
    """Un delta rechazado por §30 queda persistido con status=rejected y
    reason poblado, para auditoria."""
    import sqlite3

    active = _install_active_policy(meristem_settings.db_path, canonical_examples)
    delta = _delta_for(canonical_examples, active["policy_id"])
    delta["patches"] = [
        {
            "op": "replace",
            "path": "rules.max_watering_duration_s",
            "value": 120,
        }
    ]

    meristem_client.post("/deltas/propose", json=delta)

    with sqlite3.connect(meristem_settings.db_path) as conn:
        rows = list(
            conn.execute(
                "SELECT delta_id, status, reason FROM deltas"
            )
        )
    assert len(rows) == 1
    assert rows[0][1] == persistence.DELTA_STATUS_REJECTED
    assert rows[0][2] == "violates_safety_rule"


def test_rejected_delta_logs_blocked_attempt(
    meristem_client: TestClient, meristem_settings, canonical_examples
) -> None:
    """Gap 4: el intento bloqueado se persiste en decisions_log (no como
    ContradictionAlert)."""
    import sqlite3

    active = _install_active_policy(meristem_settings.db_path, canonical_examples)
    delta = _delta_for(canonical_examples, active["policy_id"])
    delta["patches"] = [
        {"op": "replace", "path": "rules.tank_minimum_pct", "value": 10.0}
    ]

    meristem_client.post("/deltas/propose", json=delta)

    with sqlite3.connect(meristem_settings.db_path) as conn:
        rows = list(
            conn.execute("SELECT action FROM decisions_log")
        )
    assert ("blocked_by_safety",) in rows
