"""Config de pytest para meristem.

Anade `code/shared` al sys.path para que los schemas compartidos
(`from schemas import ...`) sean importables sin instalar el paquete de
forma editable. Esto mantiene el repo usable directamente con `pytest`
desde el root del proyecto o desde `code/meristem/`.
"""

from __future__ import annotations

import sys
from pathlib import Path

_THIS = Path(__file__).resolve()
_MERISTEM_ROOT = _THIS.parents[1]
_CODE_ROOT = _MERISTEM_ROOT.parent
_SHARED = _CODE_ROOT / "shared"

for path in (_MERISTEM_ROOT, _SHARED):
    path_str = str(path)
    if path.exists() and path_str not in sys.path:
        sys.path.insert(0, path_str)
