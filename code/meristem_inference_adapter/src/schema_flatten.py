"""Flattening de JSON Schema para Gemini `response_schema` (punto 1 de #46).

Gemini API rechaza `$ref` y `$defs`. Pydantic v2 los genera por defecto para
tipos anidados (ej. `PolicyPacket.model_json_schema()` referencia
`SoilMoistureThresholds`, `WateringWindow`, etc. via `$ref`).

Estrategia:
1. `jsonref.replace_refs(schema, proxies=False)` → inline de refs como dicts planos.
2. Serializar/deserializar JSON para desactivar cualquier objeto lazy residual.
3. Podar `$defs` y `definitions` del nivel raiz.
4. Verificar recursivamente que no queda ningun `$ref` en el resultado.

Verificado sobre `PolicyPacket.model_json_schema()` (5 definiciones, 6 refs).
"""

from __future__ import annotations

import copy
import json
from typing import Any

import jsonref


class SchemaFlattenError(ValueError):
    """Error al aplanar un JSON Schema (refs circulares, etc.)."""


def flatten_json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Devuelve el schema con `$ref`/`$defs` resueltos inline.

    Args:
        schema: JSON Schema tal cual lo emite pydantic v2.

    Returns:
        Schema equivalente sin `$ref` ni `$defs`. No muta el input.

    Raises:
        SchemaFlattenError: si tras aplanar quedan `$ref` (ref no resuelta,
            probable ciclo).
    """
    # Deep-copy defensivo — no mutar el input del caller.
    src = copy.deepcopy(schema)

    # jsonref.replace_refs con proxies=False devuelve dicts/listas planos donde
    # fuera posible, pero puede dejar proxies lazy en contextos anidados. El
    # round-trip json.dumps/loads normaliza a estructuras puras.
    #
    # Si el schema contiene un ciclo (A -> B -> A), jsonref lo materializa como
    # estructura Python auto-referencial y json.dumps lanza
    # `ValueError: Circular reference detected`. Convertimos a SchemaFlattenError
    # para dar al caller un error tipado en vez de un ValueError generico.
    resolved = jsonref.replace_refs(src, proxies=False)
    try:
        normalized = json.loads(json.dumps(resolved))
    except ValueError as exc:
        raise SchemaFlattenError(
            f"flatten fallo al normalizar el schema: {exc}. "
            "Probable ciclo entre definiciones."
        ) from exc

    # Poda de contenedores de definiciones en el nivel raiz. Draft-07 usa
    # `definitions`; 2020-12 usa `$defs`. Pydantic v2 emite `$defs`.
    normalized.pop("$defs", None)
    normalized.pop("definitions", None)

    remaining = _find_ref_path(normalized)
    if remaining is not None:
        raise SchemaFlattenError(
            f"flatten incompleto: `$ref` residual en path {remaining!r}. "
            "Probable ciclo o ref externa no resoluble."
        )

    return normalized


def _find_ref_path(node: Any, path: tuple[str, ...] = ()) -> tuple[str, ...] | None:
    """Busca recursivamente el primer `$ref` residual. Devuelve su path o None."""
    if isinstance(node, dict):
        if "$ref" in node:
            return path + ("$ref",)
        for key, value in node.items():
            found = _find_ref_path(value, path + (key,))
            if found is not None:
                return found
    elif isinstance(node, list):
        for i, item in enumerate(node):
            found = _find_ref_path(item, path + (f"[{i}]",))
            if found is not None:
                return found
    return None
