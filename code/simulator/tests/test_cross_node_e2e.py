from __future__ import annotations

from src.cross_node_e2e import (
    build_scenarios,
    extract_json_candidate,
    render_markdown_report,
    render_meristem_prompt,
    summarize_run,
)


def test_scenarios_validate_and_keep_tank_minimum_at_20() -> None:
    scenarios = build_scenarios()
    assert len(scenarios) >= 2
    for scenario in scenarios:
        assert scenario.active_policy.rules.tank_minimum_pct >= 20.0
        assert scenario.snapshot.origin_node_id == "rhizome_01"
        assert scenario.receipt.snapshot_id == scenario.snapshot.snapshot_id


def test_prompt_mentions_cross_node_evidence() -> None:
    scenario = build_scenarios()[0]
    prompt = render_meristem_prompt(scenario)
    assert scenario.snapshot.snapshot_id in prompt
    assert scenario.active_policy.policy_id in prompt
    assert "Evidence digest" in prompt
    assert "pollen_summary" in prompt
    assert "weather_packet" in prompt
    assert "contradiction_alert" in prompt


def test_extract_json_candidate_handles_fenced_noise() -> None:
    candidate = extract_json_candidate("respuesta previa\n```json\n{\"delta_id\": \"d1\"}\n```\n")
    assert candidate == '{"delta_id": "d1"}'


def test_extract_json_candidate_unwraps_policy_delta_wrapper() -> None:
    candidate = extract_json_candidate('{"policy_delta":{"patches":[],"rationale":"ok","ttl_seconds":21600,"priority":"normal"}}')
    assert candidate == '{"patches": [], "rationale": "ok", "ttl_seconds": 21600, "priority": "normal"}'


def test_summarize_run_and_markdown() -> None:
    summary = summarize_run(
        [
            {
                "ok": True,
                "timings_ms": {"end_to_end_ms": 2400.0, "meristem_generate_ms": 2300.0},
                "meristem": {"tokens_per_second": 8.2, "policy_delta": {"delta_id": "delta_1"}},
                "scenario_id": "s1",
            },
            {
                "ok": True,
                "timings_ms": {"end_to_end_ms": 2800.0, "meristem_generate_ms": 2600.0},
                "meristem": {"tokens_per_second": 7.8, "policy_delta": {"delta_id": "delta_2"}},
                "scenario_id": "s2",
            },
        ]
    )
    assert summary["scenarios_ok"] == 2
    assert summary["end_to_end_ms_p50"] == 2600.0
    assert summary["tokens_per_second_avg"] == 8.0

    report = {
        "captured_at": "2026-04-19T07:00:00Z",
        "model": {"name": "gemma4:e4b"},
        "host": {"label": "local-dev"},
        "summary": summary,
        "results": [
            {
                "scenario_id": "s1",
                "ok": True,
                "timings_ms": {
                    "rhizome_export_ms": 1.0,
                    "pollen_relay_ms": 2.0,
                    "meristem_generate_ms": 2300.0,
                    "end_to_end_ms": 2400.0,
                },
                "meristem": {"policy_delta": {"delta_id": "delta_1"}, "tokens_per_second": 8.2},
            }
        ],
    }
    markdown = render_markdown_report(report)
    assert "# Cross-node E2E report" in markdown
    assert "delta_1" in markdown
