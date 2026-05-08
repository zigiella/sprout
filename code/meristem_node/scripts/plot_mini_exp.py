"""Genera grafica latencia vs num_ctx desde resultados del mini-experimento.

USO:
    python scripts/plot_mini_exp.py results_d23_light.json out.png
    python scripts/plot_mini_exp.py results_d23_light.json out.png --markdown summary.md

Si no esta matplotlib instalado, genera version ASCII de la tabla.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def render_ascii_table(results: list[dict]) -> str:
    bundles = sorted({r["bundle"] for r in results})
    nctx_values = sorted({r["num_ctx"] for r in results})

    # Tabla ASCII
    lines = []
    lines.append("Latencia (ms) por (bundle, num_ctx):")
    lines.append("")
    header = f"{'num_ctx':>10} | " + " | ".join(f"{b:>10}" for b in bundles)
    lines.append(header)
    lines.append("-" * len(header))
    for nc in nctx_values:
        row = [f"{nc:>10}"]
        for b in bundles:
            match = next(
                (r for r in results if r["bundle"] == b and r["num_ctx"] == nc),
                None,
            )
            if match is None:
                row.append(f"{'-':>10}")
            else:
                row.append(f"{match['latency_ms']:>10}")
        lines.append(" | ".join(row))

    # Estadisticas globales
    lines.append("")
    lines.append("Resumen:")
    n_total = len(results)
    n_ok = sum(1 for r in results if r.get("status") == "ok")
    n_refuse = sum(1 for r in results if r.get("status") == "refuse")
    lines.append(f"  Corridas: {n_total} (ok: {n_ok}, refuse: {n_refuse})")
    if n_ok > 0:
        ok_lats = [r["latency_ms"] for r in results if r.get("status") == "ok"]
        lines.append(
            f"  Latencia ok (ms): min={min(ok_lats)}  p50={sorted(ok_lats)[len(ok_lats)//2]}  "
            f"max={max(ok_lats)}"
        )
        # Crecimiento por num_ctx (medio entre bundles)
        by_nc: dict[int, list[int]] = {}
        for r in results:
            if r.get("status") == "ok":
                by_nc.setdefault(r["num_ctx"], []).append(r["latency_ms"])
        lines.append("")
        lines.append("Latencia media por num_ctx (solo ok):")
        for nc in sorted(by_nc):
            avg = sum(by_nc[nc]) // len(by_nc[nc])
            lines.append(f"  num_ctx={nc:>5}: {avg} ms (n={len(by_nc[nc])})")

    return "\n".join(lines)


def render_matplotlib(
    results: list[dict],
    output_path: Path,
) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib no instalado; salto grafica.")
        return

    bundles = sorted({r["bundle"] for r in results})
    fig, ax = plt.subplots(figsize=(8, 5))
    for b in bundles:
        pts = sorted(
            [(r["num_ctx"], r["latency_ms"]) for r in results if r["bundle"] == b],
            key=lambda x: x[0],
        )
        if pts:
            xs, ys = zip(*pts)
            ax.plot(xs, ys, marker="o", label=b)

    ax.set_xscale("log", base=2)
    ax.set_xlabel("num_ctx (tokens)")
    ax.set_ylabel("latencia E2E (ms)")
    ax.set_title("Latencia vs num_ctx — Meristem E4B Q4_K_M, CPU Alder Lake")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(str(output_path), dpi=120)
    print(f"Grafica guardada en {output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_json", type=Path)
    parser.add_argument(
        "output_png", nargs="?", type=Path, default=None,
        help="Path para PNG (opcional)",
    )
    parser.add_argument(
        "--markdown", type=Path, default=None,
        help="Path para tabla Markdown (opcional)",
    )
    args = parser.parse_args()

    if not args.results_json.exists():
        print(f"ERROR: no encontre {args.results_json}", file=sys.stderr)
        return 1

    results = json.loads(args.results_json.read_text(encoding="utf-8"))
    print(f"Cargados {len(results)} resultados de {args.results_json}")
    print()

    ascii_table = render_ascii_table(results)
    print(ascii_table)

    if args.output_png:
        render_matplotlib(results, args.output_png)

    if args.markdown:
        # Tabla Markdown
        bundles = sorted({r["bundle"] for r in results})
        nctx_values = sorted({r["num_ctx"] for r in results})
        md_lines = ["# Mini-experimento contexto — resultados", ""]
        md_lines.append("## Latencia (ms) por (bundle × num_ctx)")
        md_lines.append("")
        header = "| num_ctx | " + " | ".join(bundles) + " |"
        sep = "|---:|" + "|".join(["---:" for _ in bundles]) + "|"
        md_lines.append(header)
        md_lines.append(sep)
        for nc in nctx_values:
            row = [f"| {nc} "]
            for b in bundles:
                match = next(
                    (r for r in results if r["bundle"] == b and r["num_ctx"] == nc),
                    None,
                )
                row.append(f"| {match['latency_ms'] if match else '—'}")
            row.append("|")
            md_lines.append(" ".join(row))
        args.markdown.write_text("\n".join(md_lines), encoding="utf-8")
        print(f"\nTabla markdown en {args.markdown}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
