"""Configuración pytest para meristem_node.

Añade el directorio del proyecto al sys.path para que `from src.X` resuelva.
Convención mínima: pytest se ejecuta desde `code/meristem_node/`.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
