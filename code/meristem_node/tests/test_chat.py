"""Tests del endpoint POST /chat (chat conversacional read-only).

Linea B dia 24: fase 3 plan IA dia 19. El operador pregunta en
castellano, LLM responde con read-only sobre histórico, citando
policy_id / decision_id.

Cubre:
- Stub mode (sin LLM): respuesta determinista predefinida
- Conversation id: nuevo si no se pasa, continúa si se pasa
- Persistencia: cada mensaje (user + assistant) queda en tabla
  conversations
- /chat/{id}/history devuelve mensajes en orden ASC
- Read-only: chat NO crea bundles ni policies
- evidence_refs: extrae policy_id mencionados en answer
"""
from __future__ import annotations

import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    """Cliente con DB temporal y stub mode (no LLM real)."""
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, "test_meristem.db")
    monkeypatch.setenv("MERISTEM_DB_PATH", db_path)
    monkeypatch.setenv("MERISTEM_USE_LLM", "false")  # stub mode
    # Borrar src.* del cache para forzar import limpio (defaults
    # se evaluan al import, ver test_recent_endpoints.py)
    for mod_name in list(sys.modules.keys()):
        if mod_name == "src" or mod_name.startswith("src."):
            del sys.modules[mod_name]
    from src import persistence
    persistence.init_db(db_path)
    from src import main as main_module
    return TestClient(main_module.app)


def test_chat_creates_new_conversation_id_when_omitted(client):
    """Sin conversation_id, /chat genera uno nuevo."""
    r = client.post("/chat", json={
        "operator_id": "test_bea",
        "message_es": "Hola, ¿cómo está la parcela A?",
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["task"] == "responder_operador"
    assert body["status"] == "ok"
    assert body["conversation_id"].startswith("conv_")
    assert "answer_es" in body
    assert isinstance(body["evidence_refs"], list)


def test_chat_stub_mode_returns_deterministic_text(client):
    """Sin LLM real, /chat devuelve stub text con la pregunta citada."""
    r = client.post("/chat", json={
        "operator_id": "test_bea",
        "message_es": "test pregunta unica xyz",
    })
    body = r.json()
    assert "Stub mode" in body["answer_es"]
    assert "test pregunta unica xyz"[:80] in body["answer_es"]
    assert body["llm_metrics"]["mode"] == "stub_disabled"


def test_chat_persists_user_and_assistant_messages(client):
    """Cada POST persiste 2 filas: user + assistant."""
    r = client.post("/chat", json={
        "operator_id": "test_bea",
        "message_es": "primera pregunta",
    })
    conv_id = r.json()["conversation_id"]

    # /chat/{id}/history debe devolver ambos mensajes en orden ASC
    h = client.get(f"/chat/{conv_id}/history")
    assert h.status_code == 200
    body = h.json()
    assert body["count"] == 2
    msgs = body["messages"]
    assert msgs[0]["role"] == "user"
    assert msgs[0]["content"] == "primera pregunta"
    assert msgs[1]["role"] == "assistant"
    assert "Stub mode" in msgs[1]["content"]


def test_chat_continues_conversation_with_id(client):
    """Pasar conversation_id continúa la conversación previa."""
    r1 = client.post("/chat", json={
        "operator_id": "test_bea",
        "message_es": "primera",
    })
    conv_id = r1.json()["conversation_id"]

    r2 = client.post("/chat", json={
        "operator_id": "test_bea",
        "message_es": "segunda",
        "conversation_id": conv_id,
    })
    assert r2.json()["conversation_id"] == conv_id

    # History ahora tiene 4 mensajes (2 turns × user+assistant)
    h = client.get(f"/chat/{conv_id}/history")
    assert h.json()["count"] == 4
    msgs = h.json()["messages"]
    assert msgs[0]["content"] == "primera"
    assert msgs[2]["content"] == "segunda"


def test_chat_does_not_create_bundles_or_policies(client):
    """Read-only estricto: /chat no debe afectar bundles/policies."""
    # /health antes
    h_before = client.get("/health").json()
    assert h_before["bundles_received_total"] == 0
    assert h_before["policies_emitted_total"] == 0

    client.post("/chat", json={
        "operator_id": "test_bea",
        "message_es": "ping",
    })

    # /health después
    h_after = client.get("/health").json()
    assert h_after["bundles_received_total"] == 0
    assert h_after["policies_emitted_total"] == 0
    # Pero sí debe haber mensajes de chat persistidos
    chat_counts = h_after.get("chat_messages", {})
    assert chat_counts.get("user", 0) >= 1
    assert chat_counts.get("assistant", 0) >= 1


def test_chat_evidence_refs_extraction(client):
    """extract_evidence_refs detecta policy_id en answer."""
    from src.inference import extract_evidence_refs

    text = (
        "Según la policy pkt_meristem_1234abcd la decisión fue X. "
        "Ver también dec_xxxx5555 para el detalle."
    )
    refs = extract_evidence_refs(text)
    assert "pkt_meristem_1234abcd" in refs
    assert "dec_xxxx5555" in refs

    # Texto sin referencias
    refs_empty = extract_evidence_refs("Todo está bien, sin más detalle.")
    assert refs_empty == []


def test_chat_validates_max_message_length(client):
    """Pydantic rechaza message_es > 1000 chars."""
    r = client.post("/chat", json={
        "operator_id": "test_bea",
        "message_es": "a" * 1001,
    })
    assert r.status_code == 422  # Unprocessable


def test_chat_health_includes_chat_counters(client):
    """/health incluye contadores de mensajes chat tras varios POSTs."""
    client.post("/chat", json={
        "operator_id": "op1",
        "message_es": "una",
    })
    client.post("/chat", json={
        "operator_id": "op2",
        "message_es": "dos",
    })
    h = client.get("/health").json()
    counts = h["chat_messages"]
    assert counts.get("user", 0) == 2
    assert counts.get("assistant", 0) == 2
