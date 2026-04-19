"""Harness E2E cross-node para rehearsal local de Sprout."""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

_THIS = Path(__file__).resolve()
SIMULATOR_ROOT = _THIS.parents[1]
CODE_ROOT = SIMULATOR_ROOT.parent
SHARED_ROOT = CODE_ROOT / "shared"
MERISTEM_ROOT = CODE_ROOT / "meristem"
REPORTS_DIR = SIMULATOR_ROOT / "reports"
DEFAULT_ENDPOINT = "http://127.0.0.1:11434"

for path in (SHARED_ROOT,):
    path_str = str(path)
    if path.exists() and path_str not in sys.path:
        sys.path.insert(0, path_str)

from schemas import (  # noqa: E402
    ContradictionAlert,
    DecisionReceipt,
    PolicyDelta,
    PolicyPacket,
    RhizomeSnapshot,
    WeatherPacket,
)
from schemas.examples.builders import (  # noqa: E402
    contradiction_alert_example,
    decision_receipt_blocked_example,
    decision_receipt_example,
    policy_packet_example,
    rhizome_snapshot_example,
    weather_packet_example,
)
from schemas.policy_delta import ALLOWED_POLICY_PATHS  # noqa: E402


@dataclass(frozen=True)
class CrossNodeScenario:
    scenario_id: str
    description: str
    snapshot: RhizomeSnapshot
    receipt: DecisionReceipt
    active_policy: PolicyPacket
    pollen_summary: str
    weather_packet: WeatherPacket | None = None
    contradiction_alert: ContradictionAlert | None = None


class AdvicePatch(BaseModel):
    op: str
    path: str
    value: Any

    @field_validator("op")
    @classmethod
    def validate_op(cls, value: str) -> str:
        if value not in {"replace", "add"}:
            raise ValueError("op debe ser replace o add")
        return value

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        if value not in ALLOWED_POLICY_PATHS:
            raise ValueError("path no soportado por el harness v1")
        return value


class MeristemDeltaAdvice(BaseModel):
    patches: list[AdvicePatch] = Field(min_length=1, max_length=2)
    rationale: str = Field(min_length=12, max_length=220)
    ttl_seconds: int = Field(ge=21600, le=86400)
    priority: str

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str) -> str:
        if value not in {"low", "normal", "high"}:
            raise ValueError("priority debe ser low, normal o high")
        return value


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    collapsed = "".join(char.lower() if char.isalnum() else "-" for char in value.strip())
    while "--" in collapsed:
        collapsed = collapsed.replace("--", "-")
    return collapsed.strip("-") or "unknown"


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * pct
    lower = int(rank)
    upper = min(len(ordered) - 1, lower + 1)
    if lower == upper:
        return ordered[lower]
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _ns_to_ms(value: int | None) -> float | None:
    if value is None:
        return None
    return round(value / 1_000_000, 3)


def _approx_first_token_latency_ms(payload: dict[str, Any]) -> float | None:
    load_duration = payload.get("load_duration")
    prompt_eval_duration = payload.get("prompt_eval_duration")
    if load_duration is None and prompt_eval_duration is None:
        return None
    return _ns_to_ms((load_duration or 0) + (prompt_eval_duration or 0))


def _compute_tokens_per_second(eval_count: int | None, eval_duration_ns: int | None) -> float | None:
    if not eval_count or not eval_duration_ns or eval_duration_ns <= 0:
        return None
    return round(eval_count / (eval_duration_ns / 1_000_000_000), 3)


def _post_json(url: str, payload: dict[str, Any], timeout_s: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_s) as response:
        return json.load(response)


def _read_meristem_system_prompt() -> str:
    prompt_path = MERISTEM_ROOT / "src" / "prompts" / "system_v1.txt"
    return prompt_path.read_text(encoding="utf-8")


def _build_active_policy() -> PolicyPacket:
    payload = policy_packet_example()
    payload["created_at"] = "2026-04-19T06:30:15Z"
    payload["rules"]["tank_minimum_pct"] = 20.0
    payload["valid_until"] = "2026-04-20T06:30:15Z"
    payload["notes"] = "Fixture rehecho para rehearsal local con hard-limit fisico de 20%."
    return PolicyPacket.model_validate(payload)


def _scenario_fresh_weather_review() -> CrossNodeScenario:
    active_policy = _build_active_policy()
    snapshot_payload = rhizome_snapshot_example()
    snapshot_payload["snapshot_id"] = "snap_rhizome_01_20260419T101000_fresh"
    snapshot_payload["created_at"] = "2026-04-19T10:10:00Z"
    snapshot_payload["active_policy_expires_at"] = active_policy.valid_until.isoformat().replace("+00:00", "Z")
    snapshot_payload["sensors"]["soil_moisture_a_pct"] = 44.0
    snapshot_payload["sensors"]["soil_moisture_b_pct"] = 31.2
    snapshot_payload["vision"]["parcel_b_status"] = "healthy"
    snapshot_payload["vision"]["visual_notes"] = "foto de Rhizome de hace 2h: color uniforme, sin curling visible"
    snapshot = RhizomeSnapshot.model_validate(snapshot_payload)

    receipt_payload = decision_receipt_example()
    receipt_payload["created_at"] = "2026-04-19T10:11:00Z"
    receipt_payload["decision_id"] = "rec_rhizome_01_20260419T101100_e2e"
    receipt_payload["snapshot_id"] = snapshot.snapshot_id
    receipt_payload["active_policy_id"] = active_policy.policy_id
    receipt_payload["action"] = "WATER_A"
    receipt = DecisionReceipt.model_validate(receipt_payload)

    weather_payload = weather_packet_example()
    weather_payload["packet_id"] = "pkt_weather_pollen_01_20260419T101200_fresh"
    weather_payload["created_at"] = "2026-04-19T10:12:00Z"
    weather_payload["observed_at"] = "2026-04-19T09:50:00Z"
    weather_payload["valid_until"] = "2026-04-19T20:00:00Z"
    weather_payload["measurements"]["wind_speed_kmh"] = 24.0
    weather_payload["measurements"]["humidity_rel_pct"] = 36.0
    weather_payload["measurements"]["rain_last_24h_mm"] = 0.0
    weather_payload["notes"] = "Pollen trae aviso de viento seco y humedad baja desde parcela con estacion."
    weather = WeatherPacket.model_validate(weather_payload)

    contradiction_payload = contradiction_alert_example()
    contradiction_payload["alert_id"] = "alert_pollen_01_20260419T101250_visual"
    contradiction_payload["created_at"] = "2026-04-19T10:12:50Z"
    contradiction_payload["observed_at"] = "2026-04-19T10:12:20Z"
    contradiction_payload["expires_at"] = "2026-04-19T16:12:50Z"
    contradiction_payload["severity"] = "warning"
    contradiction_payload["evidence"]["sensor_reading"]["soil_moisture_a_pct"] = 44.0
    contradiction_payload["evidence"]["vision_reading"]["notes"] = "Pollen detecta curling leve y tono amarillento en parcela B que Rhizome no vio."
    contradiction_payload["rationale"] = "La vision itinerante ve estres emergente en parcela B y meteo mas dura de la que conoce Rhizome."
    contradiction = ContradictionAlert.model_validate(contradiction_payload)

    return CrossNodeScenario(
        scenario_id="pollen_fresh_weather_review",
        description="Pollen llega con weather fresco y contradiccion visual leve sobre parcela B.",
        snapshot=snapshot,
        receipt=receipt,
        active_policy=active_policy,
        pollen_summary=(
            "Pollen confirma deposito suficiente, detecta estres visual emergente en parcela B y "
            "transporta meteo fresca con viento seco. Pide ajuste prudente de corto TTL."
        ),
        weather_packet=weather,
        contradiction_alert=contradiction,
    )


def _scenario_low_tank_blocked() -> CrossNodeScenario:
    active_policy = _build_active_policy()
    snapshot_payload = rhizome_snapshot_example()
    snapshot_payload["snapshot_id"] = "snap_rhizome_01_20260419T113000_lowtank"
    snapshot_payload["created_at"] = "2026-04-19T11:30:00Z"
    snapshot_payload["active_policy_expires_at"] = active_policy.valid_until.isoformat().replace("+00:00", "Z")
    snapshot_payload["sensors"]["soil_moisture_a_pct"] = 27.4
    snapshot_payload["sensors"]["soil_moisture_b_pct"] = 35.1
    snapshot_payload["sensors"]["tank_level_pct"] = 18.0
    snapshot_payload["vision"]["parcel_a_status"] = "stressed"
    snapshot_payload["vision"]["visual_notes"] = "parcela A seca; deposito bajo; Rhizome ya bloqueo una accion previa"
    snapshot = RhizomeSnapshot.model_validate(snapshot_payload)

    receipt_payload = decision_receipt_blocked_example()
    receipt_payload["decision_id"] = "rec_rhizome_01_20260419T113040_block"
    receipt_payload["snapshot_id"] = snapshot.snapshot_id
    receipt_payload["created_at"] = "2026-04-19T11:30:40Z"
    receipt_payload["active_policy_id"] = active_policy.policy_id
    receipt_payload["rationale_short"] = "Bloqueo preventivo: deposito al 18%, por debajo del hard-limit de 20%."
    receipt_payload["rationale_full"] = (
        "Rhizome detecta estres en parcela A pero no ejecuta porque el deposito cae al 18%, por "
        "debajo del limite fisico del firmware. Se solicita revision estrategica."
    )
    receipt_payload["action_params"]["reason"] = "tank_minimum_pct hard limit"
    receipt = DecisionReceipt.model_validate(receipt_payload)

    return CrossNodeScenario(
        scenario_id="low_tank_blocked_reassessment",
        description="Rhizome ya bloqueo por deposito bajo; Pollen solo transporta el caso a Meristem.",
        snapshot=snapshot,
        receipt=receipt,
        active_policy=active_policy,
        pollen_summary=(
            "Pollen no añade meteo ni vision nueva; solo entrega a Meristem un caso de bloqueo fisico "
            "para que reajuste politicas sin pedir acciones imposibles."
        ),
    )


def build_scenarios() -> list[CrossNodeScenario]:
    return [_scenario_fresh_weather_review(), _scenario_low_tank_blocked()]


def scenario_map() -> dict[str, CrossNodeScenario]:
    return {scenario.scenario_id: scenario for scenario in build_scenarios()}


def build_rhizome_export(scenario: CrossNodeScenario) -> dict[str, Any]:
    return {
        "snapshot": scenario.snapshot.model_dump(mode="json"),
        "receipt": scenario.receipt.model_dump(mode="json"),
        "active_policy": scenario.active_policy.model_dump(mode="json"),
    }


def build_pollen_relay(scenario: CrossNodeScenario) -> dict[str, Any]:
    relay: dict[str, Any] = {
        "summary": scenario.pollen_summary,
        "transported_items": [],
    }
    if scenario.weather_packet is not None:
        relay["transported_items"].append("weather_packet")
        relay["weather_packet"] = scenario.weather_packet.model_dump(mode="json")
    if scenario.contradiction_alert is not None:
        relay["transported_items"].append("contradiction_alert")
        relay["contradiction_alert"] = scenario.contradiction_alert.model_dump(mode="json")
    return relay


def render_meristem_prompt(scenario: CrossNodeScenario) -> str:
    allowed_paths = ", ".join(sorted(ALLOWED_POLICY_PATHS))
    digest = {
        "scenario_id": scenario.scenario_id,
        "target_node_id": scenario.snapshot.origin_node_id,
        "snapshot": {
            "snapshot_id": scenario.snapshot.snapshot_id,
            "mode": scenario.snapshot.mode.value,
            "soil_moisture_a_pct": scenario.snapshot.sensors.soil_moisture_a_pct,
            "soil_moisture_b_pct": scenario.snapshot.sensors.soil_moisture_b_pct,
            "tank_level_pct": scenario.snapshot.sensors.tank_level_pct,
            "vision": {
                "parcel_a_status": scenario.snapshot.vision.parcel_a_status,
                "parcel_b_status": scenario.snapshot.vision.parcel_b_status,
                "visual_notes": scenario.snapshot.vision.visual_notes,
            },
        },
        "last_receipt": {
            "decision_id": scenario.receipt.decision_id,
            "action": scenario.receipt.action.value,
            "executed": scenario.receipt.executed,
            "blocked_reason": scenario.receipt.blocked_reason,
            "rationale_short": scenario.receipt.rationale_short,
        },
        "active_policy": {
            "policy_id": scenario.active_policy.policy_id,
            "valid_until": scenario.active_policy.valid_until.isoformat().replace("+00:00", "Z"),
            "mode_default": scenario.active_policy.mode_default.value,
            "rules": {
                "parcel_a_min_pct": scenario.active_policy.rules.soil_moisture_thresholds.parcel_a.min_pct,
                "parcel_b_min_pct": scenario.active_policy.rules.soil_moisture_thresholds.parcel_b.min_pct,
                "max_watering_duration_s": scenario.active_policy.rules.max_watering_duration_s,
                "daily_water_budget_liters": scenario.active_policy.rules.daily_water_budget_liters,
                "tank_minimum_pct": scenario.active_policy.rules.tank_minimum_pct,
                "require_vision_confirmation": scenario.active_policy.rules.require_vision_confirmation,
                "conservative_triggers": scenario.active_policy.rules.conservative_triggers,
            },
        },
        "pollen_summary": scenario.pollen_summary,
        "weather_packet": (
            None
            if scenario.weather_packet is None
            else {
                "packet_id": scenario.weather_packet.packet_id,
                "valid_until": scenario.weather_packet.valid_until.isoformat().replace("+00:00", "Z"),
                "temperature_c": scenario.weather_packet.measurements.temperature_c,
                "humidity_rel_pct": scenario.weather_packet.measurements.humidity_rel_pct,
                "wind_speed_kmh": scenario.weather_packet.measurements.wind_speed_kmh,
                "rain_last_24h_mm": scenario.weather_packet.measurements.rain_last_24h_mm,
                "notes": scenario.weather_packet.notes,
            }
        ),
        "contradiction_alert": (
            None
            if scenario.contradiction_alert is None
            else {
                "alert_id": scenario.contradiction_alert.alert_id,
                "severity": scenario.contradiction_alert.severity.value,
                "recommended_action": scenario.contradiction_alert.recommended_action,
                "rationale": scenario.contradiction_alert.rationale,
            }
        ),
    }
    return (
        f"Escenario: {scenario.description}\n"
        f"Objetivo: emitir una advice compacta para construir un PolicyDelta prudente para {scenario.snapshot.origin_node_id}.\n"
        f"Devuelve SOLO un objeto JSON de primer nivel con estas claves exactas:\n"
        f"- patches\n- rationale\n- ttl_seconds\n- priority\n"
        f"No devuelvas wrappers como `policy_delta`, `result` ni texto fuera del JSON.\n"
        f"Formato esperado (ejemplo de forma, no de contenido):\n"
        f'{{"patches":[{{"op":"replace","path":"rules.soil_moisture_thresholds.parcel_b.min_pct","value":34.0}}],"rationale":"ajuste prudente por estres visual y viento seco","ttl_seconds":43200,"priority":"high"}}\n'
        f"Condiciones duras:\n"
        f"- target_node_id debe ser {scenario.snapshot.origin_node_id}\n"
        f"- base_policy_id debe ser {scenario.active_policy.policy_id}\n"
        f"- ttl_seconds entre 21600 y 86400\n"
        f"- maximo 2 patches\n"
        f"- usa solo patch paths de esta lista: {allowed_paths}\n"
        f"- usa solo ops replace o add\n"
        f"- no cambies tank_minimum_pct por debajo de 20\n"
        f"- rationale breve, concreta y no mas de 220 caracteres\n"
        f"- si la evidencia no justifica grandes cambios, emite un delta pequeno pero util\n\n"
        f"Evidence digest:\n"
        f"{json.dumps(digest, ensure_ascii=True, indent=2)}\n"
    )


def extract_json_candidate(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        raise ValueError("respuesta vacia de Ollama")
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict) and "policy_delta" in parsed and isinstance(parsed["policy_delta"], dict):
            return json.dumps(parsed["policy_delta"], ensure_ascii=True)
        return stripped
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("no se encontro JSON util en la respuesta")
        candidate = stripped[start : end + 1]
        parsed = json.loads(candidate)
        if isinstance(parsed, dict) and "policy_delta" in parsed and isinstance(parsed["policy_delta"], dict):
            return json.dumps(parsed["policy_delta"], ensure_ascii=True)
        return candidate


def materialize_policy_delta(scenario: CrossNodeScenario, advice: MeristemDeltaAdvice) -> PolicyDelta:
    created_at = utc_now_iso()
    delta_suffix = scenario.scenario_id.replace("-", "_")
    payload = {
        "schema_version": "1.0",
        "created_at": created_at,
        "origin_node_id": "meristem_01",
        "signature": None,
        "delta_id": f"delta_{scenario.snapshot.origin_node_id}_{delta_suffix}_{created_at[11:19].replace(':', '')}",
        "target_node_id": scenario.snapshot.origin_node_id,
        "base_policy_id": scenario.active_policy.policy_id,
        "patches": [patch.model_dump(mode="json") for patch in advice.patches],
        "rationale": advice.rationale,
        "ttl_seconds": advice.ttl_seconds,
        "priority": advice.priority,
    }
    return PolicyDelta.model_validate(payload)


def call_meristem_local(
    *,
    endpoint: str,
    model: str,
    scenario: CrossNodeScenario,
    timeout_s: int,
    keep_alive: str,
    num_predict: int,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "system": _read_meristem_system_prompt(),
        "prompt": render_meristem_prompt(scenario),
        "stream": False,
        "keep_alive": keep_alive,
        "format": "json",
        "options": {"temperature": 0.0, "num_predict": num_predict},
    }
    started = time.perf_counter()
    try:
        response = _post_json(f"{endpoint}/api/generate", payload, timeout_s)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "wall_clock_ms": round((time.perf_counter() - started) * 1000, 3),
            "error": f"HTTP {exc.code}: {body}",
        }
    except Exception as exc:
        return {
            "ok": False,
            "wall_clock_ms": round((time.perf_counter() - started) * 1000, 3),
            "error": str(exc),
        }

    wall_clock_ms = round((time.perf_counter() - started) * 1000, 3)
    validation_started = time.perf_counter()
    try:
        response_text = response.get("response", "")
        candidate_json = extract_json_candidate(response_text)
        advice = MeristemDeltaAdvice.model_validate_json(candidate_json)
        policy_delta = materialize_policy_delta(scenario, advice)
        validation_ms = round((time.perf_counter() - validation_started) * 1000, 3)
        return {
            "ok": True,
            "wall_clock_ms": wall_clock_ms,
            "validation_ms": validation_ms,
            "advice": advice.model_dump(mode="json"),
            "policy_delta": policy_delta.model_dump(mode="json"),
            "response_preview": response_text[:240],
            "total_duration_ms": _ns_to_ms(response.get("total_duration")),
            "load_duration_ms": _ns_to_ms(response.get("load_duration")),
            "prompt_eval_duration_ms": _ns_to_ms(response.get("prompt_eval_duration")),
            "first_token_latency_ms": _approx_first_token_latency_ms(response),
            "eval_duration_ms": _ns_to_ms(response.get("eval_duration")),
            "eval_count": response.get("eval_count"),
            "tokens_per_second": _compute_tokens_per_second(response.get("eval_count"), response.get("eval_duration")),
            "done_reason": response.get("done_reason"),
        }
    except Exception as exc:
        validation_ms = round((time.perf_counter() - validation_started) * 1000, 3)
        return {
            "ok": False,
            "wall_clock_ms": wall_clock_ms,
            "validation_ms": validation_ms,
            "error": str(exc),
            "response_preview": response.get("response", "")[:240],
            "done_reason": response.get("done_reason"),
        }


def run_scenario(
    *,
    endpoint: str,
    model: str,
    scenario: CrossNodeScenario,
    timeout_s: int,
    keep_alive: str,
    num_predict: int,
) -> dict[str, Any]:
    started = time.perf_counter()

    rhizome_started = time.perf_counter()
    rhizome_export = build_rhizome_export(scenario)
    rhizome_ms = round((time.perf_counter() - rhizome_started) * 1000, 3)

    pollen_started = time.perf_counter()
    pollen_relay = build_pollen_relay(scenario)
    pollen_ms = round((time.perf_counter() - pollen_started) * 1000, 3)

    meristem_result = call_meristem_local(
        endpoint=endpoint,
        model=model,
        scenario=scenario,
        timeout_s=timeout_s,
        keep_alive=keep_alive,
        num_predict=num_predict,
    )
    meristem_ms = meristem_result.get("wall_clock_ms")
    validation_ms = meristem_result.get("validation_ms")
    end_to_end_ms = round((time.perf_counter() - started) * 1000, 3)

    return {
        "scenario_id": scenario.scenario_id,
        "description": scenario.description,
        "ok": meristem_result["ok"],
        "rhizome_export": rhizome_export,
        "pollen_relay": pollen_relay,
        "timings_ms": {
            "rhizome_export_ms": rhizome_ms,
            "pollen_relay_ms": pollen_ms,
            "meristem_generate_ms": meristem_ms,
            "validation_ms": validation_ms,
            "end_to_end_ms": end_to_end_ms,
        },
        "meristem": {key: value for key, value in meristem_result.items() if key not in {"ok", "wall_clock_ms", "validation_ms"}},
    }


def summarize_run(results: list[dict[str, Any]]) -> dict[str, Any]:
    successes = [result for result in results if result.get("ok")]
    failures = [result for result in results if not result.get("ok")]
    e2e_values = [result["timings_ms"]["end_to_end_ms"] for result in successes if result["timings_ms"].get("end_to_end_ms") is not None]
    meristem_values = [result["timings_ms"]["meristem_generate_ms"] for result in successes if result["timings_ms"].get("meristem_generate_ms") is not None]
    tok_s_values = [result["meristem"].get("tokens_per_second") for result in successes if result["meristem"].get("tokens_per_second") is not None]

    return {
        "scenarios_total": len(results),
        "scenarios_ok": len(successes),
        "scenarios_failed": len(failures),
        "end_to_end_ms_p50": round(percentile(e2e_values, 0.50), 3) if e2e_values else None,
        "end_to_end_ms_p95": round(percentile(e2e_values, 0.95), 3) if e2e_values else None,
        "meristem_generate_ms_p50": round(percentile(meristem_values, 0.50), 3) if meristem_values else None,
        "meristem_generate_ms_p95": round(percentile(meristem_values, 0.95), 3) if meristem_values else None,
        "tokens_per_second_avg": round(statistics.fmean(tok_s_values), 3) if tok_s_values else None,
        "result_class": "failed" if failures else "engineering-pass",
    }


def render_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Cross-node E2E report",
        "",
        f"- captured_at: `{report['captured_at']}`",
        f"- model: `{report['model']['name']}`",
        f"- host: `{report['host']['label']}`",
        f"- scenarios_ok: `{report['summary']['scenarios_ok']}/{report['summary']['scenarios_total']}`",
        f"- end_to_end_ms_p50: `{report['summary']['end_to_end_ms_p50']}`",
        f"- tokens_per_second_avg: `{report['summary']['tokens_per_second_avg']}`",
        "",
        "## Scenarios",
        "",
    ]
    for result in report["results"]:
        lines.extend(
            [
                f"### {result['scenario_id']}",
                "",
                f"- ok: `{result['ok']}`",
                f"- rhizome_export_ms: `{result['timings_ms']['rhizome_export_ms']}`",
                f"- pollen_relay_ms: `{result['timings_ms']['pollen_relay_ms']}`",
                f"- meristem_generate_ms: `{result['timings_ms']['meristem_generate_ms']}`",
                f"- end_to_end_ms: `{result['timings_ms']['end_to_end_ms']}`",
            ]
        )
        if result["ok"]:
            lines.extend(
                [
                    f"- delta_id: `{result['meristem']['policy_delta']['delta_id']}`",
                    f"- tokens_per_second: `{result['meristem'].get('tokens_per_second')}`",
                ]
            )
        else:
            lines.append(f"- error: `{result['meristem'].get('error')}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _default_output_paths(model: str, host_label: str | None) -> tuple[Path, Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    date_prefix = time.strftime("%Y-%m-%d")
    model_slug = slugify(model.replace(":", "-"))
    host_slug = slugify(host_label or platform.node() or "unknown-host")
    stem = f"{date_prefix}_{model_slug}_{host_slug}_cross-node-e2e"
    return REPORTS_DIR / f"{stem}.json", REPORTS_DIR / f"{stem}.md"


def run_harness(
    *,
    endpoint: str,
    model: str,
    scenario_ids: list[str] | None,
    timeout_s: int,
    keep_alive: str,
    num_predict: int,
    host_label: str | None = None,
) -> dict[str, Any]:
    available = scenario_map()
    selected_ids = scenario_ids or list(available.keys())
    selected = [available[scenario_id] for scenario_id in selected_ids]

    results: list[dict[str, Any]] = []
    for scenario in selected:
        result = run_scenario(
            endpoint=endpoint,
            model=model,
            scenario=scenario,
            timeout_s=timeout_s,
            keep_alive=keep_alive,
            num_predict=num_predict,
        )
        results.append(result)
        print(
            f"[{'OK' if result['ok'] else 'FAIL'}] {scenario.scenario_id} "
            f"e2e={result['timings_ms']['end_to_end_ms']}ms "
            f"meristem={result['timings_ms']['meristem_generate_ms']}ms"
        )

    return {
        "captured_at": utc_now_iso(),
        "host": {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "label": host_label or slugify(platform.node() or "unknown-host"),
        },
        "model": {"name": model, "runtime": "ollama", "endpoint": endpoint},
        "benchmark_config": {
            "timeout_sec": timeout_s,
            "keep_alive": keep_alive,
            "num_predict": num_predict,
            "scenario_ids": selected_ids,
        },
        "summary": summarize_run(results),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Modelo Ollama usado por Meristem, por ejemplo gemma4:e4b.")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="Endpoint base de Ollama.")
    parser.add_argument("--scenario", action="append", dest="scenario_ids", help="Scenario id a ejecutar. Repetible.")
    parser.add_argument("--timeout-sec", type=int, default=180, help="Timeout por llamada a Ollama.")
    parser.add_argument("--keep-alive", default="15m", help="Valor keep_alive para Ollama.")
    parser.add_argument("--num-predict", type=int, default=192, help="Tokens maximos para la respuesta estructurada.")
    parser.add_argument("--hardware-label", default=None, help="Etiqueta opcional para los ficheros de salida.")
    parser.add_argument("--output-json", type=Path, default=None, help="Ruta del reporte JSON.")
    parser.add_argument("--output-md", type=Path, default=None, help="Ruta del resumen Markdown.")
    args = parser.parse_args()

    report = run_harness(
        endpoint=args.endpoint,
        model=args.model,
        scenario_ids=args.scenario_ids,
        timeout_s=args.timeout_sec,
        keep_alive=args.keep_alive,
        num_predict=args.num_predict,
        host_label=args.hardware_label,
    )

    output_json, output_md = _default_output_paths(args.model, args.hardware_label)
    if args.output_json is not None:
        output_json = args.output_json
    if args.output_md is not None:
        output_md = args.output_md

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown_report(report), encoding="utf-8")
    print(output_json)
    print(output_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
