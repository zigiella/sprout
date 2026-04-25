"""Build the canonical prompt set for Rhizome benchmark runs."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from .common import DEFAULT_PROMPT_SET_PATH

SHARED_EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "shared" / "schemas" / "examples"


def _load_json(name: str) -> dict[str, Any]:
    path = SHARED_EXAMPLES_DIR / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_examples() -> dict[str, dict[str, Any]]:
    return {
        "rhizome_snapshot": _load_json("rhizome_snapshot"),
        "policy_packet": _load_json("policy_packet"),
        "policy_delta": _load_json("policy_delta"),
        "weather_packet": _load_json("weather_packet"),
        "contradiction_alert": _load_json("contradiction_alert"),
        "decision_receipt": _load_json("decision_receipt"),
        "decision_receipt_blocked": _load_json("decision_receipt_blocked"),
    }


def _json_block(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=True, sort_keys=True)


def _record(
    *,
    prompt_id: str,
    category: str,
    max_tokens: int,
    prompt: str,
    source_examples: list[str],
    image_paths: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": prompt_id,
        "category": category,
        "modality": "multimodal" if image_paths else "text",
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "image_paths": image_paths or [],
        "source_examples": source_examples,
        "prompt": prompt.strip(),
    }


def build_prompt_records() -> list[dict[str, Any]]:
    examples = load_examples()
    legend = (
        "Leyenda visual: panel superior izquierdo = parcela A; panel superior derecho = parcela B; "
        "panel inferior izquierdo = deposito; panel inferior derecho = meteo. "
        "Verde = saludable, naranja/rojo = estres, azul = deposito suficiente, "
        "rojo en tanque = deposito critico, nube con gotas = lluvia cercana."
    )

    dry_a = copy.deepcopy(examples["rhizome_snapshot"])
    dry_a["sensors"]["soil_moisture_a_pct"] = 29.5
    dry_a["sensors"]["tank_level_pct"] = 66.0

    dry_b = copy.deepcopy(examples["rhizome_snapshot"])
    dry_b["sensors"]["soil_moisture_b_pct"] = 26.0
    dry_b["sensors"]["tank_level_pct"] = 64.0

    tank_low = copy.deepcopy(examples["rhizome_snapshot"])
    tank_low["sensors"]["soil_moisture_a_pct"] = 28.0
    tank_low["sensors"]["tank_level_pct"] = 11.0

    healthy_idle = copy.deepcopy(examples["rhizome_snapshot"])
    healthy_idle["sensors"]["soil_moisture_a_pct"] = 56.0
    healthy_idle["sensors"]["soil_moisture_b_pct"] = 59.0

    fresh_weather = copy.deepcopy(examples["weather_packet"])
    stale_weather = copy.deepcopy(examples["weather_packet"])
    stale_weather["valid_until"] = "2026-04-16T11:00:00Z"
    stale_weather["notes"] = "Packet stale on purpose for benchmark."

    contradiction_critical = copy.deepcopy(examples["contradiction_alert"])
    contradiction_critical["severity"] = "critical"
    contradiction_critical["recommended_action"] = "block_and_notify"

    records = [
        _record(
            prompt_id="decision_water_a_from_snapshot",
            category="decision_text",
            max_tokens=72,
            source_examples=["rhizome_snapshot", "policy_packet"],
            prompt=f"""
Eres Rhizome. Evalua si toca regar la parcela A y responde solo en JSON con:
action, confidence, rationale_short.

Snapshot:
{_json_block(dry_a)}

Politica:
{_json_block(examples["policy_packet"])}
""",
        ),
        _record(
            prompt_id="decision_water_b_from_snapshot",
            category="decision_text",
            max_tokens=72,
            source_examples=["rhizome_snapshot", "policy_packet"],
            prompt=f"""
Actua como motor de decision local de Rhizome. Prioriza solo la parcela mas necesitada.
Devuelve JSON con action, target_parcel y rationale_short.

Snapshot:
{_json_block(dry_b)}

Politica:
{_json_block(examples["policy_packet"])}
""",
        ),
        _record(
            prompt_id="decision_block_if_tank_low",
            category="decision_text",
            max_tokens=72,
            source_examples=["rhizome_snapshot", "policy_packet", "decision_receipt_blocked"],
            prompt=f"""
Decide la accion segura. Si el deposito esta por debajo del minimo, bloquea.
Devuelve JSON con action, blocked_reason y rationale_short.

Snapshot:
{_json_block(tank_low)}

Politica:
{_json_block(examples["policy_packet"])}

Receipt bloqueado de referencia:
{_json_block(examples["decision_receipt_blocked"])}
""",
        ),
        _record(
            prompt_id="decision_skip_if_healthy",
            category="decision_text",
            max_tokens=64,
            source_examples=["rhizome_snapshot", "policy_packet"],
            prompt=f"""
Evalua el estado y responde con JSON minimo: action, next_check_in_s, rationale_short.
Si ninguna parcela necesita riego ahora, no inventes accion de agua.

Snapshot:
{_json_block(healthy_idle)}

Politica:
{_json_block(examples["policy_packet"])}
""",
        ),
        _record(
            prompt_id="decision_defer_due_to_warning_contradiction",
            category="decision_text",
            max_tokens=80,
            source_examples=["rhizome_snapshot", "policy_packet", "contradiction_alert"],
            prompt=f"""
Haz una decision prudente. Si ves contradiccion warning entre sensores y vision, puedes diferir.
Responde en JSON con action, confidence y rationale_short.

Snapshot:
{_json_block(dry_a)}

Politica:
{_json_block(examples["policy_packet"])}

Contradiccion:
{_json_block(examples["contradiction_alert"])}
""",
        ),
        _record(
            prompt_id="decision_use_fresh_ferried_weather",
            category="decision_text",
            max_tokens=80,
            source_examples=["rhizome_snapshot", "policy_packet", "weather_packet"],
            prompt=f"""
Evalua si el weather packet fresco deberia volver mas conservadora la decision.
Devuelve JSON con action, mode_shift y rationale_short.

Snapshot:
{_json_block(dry_a)}

Politica:
{_json_block(examples["policy_packet"])}

Weather packet fresco:
{_json_block(fresh_weather)}
""",
        ),
        _record(
            prompt_id="decision_reject_stale_weather",
            category="decision_text",
            max_tokens=72,
            source_examples=["rhizome_snapshot", "policy_packet", "weather_packet"],
            prompt=f"""
Evalua la decision y explica si el weather packet debe ignorarse por TTL.
Devuelve JSON con use_weather_packet, action y rationale_short.

Snapshot:
{_json_block(dry_a)}

Politica:
{_json_block(examples["policy_packet"])}

Weather packet stale:
{_json_block(stale_weather)}
""",
        ),
        _record(
            prompt_id="policy_delta_apply_budget_change",
            category="policy_delta",
            max_tokens=96,
            source_examples=["policy_packet", "policy_delta"],
            prompt=f"""
Actua como auditor de policy delta. Resume si el delta es seguro de aplicar.
Devuelve JSON con apply, changed_fields y rationale_short.

Policy activa:
{_json_block(examples["policy_packet"])}

Delta:
{_json_block(examples["policy_delta"])}
""",
        ),
        _record(
            prompt_id="policy_delta_audit_for_trigger_growth",
            category="policy_delta",
            max_tokens=96,
            source_examples=["policy_packet", "policy_delta"],
            prompt=f"""
Inspecciona el delta y responde con JSON:
apply, conservative_triggers_delta, risk_notes.

Policy activa:
{_json_block(examples["policy_packet"])}

Delta:
{_json_block(examples["policy_delta"])}
""",
        ),
        _record(
            prompt_id="receipt_success_overlay",
            category="receipt_audit",
            max_tokens=56,
            source_examples=["decision_receipt"],
            prompt=f"""
Genera una frase corta para overlay de video a partir del receipt.
Responde en JSON con overlay_line y confidence.

Decision receipt:
{_json_block(examples["decision_receipt"])}
""",
        ),
        _record(
            prompt_id="receipt_blocked_overlay",
            category="receipt_audit",
            max_tokens=56,
            source_examples=["decision_receipt_blocked"],
            prompt=f"""
Genera una frase corta para overlay de video a partir del receipt bloqueado.
Responde en JSON con overlay_line y blocked_reason.

Decision receipt:
{_json_block(examples["decision_receipt_blocked"])}
""",
        ),
        _record(
            prompt_id="contradiction_triage_warning",
            category="contradiction",
            max_tokens=88,
            source_examples=["contradiction_alert"],
            prompt=f"""
Clasifica la contradiccion y propone siguiente paso local.
Responde en JSON con severity, recommended_action y rationale_short.

Alert:
{_json_block(examples["contradiction_alert"])}
""",
        ),
        _record(
            prompt_id="contradiction_triage_critical",
            category="contradiction",
            max_tokens=88,
            source_examples=["contradiction_alert"],
            prompt=f"""
Clasifica la contradiccion critica y decide si Rhizome debe bloquear.
Responde en JSON con block_now, recommended_action y rationale_short.

Alert:
{_json_block(contradiction_critical)}
""",
        ),
        _record(
            prompt_id="policy_window_validation",
            category="policy_check",
            max_tokens=64,
            source_examples=["policy_packet"],
            prompt=f"""
Resume si la politica define una ventana de riego coherente y segura.
Responde en JSON con window_ok, max_duration_s y rationale_short.

Policy:
{_json_block(examples["policy_packet"])}
""",
        ),
        _record(
            prompt_id="budget_guardrail_check",
            category="policy_check",
            max_tokens=64,
            source_examples=["policy_packet", "decision_receipt"],
            prompt=f"""
Con esta politica y este receipt, estima si el presupuesto diario sigue dentro de margen.
Devuelve JSON con within_budget, liters_spent_now y rationale_short.

Policy:
{_json_block(examples["policy_packet"])}

Receipt:
{_json_block(examples["decision_receipt"])}
""",
        ),
        _record(
            prompt_id="short_state_summary_for_pollen",
            category="summary",
            max_tokens=72,
            source_examples=["rhizome_snapshot"],
            prompt=f"""
Resume el snapshot para Pollen en maximo tres bullets JSON.
Devuelve JSON con summary_lines.

Snapshot:
{_json_block(examples["rhizome_snapshot"])}
""",
        ),
        _record(
            prompt_id="audit_snapshot_for_risks",
            category="summary",
            max_tokens=72,
            source_examples=["rhizome_snapshot"],
            prompt=f"""
Lista los riesgos operativos del snapshot. Responde en JSON con risks y confidence.

Snapshot:
{_json_block(tank_low)}
""",
        ),
        _record(
            prompt_id="weather_conflict_resolution",
            category="weather",
            max_tokens=80,
            source_examples=["weather_packet", "contradiction_alert"],
            prompt=f"""
Tienes weather prestado y una contradiccion visual. Decide que pesa mas.
Devuelve JSON con use_weather_packet, action_hint y rationale_short.

Weather:
{_json_block(fresh_weather)}

Contradiccion:
{_json_block(examples["contradiction_alert"])}
""",
        ),
        _record(
            prompt_id="local_vs_ferried_preference",
            category="weather",
            max_tokens=72,
            source_examples=["weather_packet"],
            prompt=f"""
Explica en JSON cuando Rhizome deberia preferir meteo local frente a meteo ferried.
Usa este packet como contexto y responde con prefer_local_station, ttl_note y rationale_short.

Weather packet:
{_json_block(examples["weather_packet"])}
""",
        ),
        _record(
            prompt_id="two_parcel_prioritization",
            category="decision_text",
            max_tokens=80,
            source_examples=["rhizome_snapshot", "policy_packet"],
            prompt=f"""
Prioriza entre dos parcelas y devuelve JSON con action, target_parcel y rationale_short.

Snapshot:
{_json_block(dry_b)}

Politica:
{_json_block(examples["policy_packet"])}
""",
        ),
        _record(
            prompt_id="tank_recovery_plan",
            category="safety",
            max_tokens=88,
            source_examples=["rhizome_snapshot", "decision_receipt_blocked"],
            prompt=f"""
Si el deposito cae por debajo del minimo, que hace Rhizome en la siguiente hora?
Responde en JSON con mode, next_actions y rationale_short.

Snapshot:
{_json_block(tank_low)}

Receipt bloqueado:
{_json_block(examples["decision_receipt_blocked"])}
""",
        ),
        _record(
            prompt_id="no_pollen_48h_conservative_shift",
            category="policy_check",
            max_tokens=72,
            source_examples=["policy_packet"],
            prompt=f"""
La politica incluye no_pollen_visit_48h como trigger conservador.
Responde en JSON con mode_shift y expected_effect.

Policy:
{_json_block(examples["policy_packet"])}
""",
        ),
        _record(
            prompt_id="receipt_postmortem",
            category="receipt_audit",
            max_tokens=88,
            source_examples=["decision_receipt", "decision_receipt_blocked"],
            prompt=f"""
Compara un receipt exitoso y uno bloqueado. Devuelve JSON con top_differences y operator_note.

Receipt OK:
{_json_block(examples["decision_receipt"])}

Receipt blocked:
{_json_block(examples["decision_receipt_blocked"])}
""",
        ),
        _record(
            prompt_id="sync_summary_for_pollen_handoff",
            category="sync",
            max_tokens=80,
            source_examples=["rhizome_snapshot", "policy_packet", "weather_packet"],
            prompt=f"""
Prepara un resumen de handoff para Pollen.
Devuelve JSON con snapshot_status, policy_status y weather_status.

Snapshot:
{_json_block(examples["rhizome_snapshot"])}

Policy:
{_json_block(examples["policy_packet"])}

Weather:
{_json_block(examples["weather_packet"])}
""",
        ),
        _record(
            prompt_id="esp32_command_sanity",
            category="safety",
            max_tokens=72,
            source_examples=["decision_receipt", "policy_packet"],
            prompt=f"""
Genera el comando de alto nivel mas coherente para la capa ESP32.
Devuelve JSON con action, duration_s y safety_note.

Decision receipt de referencia:
{_json_block(examples["decision_receipt"])}

Policy:
{_json_block(examples["policy_packet"])}
""",
        ),
        _record(
            prompt_id="vision_parcel_a_dry_decision",
            category="decision_multimodal",
            max_tokens=96,
            image_paths=["assets/parcel_a_dry.png"],
            source_examples=["rhizome_snapshot", "policy_packet"],
            prompt=f"""
Combina la lectura visual con el snapshot y devuelve JSON con:
action, target_parcel, confidence, rationale_short.
{legend}

Snapshot:
{_json_block(dry_a)}

Politica:
{_json_block(examples["policy_packet"])}
""",
        ),
        _record(
            prompt_id="vision_parcel_b_dry_decision",
            category="decision_multimodal",
            max_tokens=96,
            image_paths=["assets/parcel_b_dry.png"],
            source_examples=["rhizome_snapshot", "policy_packet"],
            prompt=f"""
Mira la imagen sintetica y prioriza la parcela mas necesitada.
Devuelve JSON con action, target_parcel y rationale_short.
{legend}

Snapshot:
{_json_block(dry_b)}

Politica:
{_json_block(examples["policy_packet"])}
""",
        ),
        _record(
            prompt_id="vision_tank_low_guardrail",
            category="safety_multimodal",
            max_tokens=88,
            image_paths=["assets/tank_low_guardrail.png"],
            source_examples=["rhizome_snapshot", "policy_packet", "decision_receipt_blocked"],
            prompt=f"""
Evalua si Rhizome debe bloquear la accion por seguridad.
Devuelve JSON con action, blocked_reason y rationale_short.
{legend}

Snapshot:
{_json_block(tank_low)}

Politica:
{_json_block(examples["policy_packet"])}

Receipt bloqueado de referencia:
{_json_block(examples["decision_receipt_blocked"])}
""",
        ),
        _record(
            prompt_id="vision_sensor_vs_snapshot_contradiction",
            category="contradiction_multimodal",
            max_tokens=96,
            image_paths=["assets/sensor_vision_conflict.png"],
            source_examples=["rhizome_snapshot", "policy_packet", "contradiction_alert"],
            prompt=f"""
La imagen muestra aspecto sano, pero el snapshot indica sequedad. Decide si diferir o alertar.
Devuelve JSON con action, use_vision_signal y rationale_short.
{legend}

Snapshot:
{_json_block(dry_a)}

Politica:
{_json_block(examples["policy_packet"])}

Contradiccion:
{_json_block(examples["contradiction_alert"])}
""",
        ),
        _record(
            prompt_id="vision_incoming_rain_mode_shift",
            category="weather_multimodal",
            max_tokens=96,
            image_paths=["assets/incoming_rain_shift.png"],
            source_examples=["rhizome_snapshot", "policy_packet", "weather_packet"],
            prompt=f"""
Usa la imagen y el weather packet para decidir si toca volver mas conservadora la politica.
Devuelve JSON con action, mode_shift y rationale_short.
{legend}

Snapshot:
{_json_block(dry_a)}

Politica:
{_json_block(examples["policy_packet"])}

Weather packet:
{_json_block(fresh_weather)}
""",
        ),
    ]
    return records


def render_prompt_set() -> str:
    return "".join(json.dumps(record, ensure_ascii=True) + "\n" for record in build_prompt_records())


def stale_prompt_set(path: Path = DEFAULT_PROMPT_SET_PATH) -> bool:
    expected = render_prompt_set()
    if not path.exists():
        return True
    return path.read_text(encoding="utf-8") != expected


def write_prompt_set(path: Path = DEFAULT_PROMPT_SET_PATH) -> Path:
    path.write_text(render_prompt_set(), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check whether prompt_set.jsonl is up to date.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PROMPT_SET_PATH,
        help="Path to write the generated JSONL prompt set.",
    )
    args = parser.parse_args()

    if args.check:
        if stale_prompt_set(args.output):
            print(str(args.output))
            return 1
        print("Prompt set is up to date.")
        return 0

    output_path = write_prompt_set(args.output)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
