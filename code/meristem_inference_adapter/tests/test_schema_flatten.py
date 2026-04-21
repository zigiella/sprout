"""Tests de `schema_flatten` — punto 1 de #46.

Verificaciones:
- Schema simple sin refs se devuelve equivalente (no muta, no falla).
- Input no se muta (el deep-copy defensivo funciona).
- PolicyPacket.model_json_schema() (pydantic v2 real) queda sin $ref ni $defs.
- Un ref circular deberia disparar SchemaFlattenError (caso defensivo).
"""

from __future__ import annotations

import copy
import json
from typing import Any

import pytest

from src.schema_flatten import SchemaFlattenError, flatten_json_schema


def _json_equal(a: Any, b: Any) -> bool:
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def _has_ref_or_defs(obj: Any) -> bool:
    s = json.dumps(obj)
    return '"$ref"' in s or '"$defs"' in s or '"definitions"' in s


def test_flatten_schema_sin_refs_es_equivalente():
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name"],
    }
    out = flatten_json_schema(schema)
    assert _json_equal(out, schema)


def test_flatten_no_muta_input():
    schema = {
        "$defs": {"Foo": {"type": "string"}},
        "type": "object",
        "properties": {"foo": {"$ref": "#/$defs/Foo"}},
    }
    original = copy.deepcopy(schema)
    _ = flatten_json_schema(schema)
    assert _json_equal(schema, original), "el input original fue mutado"


def test_flatten_inline_ref_basico():
    schema = {
        "$defs": {"Foo": {"type": "string", "minLength": 1}},
        "type": "object",
        "properties": {"foo": {"$ref": "#/$defs/Foo"}},
        "required": ["foo"],
    }
    out = flatten_json_schema(schema)
    assert "$defs" not in out
    assert out["properties"]["foo"] == {"type": "string", "minLength": 1}
    assert not _has_ref_or_defs(out)


def test_flatten_legacy_definitions_tambien_se_eliminan():
    # draft-07 usa `definitions` en vez de `$defs`. jsonref los resuelve igual.
    schema = {
        "definitions": {"Foo": {"type": "string"}},
        "type": "object",
        "properties": {"foo": {"$ref": "#/definitions/Foo"}},
    }
    out = flatten_json_schema(schema)
    assert "definitions" not in out
    assert out["properties"]["foo"] == {"type": "string"}


def test_flatten_policy_packet_real():
    """El test critico del punto 1 del comentario de #46."""
    # Import tardio para que los tests que no necesitan shared sigan corriendo
    # si el path no estuviera configurado.
    from schemas.policy_packet import PolicyPacket

    raw = PolicyPacket.model_json_schema()
    # Pre-condicion: el schema original tiene refs (si no, este test no valida nada).
    assert "$defs" in raw, "PolicyPacket deberia generar $defs en pydantic v2"
    assert _has_ref_or_defs(raw)

    flat = flatten_json_schema(raw)

    assert not _has_ref_or_defs(flat), (
        "PolicyPacket aplanado conserva $ref o $defs — Gemini rechazaria este schema"
    )
    # Sanity estructural: el objeto aplanado sigue siendo un schema de tipo objeto
    # con las propiedades principales.
    assert flat["type"] == "object"
    assert "properties" in flat
    assert "rules" in flat["properties"]
    # Y `rules` expandido internamente, no como {"$ref": "..."}
    rules = flat["properties"]["rules"]
    assert "properties" in rules
    assert "soil_moisture_thresholds" in rules["properties"]


def test_flatten_ref_circular_levanta_error():
    # $ref circular: A -> B -> A. jsonref con proxies=False puede dejar el
    # segundo nivel sin resolver porque detecta el ciclo.
    schema: dict[str, Any] = {
        "$defs": {
            "A": {"type": "object", "properties": {"next": {"$ref": "#/$defs/B"}}},
            "B": {"type": "object", "properties": {"next": {"$ref": "#/$defs/A"}}},
        },
        "type": "object",
        "properties": {"root": {"$ref": "#/$defs/A"}},
    }
    # Esto podria completarse sin error (jsonref repite la estructura hasta una
    # profundidad) o disparar SchemaFlattenError. Ambos son aceptables; el test
    # fija que NO producimos un dict con `$ref` sin avisar.
    try:
        out = flatten_json_schema(schema)
    except SchemaFlattenError:
        return  # ok, ciclo detectado
    assert not _has_ref_or_defs(out), (
        "schema con ciclo aplanado silenciosamente conservo refs residuales"
    )
