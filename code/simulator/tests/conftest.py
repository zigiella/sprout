"""Config de pytest para simulator."""

from __future__ import annotations

import sys
from pathlib import Path

_THIS = Path(__file__).resolve()
_SIMULATOR_ROOT = _THIS.parents[1]
_CODE_ROOT = _SIMULATOR_ROOT.parent
_SHARED = _CODE_ROOT / "shared"

for path in (_SIMULATOR_ROOT, _SHARED):
    path_str = str(path)
    if path.exists() and path_str not in sys.path:
        sys.path.insert(0, path_str)
