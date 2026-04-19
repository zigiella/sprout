"""Tests de GET /policies/{rhizome_id}."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from src import persistence


def test_get_policy_404_when_none(meristem_client: TestClient) -> None:
    response = meristem_client.get("/policies/rhizome_01")
    assert response.status_code == 404
    assert response.json()["detail"]["reason"] == "no_active_policy"


def test_get_policy_returns_active(
    meristem_client: TestClient, meristem_settings, canonical_examples
) -> None:
    packet = canonical_examples()["policy_packet"]
    # Aseguramos que la policy no este expirada.
    future = (datetime.now(timezone.utc) + timedelta(hours=6)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    packet = deepcopy(packet)
    packet["valid_until"] = future
    persistence.upsert_policy(meristem_settings.db_path, packet)

    response = meristem_client.get("/policies/rhizome_01")
    assert response.status_code == 200
    assert response.json()["policy_id"] == packet["policy_id"]


def test_get_policy_ignores_expired(
    meristem_client: TestClient, meristem_settings, canonical_examples
) -> None:
    packet = deepcopy(canonical_examples()["policy_packet"])
    # valid_until en el pasado.
    past = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    packet["valid_until"] = past
    persistence.upsert_policy(meristem_settings.db_path, packet)

    response = meristem_client.get("/policies/rhizome_01")
    assert response.status_code == 404
