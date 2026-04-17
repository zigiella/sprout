"""Persistencia local de Meristem.

SQLite, sin servidor externo. En el bootstrap solo garantizamos que las
tablas existen para que el PR del policy_engine pueda empezar a escribir.

Tablas (spec 12_meristem_spec.md §7):
- `evidence`: snapshots, alerts, packets entrantes (raw JSON).
- `policies`: policy_packets emitidos.
- `deltas`: policy_deltas propuestos/validados/revocados.
- `decisions_log`: decisiones importadas via Pollen para auditoria.
- `shadow_comparisons`: diffs local vs sombra (solo si SHADOW_ENABLED).
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    received_at TEXT NOT NULL,
    kind TEXT NOT NULL,
    origin_node_id TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS policies (
    policy_id TEXT PRIMARY KEY,
    target_node_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    valid_until TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS deltas (
    delta_id TEXT PRIMARY KEY,
    target_node_id TEXT NOT NULL,
    base_policy_id TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decisions_log (
    decision_id TEXT PRIMARY KEY,
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
    """Context manager que devuelve una conexion SQLite con row_factory."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
