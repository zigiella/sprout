"""Analyze committed benchmark reports and derive provisional architecture notes."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common import BENCHMARKS_DIR, bytes_to_gib, utc_now_iso

RHIZOME_MIN_TEXT_TOKENS_PER_SEC = 5.0
RHIZOME_MAX_MULTIMODAL_LATENCY_MS = 15_000.0
MIN_SAFE_MEMORY_HEADROOM_GIB = 0.5
DEFAULT_ANALYSIS_OUTPUT = BENCHMARKS_DIR / "2026-04-18_local-proxy-analysis.md"


@dataclass(frozen=True)
class BenchmarkReport:
    """Compact benchmark view used for comparisons."""

    path: Path
    captured_at: str
    model_name: str
    host_label: str
    host_model: str | None
    host_total_memory_bytes: int | None
    requests_ok: int
    requests_total: int
    wall_clock_ms_p50: float | None
    wall_clock_ms_p95: float | None
    first_token_latency_ms_p50: float | None
    first_token_latency_ms_p95: float | None
    tokens_per_second_avg: float | None
    memory_peak_used_gib_max: float | None

    @property
    def requests_ok_display(self) -> str:
        return f"{self.requests_ok}/{self.requests_total}"

    @property
    def memory_headroom_gib(self) -> float | None:
        if self.host_total_memory_bytes is None or self.memory_peak_used_gib_max is None:
            return None
        total_gib = bytes_to_gib(self.host_total_memory_bytes)
        if total_gib is None:
            return None
        return round(total_gib - self.memory_peak_used_gib_max, 3)

    @property
    def meets_text_threshold(self) -> bool | None:
        if self.tokens_per_second_avg is None:
            return None
        return self.tokens_per_second_avg >= RHIZOME_MIN_TEXT_TOKENS_PER_SEC

    @property
    def meets_headroom_threshold(self) -> bool | None:
        headroom = self.memory_headroom_gib
        if headroom is None:
            return None
        return headroom >= MIN_SAFE_MEMORY_HEADROOM_GIB


def _load_report(path: Path) -> BenchmarkReport:
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary = payload["summary"]
    host = payload["host"]
    model = payload["model"]
    return BenchmarkReport(
        path=path,
        captured_at=payload["captured_at"],
        model_name=model["name"],
        host_label=host.get("label") or host.get("hostname") or "unknown-host",
        host_model=host.get("model"),
        host_total_memory_bytes=host.get("total_memory_bytes"),
        requests_ok=summary["requests_ok"],
        requests_total=summary["requests_total"],
        wall_clock_ms_p50=summary.get("wall_clock_ms_p50"),
        wall_clock_ms_p95=summary.get("wall_clock_ms_p95"),
        first_token_latency_ms_p50=summary.get("first_token_latency_ms_p50"),
        first_token_latency_ms_p95=summary.get("first_token_latency_ms_p95"),
        tokens_per_second_avg=summary.get("tokens_per_second_avg"),
        memory_peak_used_gib_max=summary.get("memory_peak_used_gib_max"),
    )


def load_benchmark_reports(directory: Path = BENCHMARKS_DIR) -> list[BenchmarkReport]:
    reports: list[BenchmarkReport] = []
    for path in sorted(directory.glob("*.json")):
        reports.append(_load_report(path))
    reports.sort(key=lambda report: (report.captured_at, report.model_name))
    return reports


def _ratio_pct(faster_value: float | None, slower_value: float | None) -> float | None:
    if faster_value is None or slower_value is None or slower_value == 0:
        return None
    return round(((faster_value / slower_value) - 1.0) * 100.0, 1)


def _reduction_pct(reference_value: float | None, lower_value: float | None) -> float | None:
    if reference_value is None or lower_value is None or reference_value == 0:
        return None
    return round((1.0 - (lower_value / reference_value)) * 100.0, 1)


def build_observations(reports: list[BenchmarkReport]) -> list[str]:
    observations: list[str] = []
    by_host: dict[str, dict[str, BenchmarkReport]] = {}
    for report in reports:
        by_host.setdefault(report.host_label, {})[report.model_name] = report

    for host_label, host_reports in by_host.items():
        e2b_proxy = host_reports.get("gemma2:2b")
        gemma4_e4b = host_reports.get("gemma4:e4b")
        e4b_proxy = host_reports.get("gemma2:9b")

        if e2b_proxy and gemma4_e4b:
            tok_gain = _ratio_pct(e2b_proxy.tokens_per_second_avg, gemma4_e4b.tokens_per_second_avg)
            lat_reduction = _reduction_pct(gemma4_e4b.wall_clock_ms_p50, e2b_proxy.wall_clock_ms_p50)
            observations.append(
                f"En `{host_label}`, el proxy E2B (`gemma2:2b`) supera a `gemma4:e4b` con "
                f"{tok_gain}% mas tok/s y {lat_reduction}% menos latencia p50."
            )

        if e2b_proxy and e4b_proxy:
            tok_gain = _ratio_pct(e2b_proxy.tokens_per_second_avg, e4b_proxy.tokens_per_second_avg)
            lat_reduction = _reduction_pct(e4b_proxy.wall_clock_ms_p50, e2b_proxy.wall_clock_ms_p50)
            observations.append(
                f"En `{host_label}`, el proxy E2B (`gemma2:2b`) supera al proxy E4B (`gemma2:9b`) con "
                f"{tok_gain}% mas tok/s y {lat_reduction}% menos latencia p50."
            )

        if e4b_proxy and e4b_proxy.meets_text_threshold is False:
            observations.append(
                f"`{e4b_proxy.model_name}` cae por debajo del minimo de Rhizome (`{RHIZOME_MIN_TEXT_TOKENS_PER_SEC}` tok/s) "
                f"con `{e4b_proxy.tokens_per_second_avg}` tok/s."
            )

        if gemma4_e4b and gemma4_e4b.meets_headroom_threshold is False:
            observations.append(
                f"`gemma4:e4b` deja solo `{gemma4_e4b.memory_headroom_gib}` GiB de headroom en `{host_label}`, "
                f"por debajo del margen prudente de `{MIN_SAFE_MEMORY_HEADROOM_GIB}` GiB."
            )

    return observations


def build_preliminary_hypothesis(reports: list[BenchmarkReport]) -> list[str]:
    if not reports:
        return [
            "Aun no hay reports comprometidos; la hipotesis de arquitectura sigue bloqueada hasta tener baselines.",
        ]

    return [
        "Hipotesis provisional: Rhizome debe optimizar el loop local de decision para modelos clase E2B; "
        "cualquier E4B queda fuera del camino critico hasta que Jetson demuestre lo contrario.",
        f"Umbral provisional para mantener Ollama como primario en Jetson: >=`{RHIZOME_MIN_TEXT_TOKENS_PER_SEC}` tok/s "
        f"en texto sostenido, p95 multimodal <=`{int(RHIZOME_MAX_MULTIMODAL_LATENCY_MS/1000)}` s, sin OOM y con al menos "
        f"`{MIN_SAFE_MEMORY_HEADROOM_GIB}` GiB de headroom tras warm restart.",
        "Candidato a fallback `llama.cpp`: cualquier configuracion de Ollama que no cargue, caiga por debajo del umbral de tok/s, "
        "supere el p95 multimodal o pierda estabilidad entre corridas calientes.",
    ]


def render_markdown_analysis(reports: list[BenchmarkReport]) -> str:
    lines = [
        "# Local proxy analysis for Rhizome",
        "",
        f"Generated at: `{utc_now_iso()}`",
        "",
        "## Thresholds carried into #5",
        "",
        f"- Rhizome text floor from `docs/10_rhizome_spec.md`: `>= {RHIZOME_MIN_TEXT_TOKENS_PER_SEC}` tok/s.",
        f"- Rhizome multimodal ceiling from `docs/10_rhizome_spec.md`: `<= {int(RHIZOME_MAX_MULTIMODAL_LATENCY_MS/1000)}` s.",
        f"- Provisional memory headroom guardrail for warm restarts: `>= {MIN_SAFE_MEMORY_HEADROOM_GIB}` GiB free after peak.",
        "",
        "## Reports",
        "",
        "| Model | Host | Requests OK | p50 ms | p95 ms | tok/s avg | RAM peak GiB | Headroom GiB | Text floor |",
        "|------|------|------------:|-------:|-------:|----------:|-------------:|-------------:|-----------|",
    ]

    for report in reports:
        text_floor = "yes" if report.meets_text_threshold else "no"
        lines.append(
            "| "
            f"`{report.model_name}` | `{report.host_label}` | {report.requests_ok_display} | "
            f"{report.wall_clock_ms_p50 if report.wall_clock_ms_p50 is not None else 'n/a'} | "
            f"{report.wall_clock_ms_p95 if report.wall_clock_ms_p95 is not None else 'n/a'} | "
            f"{report.tokens_per_second_avg if report.tokens_per_second_avg is not None else 'n/a'} | "
            f"{report.memory_peak_used_gib_max if report.memory_peak_used_gib_max is not None else 'n/a'} | "
            f"{report.memory_headroom_gib if report.memory_headroom_gib is not None else 'n/a'} | "
            f"{text_floor} |"
        )

    observations = build_observations(reports)
    lines.extend(["", "## Observations", ""])
    if observations:
        lines.extend(f"- {observation}" for observation in observations)
    else:
        lines.append("- No hay suficientes reports para observaciones comparativas.")

    hypothesis = build_preliminary_hypothesis(reports)
    lines.extend(["", "## Provisional architecture hypothesis", ""])
    lines.extend(f"- {item}" for item in hypothesis)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=BENCHMARKS_DIR, help="Directory containing benchmark JSON reports.")
    parser.add_argument("--output", type=Path, default=None, help="Optional path to write the markdown analysis.")
    parser.add_argument(
        "--write-default-output",
        action="store_true",
        help="Write the analysis to the default markdown file in benchmarks/.",
    )
    args = parser.parse_args()

    reports = load_benchmark_reports(args.directory)
    markdown = render_markdown_analysis(reports)

    output_path: Path | None = args.output
    if args.write_default_output:
        output_path = DEFAULT_ANALYSIS_OUTPUT

    if output_path is not None:
        output_path.write_text(markdown + "\n", encoding="utf-8")
        print(output_path)
        return 0

    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
