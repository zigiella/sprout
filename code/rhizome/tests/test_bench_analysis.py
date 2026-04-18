from __future__ import annotations

from pathlib import Path

from bench.analyze_reports import BenchmarkReport, build_observations, build_preliminary_hypothesis, render_markdown_analysis


def _report(model_name: str, *, tok_s: float, p50: float, peak_gib: float) -> BenchmarkReport:
    return BenchmarkReport(
        path=Path(f"{model_name}.json"),
        captured_at="2026-04-18T08:00:00Z",
        model_name=model_name,
        host_label="hp-probook-460-g11",
        host_model="HP ProBook 460 16 inch G11 Notebook PC",
        host_total_memory_bytes=16 * 1024**3,
        requests_ok=1,
        requests_total=1,
        wall_clock_ms_p50=p50,
        wall_clock_ms_p95=p50,
        first_token_latency_ms_p50=p50 * 0.9,
        first_token_latency_ms_p95=p50 * 0.9,
        tokens_per_second_avg=tok_s,
        memory_peak_used_gib_max=peak_gib,
    )


def test_build_observations_highlights_e2b_advantage() -> None:
    reports = [
        _report("gemma2:2b", tok_s=9.0, p50=54000.0, peak_gib=14.4),
        _report("gemma4:e4b", tok_s=6.0, p50=106000.0, peak_gib=15.46),
        _report("gemma2:9b", tok_s=2.3, p50=222000.0, peak_gib=15.46),
    ]

    observations = build_observations(reports)

    assert any("supera a `gemma4:e4b`" in observation for observation in observations)
    assert any("cae por debajo del minimo" in observation for observation in observations)


def test_render_markdown_analysis_includes_hypothesis() -> None:
    reports = [
        _report("gemma2:2b", tok_s=9.0, p50=54000.0, peak_gib=14.4),
        _report("gemma4:e4b", tok_s=6.0, p50=106000.0, peak_gib=15.46),
    ]

    rendered = render_markdown_analysis(reports)
    hypothesis = build_preliminary_hypothesis(reports)

    assert "# Local proxy analysis for Rhizome" in rendered
    assert "## Provisional architecture hypothesis" in rendered
    assert hypothesis[0] in rendered
