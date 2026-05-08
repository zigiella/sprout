"""Tests del sub-PR aditivo día 23: policy_origin + policy_scope.

Cubre:
- Defaults retro-compatibles (PolicyPacket sin estos campos asume
  meristem-durable + durable)
- Persistencia con campos explícitos (policy_origin=pollen-visit,
  policy_scope=transient)
- Migración aditiva (BBDD vieja sin columnas → ALTER TABLE las añade
  con default sin perder datos)
- /health expone policies_by_scope con desglose
- /status TargetStatus expone policies_durable_count +
  policies_transient_count + latest_policy_origin/scope
- get_target_summary correctamente
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    """Cliente con DB temporal aislada (mismo patrón que test_recent_endpoints)."""
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test_meristem.db")
    monkeypatch.setenv("MERISTEM_DB_PATH", db_path)
    monkeypatch.setenv("MERISTEM_USE_LLM", "false")

    for mod_name in list(sys.modules.keys()):
        if mod_name == "src" or mod_name.startswith("src."):
            del sys.modules[mod_name]

    from src import persistence
    from src.ws_manager import manager
    from src import main as main_module

    persistence.init_db(db_path)

    manager._websocket = None
    manager._pollen_id = None
    manager._app_version = None
    manager._connected_at = None
    manager._last_heartbeat = None

    return TestClient(main_module.app)


def _bundle_payload(target: str = "rhizome_test_01"):
    """Bundle limpio que dispara CONFIRM_POLICY."""
    return {
        "source_pollen_id": "pollen_test",
        "target_rhizome_id": target,
        "active_policy_id": "pkt_test_baseline",
        "rhizome_snapshot": {
            "snapshot_id": "snap_test_01",
            "mode": "normal",
            "alert_latched": False,
            "pending_contradictions": [],
            "soil_a_pct": 35,
            "soil_b_pct": 42,
            "tank_pct": 78,
        },
        "decision_receipts": [
            {"action": "WATER_A", "duration_s": 18, "confidence": 0.92},
        ],
        "weather_digest": {"isStale": False, "summary": "test"},
        "validation_stamps": [],
    }


def test_policy_packet_defaults_retrocompat():
    """PolicyPacket sin policy_origin/scope explícitos asume defaults."""
    from src.schemas import PolicyPacket
    p = PolicyPacket(
        policy_id="pkt_test_X",
        target_node_id="rhizome_test",
        valid_until=datetime.now() + timedelta(days=7),
        rationale="test",
    )
    assert p.policy_origin == "meristem-durable"
    assert p.policy_scope == "durable"


def test_policy_packet_explicit_fields():
    """PolicyPacket con campos explícitos los preserva."""
    from src.schemas import PolicyPacket
    p = PolicyPacket(
        policy_id="pkt_test_Y",
        target_node_id="rhizome_test",
        valid_until=datetime.now() + timedelta(hours=12),
        rationale="test transient",
        policy_origin="pollen-visit",
        policy_scope="transient",
    )
    assert p.policy_origin == "pollen-visit"
    assert p.policy_scope == "transient"


def test_persist_policy_with_default_fields(client):
    """Tras POST /visit, la policy se persiste con defaults durable."""
    r = client.post("/visit", json=_bundle_payload(target="rhizome_dur"))
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

    # Health debe mostrar policies_by_scope con durable >= 1
    r = client.get("/health")
    body = r.json()
    assert body["policies_by_scope"].get("durable", 0) >= 1
    assert body["policies_by_scope"].get("transient", 0) == 0


def test_target_status_includes_scope_breakdown(client):
    """TargetStatus expone policies_durable_count + policies_transient_count."""
    r = client.post("/visit", json=_bundle_payload(target="rhizome_breakdown"))
    assert r.status_code == 200

    r = client.get("/status")
    body = r.json()
    assert len(body["targets"]) == 1
    target = body["targets"][0]
    assert target["target_node_id"] == "rhizome_breakdown"
    assert target["policies_durable_count"] >= 1
    assert target["policies_transient_count"] == 0
    assert target["latest_policy_origin"] == "meristem-durable"
    assert target["latest_policy_scope"] == "durable"


def test_persist_policy_with_transient_scope_explicit():
    """Inserción manual con scope=transient se persiste correctamente."""
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test_transient.db")
    os.environ["MERISTEM_DB_PATH"] = db_path

    for mod_name in list(sys.modules.keys()):
        if mod_name == "src" or mod_name.startswith("src."):
            del sys.modules[mod_name]

    from src import persistence
    from src.schemas import PolicyPacket

    persistence.init_db(db_path)

    pol = PolicyPacket(
        policy_id="pkt_transient_Z",
        target_node_id="rhizome_transient",
        valid_until=datetime.now() + timedelta(hours=12),
        rationale="visita Pollen via Mini-Evaluator",
        policy_origin="pollen-visit",
        policy_scope="transient",
    )
    persistence.insert_policy(pol, evidence_refs=["b_test_1"])

    counts = persistence.count_policies_by_scope()
    assert counts.get("transient", 0) == 1
    assert counts.get("durable", 0) == 0


def test_migration_old_db_alter_table_aditive():
    """BBDD vieja sin columnas → init_db las añade con defaults."""
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test_oldschema.db")

    # Crear BBDD con schema antiguo (sin policy_origin/scope) manualmente
    con = sqlite3.connect(db_path)
    con.executescript("""
        CREATE TABLE policies (
            policy_id TEXT PRIMARY KEY,
            emitted_at TEXT NOT NULL,
            target_node_id TEXT NOT NULL,
            raw_json TEXT NOT NULL,
            evidence_refs TEXT NOT NULL
        );
        CREATE TABLE bundles (
            bundle_id TEXT PRIMARY KEY,
            received_at TEXT NOT NULL,
            source_pollen_id TEXT NOT NULL,
            target_rhizome_id TEXT NOT NULL,
            active_policy_id TEXT NOT NULL,
            raw_json TEXT NOT NULL
        );
        CREATE TABLE decisions (
            decision_id TEXT PRIMARY KEY,
            bundle_id TEXT NOT NULL,
            policy_id TEXT NOT NULL,
            rule_applied TEXT NOT NULL,
            reason_code TEXT NOT NULL,
            llm_metrics TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)
    # Insertamos una policy antigua sin las columnas nuevas
    con.execute(
        "INSERT INTO policies (policy_id, emitted_at, target_node_id, raw_json, evidence_refs) "
        "VALUES (?, ?, ?, ?, ?)",
        ("pkt_old_X", datetime.now().isoformat(), "rhizome_old", '{"raw":"json"}', "[]"),
    )
    con.commit()
    con.close()

    # Ahora init_db ejecuta migración aditiva
    os.environ["MERISTEM_DB_PATH"] = db_path
    for mod_name in list(sys.modules.keys()):
        if mod_name == "src" or mod_name.startswith("src."):
            del sys.modules[mod_name]
    from src import persistence
    persistence.init_db(db_path)

    # Verificar que las columnas existen y la policy antigua tiene defaults
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM policies WHERE policy_id = 'pkt_old_X'").fetchone()
    assert row["policy_origin"] == "meristem-durable"
    assert row["policy_scope"] == "durable"
    con.close()


def test_health_exposes_policies_by_scope(client):
    """/health incluye policies_by_scope (vacío al principio)."""
    r = client.get("/health")
    body = r.json()
    assert "policies_by_scope" in body
    assert body["policies_by_scope"] == {}

    r = client.post("/visit", json=_bundle_payload())
    assert r.status_code == 200

    r = client.get("/health")
    body = r.json()
    assert body["policies_by_scope"].get("durable") == 1
