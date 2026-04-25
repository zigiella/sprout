from __future__ import annotations

from bench.common import percentile, slugify
from bench.run_ollama_benchmark import build_phase_plan, summarize_results


def test_percentile_interpolates() -> None:
    assert percentile([10.0, 20.0, 30.0, 40.0], 0.50) == 25.0
    assert percentile([10.0, 20.0, 30.0, 40.0], 0.95) == 38.5


def test_slugify_compacts_hardware_labels() -> None:
    assert slugify("HP ProBook 460 16 inch G11") == "hp-probook-460-16-inch-g11"


def test_summarize_results_aggregates_metrics() -> None:
    summary = summarize_results(
        [
            {
                "ok": True,
                "modality": "text",
                "wall_clock_ms": 1000.0,
                "first_token_latency_ms": 200.0,
                "tokens_per_second": 8.0,
                "memory_peak_used_bytes": 4 * 1024**3,
            },
            {
                "ok": True,
                "modality": "text",
                "wall_clock_ms": 2000.0,
                "first_token_latency_ms": 350.0,
                "tokens_per_second": 6.0,
                "memory_peak_used_bytes": 5 * 1024**3,
            },
        ],
        repeat_count=1,
    )

    assert summary["requests_total"] == 2
    assert summary["requests_failed"] == 0
    assert summary["wall_clock_ms_p50"] == 1500.0
    assert summary["tokens_per_second_avg"] == 7.0
    assert summary["memory_peak_used_gib_max"] == 5.0
    assert summary["result_class"] == "demo-pass"
    assert summary["by_modality"]["text"]["requests_total"] == 2


def test_summarize_results_groups_by_phase_and_modality() -> None:
    summary = summarize_results(
        [
            {
                "ok": True,
                "phase": "cold",
                "modality": "text",
                "wall_clock_ms": 2200.0,
                "first_token_latency_ms": 800.0,
                "tokens_per_second": 5.2,
                "memory_peak_used_bytes": 6 * 1024**3,
            },
            {
                "ok": True,
                "phase": "warm",
                "modality": "multimodal",
                "wall_clock_ms": 1400.0,
                "first_token_latency_ms": 350.0,
                "tokens_per_second": 7.5,
                "memory_peak_used_bytes": 6 * 1024**3,
            },
            {
                "ok": True,
                "phase": "repeat",
                "modality": "multimodal",
                "wall_clock_ms": 1300.0,
                "first_token_latency_ms": 320.0,
                "tokens_per_second": 7.1,
                "memory_peak_used_bytes": 6 * 1024**3,
            },
            {
                "ok": True,
                "phase": "repeat",
                "modality": "multimodal",
                "wall_clock_ms": 1350.0,
                "first_token_latency_ms": 330.0,
                "tokens_per_second": 6.9,
                "memory_peak_used_bytes": 6 * 1024**3,
            },
        ],
        repeat_count=3,
        phase_repeat_counts={"cold": 1, "warm": 1, "repeat": 3},
    )

    assert summary["by_phase"]["cold"]["result_class"] == "demo-pass"
    assert summary["by_phase"]["repeat"]["result_class"] == "engineering-pass"
    assert summary["by_modality"]["multimodal"]["requests_total"] == 3
    assert summary["by_phase_and_modality"]["repeat"]["multimodal"]["requests_total"] == 2


def test_build_phase_plan_for_cold_warm_repeat() -> None:
    plan = build_phase_plan("cold,warm,repeat", keep_alive="30m", repeat_count=4)
    assert [phase.name for phase in plan] == ["cold", "warm", "repeat"]
    assert plan[0].keep_alive == "0"
    assert plan[1].warmup_before_phase is True
    assert plan[2].repeat_count == 4
