"""Tests de POST /ingest — acepta los 4 tipos de evidencia, 422 en invalidos."""

from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

_KIND_BY_FIXTURE = {
    "rhizome_snapshot": "rhizome_snapshot",
    "decision_receipt": "decision_receipt",
    "weather_packet": "weather_packet",
    "contradiction_alert": "contradiction_alert",
}


@pytest.mark.parametrize("fixture_name,kind", list(_KIND_BY_FIXTURE.items()))
def test_ingest_accepts_canonical_fixtures(
    meristem_client: TestClient,
    canonical_examples,
    fixture_name: str,
    kind: str,
) -> None:
    """Criterio #28: un test por schema verificando que `/ingest` las acepta.

    La lista cubre los 4 tipos que /ingest debe consumir segun el spec.
    PolicyPacket y PolicyDelta no entran por /ingest: son salidas de Meristem
    (policies) o inputs de /deltas/propose (deltas). Se testean aparte.
    """
    examples = canonical_examples()
    payload = examples[fixture_name]

    response = meristem_client.post(
        "/ingest", json={"kind": kind, "payload": payload}
    )
    assert response.status_code == 202, response.text
    body = response.json()
    assert body["kind"] == kind
    assert isinstance(body["stored_id"], int)
    assert body["stored_id"] > 0


def test_ingest_rejects_unknown_kind(meristem_client: TestClient) -> None:
    response = meristem_client.post(
        "/ingest", json={"kind": "unknown_kind", "payload": {}}
    )
    # Literal fuera de rango => el envelope no valida => 422.
    assert response.status_code == 422


def test_ingest_rejects_invalid_payload(
    meristem_client: TestClient, canonical_examples
) -> None:
    """Payload del kind correcto pero con campos invalidos => 422."""
    bad = deepcopy(canonical_examples()["rhizome_snapshot"])
    # Rompemos un campo requerido (origin_node_id vacio).
    bad["origin_node_id"] = ""

    response = meristem_client.post(
        "/ingest", json={"kind": "rhizome_snapshot", "payload": bad}
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["kind"] == "rhizome_snapshot"
    assert "errors" in detail


def test_ingest_persists_to_sqlite(
    meristem_client: TestClient,
    meristem_settings,
    canonical_examples,
) -> None:
    """Post un snapshot y verifica que aparece en la tabla `evidence`."""
    import sqlite3

    payload = canonical_examples()["rhizome_snapshot"]
    meristem_client.post(
        "/ingest", json={"kind": "rhizome_snapshot", "payload": payload}
    )

    with sqlite3.connect(meristem_settings.db_path) as conn:
        rows = list(
            conn.execute(
                "SELECT kind, origin_node_id FROM evidence"
            )
        )
    assert len(rows) == 1
    assert rows[0] == ("rhizome_snapshot", payload["origin_node_id"])
