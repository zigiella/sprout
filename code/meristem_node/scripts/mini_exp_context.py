"""Mini-experimento: latencia + calidad rationale vs num_ctx.

Mide cómo se comporta Gemma 4 E4B Q4_K_M en CPU Alder Lake variando
`num_ctx`, con o sin tool calling, sobre un subset de los bundles
ejemplo de Meristem-nodo.

Material para writeup §3 (Arquitectura → memoria por tools, no por
stuffing) y para validar empíricamente el principio "decisión vs
explicación se separan, siempre".

USO:
    # Pre-requisito: levantar stack
    #   1. llama-server :8080 con E4B Q4_K_M
    #   2. meristem_inference_adapter :12000
    #   3. meristem_node :13000 (con MERISTEM_USE_LLM=true)
    #
    # Ejecutar desde code/meristem_node/:
    cd code/meristem_node
    python scripts/mini_exp_context.py

    # Versión LIGHT (4 corridas, ~10-15 min):
    python scripts/mini_exp_context.py --light

    # Bundles específicos:
    python scripts/mini_exp_context.py --bundles M1,M3,M6

    # Output JSON con todos los datos:
    python scripts/mini_exp_context.py --output-json results.json

OUTPUT:
- Tabla en stdout con (bundle, num_ctx, latencia_ms, prompt_tokens,
  output_tokens, tool_iterations, parsed_ok)
- Opcional JSON con detalle completo para análisis posterior
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import httpx


# Configuración por defecto
DEFAULT_ADAPTER_URL = "http://localhost:12000"
DEFAULT_MERISTEM_URL = "http://localhost:13000"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

# Valores num_ctx a barrer. Light: 4 puntos. Full: 6 puntos.
NUM_CTX_FULL = [1024, 2048, 4096, 8192, 16384, 32768]
NUM_CTX_LIGHT = [2048, 4096, 8192, 16384]

# Bundles por defecto. Cubrimos 3 reglas + el de tool calling.
DEFAULT_BUNDLES = ["M1", "M3", "M6"]


def load_bundle(name: str) -> dict[str, Any]:
    """Carga un bundle ejemplo por shorthand (M1, M3, R2, M6)."""
    candidates = list(EXAMPLES_DIR.glob(f"bundle_{name}*.json"))
    if not candidates:
        raise FileNotFoundError(f"No encontré bundle '{name}' en {EXAMPLES_DIR}")
    with candidates[0].open(encoding="utf-8") as f:
        return json.load(f)


def post_visit_with_num_ctx(
    bundle: dict[str, Any], num_ctx: int, meristem_url: str,
) -> tuple[int, dict[str, Any]]:
    """Hace POST /visit forzando num_ctx via header.

    NOTA: actualmente num_ctx se establece dentro de inference.py.
    Para el experimento, este script asume que se ha modificado
    temporalmente inference.py para leer un header `X-Meristem-Num-Ctx`
    o variable de entorno. Si no, hay que iterar editando el código
    entre corridas (incluido como TODO en bitácora).

    Returns: (status_code, response_json_or_error)
    """
    headers = {
        "Content-Type": "application/json",
        "X-Meristem-Num-Ctx": str(num_ctx),  # placeholder para futuro
    }
    t_start = time.perf_counter()
    try:
        with httpx.Client(timeout=300.0) as client:
            r = client.post(f"{meristem_url}/visit", json=bundle, headers=headers)
        latency_ms = int((time.perf_counter() - t_start) * 1000)
        return latency_ms, r.json()
    except httpx.HTTPError as e:
        latency_ms = int((time.perf_counter() - t_start) * 1000)
        return latency_ms, {"_error": str(e)}


def fetch_last_decision_metrics(meristem_url: str) -> dict[str, Any]:
    """Lee los llm_metrics de la última decisión persistida.

    NOTA: Meristem-nodo no expone aún `/decisions/latest`. Como
    workaround, leemos directamente desde sqlite via sql query.
    Para v0 del experimento, se acepta que algún campo sea None.
    """
    # TODO: añadir endpoint /decisions/latest en meristem_node si se
    # repite mucho este patrón.
    return {}


def run_experiment(
    bundles: list[str],
    num_ctx_values: list[int],
    meristem_url: str = DEFAULT_MERISTEM_URL,
    output_json: Path | None = None,
) -> list[dict[str, Any]]:
    """Ejecuta la matriz bundle × num_ctx y devuelve resultados."""
    print(f"\n{'='*72}")
    print(f"Mini-experimento contexto: {len(bundles)} bundles × {len(num_ctx_values)} valores num_ctx = {len(bundles)*len(num_ctx_values)} corridas")
    print(f"Bundles: {bundles}")
    print(f"num_ctx: {num_ctx_values}")
    print(f"Meristem URL: {meristem_url}")
    print(f"{'='*72}\n")

    results: list[dict[str, Any]] = []
    for bundle_name in bundles:
        try:
            bundle = load_bundle(bundle_name)
        except FileNotFoundError as e:
            print(f"⚠ {e}")
            continue
        for num_ctx in num_ctx_values:
            print(f"→ {bundle_name} @ num_ctx={num_ctx}...", end=" ", flush=True)
            latency_ms, response = post_visit_with_num_ctx(
                bundle, num_ctx, meristem_url
            )
            entry = {
                "bundle": bundle_name,
                "num_ctx": num_ctx,
                "latency_ms": latency_ms,
                "status": response.get("status", "?"),
                "reason_code": response.get("reason_code"),
                "rationale_chars": (
                    len(response.get("payload", {}).get("rationale_for_operator", ""))
                    if response.get("payload")
                    else 0
                ),
                "_raw_response": response if "_error" not in response else None,
                "_error": response.get("_error"),
            }
            print(f"{latency_ms}ms · {entry['status']}/{entry['reason_code']}")
            results.append(entry)

    print(f"\n{'='*72}")
    print(f"Resumen ({len(results)} corridas):")
    print(f"{'='*72}")
    print(f"{'bundle':<8} {'num_ctx':>8} {'latency_ms':>12} {'status':<10} {'reason_code':<28} {'rationale_chars':>16}")
    for r in results:
        print(
            f"{r['bundle']:<8} {r['num_ctx']:>8} {r['latency_ms']:>12} "
            f"{r['status']:<10} {(r['reason_code'] or '?'):<28} "
            f"{r['rationale_chars']:>16}"
        )

    if output_json:
        output_json.write_text(
            json.dumps(results, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n→ Detalle completo en {output_json}")

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bundles",
        type=str,
        default=",".join(DEFAULT_BUNDLES),
        help=f"Bundles a probar (comma-separated). Default: {','.join(DEFAULT_BUNDLES)}",
    )
    parser.add_argument(
        "--light",
        action="store_true",
        help=f"Versión light: solo {len(NUM_CTX_LIGHT)} valores num_ctx en lugar de {len(NUM_CTX_FULL)}",
    )
    parser.add_argument(
        "--meristem-url",
        type=str,
        default=DEFAULT_MERISTEM_URL,
        help=f"URL del meristem-node. Default: {DEFAULT_MERISTEM_URL}",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help="Path opcional para volcar resultados completos en JSON",
    )
    args = parser.parse_args()

    bundles = [b.strip() for b in args.bundles.split(",") if b.strip()]
    num_ctx_values = NUM_CTX_LIGHT if args.light else NUM_CTX_FULL

    # Sanity check: meristem-node responde
    try:
        with httpx.Client(timeout=2.0) as client:
            r = client.get(f"{args.meristem_url}/health")
        if r.status_code != 200:
            print(f"⚠ meristem-node {args.meristem_url}/health responde {r.status_code}")
            return 2
        health = r.json()
        if health.get("llm_mode") != "real":
            print(f"⚠ llm_mode={health.get('llm_mode')!r} — el experimento requiere 'real'")
            print(f"  Levanta el adapter + llama-server y reinicia meristem-node con MERISTEM_USE_LLM=true")
            return 3
    except httpx.HTTPError as e:
        print(f"⚠ meristem-node {args.meristem_url} no responde: {e}")
        print(f"  Levanta el stack:")
        print(f"    1. llama-server :8080 con E4B Q4_K_M")
        print(f"    2. meristem_inference_adapter :12000")
        print(f"    3. cd code/meristem_node && MERISTEM_USE_LLM=true python -m src.main")
        return 4

    run_experiment(
        bundles=bundles,
        num_ctx_values=num_ctx_values,
        meristem_url=args.meristem_url,
        output_json=args.output_json,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
