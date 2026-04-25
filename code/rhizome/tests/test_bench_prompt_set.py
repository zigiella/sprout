from __future__ import annotations

import json

from bench.build_prompt_set import build_prompt_records, render_prompt_set, stale_prompt_set
from bench.common import DEFAULT_PROMPT_SET_PATH
from bench.render_synthetic_images import ASSETS_DIR, stale_assets


def test_prompt_set_has_enough_records() -> None:
    records = build_prompt_records()
    assert len(records) >= 20
    assert len({record["id"] for record in records}) == len(records)


def test_prompt_set_has_representative_categories() -> None:
    categories = {record["category"] for record in build_prompt_records()}
    assert {"decision_text", "policy_delta", "receipt_audit", "weather", "safety", "decision_multimodal"} <= categories


def test_prompt_set_includes_multimodal_records() -> None:
    records = build_prompt_records()
    multimodal = [record for record in records if record["modality"] == "multimodal"]
    assert len(multimodal) >= 5
    assert all(record["image_paths"] for record in multimodal)
    for record in multimodal:
        for relative_path in record["image_paths"]:
            assert (DEFAULT_PROMPT_SET_PATH.parent / relative_path).exists()


def test_rendered_prompt_set_is_valid_jsonl() -> None:
    lines = [line for line in render_prompt_set().splitlines() if line.strip()]
    assert len(lines) >= 20
    first = json.loads(lines[0])
    assert "prompt" in first
    assert "max_tokens" in first


def test_committed_prompt_set_is_up_to_date() -> None:
    assert DEFAULT_PROMPT_SET_PATH.exists()
    assert stale_prompt_set() is False


def test_synthetic_assets_are_up_to_date() -> None:
    assert ASSETS_DIR.exists()
    assert stale_assets() is False
