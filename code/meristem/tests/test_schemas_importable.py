"""Verifica que Meristem puede importar los 6 schemas canonicos desde
`code/shared/schemas/` sin duplicarlos.

El `conftest.py` de esta suite anade `code/shared` al sys.path, replicando
lo que haria un `pip install -e ../shared` en un entorno real.
"""

from __future__ import annotations


def test_six_canonical_schemas_importable() -> None:
    from schemas import (
        ContradictionAlert,
        DecisionReceipt,
        PolicyDelta,
        PolicyPacket,
        RhizomeSnapshot,
        WeatherPacket,
    )

    # Sanity: cada uno debe ser una clase Pydantic con campo schema_version.
    for cls in (
        ContradictionAlert,
        DecisionReceipt,
        PolicyDelta,
        PolicyPacket,
        RhizomeSnapshot,
        WeatherPacket,
    ):
        assert hasattr(cls, "model_fields"), cls
        assert "schema_version" in cls.model_fields, cls
