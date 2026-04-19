"""Persistencia local de Meristem.

SQLite, sin servidor externo. Tablas (spec 12_meristem_spec.md §7):

- `evidence`: snapshots, alerts, packets entrantes (raw JSON).
- `policies`: policy_packets emitidos.
- `deltas`: policy_deltas propuestos/validados/rechazados.
- `decisions_log`: decisiones importadas via Pollen + intentos bloqueados
  por safety_rules (auditoria local, ver §30 Gap 4).
- `shadow_comparisons`: diffs local vs sombra (solo si SHADOW_ENABLED).
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    received_at TEXT NOT NULL,
    kind TEXT NOT NULL,
    origin_node_id TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_evidence_kind ON evidence(kind);
CREATE INDEX IF NOT EXISTS idx_evidence_origin ON evidence(origin_node_id);

CREATE TABLE IF NOT EXISTS policies (
    policy_id TEXT PRIMARY KEY,
    target_node_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    valid_until TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_policies_target ON policies(target_node_id);

CREATE TABLE IF NOT EXISTS deltas (
    delta_id TEXT PRIMARY KEY,
    target_node_id TEXT NOT NULL,
    base_policy_id TEXT NOT NULL,
    status TEXT NOT NULL,
    reason TEXT,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_deltas_target_status ON deltas(target_node_id, status);

CREATE TABLE IF NOT EXISTS decisions_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origin_node_id TEXT NOT NULL,
    received_at TEXT NOT NULL,
    action TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shadow_comparisons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    local_output_json TEXT NOT NULL,
    shadow_output_json TEXT NOT NULL,
    agreement INTEGER NOT NULL,
    notes TEXT
);
"""

# Estados posibles del campo `deltas.status`. Son los que usa /deltas/propose
# y /deltas/pending. `pending` existe para el flujo ideal (Pollen propone,
# Meristem valida en batch) aunque en este PR /deltas/propose valida sincrono.
DELTA_STATUS_PENDING = "pending"
DELTA_STATUS_VALIDATED = "validated"
DELTA_STATUS_REJECTED = "rejected"


def init_db(db_path: str | Path) -> None:
    """Crea las tablas si no existen. Idempotente."""
    path = Path(db_path)
    if path.parent and str(path.parent) not in {"", "."}:
        path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(path)) as conn:
        conn.executescript(_SCHEMA_SQL)
        conn.commit()


@contextmanager
def connect(db_path: str | Path) -> Iterator[sqlite3.Connection]:
    """Context manager con row_factory preconfigurada."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _utcnow_zulu() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------

def insert_evidence(
    db_path: str | Path,
    kind: str,
    origin_node_id: str,
    payload: dict[str, Any],
) -> int:
    """Persiste un payload de evidence. Devuelve el rowid asignado."""
    with connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO evidence(received_at, kind, origin_node_id, payload_json) "
            "VALUES (?, ?, ?, ?)",
            (_utcnow_zulu(), kind, origin_node_id, json.dumps(payload)),
        )
        conn.commit()
        return int(cur.lastrowid)


# ---------------------------------------------------------------------------
# Policies
# ---------------------------------------------------------------------------

def upsert_policy(db_path: str | Path, packet: dict[str, Any]) -> None:
    """Persiste una PolicyPacket ya validada. Si ya existe policy_id, la
    sustituye — idempotencia por policy_id.
    """
    with connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO policies"
            "(policy_id, target_node_id, created_at, valid_until, payload_json) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                packet["policy_id"],
                packet["target_node_id"],
                packet["created_at"],
                packet["valid_until"],
                json.dumps(packet),
            ),
        )
        conn.commit()


def get_active_policy(
    db_path: str | Path, target_node_id: str, now: datetime | None = None
) -> dict[str, Any] | None:
    """Devuelve la PolicyPacket activa (no expirada) mas reciente para el
    nodo, o None si no hay ninguna.
    """
    now = now or datetime.now(timezone.utc)
    now_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT payload_json FROM policies "
            "WHERE target_node_id = ? AND valid_until > ? "
            "ORDER BY created_at DESC LIMIT 1",
            (target_node_id, now_str),
        ).fetchone()
    if row is None:
        return None
    return json.loads(row["payload_json"])


# ---------------------------------------------------------------------------
# Deltas
# ---------------------------------------------------------------------------

def insert_delta(
    db_path: str | Path,
    delta: dict[str, Any],
    status: str,
    reason: str | None = None,
) -> None:
    """Persiste un PolicyDelta con su status (`pending`/`validated`/`rejected`)."""
    with connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO deltas"
            "(delta_id, target_node_id, base_policy_id, status, reason, "
            "created_at, payload_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                delta["delta_id"],
                delta["target_node_id"],
                delta["base_policy_id"],
                status,
                reason,
                delta["created_at"],
                json.dumps(delta),
            ),
        )
        conn.commit()


def list_deltas(
    db_path: str | Path, target_node_id: str, status: str
) -> list[dict[str, Any]]:
    """Lista los deltas en un estado para un nodo. Ordenados por created_at asc."""
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT payload_json FROM deltas "
            "WHERE target_node_id = ? AND status = ? "
            "ORDER BY created_at ASC",
            (target_node_id, status),
        ).fetchall()
    return [json.loads(r["payload_json"]) for r in rows]


# ---------------------------------------------------------------------------
# Decisions log (auditoria local)
# ---------------------------------------------------------------------------

def append_decision_log(
    db_path: str | Path,
    origin_node_id: str,
    action: str,
    payload: dict[str, Any],
) -> int:
    """Anade una entrada al log de decisiones. Uso:
    - Decisiones importadas via Pollen (action = receipt.action, payload = receipt).
    - Intentos de emision bloqueados por safety_rules (action = 'blocked_by_safety',
      payload = {packet/delta intentado, violaciones}). Ver §30 Gap 4.
    """
    with connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO decisions_log(origin_node_id, received_at, action, payload_json) "
            "VALUES (?, ?, ?, ?)",
            (origin_node_id, _utcnow_zulu(), action, json.dumps(payload)),
        )
        conn.commit()
        return int(cur.lastrowid)
