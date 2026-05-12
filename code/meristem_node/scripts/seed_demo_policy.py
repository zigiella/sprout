"""Seed de 1 policy demo en la BBDD para que el primer 'cargar política'
desde Pollen devuelva algo visible.

Uso:
    cd code/meristem_node
    python scripts/seed_demo_policy.py [--db-path PATH] [--target rhizome_01]

Por defecto seedea para target=rhizome_01 contra la BBDD que use Meristem
(env MERISTEM_DB_PATH o `meristem_node.db` en cwd).
"""
from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db-path",
        default=None,
        help="Ruta SQLite. Por defecto la que usa Meristem (env MERISTEM_DB_PATH o ./meristem_node.db).",
    )
    parser.add_argument(
        "--target",
        default="rhizome_01",
        help="target_node_id de la policy demo (default: rhizome_01).",
    )
    args = parser.parse_args()

    # Importar tras parsear args (init_db lee env)
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))
    from src import persistence
    from src.schemas import PolicyPacket

    db_path = args.db_path or str(persistence.DEFAULT_DB_PATH)
    persistence.init_db(db_path)

    policy = PolicyPacket(
        schema_version="1.0",
        policy_id=f"pkt_meristem_demo_{uuid.uuid4().hex[:8]}",
        target_node_id=args.target,
        valid_until=datetime.now() + timedelta(days=7),
        mode_default="normal",
        rules={
            "soil_dry_threshold_pct": 30,
            "tank_minimum_pct": 20,
            "max_seconds_per_event": 60,
            "watering_windows": ["06:00-08:00", "20:00-21:30"],
            "daily_budget_ml": 2000,
        },
        rationale=(
            "Policy seedeada para demo: baseline normal coherente con "
            "campaña primavera, sin alertas activas. El operador la "
            "verá como 'política actualizada' al cargarla desde Pollen."
        ),
        signature="<demo-seed-v0>",
        policy_origin="meristem-durable",
        policy_scope="durable",
    )

    record = persistence.insert_policy(
        policy=policy,
        evidence_refs=[],  # seed manual, no viene de un bundle
        db_path=db_path,
    )
    print(f"OK seed policy {record.policy_id} para target={args.target}")
    print(f"   emitted_at: {record.emitted_at.isoformat()}")
    print(f"   db_path:    {db_path}")
    print(f"   valid_until {policy.valid_until.isoformat()}")
    print(f"   mode:       {policy.mode_default}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
