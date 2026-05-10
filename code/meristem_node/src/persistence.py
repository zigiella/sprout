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
    evidence_refs TEXT NOT NULL,  -- JSON list of bundle_ids
    -- Sub-PR aditivo dia 23 (forward-compat con feature beta voz->politica):
    policy_origin TEXT NOT NULL DEFAULT 'meristem-durable',
    policy_scope TEXT NOT NULL DEFAULT 'durable'
);

CREATE INDEX IF NOT EXISTS idx_policies_target
    ON policies(target_node_id, emitted_at DESC);

-- NOTA: indice idx_policies_target_scope se crea en _run_migrations
-- porque referencia a policy_scope, columna añadida en sub-PR día 23.
-- El executescript del SCHEMA falla si la columna aún no existe en BBDDs
-- antiguas; la migración aditiva crea la columna primero y luego el índice.

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

CREATE TABLE IF NOT EXISTS pollen_sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    direction TEXT NOT NULL,  -- 'in' (Pollen->Meristem) | 'out' (Meristem->Pollen)
    event TEXT NOT NULL,      -- WSEvent value
    payload_json TEXT NOT NULL,
    trace_id TEXT,            -- nullable
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pollen_sync_log_created
    ON pollen_sync_log(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_pollen_sync_log_trace
    ON pollen_sync_log(trace_id);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    operator_id TEXT NOT NULL,
    role TEXT NOT NULL,           -- 'user' | 'assistant'
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_conversations_conv_id
    ON conversations(conversation_id, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_conversations_operator
    ON conversations(operator_id, created_at DESC);
"""


def init_db(db_path: Path | str = DEFAULT_DB_PATH) -> None:
    """Crea tablas e índices si no existen. Idempotente.

    Ejecuta también migraciones aditivas para BBDDs anteriores al
    sub-PR de día 23 (policy_origin / policy_scope columns).
    """
    db_path = Path(db_path)
    with sqlite3.connect(db_path) as con:
        con.executescript(SCHEMA)
        _run_migrations(con)


def _run_migrations(con: sqlite3.Connection) -> None:
    """Migraciones aditivas idempotentes para BBDDs ya creadas.

    Día 23: añade `policy_origin` y `policy_scope` a tabla `policies`
    si todavía no existen (BBDDs creadas antes del sub-PR aditivo).
    Defaults preservan retrocompatibilidad — policies antiguas se
    interpretan como meristem-durable + durable.
    """
    cols = {row[1] for row in con.execute("PRAGMA table_info(policies)").fetchall()}
    if "policy_origin" not in cols:
        con.execute(
            "ALTER TABLE policies ADD COLUMN policy_origin TEXT NOT NULL "
            "DEFAULT 'meristem-durable'"
        )
    if "policy_scope" not in cols:
        con.execute(
            "ALTER TABLE policies ADD COLUMN policy_scope TEXT NOT NULL "
            "DEFAULT 'durable'"
        )
    # Indice puede crearse de forma idempotente independientemente.
    con.execute(
        "CREATE INDEX IF NOT EXISTS idx_policies_target_scope "
        "ON policies(target_node_id, policy_scope, emitted_at DESC)"
    )


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
            (policy_id, emitted_at, target_node_id, raw_json, evidence_refs,
             policy_origin, policy_scope)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.policy_id,
                record.emitted_at.isoformat(),
                record.target_node_id,
                record.raw_json,
                json.dumps(record.evidence_refs),
                policy.policy_origin,
                policy.policy_scope,
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


def count_policies_by_scope(
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict[str, int]:
    """Para `/health` y demo: distribución de policies por scope.

    Sub-PR aditivo día 23. Cuando la feature beta voz→política
    (Mini-Evaluator Pollen, PR #92) entregue policies transitorias,
    este desglose visibiliza el reparto durable vs transient en demo
    y writeup.
    """
    with _connect(db_path) as con:
        rows = con.execute(
            "SELECT policy_scope, COUNT(*) AS c FROM policies GROUP BY policy_scope"
        ).fetchall()
    return {r["policy_scope"]: int(r["c"]) for r in rows}


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

        # 2. Policies count + desglose por scope + última policy
        pol_count = con.execute(
            "SELECT COUNT(*) AS c FROM policies WHERE target_node_id = ?",
            (target_node_id,),
        ).fetchone()
        policies_emitted = int(pol_count["c"]) if pol_count else 0

        # Desglose por scope (durable / transient) — sub-PR aditivo día 23
        scope_rows = con.execute(
            """
            SELECT policy_scope, COUNT(*) AS c FROM policies
            WHERE target_node_id = ?
            GROUP BY policy_scope
            """,
            (target_node_id,),
        ).fetchall()
        scope_counts = {r["policy_scope"]: int(r["c"]) for r in scope_rows}
        policies_durable_count = scope_counts.get("durable", 0)
        policies_transient_count = scope_counts.get("transient", 0)

        latest_pol_row = con.execute(
            """
            SELECT policy_id, emitted_at, raw_json, policy_origin, policy_scope
            FROM policies
            WHERE target_node_id = ?
            ORDER BY emitted_at DESC LIMIT 1
            """,
            (target_node_id,),
        ).fetchone()

        latest_policy_id = None
        latest_policy_emitted_at = None
        latest_policy_mode = None
        latest_policy_valid_until = None
        latest_policy_origin = None
        latest_policy_scope = None
        if latest_pol_row:
            latest_policy_id = latest_pol_row["policy_id"]
            latest_policy_emitted_at = latest_pol_row["emitted_at"]
            latest_policy_origin = latest_pol_row["policy_origin"]
            latest_policy_scope = latest_pol_row["policy_scope"]
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
        "policies_durable_count": policies_durable_count,
        "policies_transient_count": policies_transient_count,
        "latest_policy_id": latest_policy_id,
        "latest_policy_emitted_at": latest_policy_emitted_at,
        "latest_policy_mode": latest_policy_mode,
        "latest_policy_valid_until": latest_policy_valid_until,
        "latest_policy_origin": latest_policy_origin,
        "latest_policy_scope": latest_policy_scope,
        "latest_reason_code": latest_reason_code,
        "latest_rule_applied": latest_rule_applied,
    }


# ---------------------------------------------------------------------------
# Pollen sync log (WebSocket protocol audit trail)
# ---------------------------------------------------------------------------


def log_ws_event(
    direction: str,
    event: str,
    payload: dict[str, Any],
    trace_id: str | None = None,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> int:
    """Persiste un mensaje WS para audit/demo.

    Args:
        direction: 'in' (Pollen→Meristem) | 'out' (Meristem→Pollen)
        event: nombre del evento (WSEvent value)
        payload: dict con el payload del mensaje
        trace_id: opcional, para correlacionar request/response

    Returns:
        id auto-incrementado de la fila insertada
    """
    if direction not in ("in", "out"):
        raise ValueError(f"direction debe ser 'in' o 'out', no {direction!r}")
    with _connect(db_path) as con:
        cur = con.execute(
            """
            INSERT INTO pollen_sync_log
            (direction, event, payload_json, trace_id, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                direction,
                event,
                json.dumps(payload, ensure_ascii=False),
                trace_id,
                datetime.now().isoformat(),
            ),
        )
        return int(cur.lastrowid or 0)


def count_ws_events_by_event(
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict[str, int]:
    """Para `/health`: distribución de eventos WS recibidos/emitidos.

    Útil al jurado: muestra el flujo bidireccional persistente con Pollen.
    """
    with _connect(db_path) as con:
        rows = con.execute(
            "SELECT event, COUNT(*) AS c FROM pollen_sync_log GROUP BY event"
        ).fetchall()
    return {r["event"]: int(r["c"]) for r in rows}


def get_recent_ws_events(
    limit: int = 20,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    """Devuelve los últimos N eventos WS en orden descendente.

    Útil para `/sync-state` endpoint que la UI Meristem va a leer.
    """
    with _connect(db_path) as con:
        rows = con.execute(
            """
            SELECT id, direction, event, payload_json, trace_id, created_at
            FROM pollen_sync_log
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    result = []
    for r in rows:
        try:
            payload = json.loads(r["payload_json"])
        except json.JSONDecodeError:
            payload = {}
        result.append({
            "id": int(r["id"]),
            "direction": r["direction"],
            "event": r["event"],
            "payload": payload,
            "trace_id": r["trace_id"],
            "created_at": r["created_at"],
        })
    return result


# ---------------------------------------------------------------------------
# Listas recientes (para UI: zona "visitas recibidas" + "policies emitidas")
# ---------------------------------------------------------------------------


def list_recent_bundles(
    limit: int = 20, db_path: Path | str = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    """Devuelve los últimos N bundles entregados a Meristem (orden DESC).

    Cada item incluye también el reason_code de la decision que se
    tomó sobre ese bundle (joineando contra decisions). Si el bundle
    aún no tiene decision (no debería pasar tras /visit completo),
    reason_code es None.
    """
    with _connect(db_path) as con:
        rows = con.execute(
            """
            SELECT
                b.bundle_id,
                b.received_at,
                b.source_pollen_id,
                b.target_rhizome_id,
                b.active_policy_id,
                d.reason_code,
                d.rule_applied
            FROM bundles b
            LEFT JOIN decisions d ON d.bundle_id = b.bundle_id
            ORDER BY b.received_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "bundle_id": r["bundle_id"],
            "received_at": r["received_at"],
            "source_pollen_id": r["source_pollen_id"],
            "target_rhizome_id": r["target_rhizome_id"],
            "active_policy_id": r["active_policy_id"],
            "reason_code": r["reason_code"],
            "rule_applied": r["rule_applied"],
        }
        for r in rows
    ]


def list_recent_policies(
    limit: int = 20, db_path: Path | str = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    """Devuelve las últimas N policies emitidas (orden DESC por emitted_at).

    Cada item incluye policy_id, target_node_id, mode, valid_until,
    rationale (recortado si es largo) y evidencia.
    """
    with _connect(db_path) as con:
        rows = con.execute(
            """
            SELECT policy_id, emitted_at, target_node_id, raw_json, evidence_refs
            FROM policies
            ORDER BY emitted_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    result = []
    for r in rows:
        try:
            packet = json.loads(r["raw_json"])
        except json.JSONDecodeError:
            packet = {}
        try:
            ev_refs = json.loads(r["evidence_refs"])
        except (json.JSONDecodeError, TypeError):
            ev_refs = []
        rationale = packet.get("rationale", "")
        # Recortamos rationale técnico para list view (full visible en drill-down)
        rationale_short = (
            rationale if len(rationale) <= 160 else rationale[:157] + "..."
        )
        result.append({
            "policy_id": r["policy_id"],
            "emitted_at": r["emitted_at"],
            "target_node_id": r["target_node_id"],
            "mode_default": packet.get("mode_default"),
            "valid_until": packet.get("valid_until"),
            "rationale_short": rationale_short,
            "evidence_refs": ev_refs,
        })
    return result


# ---------------------------------------------------------------------------
# Conversaciones (chat read-only, fase 3 plan IA dia 19)
# ---------------------------------------------------------------------------


def insert_conversation_message(
    conversation_id: str,
    operator_id: str,
    role: str,
    content: str,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> int:
    """Persiste un mensaje de la conversacion (user o assistant).

    Returns: id auto-incrementado de la fila insertada.
    """
    if role not in ("user", "assistant"):
        raise ValueError(f"role debe ser user o assistant, no {role!r}")
    with _connect(db_path) as con:
        cur = con.execute(
            """
            INSERT INTO conversations
            (conversation_id, operator_id, role, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                conversation_id,
                operator_id,
                role,
                content,
                datetime.now().isoformat(),
            ),
        )
        return int(cur.lastrowid or 0)


def get_conversation_history(
    conversation_id: str,
    limit: int = 20,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    """Devuelve los ultimos N mensajes de una conversacion en orden ASC.

    Para construir el contexto del LLM en chats con continuidad.
    """
    with _connect(db_path) as con:
        rows = con.execute(
            """
            SELECT conversation_id, operator_id, role, content, created_at
            FROM conversations
            WHERE conversation_id = ?
            ORDER BY id ASC
            LIMIT ?
            """,
            (conversation_id, limit),
        ).fetchall()
    return [
        {
            "conversation_id": r["conversation_id"],
            "operator_id": r["operator_id"],
            "role": r["role"],
            "content": r["content"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]


def count_conversation_messages(
    db_path: Path | str = DEFAULT_DB_PATH,
) -> dict[str, int]:
    """Para /health: contadores totales de mensajes por rol.

    Util para demo/audit: muestra que el chat se ha usado.
    """
    with _connect(db_path) as con:
        rows = con.execute(
            "SELECT role, COUNT(*) AS c FROM conversations GROUP BY role"
        ).fetchall()
    return {r["role"]: int(r["c"]) for r in rows}
