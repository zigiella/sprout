"""Read-only Rhizome HTTP facade for Pollen.

This is a small host-side bridge for the MVP: it exposes the local Rhizome
read API that Pollen already knows how to consume, without touching ESP32,
actuators or the llama.cpp inference runtime.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

VERSION = "0.1.0"
SUPPORTED_LOCALES = {"es", "en"}
MAX_POLICY_BODY_BYTES = 128 * 1024
POLICY_ORIGIN_POLLEN_VISIT = "pollen-visit"
POLICY_SCOPE_TRANSIENT = "transient"
POLICY_TTL_MAX_SECONDS = 12 * 60 * 60
SAFE_ID_RE = re.compile(r"[^A-Za-z0-9_.-]+")
NARRATOR_TIMEOUT_S = 45
NARRATOR_MAX_RECEIPTS = 8


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_data_dir() -> Path:
    return _repo_root() / "code" / "shared" / "schemas" / "examples"


def default_state_dir(node_id: str) -> Path:
    return Path("/tmp") / "sprout_rhizome_sync_facade" / node_id


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    tmp_path.replace(path)


def _parse_zulu(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _format_zulu(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_id(value: str) -> str:
    safe = SAFE_ID_RE.sub("_", value).strip("._")
    return safe or "policy"


def _select_locale(query: dict[str, list[str]]) -> str:
    raw = query.get("locale", ["es"])[0].lower().strip()
    locale = raw.split("-")[0]
    return locale if locale in SUPPORTED_LOCALES else "es"


def _receipt_sort_key(receipt: dict[str, Any]) -> datetime:
    return _parse_zulu(receipt.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc)


def _receipt_window(receipts: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "total": len(receipts),
        "water": 0,
        "water_proposed": 0,
        "water_not_executed": 0,
        "block": 0,
        "alert": 0,
        "other": 0,
        "executed": 0,
    }
    for receipt in receipts:
        action = str(receipt.get("action", "")).upper()
        if action.startswith("WATER"):
            counts["water_proposed"] += 1
            if receipt.get("executed") is True:
                counts["water"] += 1
            else:
                counts["water_not_executed"] += 1
        elif action == "BLOCK":
            counts["block"] += 1
        elif action == "ALERT":
            counts["alert"] += 1
        else:
            counts["other"] += 1
        if receipt.get("executed") is True:
            counts["executed"] += 1
    return counts


def _tank_pct(snapshot: dict[str, Any]) -> float | None:
    value = snapshot.get("sensors", {}).get("tank_level_pct")
    return float(value) if isinstance(value, int | float) else None


def _severity(snapshot: dict[str, Any], counts: dict[str, int]) -> str:
    tank = _tank_pct(snapshot)
    if counts["alert"] > 0:
        return "alert"
    if counts["block"] > 0 or (tank is not None and tank < 30):
        return "attention"
    return "ok"


def _is_simulation_data(data_dir: Path) -> bool:
    normalized = str(data_dir.resolve()).replace("\\", "/")
    return "/demo_data/" in normalized or "/schemas/examples" in normalized


def _plural_es(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def _plural_en(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def _extract_json_object(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    if not stripped:
        return None
    if stripped.startswith("```"):
        first = stripped.find("{")
        last = stripped.rfind("}")
        if first != -1 and last > first:
            stripped = stripped[first : last + 1]
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _bounded_string(value: Any, max_len: int) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = " ".join(value.strip().split())
    if not cleaned or len(cleaned) > max_len:
        return None
    return cleaned


def _validated_narrative_patch(payload: Any) -> dict[str, Any] | None:
    obj = _require_dict_or_none(payload)
    if obj is None:
        return None

    headline = _bounded_string(obj.get("headline"), 140)
    summary = _bounded_string(obj.get("summary"), 700)
    recommendation = _bounded_string(obj.get("recommendation"), 260)
    highlights_raw = obj.get("highlights")
    if not headline or not summary or not recommendation or not isinstance(highlights_raw, list):
        return None

    highlights: list[str] = []
    for item in highlights_raw[:5]:
        highlight = _bounded_string(item, 220)
        if highlight:
            highlights.append(highlight)
    if not highlights:
        return None

    return {
        "headline": headline,
        "summary": summary,
        "highlights": highlights,
        "recommendation": recommendation,
    }


def _require_dict_or_none(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _compact_receipt_for_narrator(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision_id": receipt.get("decision_id"),
        "created_at": receipt.get("created_at"),
        "action": receipt.get("action"),
        "executed": receipt.get("executed"),
        "blocked_reason": receipt.get("blocked_reason"),
        "action_params": receipt.get("action_params"),
        "confidence": receipt.get("confidence"),
        "rationale_short": receipt.get("rationale_short"),
    }


def _gemma_visit_narrative(
    *,
    adapter_url: str,
    model: str,
    locale: str,
    node_id: str,
    snapshot: dict[str, Any],
    receipts: list[dict[str, Any]],
    deterministic_summary: dict[str, Any],
) -> tuple[dict[str, Any] | None, str | None]:
    adapter_url = adapter_url.rstrip("/")
    recent_receipts = sorted(receipts, key=_receipt_sort_key)[-NARRATOR_MAX_RECEIPTS:]
    prompt = {
        "task": "rhizome_visit_summary_narrator",
        "locale": locale,
        "node_id": node_id,
        "rules": [
            "Return only valid JSON.",
            "Do not change counts, actions, timestamps, execution flags or reason codes.",
            "Do not claim water was executed unless executed=true.",
            "Do not invent sensor readings or events.",
            "Write for a farmer returning after being away.",
            "No chain-of-thought.",
        ],
        "truth_fields": {
            "severity": deterministic_summary["severity"],
            "counts": deterministic_summary["counts"],
            "simulation": deterministic_summary["simulation"],
            "latest_snapshot_id": deterministic_summary.get("latest_snapshot_id"),
        },
        "current_snapshot": {
            "snapshot_id": snapshot.get("snapshot_id"),
            "created_at": snapshot.get("created_at"),
            "sensors": snapshot.get("sensors", {}),
            "mode": snapshot.get("mode"),
            "pending_contradictions": snapshot.get("pending_contradictions", []),
        },
        "recent_receipts": [_compact_receipt_for_narrator(receipt) for receipt in recent_receipts],
        "deterministic_draft": {
            "headline": deterministic_summary["headline"],
            "summary": deterministic_summary["summary"],
            "highlights": deterministic_summary["highlights"],
            "recommendation": deterministic_summary["recommendation"],
        },
        "output_schema": {
            "headline": "string",
            "summary": "string",
            "highlights": ["string"],
            "recommendation": "string",
        },
    }
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Gemma 4 inside Sprout Pollen/Rhizome. "
                    "Rewrite validated irrigation receipts into a short operator summary. "
                    "You are not a source of truth."
                ),
            },
            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
        ],
        "stream": False,
        "think": False,
        "options": {"temperature": 0.2, "num_ctx": 2048, "num_predict": 320},
    }
    request = urllib.request.Request(
        f"{adapter_url}/api/chat",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=NARRATOR_TIMEOUT_S) as response:
            response_body = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return None, f"gemma_narrator_error:{exc.__class__.__name__}"

    content = response_body.get("message", {}).get("content", "")
    parsed = _extract_json_object(content) if isinstance(content, str) else None
    patch = _validated_narrative_patch(parsed)
    if patch is None:
        return None, "gemma_narrator_invalid_json_or_schema"
    return patch, None


class PolicyValidationError(ValueError):
    def __init__(self, reason_code: str, detail: str, status: HTTPStatus = HTTPStatus.BAD_REQUEST) -> None:
        super().__init__(detail)
        self.reason_code = reason_code
        self.detail = detail
        self.status = status


def _require_dict(value: Any, reason_code: str, detail: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PolicyValidationError(reason_code, detail)
    return value


def _require_string(value: Any, reason_code: str, detail: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PolicyValidationError(reason_code, detail)
    return value.strip()


def _require_number(value: Any, reason_code: str, detail: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise PolicyValidationError(reason_code, detail)
    return float(value)


def _validate_hour(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 23:
        raise PolicyValidationError("policy_schema_invalid", f"{field_name} debe ser entero 0..23")
    return value


def _validate_threshold_map(value: Any) -> None:
    thresholds = _require_dict(
        value,
        "policy_schema_invalid",
        "rules.soil_moisture_thresholds debe ser object",
    )
    if not thresholds:
        raise PolicyValidationError("policy_schema_invalid", "rules.soil_moisture_thresholds no puede estar vacio")

    for name, raw_threshold in thresholds.items():
        _require_string(name, "policy_schema_invalid", "threshold id no puede estar vacio")
        threshold = _require_dict(raw_threshold, "policy_schema_invalid", f"threshold {name} debe ser object")
        min_pct = _require_number(
            threshold.get("min_pct"),
            "policy_schema_invalid",
            f"threshold {name}.min_pct debe ser numero",
        )
        target_pct = _require_number(
            threshold.get("target_pct"),
            "policy_schema_invalid",
            f"threshold {name}.target_pct debe ser numero",
        )
        if not 0 <= min_pct <= 100 or not 0 <= target_pct <= 100:
            raise PolicyValidationError("policy_schema_invalid", f"threshold {name} debe estar en 0..100")
        if target_pct < min_pct:
            raise PolicyValidationError("policy_schema_invalid", f"threshold {name}.target_pct < min_pct")


def _validate_policy_packet(raw_policy: Any, node_id: str) -> dict[str, Any]:
    policy = _require_dict(raw_policy, "policy_schema_invalid", "PolicyPacket debe ser JSON object")

    required = {
        "schema_version",
        "created_at",
        "origin_node_id",
        "policy_id",
        "target_node_id",
        "valid_until",
        "version_chain",
        "mode_default",
        "rules",
    }
    missing = sorted(field for field in required if field not in policy)
    if missing:
        raise PolicyValidationError("policy_schema_missing_fields", f"faltan campos requeridos: {missing}")

    if policy.get("schema_version") != "1.0":
        raise PolicyValidationError("policy_schema_invalid", "schema_version debe ser '1.0'")

    policy_id = _require_string(policy.get("policy_id"), "policy_schema_invalid", "policy_id requerido")
    _require_string(policy.get("origin_node_id"), "policy_schema_invalid", "origin_node_id requerido")
    target_node_id = _require_string(policy.get("target_node_id"), "policy_schema_invalid", "target_node_id requerido")
    if target_node_id != node_id:
        raise PolicyValidationError(
            "target_node_mismatch",
            f"target_node_id={target_node_id!r} no coincide con node_id={node_id!r}",
            status=HTTPStatus.CONFLICT,
        )

    origin = policy.get("policy_origin")
    if origin != POLICY_ORIGIN_POLLEN_VISIT:
        raise PolicyValidationError(
            "policy_origin_invalid",
            "POST /policy acepta solo policy_origin='pollen-visit'",
        )

    scope = policy.get("policy_scope", POLICY_SCOPE_TRANSIENT)
    if scope != POLICY_SCOPE_TRANSIENT:
        raise PolicyValidationError(
            "policy_scope_invalid",
            "policy_origin='pollen-visit' exige policy_scope='transient' o campo omitido",
        )

    try:
        created_at = _parse_zulu(policy.get("created_at"))
        valid_until = _parse_zulu(policy.get("valid_until"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise PolicyValidationError("policy_schema_invalid", "created_at y valid_until deben ser UTC Zulu") from exc
    if created_at is None or valid_until is None:
        raise PolicyValidationError("policy_schema_invalid", "created_at y valid_until deben ser UTC Zulu")
    if valid_until <= created_at:
        raise PolicyValidationError("policy_valid_until_invalid", "valid_until debe ser posterior a created_at")
    if valid_until <= datetime.now(timezone.utc):
        raise PolicyValidationError("policy_expired", "PolicyPacket pollen-visit ya esta caducado")
    ttl_seconds = (valid_until - created_at).total_seconds()
    if ttl_seconds > POLICY_TTL_MAX_SECONDS:
        raise PolicyValidationError("policy_ttl_invalid", "PolicyPacket pollen-visit no puede superar TTL 12h")

    version_chain = policy.get("version_chain")
    if not isinstance(version_chain, list) or not version_chain:
        raise PolicyValidationError("policy_schema_invalid", "version_chain debe ser lista no vacia")
    for version in version_chain:
        _require_string(version, "policy_schema_invalid", "version_chain contiene valor invalido")

    if policy.get("mode_default") not in {"normal", "conservative", "alert"}:
        raise PolicyValidationError("policy_schema_invalid", "mode_default invalido")

    rules = _require_dict(policy.get("rules"), "policy_schema_invalid", "rules debe ser object")
    window = _require_dict(
        rules.get("watering_window"),
        "policy_schema_invalid",
        "rules.watering_window debe ser object",
    )
    start_hour = _validate_hour(window.get("start_hour_local"), "rules.watering_window.start_hour_local")
    end_hour = _validate_hour(window.get("end_hour_local"), "rules.watering_window.end_hour_local")
    if end_hour <= start_hour:
        raise PolicyValidationError("policy_schema_invalid", "watering_window no puede cruzar medianoche en MVP")

    _validate_threshold_map(rules.get("soil_moisture_thresholds"))

    max_duration = rules.get("max_watering_duration_s")
    if not isinstance(max_duration, int) or max_duration <= 0:
        raise PolicyValidationError("policy_schema_invalid", "max_watering_duration_s debe ser entero positivo")

    daily_budget = _require_number(
        rules.get("daily_water_budget_liters"),
        "policy_schema_invalid",
        "daily_water_budget_liters debe ser numero",
    )
    if daily_budget <= 0:
        raise PolicyValidationError("policy_schema_invalid", "daily_water_budget_liters debe ser positivo")

    tank_minimum = _require_number(
        rules.get("tank_minimum_pct"),
        "policy_schema_invalid",
        "tank_minimum_pct debe ser numero",
    )
    if not 0 <= tank_minimum <= 100:
        raise PolicyValidationError("policy_schema_invalid", "tank_minimum_pct debe estar en 0..100")

    if not isinstance(rules.get("require_vision_confirmation"), bool):
        raise PolicyValidationError("policy_schema_invalid", "require_vision_confirmation debe ser boolean")

    triggers = rules.get("conservative_triggers", [])
    if not isinstance(triggers, list) or not all(isinstance(item, str) for item in triggers):
        raise PolicyValidationError("policy_schema_invalid", "conservative_triggers debe ser lista de strings")

    normalized = json.loads(json.dumps(policy, ensure_ascii=False))
    normalized["policy_id"] = policy_id
    normalized["policy_origin"] = POLICY_ORIGIN_POLLEN_VISIT
    normalized["policy_scope"] = POLICY_SCOPE_TRANSIENT
    return normalized


def _explain_receipt(receipt: dict[str, Any], locale: str) -> str:
    action = str(receipt.get("action", "")).upper()
    params = receipt.get("action_params", {})
    rationale = str(receipt.get("rationale_full") or receipt.get("rationale_short") or "").strip()
    blocked_reason = str(receipt.get("blocked_reason") or "").strip()
    executed = receipt.get("executed") is True

    if locale == "en":
        if action.startswith("WATER"):
            duration = params.get("duration_s")
            liters = params.get("expected_liters")
            if not executed:
                return (
                    f"Rhizome proposed {action} for {duration}s, expecting about {liters} L, "
                    f"but did not execute it. Reason code: {blocked_reason or 'not specified'}. "
                    f"Receipt note: {rationale}"
                )
            return (
                f"Rhizome executed {action} for {duration}s, expecting about {liters} L. "
                "The decision was allowed because the snapshot and active policy did not hit "
                f"a safety veto. Receipt note: {rationale}"
            )
        if action == "BLOCK":
            return (
                "Rhizome blocked the proposed action because a safety condition had priority. "
                f"Reason code: {blocked_reason or 'not specified'}. "
                "The detailed DecisionReceipt remains available for audit."
            )
        if action == "ALERT":
            return "Rhizome raised an alert and did not water."
        return f"Rhizome recorded {action}."

    if action.startswith("WATER"):
        duration = params.get("duration_s")
        liters = params.get("expected_liters")
        if not executed:
            return (
                f"Rhizome propuso {action} durante {duration}s, con unos {liters} L esperados, "
                f"pero no lo ejecutó. Código: {blocked_reason or 'sin especificar'}. "
                f"Nota del recibo: {rationale}"
            )
        return (
            f"Rhizome ejecutó {action} durante {duration}s, con unos {liters} L esperados. "
            "La decisión pasó porque el snapshot y la política activa no activaron ningún veto "
            f"de seguridad. Nota del recibo: {rationale}"
        )
    if action == "BLOCK":
        return (
            "Rhizome bloqueó la acción propuesta porque una condición de seguridad tenía prioridad. "
            f"Código: {blocked_reason or 'sin especificar'}. Nota del recibo: {rationale}"
        )
    if action == "ALERT":
        return f"Rhizome elevó una alerta y no regó. Nota del recibo: {rationale}"
    return f"Rhizome registró {action}. Nota del recibo: {rationale}"


def _summary_text(
    node_id: str,
    snapshot: dict[str, Any],
    receipts: list[dict[str, Any]],
    counts: dict[str, int],
    locale: str,
) -> tuple[str, str, list[str], str]:
    tank = _tank_pct(snapshot)
    sensors = snapshot.get("sensors", {})
    soil_a = sensors.get("soil_moisture_a_pct")
    soil_b = sensors.get("soil_moisture_b_pct")
    latest = sorted(receipts, key=_receipt_sort_key)[-1] if receipts else None
    latest_action = latest.get("action") if latest else None

    if locale == "en":
        headline = f"{node_id}: {counts['total']} decisions since the last visit"
        if counts["block"] or counts["alert"]:
            headline = f"{node_id}: attention needed after your absence"
        highlights = [
            (
                f"{_plural_en(counts['water'], 'watering event executed', 'watering events executed')}, "
                f"{_plural_en(counts['water_not_executed'], 'water proposal not executed', 'water proposals not executed')}, "
                f"{_plural_en(counts['block'], 'safety block', 'safety blocks')}, "
                f"{_plural_en(counts['alert'], 'alert', 'alerts')}."
            ),
            f"Current tank level is {tank:.0f}%." if tank is not None else "Current tank level is unavailable.",
            (
                f"Soil probes A/B read {soil_a:.0f}% / {soil_b:.0f}%."
                if isinstance(soil_a, int | float) and isinstance(soil_b, int | float)
                else "Soil probe readings are incomplete."
            ),
        ]
        if latest_action:
            highlights.append(f"Latest recorded decision: {latest_action}.")
        summary = (
            f"While you were away, {node_id} recorded {counts['total']} decisions. "
            f"It executed {_plural_en(counts['water'], 'watering event', 'watering events')} "
            f"and recorded {_plural_en(counts['water_not_executed'], 'water proposal not executed', 'water proposals not executed')}. "
            f"It also recorded {_plural_en(counts['block'], 'blocked action', 'blocked actions')}. "
            f"Tank is now {tank:.0f}% and soil probes A/B are {soil_a:.0f}% / {soil_b:.0f}%."
            if (
                tank is not None
                and isinstance(soil_a, int | float)
                and isinstance(soil_b, int | float)
            )
            else f"While you were away, {node_id} recorded {counts['total']} decisions."
        )
        recommendation = (
            "Review the blocked receipt before carrying new water policies."
            if counts["block"] or counts["alert"]
            else "No urgent intervention is suggested by this summary."
        )
        return headline, summary, highlights, recommendation

    headline = f"{node_id}: {counts['total']} decisiones desde la ultima visita"
    if counts["block"] or counts["alert"]:
        headline = f"{node_id}: conviene revisar lo ocurrido en tu ausencia"
    highlights = [
        (
            f"{_plural_es(counts['water'], 'riego ejecutado', 'riegos ejecutados')}, "
            f"{_plural_es(counts['water_not_executed'], 'propuesta de riego no ejecutada', 'propuestas de riego no ejecutadas')}, "
            f"{_plural_es(counts['block'], 'bloqueo de seguridad', 'bloqueos de seguridad')}, "
            f"{_plural_es(counts['alert'], 'alerta', 'alertas')}."
        ),
        f"El deposito esta al {tank:.0f}%." if tank is not None else "No hay lectura de deposito.",
        (
            f"Las sondas de suelo A/B marcan {soil_a:.0f}% / {soil_b:.0f}%."
            if isinstance(soil_a, int | float) and isinstance(soil_b, int | float)
            else "Las lecturas de suelo estan incompletas."
        ),
    ]
    if latest_action:
        highlights.append(f"Ultima decision registrada: {latest_action}.")
    summary = (
        f"Durante tu ausencia, {node_id} registro {counts['total']} decisiones. "
        f"Ejecutó {_plural_es(counts['water'], 'riego', 'riegos')} "
        f"y registró {_plural_es(counts['water_not_executed'], 'propuesta de riego no ejecutada', 'propuestas de riego no ejecutadas')}. "
        f"También registró {_plural_es(counts['block'], 'accion bloqueada', 'acciones bloqueadas')}. "
        f"El deposito esta al {tank:.0f}% y las sondas A/B marcan {soil_a:.0f}% / {soil_b:.0f}%."
        if (
            tank is not None
            and isinstance(soil_a, int | float)
            and isinstance(soil_b, int | float)
        )
        else f"Durante tu ausencia, {node_id} registro {counts['total']} decisiones."
    )
    recommendation = (
        "Revisa el recibo bloqueado antes de transportar nuevas politicas."
        if counts["block"] or counts["alert"]
        else "El resumen no sugiere una intervencion urgente."
    )
    return headline, summary, highlights, recommendation


class RhizomeReadStore:
    """Loads contract-shaped JSON objects and stores transient policies."""

    def __init__(
        self,
        data_dir: Path | None = None,
        node_id: str = "rhizome_01",
        state_dir: Path | None = None,
        narrator_url: str | None = None,
        narrator_model: str = "gemma4:e2b",
    ) -> None:
        self.data_dir = data_dir or default_data_dir()
        self.node_id = node_id
        self.state_dir = state_dir or default_state_dir(node_id)
        self.simulation = _is_simulation_data(self.data_dir)
        self.narrator_url = narrator_url
        self.narrator_model = narrator_model

    @property
    def active_policy_path(self) -> Path:
        return self.state_dir / "active_policy.json"

    def status(self) -> dict[str, str]:
        payload = {
            "status": "ready",
            "version": VERSION,
            "node_id": self.node_id,
            "mode": "read_only_facade",
            "source": str(self.data_dir),
        }
        active_policy = self.active_policy_record()
        if active_policy is not None:
            payload["active_policy_id"] = active_policy["policy"]["policy_id"]
            payload["active_policy_origin"] = active_policy["policy"].get("policy_origin", "")
            payload["active_policy_scope"] = active_policy["policy"].get("policy_scope", "")
        if self.narrator_url:
            payload["gemma_visit_narrator"] = "configured"
        return payload

    def latest_snapshot(self) -> dict[str, Any]:
        return _load_json(self.data_dir / "rhizome_snapshot.json")

    def receipts(self, since: str | None = None) -> list[dict[str, Any]]:
        candidates = [
            self.data_dir / "decision_receipt.json",
            self.data_dir / "decision_receipt_blocked.json",
        ]
        receipts = [
            receipt
            for path in candidates
            if path.exists()
            for receipt in [_load_json(path)]
        ]

        since_dt = _parse_zulu(since)
        if since_dt is None:
            return receipts

        filtered: list[dict[str, Any]] = []
        for receipt in receipts:
            created_at = _parse_zulu(receipt.get("created_at"))
            if created_at is not None and created_at >= since_dt:
                filtered.append(receipt)
        return filtered

    def explain_decision(self, decision_id: str) -> dict[str, str] | None:
        for receipt in self.receipts():
            if receipt.get("decision_id") == decision_id:
                return {
                    "decision_id": decision_id,
                    "node_id": self.node_id,
                    "explanation": _explain_receipt(receipt, "es"),
                    "source": "deterministic_receipt_explainer",
                }
        return None

    def explain_decision_locale(self, decision_id: str, locale: str) -> dict[str, str] | None:
        for receipt in self.receipts():
            if receipt.get("decision_id") == decision_id:
                return {
                    "decision_id": decision_id,
                    "node_id": self.node_id,
                    "locale": locale,
                    "explanation": _explain_receipt(receipt, locale),
                    "source": "deterministic_receipt_explainer",
                }
        return None

    def visit_summary(self, since: str | None = None, locale: str = "es") -> dict[str, Any]:
        snapshot = self.latest_snapshot()
        receipts = self.receipts(since=since)
        counts = _receipt_window(receipts)
        severity = _severity(snapshot, counts)
        headline, summary, highlights, recommendation = _summary_text(
            self.node_id,
            snapshot,
            receipts,
            counts,
            locale,
        )
        payload: dict[str, Any] = {
            "node_id": self.node_id,
            "locale": locale,
            "since": since,
            "severity": severity,
            "headline": headline,
            "summary": summary,
            "highlights": highlights,
            "recommendation": recommendation,
            "counts": counts,
            "latest_snapshot_id": snapshot.get("snapshot_id"),
            "source": "deterministic_visit_summary",
            "narrative_source": "deterministic_visit_summary",
            "simulation": self.simulation,
            "gemma_narrator": {
                "enabled": bool(self.narrator_url),
                "used": False,
                "model": self.narrator_model if self.narrator_url else None,
            },
        }
        if not self.narrator_url:
            return payload

        patch, error = _gemma_visit_narrative(
            adapter_url=self.narrator_url,
            model=self.narrator_model,
            locale=locale,
            node_id=self.node_id,
            snapshot=snapshot,
            receipts=receipts,
            deterministic_summary=payload,
        )
        if patch is None:
            payload["gemma_narrator"]["error"] = error or "gemma_narrator_unknown_error"
            return payload

        payload.update(patch)
        payload["narrative_source"] = "gemma_visit_narrator"
        payload["gemma_narrator"]["used"] = True
        return payload

    def active_policy_record(self) -> dict[str, Any] | None:
        if not self.active_policy_path.exists():
            return None
        return _load_json(self.active_policy_path)

    def accept_policy(self, raw_policy: Any) -> dict[str, Any]:
        policy = _validate_policy_packet(raw_policy, self.node_id)
        accepted_at = _format_zulu(datetime.now(timezone.utc))
        policy_id = policy["policy_id"]
        policy_file = self.state_dir / "policies" / f"{_safe_id(policy_id)}.json"
        record = {
            "accepted_at": accepted_at,
            "node_id": self.node_id,
            "policy": policy,
            "metadata": {
                "active_for_next_decision": True,
                "hard_limits_checked_by_facade": False,
                "schema_gate": "rhizome_sync_facade_v0",
            },
        }
        _write_json_atomic(policy_file, record)
        _write_json_atomic(self.active_policy_path, record)
        self._append_policy_event(policy_id, accepted_at)

        return {
            "status": "accepted",
            "node_id": self.node_id,
            "policy_id": policy_id,
            "target_node_id": policy["target_node_id"],
            "policy_origin": policy["policy_origin"],
            "policy_scope": policy["policy_scope"],
            "accepted_at": accepted_at,
            "active_for_next_decision": True,
            "hard_limits_checked_by_facade": False,
            "storage": {
                "active_policy": str(self.active_policy_path),
                "policy_record": str(policy_file),
            },
            "warnings": [
                "POST /policy valida schema y TTL; hard limits fisicos siguen en Mini-Evaluator y ESP32."
            ],
        }

    def _append_policy_event(self, policy_id: str, accepted_at: str) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        event = {
            "event": "policy_accepted",
            "accepted_at": accepted_at,
            "node_id": self.node_id,
            "policy_id": policy_id,
        }
        with (self.state_dir / "policy_events.jsonl").open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


class RhizomeSyncHandler(BaseHTTPRequestHandler):
    store: RhizomeReadStore = RhizomeReadStore()

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_json(self, status: HTTPStatus, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> Any:
        content_length_raw = self.headers.get("Content-Length")
        if not content_length_raw:
            raise PolicyValidationError("empty_body", "Content-Length requerido")
        try:
            content_length = int(content_length_raw)
        except ValueError as exc:
            raise PolicyValidationError("invalid_content_length", "Content-Length invalido") from exc
        if content_length <= 0:
            raise PolicyValidationError("empty_body", "Body JSON requerido")
        if content_length > MAX_POLICY_BODY_BYTES:
            raise PolicyValidationError("body_too_large", "Body demasiado grande")

        raw_body = self.rfile.read(content_length)
        try:
            return json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PolicyValidationError("invalid_json", "Body debe ser JSON UTF-8 valido") from exc

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)
        locale = _select_locale(query)

        try:
            if path == "/status":
                self._send_json(HTTPStatus.OK, self.store.status())
                return

            if path == "/snapshot/latest":
                self._send_json(HTTPStatus.OK, self.store.latest_snapshot())
                return

            if path == "/receipts":
                since = query.get("since", [None])[0]
                self._send_json(HTTPStatus.OK, self.store.receipts(since=since))
                return

            if path == "/summary/since":
                since = query.get("since", [None])[0]
                self._send_json(HTTPStatus.OK, self.store.visit_summary(since=since, locale=locale))
                return

            if path == "/policy/active":
                active_policy = self.store.active_policy_record()
                if active_policy is None:
                    self._send_json(
                        HTTPStatus.NOT_FOUND,
                        {"error": "policy_not_found", "node_id": self.store.node_id},
                    )
                    return
                self._send_json(HTTPStatus.OK, active_policy)
                return

            prefix = "/explain/decision/"
            if path.startswith(prefix):
                decision_id = unquote(path[len(prefix) :])
                explanation = self.store.explain_decision_locale(decision_id, locale)
                if explanation is None:
                    self._send_json(
                        HTTPStatus.NOT_FOUND,
                        {"error": "decision_not_found", "decision_id": decision_id},
                    )
                    return
                self._send_json(HTTPStatus.OK, explanation)
                return

            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found", "path": parsed.path})
        except FileNotFoundError as exc:
            self._send_json(
                HTTPStatus.SERVICE_UNAVAILABLE,
                {"error": "data_file_missing", "path": str(exc.filename)},
            )
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "bad_request", "detail": str(exc)})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        try:
            if path == "/policy":
                payload = self._read_json_body()
                ack = self.store.accept_policy(payload)
                self._send_json(HTTPStatus.OK, ack)
                return

            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found", "path": parsed.path})
        except PolicyValidationError as exc:
            self._send_json(
                exc.status,
                {
                    "error": "policy_rejected",
                    "reason_code": exc.reason_code,
                    "detail": exc.detail,
                    "node_id": self.store.node_id,
                },
            )
        except OSError as exc:
            self._send_json(
                HTTPStatus.SERVICE_UNAVAILABLE,
                {"error": "policy_storage_error", "detail": str(exc), "node_id": self.store.node_id},
            )


def make_server(
    host: str,
    port: int,
    data_dir: Path | None = None,
    node_id: str = "rhizome_01",
    state_dir: Path | None = None,
    narrator_url: str | None = None,
    narrator_model: str = "gemma4:e2b",
) -> ThreadingHTTPServer:
    class Handler(RhizomeSyncHandler):
        store = RhizomeReadStore(
            data_dir=data_dir,
            node_id=node_id,
            state_dir=state_dir,
            narrator_url=narrator_url,
            narrator_model=narrator_model,
        )

    return ThreadingHTTPServer((host, port), Handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve Rhizome read endpoints for Pollen.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=13010)
    parser.add_argument("--data-dir", type=Path, default=default_data_dir())
    parser.add_argument("--node-id", default="rhizome_01")
    parser.add_argument("--state-dir", type=Path, default=None)
    parser.add_argument("--narrator-url", default=None, help="Optional Ollama-compatible adapter URL for Gemma visit summaries.")
    parser.add_argument("--narrator-model", default="gemma4:e2b")
    args = parser.parse_args()

    server = make_server(
        args.host,
        args.port,
        args.data_dir,
        args.node_id,
        args.state_dir,
        narrator_url=args.narrator_url,
        narrator_model=args.narrator_model,
    )
    print(
        f"rhizome_sync_facade node_id={args.node_id} listening on http://{args.host}:{args.port}",
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
