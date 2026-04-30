"""Persistence layer SQLite para Meristem-nodo.

Tres tablas con relaciones simples:
- bundles    : lo que Pollen entrega
- policies   : lo que Meristem emite
- decisions  : trazabilidad bundle → policy con rule_applied y métricas LLM

Por qué SQLite (no en memoria):
1. **Reproducibilidad de demo**: el jurado puede pedir "muestra la
   policy de hace 3 visitas" y respondemos.
2. **Trazabilidad para writeup**: el repo queda con datos de ejemplo
   ya generados.
3. **Base para post-demo**: cuando Bea pidió "consolidar datos +
   identificar patrones", la tabla `bundles` ya está. Sin refactor.
4. **Coste casi cero**: file-based, sin servicio extra, parte de
   stdlib Python.

File path: por defecto `meristem_node.db` en el cwd. Configurable vía
env `MERISTEM_DB_PATH`.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from .schemas import (
    Action,
    Bundle,
    BundleRecord,
    DecisionRecord,
    PolicyPacket,
    PolicyRecord,
)


# Path por defecto: file en cwd. Override via env.
DEFAULT_DB_PATH = Path(
    os.environ.get("MERISTEM_DB_PATH", "meristem_node.db")
)


# ---------------------------------------------------------------------------
# Schema setup (idempotente)
# ---------------------------------------------------------------------------


SCHEMA = """
CREATE TABLE IF NOT EXISTS bundles (
    bundle_id TEXT PRIMARY KEY,
    received_at TEXT NOT NULL,
    source_pollen_id TEXT NOT NULL,
    target_rhizome_id TEXT NOT NULL,
    active_policy_id TEXT NOT NULL,
    raw_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bundles_target
    ON bundles(target_rhizome_id, received_at DESC);

CREATE TABLE IF NOT EXISTS policies (
    policy_id TEXT PRIMARY KEY,
    emitted_at TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    raw_json TEXT NOT NULL,
    evidence_refs TEXT NOT NULL  -- JSON list of bundle_ids
);

CREATE INDEX IF NOT EXISTS idx_policies_target
    ON policies(target_node_id, emitted_at DESC);

CREATE TABLE IF NOT EXISTS decisions (
    decision_id TEXT PRIMARY KEY,
    bundle_id TEXT NOT NULL,
    policy_id TEXT NOT NULL,
    rule_applied TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    llm_metrics TEXT NOT NULL,  -- JSON
    created_at TEXT NOT NULL,
    FOREIGN KEY (bundle_id) REFERENCES bundles(bundle_id),
    FOREIGN KEY (policy_id) REFERENCES policies(policy_id)
);

CREATE INDEX IF NOT EXISTS idx_decisions_bundle
    ON decisions(bundle_id, created_at DESC);
"""


def init_db(db_path: Path | str = DEFAULT_DB_PATH) -> None:
    """Crea tablas e índices si no existen. Idempotente."""
    db_path = Path(db_path)
    with sqlite3.connect(db_path) as con:
        con.executescript(SCHEMA)


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------


def _connect(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    return con


# ---------------------------------------------------------------------------
# Inserts
# ---------------------------------------------------------------------------


def insert_bundle(bundle: Bundle, db_path: Path | str = DEFAULT_DB_PATH) -> BundleRecord:
    """Persiste un bundle entrante. Devuelve BundleRecord."""
    record = BundleRecord(
        bundle_id=bundle.bundle_id,
        received_at=bundle.received_at,
        source_pollen_id=bundle.source_pollen_id,
        target_rhizome_id=bundle.target_rhizome_id,
        active_policy_id=bundle.active_policy_id,
        raw_json=bundle.model_dump_json(),
    )
    with _connect(db_path) as con:
        con.execute(
            """
            INSERT OR REPLACE INTO bundles
            (bundle_id, received_at, source_pollen_id, target_rhizome_id,
             active_policy_id, raw_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record.bundle_id,
                record.received_at.isoformat(),
                record.source_pollen_id,
                record.target_rhizome_id,
                record.active_policy_id,
                record.raw_json,
            ),
        )
    return record


def insert_policy(
    policy: PolicyPacket,
    evidence_refs: list[str],
    db_path: Path | str = DEFAULT_DB_PATH,
) -> PolicyRecord:
    """Persiste una policy emitida. Devuelve PolicyRecord."""
    record = PolicyRecord(
        policy_id=policy.policy_id,
        emitted_at=datetime.now(),
        target_node_id=policy.target_node_id,
        raw_json=policy.model_dump_json(),
        evidence_refs=evidence_refs,
    )
    with _connect(db_path) as con:
        con.execute(
            """
            INSERT OR REPLACE INTO policies
            (policy_id, emitted_at, target_node_id, raw_json, evidence_refs)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                record.policy_id,
                record.emitted_at.isoformat(),
                record.target_node_id,
                record.raw_json,
                json.dumps(record.evidence_refs),
            ),
        )
    return record


def insert_decision(
    decision: DecisionRecord,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> DecisionRecord:
    """Persiste una decisión (link bundle ↔ policy ↔ rule + métricas LLM)."""
    with _connect(db_path) as con:
        con.execute(
            """
            INSERT OR REPLACE INTO decisions
            (decision_id, bundle_id, policy_id, rule_applied, reason_code,
             llm_metrics, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision.decision_id,
                decision.bundle_id,
                decision.policy_id,
                decision.rule_applied.value,
                decision.reason_code,
                json.dumps(decision.llm_metrics),
                datetime.now().isoformat(),
            ),
        )
    return decision


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------


def get_latest_policy_for(
    target_node_id: str, db_path: Path | str = DEFAULT_DB_PATH
) -> PolicyPacket | None:
    """Devuelve la última policy emitida para un nodo Rhizome concreto."""
    with _connect(db_path) as con:
        row = con.execute(
            """
            SELECT raw_json FROM policies
            WHERE target_node_id = ?
            ORDER BY emitted_at DESC
            LIMIT 1
            """,
            (target_node_id,),
        ).fetchone()
    if not row:
        return None
    return PolicyPacket.model_validate_json(row["raw_json"])


def get_latest_policy_global(
    db_path: Path | str = DEFAULT_DB_PATH,
) -> PolicyPacket | None:
    """Devuelve la última policy emitida cualquiera (debug/demo)."""
    with _connect(db_path) as con:
        row = con.execute(
            """
            SELECT raw_json FROM policies
            ORDER BY emitted_at DESC
            LIMIT 1
            """,
        ).fetchone()
    if not row:
        return None
    return PolicyPacket.model_validate_json(row["raw_json"])


def get_policy_by_id(
    policy_id: str, db_path: Path | str = DEFAULT_DB_PATH
) -> PolicyPacket | None:
    """Trazabilidad: una policy concreta por id."""
    with _connect(db_path) as con:
        row = con.execute(
            "SELECT raw_json FROM policies WHERE policy_id = ?",
            (policy_id,),
        ).fetchone()
    if not row:
        return None
    return PolicyPacket.model_validate_json(row["raw_json"])


def count_bundles(db_path: Path | str = DEFAULT_DB_PATH) -> int:
    """Para `/health`: cuántos bundles se han recibido en total."""
    with _connect(db_path) as con:
        row = con.execute("SELECT COUNT(*) AS c FROM bundles").fetchone()
    return int(row["c"]) if row else 0


def count_policies(db_path: Path | str = DEFAULT_DB_PATH) -> int:
    """Para `/health`: cuántas policies se han emitido en total."""
    with _connect(db_path) as con:
        row = con.execute("SELECT COUNT(*) AS c FROM policies").fetchone()
    return int(row["c"]) if row else 0


def count_decisions_by_rule(
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict[str, int]:
    """Para `/health` y demo: distribución de reglas aplicadas.

    Útil al jurado: muestra que las 4 reglas se ejercitan en producción.
    """
    with _connect(db_path) as con:
        rows = con.execute(
            "SELECT rule_applied, COUNT(*) AS c FROM decisions GROUP BY rule_applied"
        ).fetchall()
    return {r["rule_applied"]: int(r["c"]) for r in rows}
