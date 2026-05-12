"""Tests de los endpoints HTTP fallback para Pollen (Variante D-bis, día 26).

Para Floema Android sin WebSocket persistente. Cada endpoint HTTP es
equivalente al evento WebSocket homónimo. Estos tests no usan
TestClient.websocket_connect — son POSTs HTTP normales.

Cubre:
- hello → meristem_ready con policies_ready_for_pickup
- /health refleja connected + mode=http tras hello
- heartbeat refresca last_heartbeat
- 409 si heartbeat/bundles-pushed/policies-pulled sin hello previo
- bundles-pushed y policies-pulled ack
- goodbye limpia el estado
- hello duplicado es idempotente (refresca, no error)
"""
from __future__ import annotations

import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    """Cliente con DB temporal aislada y manager reset."""
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test_meristem.db")
    monkeypatch.setenv("MERISTEM_DB_PATH", db_path)
    from src.ws_manager import manager
    manager._websocket = None
    manager._pollen_id = None
    manager._app_version = None
    manager._connected_at = None
    manager._last_heartbeat = None
    from importlib import reload
    from src import persistence
    reload(persistence)
    persistence.init_db(db_path)
    from src import main as main_module
    reload(main_module)
    return TestClient(main_module.app)


# ---------------------------------------------------------------------------
# hello + ready
# ---------------------------------------------------------------------------


def test_hello_returns_meristem_ready_payload(client):
    """POST /pollen/hello devuelve meristem_ready con pickup list."""
    r = client.post("/pollen/hello", json={
        "pollen_id": "pollen_test_http_01",
        "app_version": "0.1.0",
        "bundles_pending_count": 0,
        "policies_to_pickup_target_ids": [],
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert "meristem_id" in body
    assert body["version"] == "0.1.0"
    assert body["policies_ready_for_pickup"] == []  # no hay policies seedeadas


def test_hello_returns_pickup_when_policies_exist(client):
    """Si hay policies para los target_ids pedidos, vienen en pickup."""
    # Seedear 1 policy primero usando /visit con bundle real
    bundle = {
        "source_pollen_id": "pollen_seed",
        "target_rhizome_id": "rhizome_01",
        "active_policy_id": "pkt_baseline",
        "rhizome_snapshot": {
            "snapshot_id": "snap_x",
            "mode": "normal",
            "alert_latched": False,
            "pending_contradictions": [],
        },
        "decision_receipts": [],
        "validation_stamps": [],
    }
    r_visit = client.post("/visit", json=bundle)
    assert r_visit.status_code == 200

    r = client.post("/pollen/hello", json={
        "pollen_id": "pollen_test_http_01",
        "app_version": "0.1.0",
        "bundles_pending_count": 0,
        "policies_to_pickup_target_ids": ["rhizome_01"],
    })
    body = r.json()
    pickup = body["policies_ready_for_pickup"]
    assert len(pickup) == 1
    assert pickup[0]["target_node_id"] == "rhizome_01"
    assert pickup[0]["policy_id"].startswith("pkt_meristem_")


def test_health_reflects_http_mode_after_hello(client):
    """/health.pollen_connection muestra mode=http tras hello HTTP."""
    client.post("/pollen/hello", json={
        "pollen_id": "pollen_test_http_01",
        "app_version": "0.1.0",
        "bundles_pending_count": 0,
        "policies_to_pickup_target_ids": [],
    })
    h = client.get("/health").json()
    p = h["pollen_connection"]
    assert p["connected"] is True
    assert p["mode"] == "http"
    assert p["pollen_id"] == "pollen_test_http_01"
    assert p["app_version"] == "0.1.0"


def test_hello_is_idempotent(client):
    """Segundo hello con mismo pollen_id no rompe (refresca sesión)."""
    payload = {
        "pollen_id": "pollen_test_http_01",
        "app_version": "0.1.0",
        "bundles_pending_count": 0,
        "policies_to_pickup_target_ids": [],
    }
    r1 = client.post("/pollen/hello", json=payload)
    assert r1.status_code == 200
    r2 = client.post("/pollen/hello", json=payload)
    assert r2.status_code == 200  # no 409


# ---------------------------------------------------------------------------
# heartbeat
# ---------------------------------------------------------------------------


def test_heartbeat_409_without_hello(client):
    """POST /pollen/heartbeat sin hello previo → 409."""
    r = client.post("/pollen/heartbeat")
    assert r.status_code == 409


def test_heartbeat_after_hello_ok(client):
    """POST /pollen/heartbeat tras hello → 200 online:true."""
    client.post("/pollen/hello", json={
        "pollen_id": "pollen_test_http_01",
        "app_version": "0.1.0",
        "bundles_pending_count": 0,
        "policies_to_pickup_target_ids": [],
    })
    r = client.post("/pollen/heartbeat")
    assert r.status_code == 200
    assert r.json() == {"online": True}


# ---------------------------------------------------------------------------
# bundles-pushed / policies-pulled (ack)
# ---------------------------------------------------------------------------


def test_bundles_pushed_409_without_hello(client):
    r = client.post("/pollen/bundles-pushed", json={
        "count": 0, "bundle_ids": [],
    })
    assert r.status_code == 409


def test_bundles_pushed_ack_after_hello(client):
    client.post("/pollen/hello", json={
        "pollen_id": "pollen_test_http_01",
        "app_version": "0.1.0",
        "bundles_pending_count": 0,
        "policies_to_pickup_target_ids": [],
    })
    r = client.post("/pollen/bundles-pushed", json={
        "count": 2, "bundle_ids": ["b_aaa", "b_bbb"],
    })
    assert r.status_code == 200
    assert r.json() == {"status": "ack"}


def test_policies_pulled_409_without_hello(client):
    r = client.post("/pollen/policies-pulled", json={
        "count": 0, "policy_ids": [],
    })
    assert r.status_code == 409


def test_policies_pulled_ack_after_hello(client):
    client.post("/pollen/hello", json={
        "pollen_id": "pollen_test_http_01",
        "app_version": "0.1.0",
        "bundles_pending_count": 0,
        "policies_to_pickup_target_ids": [],
    })
    r = client.post("/pollen/policies-pulled", json={
        "count": 1, "policy_ids": ["pkt_demo_xyz"],
    })
    assert r.status_code == 200
    assert r.json() == {"status": "ack"}


# ---------------------------------------------------------------------------
# goodbye
# ---------------------------------------------------------------------------


def test_goodbye_cleans_state(client):
    """POST /pollen/goodbye desconecta y /health refleja mode=disconnected."""
    client.post("/pollen/hello", json={
        "pollen_id": "pollen_test_http_01",
        "app_version": "0.1.0",
        "bundles_pending_count": 0,
        "policies_to_pickup_target_ids": [],
    })
    r = client.post("/pollen/goodbye")
    assert r.status_code == 200
    assert r.json() == {"status": "disconnected"}

    h = client.get("/health").json()
    p = h["pollen_connection"]
    assert p["connected"] is False
    assert p["mode"] == "disconnected"


# ---------------------------------------------------------------------------
# Persistencia de eventos (audit trail)
# ---------------------------------------------------------------------------


def test_hello_persists_event_in_audit_log(client):
    """log_ws_event registra pollen_hello incluso en modo HTTP (mismo audit)."""
    client.post("/pollen/hello", json={
        "pollen_id": "pollen_test_http_01",
        "app_version": "0.1.0",
        "bundles_pending_count": 0,
        "policies_to_pickup_target_ids": [],
    })
    h = client.get("/health").json()
    counts = h["ws_events_by_type"]
    assert counts.get("pollen_hello", 0) >= 1
    assert counts.get("meristem_ready", 0) >= 1
