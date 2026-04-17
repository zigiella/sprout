"""Round-trip tests for committed canonical shared-schema examples."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from schemas.examples.generate_examples import ALL_EXAMPLE_SPECS, CORE_EXAMPLE_SPECS, EXAMPLES_DIR, stale_examples


def _example_path(filename: str) -> Path:
    return EXAMPLES_DIR / filename


@pytest.mark.parametrize("spec", CORE_EXAMPLE_SPECS, ids=lambda spec: spec.filename)
def test_required_core_examples_exist(spec) -> None:
    assert _example_path(spec.filename).exists()


@pytest.mark.parametrize("spec", ALL_EXAMPLE_SPECS, ids=lambda spec: spec.filename)
def test_committed_examples_roundtrip(spec) -> None:
    payload = json.loads(_example_path(spec.filename).read_text(encoding="utf-8"))

    parsed = spec.model_cls.model_validate(payload)
    dumped = parsed.model_dump(mode="json")
    reparsed = spec.model_cls.model_validate(dumped)

    assert dumped == payload
    assert reparsed.model_dump(mode="json") == dumped


def test_generated_examples_are_up_to_date() -> None:
    assert stale_examples() == []
