"""Harness de comparacion local vs sombra.

Stub. El cuerpo entra en el PR del policy_engine junto con su bitacora.
"""

from __future__ import annotations


def compare_outputs(local_output: str, shadow_output: str) -> dict[str, object]:
    """Compara dos outputs de texto. Stub que solo reporta igualdad exacta."""
    return {
        "agreement": int(local_output.strip() == shadow_output.strip()),
        "local_len": len(local_output),
        "shadow_len": len(shadow_output),
    }
