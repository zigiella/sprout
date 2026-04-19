"""Tests del policy_engine con LLM mockeado. Sin red real.

Cubre:
- Happy path: el LLM devuelve un JSON valido → engine persiste y retorna la packet.
- Schema invalido: el LLM devuelve JSON no conforme → engine loguea y retorna None.
- Violacion §30: el LLM devuelve JSON conforme al schema pero con
  max_watering_duration_s=120 → engine NO persiste, loguea intento y retorna
  None con reason=violates_safety_rule. Criterio de aceptacion #28 explicito.
"""

from __future__ import annotations

import sqlite3
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest
from schemas.examples.builders import policy_packet_example

from src import persistence
from src.llm_client import OllamaClient
from src.persistence import init_db
from src.policy_engine import consolidate
from src.settings import Settings


class _FakeOllama:
    """Sustituto de OllamaClient que devuelve un dict precomputado."""

    def __init__(self, response: dict[str, Any]) -> None:
        self._response = response
        self.calls: list[tuple[str, str]] = []

    def generate_json(
        self, system: str, user: str, schema: dict | None = None,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        self.calls.append((system, user))
        return deepcopy(self._response)


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        ollama_host="http://localhost:11434",
        ollama_model="gemma4:e4b",
        meristem_port=7070,
        db_path=str(tmp_path / "engine.db"),
        shadow_enabled=False,
        gemini_api_key=None,
        shadow_model="gemma-4-31b-it",
    )


def _fresh_packet(overrides_rules: dict | None = None) -> dict:
    """Fixture canonica con timestamps actualizados para no llegar expirada."""
    packet = deepcopy(policy_packet_example())
    now = datetime.now(timezone.utc)
    packet["created_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    packet["valid_until"] = (now + timedelta(hours=6)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    if overrides_rules:
        packet["rules"].update(overrides_rules)
    return packet


@pytest.fixture
def db_path(tmp_path: Path) -> str:
    settings = _settings(tmp_path)
    init_db(settings.db_path)
    return settings.db_path


def test_consolidate_happy_path_persists_packet(db_path: str) -> None:
    response = _fresh_packet()
    fake = _FakeOllama(response)

    result = consolidate(
        db_path=db_path,
        target_node_id="rhizome_01",
        evidence=[],
        llm=fake,  # type: ignore[arg-type]
    )

    assert result.packet is not None
    assert result.reason is None
    # La policy quedo persistida como activa.
    active = persistence.get_active_policy(db_path, "rhizome_01")
    assert active is not None
    assert active["policy_id"] == response["policy_id"]
    # El fake fue llamado con system + user.
    assert len(fake.calls) == 1


def test_consolidate_blocks_when_llm_violates_30(db_path: str) -> None:
    """Criterio #28 (test negativo del engine): el LLM genera una packet
    con max_watering_duration_s=120. El engine NO debe persistirla."""
    bad = _fresh_packet({"max_watering_duration_s": 120})
    fake = _FakeOllama(bad)

    result = consolidate(
        db_path=db_path,
        target_node_id="rhizome_01",
        evidence=[],
        llm=fake,  # type: ignore[arg-type]
    )

    assert result.packet is None
    assert result.reason == "violates_safety_rule"
    assert result.violations is not None
    assert result.violations[0]["rule"] == "rules.max_watering_duration_s"

    # Nada persistido como policy activa.
    assert persistence.get_active_policy(db_path, "rhizome_01") is None

    # Rastro del intento en decisions_log.
    with sqlite3.connect(db_path) as conn:
        rows = list(conn.execute("SELECT action FROM decisions_log"))
    assert ("blocked_by_safety",) in rows


def test_consolidate_blocks_when_llm_violates_tank_minimum(
    db_path: str,
) -> None:
    bad = _fresh_packet({"tank_minimum_pct": 10.0})
    fake = _FakeOllama(bad)

    result = consolidate(
        db_path=db_path,
        target_node_id="rhizome_01",
        evidence=[],
        llm=fake,  # type: ignore[arg-type]
    )

    assert result.packet is None
    assert result.reason == "violates_safety_rule"
    assert any(
        v["rule"] == "rules.tank_minimum_pct" for v in result.violations
    )


def test_consolidate_blocks_when_llm_returns_invalid_schema(
    db_path: str,
) -> None:
    """Si el LLM alucina campos que no validan el schema, no se persiste."""
    fake = _FakeOllama({"schema_version": "1.0", "wrong": "shape"})

    result = consolidate(
        db_path=db_path,
        target_node_id="rhizome_01",
        evidence=[],
        llm=fake,  # type: ignore[arg-type]
    )

    assert result.packet is None
    assert result.reason == "invalid_schema"
    assert persistence.get_active_policy(db_path, "rhizome_01") is None

    with sqlite3.connect(db_path) as conn:
        rows = list(conn.execute("SELECT action FROM decisions_log"))
    assert ("blocked_invalid_schema",) in rows


def test_consolidate_passes_active_policy_into_user_prompt(
    db_path: str,
) -> None:
    """Si hay policy activa, el engine debe incluirla en el user prompt para
    continuidad."""
    seed = _fresh_packet()
    persistence.upsert_policy(db_path, seed)

    response = _fresh_packet()
    response["policy_id"] = "pkt_rhizome_01_next"
    response["version_chain"] = [seed["policy_id"], "pkt_rhizome_01_next"]
    fake = _FakeOllama(response)

    consolidate(
        db_path=db_path,
        target_node_id="rhizome_01",
        evidence=[],
        llm=fake,  # type: ignore[arg-type]
    )

    # El user prompt contiene el policy_id previo.
    _, user = fake.calls[0]
    assert seed["policy_id"] in user
