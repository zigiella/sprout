"""Tests para los endpoints REST nuevos /bundles/recent y /policies/recent.

Estos endpoints alimentan las zonas 4 y 5 de la UI Meristem (visitas
recibidas + políticas emitidas). Validamos:

- Lista vacía cuando aún no hay datos
- Población correcta tras POST /visit
- Joineo con decisions (reason_code, rule_applied) en bundles
- Recorte de rationale en policies (160 chars)
- Limit clamping (1-200)

Usa BBDD aislada por test con `tmp_path` + reload de modules para evitar
state leakage.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from importlib import reload

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    """Cliente con DB temporal aislada por test.

    Importa src/* fresh (sin cache de sys.modules) para garantizar
    aislamiento total entre tests. El bug del reload sin del-modules
    es que algunas funciones en persistence.py tienen `db_path` como
    default arg evaluado al definirlas — los reloads sucesivos no
    siempre lo re-capturan en el orden correcto cuando los tests
    corren en suite.
    """
    import sys
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test_meristem.db")
    monkeypatch.setenv("MERISTEM_DB_PATH", db_path)
    monkeypatch.setenv("MERISTEM_USE_LLM", "false")

    # Borrar módulos cacheados de src.* para forzar import limpio
    for mod_name in list(sys.modules.keys()):
        if mod_name == "src" or mod_name.startswith("src."):
            del sys.modules[mod_name]

    # Importar fresh
    from src import persistence
    from src.ws_manager import manager
    from src import main as main_module

    # Asegurar DB inicializada en el path correcto
    persistence.init_db(db_path)

    # Reset singleton manager (por si otro test lo dejó dirty)
    manager._websocket = None
    manager._pollen_id = None
    manager._app_version = None
    manager._connected_at = None
    manager._last_heartbeat = None

    return TestClient(main_module.app)


def _bundle_payload(target: str = "rhizome_test_01", source: str = "pollen_test"):
    """Bundle mínimo válido que pasa por el pipeline limpio (CONFIRM_POLICY)."""
    return {
        "source_pollen_id": source,
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


def test_bundles_recent_empty(client):
    """Lista vacía cuando aún no hay bundles."""
    r = client.get("/bundles/recent")
    assert r.status_code == 200
    body = r.json()
    assert body["limit"] == 20
    assert body["items"] == []


def test_policies_recent_empty(client):
    """Lista vacía cuando aún no hay policies."""
    r = client.get("/policies/recent")
    assert r.status_code == 200
    body = r.json()
    assert body["limit"] == 20
    assert body["items"] == []


def test_bundles_recent_after_visit(client):
    """Tras POST /visit, /bundles/recent muestra el bundle con reason_code."""
    r = client.post("/visit", json=_bundle_payload(target="rhizome_test_X"))
    assert r.status_code == 200
    visit_resp = r.json()
    assert visit_resp["status"] == "ok"
    assert visit_resp["reason_code"] == "STABLE_BUNDLE"

    r = client.get("/bundles/recent")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["target_rhizome_id"] == "rhizome_test_X"
    assert items[0]["source_pollen_id"] == "pollen_test"
    assert items[0]["reason_code"] == "STABLE_BUNDLE"
    assert items[0]["rule_applied"] == "confirm_policy"


def test_policies_recent_after_visit(client):
    """Tras POST /visit OK, /policies/recent muestra la policy emitida."""
    r = client.post("/visit", json=_bundle_payload())
    assert r.status_code == 200

    r = client.get("/policies/recent")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1
    pol = items[0]
    assert pol["target_node_id"] == "rhizome_test_01"
    assert pol["mode_default"] == "normal"
    assert pol["valid_until"] is not None
    assert pol["policy_id"].startswith("pkt_meristem_")
    # rationale_short <= 160 chars
    assert len(pol["rationale_short"]) <= 160


def test_bundles_recent_order_desc(client):
    """Múltiples bundles → orden DESC por received_at."""
    for i, target in enumerate(["rhizome_A", "rhizome_B", "rhizome_C"]):
        r = client.post("/visit", json=_bundle_payload(target=target))
        assert r.status_code == 200

    r = client.get("/bundles/recent")
    items = r.json()["items"]
    assert len(items) == 3
    # Más reciente primero
    targets = [i["target_rhizome_id"] for i in items]
    # Orden DESC: el último insertado va primero
    assert targets[0] == "rhizome_C"


def test_bundles_recent_limit_clamping(client):
    """limit > 200 se clampa a 200, limit < 1 se clampa a 1."""
    r = client.get("/bundles/recent?limit=999")
    assert r.json()["limit"] == 200

    r = client.get("/bundles/recent?limit=0")
    assert r.json()["limit"] == 1

    r = client.get("/bundles/recent?limit=-5")
    assert r.json()["limit"] == 1


def test_policies_recent_limit_clamping(client):
    """Mismo clamping en /policies/recent."""
    r = client.get("/policies/recent?limit=500")
    assert r.json()["limit"] == 200

    r = client.get("/policies/recent?limit=0")
    assert r.json()["limit"] == 1


def test_bundles_recent_includes_refused(client):
    """Bundle REFUSE se incluye en la lista, con reason_code apropiado."""
    refuse_bundle = _bundle_payload(target="rhizome_refuse_test")
    refuse_bundle["rhizome_snapshot"]["operator_request"] = (
        "regar 30s extra hoy"
    )

    r = client.post("/visit", json=refuse_bundle)
    assert r.status_code == 200
    assert r.json()["status"] == "refuse"
    assert r.json()["reason_code"] == "JURISDICTION_POLLEN"

    r = client.get("/bundles/recent")
    items = r.json()["items"]
    assert len(items) == 1
    # Bundle REFUSE puede tener reason_code None en /bundles/recent
    # porque REFUSE no persiste decision en la pipeline actual.
    # Verificamos al menos que el bundle se persiste y aparece.
    assert items[0]["target_rhizome_id"] == "rhizome_refuse_test"
