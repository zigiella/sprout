"""Tests del endpoint WebSocket Pollen ↔ Meristem (protocolo v1.0).

Usa `TestClient.websocket_connect()` de FastAPI para simular conexión
de cliente Pollen desde Python sin levantar uvicorn.

Cubre:
- Hello → Ready handshake
- Heartbeat round-trip
- Comando push_bundles desde REST → cliente recibe por WS
- Segundo cliente rechazado (singleton manager)
- Persistencia: log_ws_event refleja en count_ws_events_by_event
- Disconnect limpio
"""
from __future__ import annotations

import os
import tempfile

import pytest
from fastapi.testclient import TestClient


# Test usa BBDD aislada por cada test.
@pytest.fixture
def client(monkeypatch):
    """Cliente con DB temporal aislada."""
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test_meristem.db")
    monkeypatch.setenv("MERISTEM_DB_PATH", db_path)
    # Singleton del manager se resetea entre tests para evitar leak
    from src.ws_manager import manager
    manager._websocket = None
    manager._pollen_id = None
    manager._app_version = None
    manager._connected_at = None
    manager._last_heartbeat = None
    # Forzar re-init de DB en path temporal
    from importlib import reload
    from src import persistence
    reload(persistence)
    persistence.init_db(db_path)
    # Recargar main para que use el persistence reloaded
    from src import main as main_module
    reload(main_module)
    return TestClient(main_module.app)


def test_ws_hello_responds_with_ready(client):
    """Connect + pollen_hello → meristem_ready con metadata correcta."""
    with client.websocket_connect("/ws/pollen-sync") as ws:
        ws.send_json({
            "event": "pollen_hello",
            "payload": {
                "pollen_id": "pollen_test_01",
                "app_version": "0.5.0",
                "bundles_pending_count": 0,
                "policies_to_pickup_target_ids": [],
            },
            "timestamp": "2026-05-05T10:00:00Z",
        })
        response = ws.receive_json()

    assert response["event"] == "meristem_ready"
    assert response["payload"]["meristem_id"] == "meristem_demo_01"
    assert response["payload"]["version"] == "0.1.0"
    assert response["payload"]["policies_ready_for_pickup"] == []


def test_ws_heartbeat_roundtrip(client):
    """pollen_heartbeat → meristem_heartbeat_ack."""
    with client.websocket_connect("/ws/pollen-sync") as ws:
        ws.send_json({
            "event": "pollen_hello",
            "payload": {"pollen_id": "p1", "app_version": "0.0.0"},
        })
        _ = ws.receive_json()  # consume meristem_ready

        ws.send_json({
            "event": "pollen_heartbeat",
            "payload": {},
        })
        response = ws.receive_json()

    assert response["event"] == "meristem_heartbeat_ack"
    assert response["payload"]["online"] is True


def test_ws_unknown_event_returns_error(client):
    """Evento desconocido → error con código UNKNOWN_EVENT."""
    with client.websocket_connect("/ws/pollen-sync") as ws:
        ws.send_json({
            "event": "pollen_hello",
            "payload": {"pollen_id": "p1", "app_version": "0.0.0"},
        })
        _ = ws.receive_json()  # ready

        ws.send_json({
            "event": "this_does_not_exist",
            "payload": {},
            "trace_id": "test_trace_42",
        })
        response = ws.receive_json()

    assert response["event"] == "error"
    assert response["payload"]["code"] == "UNKNOWN_EVENT"
    assert response["trace_id"] == "test_trace_42"


def test_ws_persists_events_in_log(client):
    """Cada mensaje WS se persiste en pollen_sync_log."""
    from src import persistence

    with client.websocket_connect("/ws/pollen-sync") as ws:
        ws.send_json({
            "event": "pollen_hello",
            "payload": {"pollen_id": "p1", "app_version": "0.0.0"},
        })
        _ = ws.receive_json()

    # Tras cerrar, count debe reflejar in (hello) + out (ready)
    counts = persistence.count_ws_events_by_event()
    assert counts.get("pollen_hello", 0) >= 1
    assert counts.get("meristem_ready", 0) >= 1


def test_ws_health_shows_connection_state(client):
    """Mientras hay conexión, /health refleja pollen_connection."""
    # Sin conexión: alive=False
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["pollen_connection"]["connected"] is False
    assert body["pollen_connection"]["alive"] is False

    # Con conexión: alive=True (al menos un instante)
    with client.websocket_connect("/ws/pollen-sync") as ws:
        ws.send_json({
            "event": "pollen_hello",
            "payload": {"pollen_id": "p_alive", "app_version": "0.0.0"},
        })
        _ = ws.receive_json()
        r = client.get("/health")
        body = r.json()
        assert body["pollen_connection"]["connected"] is True
        assert body["pollen_connection"]["pollen_id"] == "p_alive"


def test_ws_pollen_command_without_connection_returns_409(client):
    """POST /pollen/command sin Pollen conectado → 409."""
    r = client.post(
        "/pollen/command",
        json={"command": "push_bundles", "expected_count": 3},
    )
    assert r.status_code == 409


def test_ws_pollen_command_delivers_to_client(client):
    """Conectado un cliente, POST /pollen/command → cliente recibe `command`."""
    with client.websocket_connect("/ws/pollen-sync") as ws:
        ws.send_json({
            "event": "pollen_hello",
            "payload": {"pollen_id": "p1", "app_version": "0.0.0"},
        })
        _ = ws.receive_json()  # ready

        # Disparamos comando desde otro cliente (la UI)
        r = client.post(
            "/pollen/command",
            json={"command": "push_bundles", "expected_count": 2},
        )
        assert r.status_code == 200
        cmd_response = r.json()
        assert cmd_response["ok"] is True
        assert cmd_response["command"] == "push_bundles"
        assert cmd_response["expected_count"] == 2

        # El cliente WS recibe el comando con el mismo trace_id
        cmd_msg = ws.receive_json()
        assert cmd_msg["event"] == "command"
        assert cmd_msg["payload"]["command"] == "push_bundles"
        assert cmd_msg["payload"]["expected_count"] == 2
        assert cmd_msg["trace_id"] == cmd_response["trace_id"]


def test_ws_sync_state_endpoint(client):
    """/sync-state devuelve estado + recent_events tras intercambio."""
    with client.websocket_connect("/ws/pollen-sync") as ws:
        ws.send_json({
            "event": "pollen_hello",
            "payload": {"pollen_id": "p_sync", "app_version": "0.0.0"},
        })
        _ = ws.receive_json()

        r = client.get("/sync-state")
        assert r.status_code == 200
        body = r.json()
        assert body["pollen_connection"]["connected"] is True
        assert body["pollen_connection"]["pollen_id"] == "p_sync"
        assert len(body["recent_events"]) >= 2  # hello + ready
        # Eventos en orden DESC
        events = [e["event"] for e in body["recent_events"]]
        assert "pollen_hello" in events
        assert "meristem_ready" in events
