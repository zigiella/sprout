"""Config de pytest para meristem.

Anade `code/shared` al sys.path para que los schemas compartidos
(`from schemas import ...`) sean importables sin instalar el paquete de
forma editable. Esto mantiene el repo usable directamente con `pytest`
desde el root del proyecto o desde `code/meristem/`.

Tambien expone fixtures compartidos:
- `meristem_settings(tmp_path)` → `Settings` con DB en tmp + shadow off.
- `meristem_client(tmp_path)`   → `TestClient` sobre `create_app(settings)`.
- `canonical_examples()`         → ejemplos JSON canonicos generados por
                                   `code/shared/schemas/examples/`.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

_THIS = Path(__file__).resolve()
_MERISTEM_ROOT = _THIS.parents[1]
_CODE_ROOT = _MERISTEM_ROOT.parent
_SHARED = _CODE_ROOT / "shared"

for path in (_MERISTEM_ROOT, _SHARED):
    path_str = str(path)
    if path.exists() and path_str not in sys.path:
        sys.path.insert(0, path_str)

# Los imports por debajo necesitan los sys.path ya aplicados.
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.main import create_app  # noqa: E402
from src.settings import Settings  # noqa: E402


def _make_settings(tmp_path: Path, shadow: bool = False) -> Settings:
    return Settings(
        ollama_host="http://localhost:11434",
        ollama_model="gemma4:e4b",
        meristem_port=7070,
        db_path=str(tmp_path / "meristem.db"),
        shadow_enabled=shadow,
        gemini_api_key=None,
        shadow_model="gemma-4-31b-it",
    )


@pytest.fixture
def meristem_settings(tmp_path: Path) -> Settings:
    return _make_settings(tmp_path)


@pytest.fixture
def meristem_client(meristem_settings: Settings) -> TestClient:
    app = create_app(meristem_settings)
    with TestClient(app) as client:
        yield client


@pytest.fixture
def canonical_examples() -> Callable[[], dict[str, dict[str, Any]]]:
    """Devuelve los ejemplos canonicos re-construidos desde builders.py
    (no los JSONs, para no depender de `make generate-examples` en CI)."""

    from schemas.examples.builders import canonical_examples as _builders_canonical

    return _builders_canonical
