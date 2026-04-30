"""IngestService — primera capa: validación + persistencia del bundle.

Responsabilidad única: dado un Bundle (ya validado por Pydantic en
FastAPI), persistirlo en SQLite y devolver el BundleRecord. Si en
algún momento añadimos validación de schema más estricta (firma,
TTL, autoridad), va aquí.
"""

from __future__ import annotations

from pathlib import Path

from .persistence import insert_bundle, DEFAULT_DB_PATH
from .schemas import Bundle, BundleRecord


def ingest(bundle: Bundle, db_path: Path | str = DEFAULT_DB_PATH) -> BundleRecord:
    """Valida (FastAPI ya lo hizo via Pydantic) y persiste. Devuelve record.

    Aquí pueden ir validaciones adicionales en v1+:
    - signature verification (cuando el bundle venga firmado)
    - TTL del bundle (rechazar bundles "demasiado viejos")
    - autoridad del source_pollen_id (lista blanca)

    Para v0, solo persistencia + trazabilidad de id.
    """
    return insert_bundle(bundle, db_path=db_path)
