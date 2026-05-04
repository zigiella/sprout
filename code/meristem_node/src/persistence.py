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


# ---------------------------------------------------------------------------
# Vista por target (para /status — demo MVP multi-Rhizome)
# ---------------------------------------------------------------------------


def list_known_targets(
    db_path: Path | str = DEFAULT_DB_PATH,
) -> list[str]:
    """Todos los Rhizome IDs que han enviado bundles persistidos.

    Devuelto ordenado alfabéticamente para output estable en demo.
    Incluye Rhizomes cuyos bundles fueron REFUSE (sin policy emitida) —
    para trazabilidad completa.
    """
    with _connect(db_path) as con:
        rows = con.execute(
            "SELECT DISTINCT target_rhizome_id FROM bundles "
            "ORDER BY target_rhizome_id ASC"
        ).fetchall()
    return [r["target_rhizome_id"] for r in rows]


def get_target_summary(
    target_node_id: str, db_path: Path | str = DEFAULT_DB_PATH,
) -> dict[str, Any] | None:
    """Resumen del estado de Meristem para un Rhizome concreto.

    Devuelve dict con:
    - target_node_id
    - bundles_received
    - last_bundle_at (último received_at, ISO string o None)
    - policies_emitted
    - latest_policy_id (None si nunca emitió por REFUSEs)
    - latest_policy_emitted_at (ISO o None)
    - latest_policy_mode (normal/conservative/alert o None)
    - latest_policy_valid_until (ISO o None)
    - latest_reason_code (de decisions.reason_code más reciente, o None)
    - latest_rule_applied (de decisions.rule_applied más reciente, o None)

    Devuelve None si el target no existe en bundles (no hay registro).
    """
    with _connect(db_path) as con:
        # 1. Counts y last_bundle_at
        bundle_row = con.execute(
            """
            SELECT COUNT(*) AS c, MAX(received_at) AS last_at
            FROM bundles WHERE target_rhizome_id = ?
            """,
            (target_node_id,),
        ).fetchone()
        if not bundle_row or int(bundle_row["c"] or 0) == 0:
            return None

        bundles_received = int(bundle_row["c"])
        last_bundle_at = bundle_row["last_at"]

        # 2. Policies count + última policy
        pol_count = con.execute(
            "SELECT COUNT(*) AS c FROM policies WHERE target_node_id = ?",
            (target_node_id,),
        ).fetchone()
        policies_emitted = int(pol_count["c"]) if pol_count else 0

        latest_pol_row = con.execute(
            """
            SELECT policy_id, emitted_at, raw_json FROM policies
            WHERE target_node_id = ?
            ORDER BY emitted_at DESC LIMIT 1
            """,
            (target_node_id,),
        ).fetchone()

        latest_policy_id = None
        latest_policy_emitted_at = None
        latest_policy_mode = None
        latest_policy_valid_until = None
        if latest_pol_row:
            latest_policy_id = latest_pol_row["policy_id"]
            latest_policy_emitted_at = latest_pol_row["emitted_at"]
            try:
                pkt = PolicyPacket.model_validate_json(latest_pol_row["raw_json"])
                latest_policy_mode = pkt.mode_default
                latest_policy_valid_until = pkt.valid_until.isoformat()
            except Exception:
                # Defensivo: si la policy persistida no parsea (no debería),
                # devolvemos lo que sí podemos.
                pass

        # 3. Última decisión para ese target (joineando policies)
        latest_dec_row = con.execute(
            """
            SELECT d.reason_code, d.rule_applied
            FROM decisions d
            JOIN policies p ON d.policy_id = p.policy_id
            WHERE p.target_node_id = ?
            ORDER BY d.created_at DESC LIMIT 1
            """,
            (target_node_id,),
        ).fetchone()
        latest_reason_code = latest_dec_row["reason_code"] if latest_dec_row else None
        latest_rule_applied = latest_dec_row["rule_applied"] if latest_dec_row else None

    return {
        "target_node_id": target_node_id,
        "bundles_received": bundles_received,
        "last_bundle_at": last_bundle_at,
        "policies_emitted": policies_emitted,
        "latest_policy_id": latest_policy_id,
        "latest_policy_emitted_at": latest_policy_emitted_at,
        "latest_policy_mode": latest_policy_mode,
        "latest_policy_valid_until": latest_policy_valid_until,
        "latest_reason_code": latest_reason_code,
        "latest_rule_applied": latest_rule_applied,
    }
