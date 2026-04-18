from __future__ import annotations

from bench.common import percentile, slugify
from bench.run_ollama_benchmark import summarize_results


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
                "wall_clock_ms": 1000.0,
                "first_token_latency_ms": 200.0,
                "tokens_per_second": 8.0,
                "memory_peak_used_bytes": 4 * 1024**3,
            },
            {
                "ok": True,
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
