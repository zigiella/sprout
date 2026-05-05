"""Read-only Rhizome HTTP facade for Pollen.

This is a small host-side bridge for the MVP: it exposes the local Rhizome
read API that Pollen already knows how to consume, without touching ESP32,
actuators or the llama.cpp inference runtime.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

VERSION = "0.1.0"
SUPPORTED_LOCALES = {"es", "en"}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_data_dir() -> Path:
    return _repo_root() / "code" / "shared" / "schemas" / "examples"


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _parse_zulu(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


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
        "block": 0,
        "alert": 0,
        "other": 0,
        "executed": 0,
    }
    for receipt in receipts:
        action = str(receipt.get("action", "")).upper()
        if action.startswith("WATER"):
            counts["water"] += 1
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


def _explain_receipt(receipt: dict[str, Any], locale: str) -> str:
    action = str(receipt.get("action", "")).upper()
    params = receipt.get("action_params", {})
    rationale = str(receipt.get("rationale_full") or receipt.get("rationale_short") or "").strip()
    blocked_reason = str(receipt.get("blocked_reason") or "").strip()

    if locale == "en":
        if action.startswith("WATER"):
            duration = params.get("duration_s")
            liters = params.get("expected_liters")
            return (
                f"Rhizome executed {action} for {duration}s, expecting about {liters} L. "
                "The decision was allowed because the snapshot and active policy did not hit "
                "a safety veto. The detailed DecisionReceipt remains available for audit."
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
                f"{counts['water']} watering events, {counts['block']} safety blocks, "
                f"{counts['alert']} alerts."
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
            f"It watered {counts['water']} times and blocked {counts['block']} actions. "
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
        f"{counts['water']} riegos, {counts['block']} bloqueos de seguridad, {counts['alert']} alertas.",
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
        f"Regó {counts['water']} veces y bloqueó {counts['block']} acciones. "
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
    """Loads contract-shaped JSON objects from a local directory."""

    def __init__(self, data_dir: Path | None = None, node_id: str = "rhizome_01") -> None:
        self.data_dir = data_dir or default_data_dir()
        self.node_id = node_id

    def status(self) -> dict[str, str]:
        return {
            "status": "ready",
            "version": VERSION,
            "node_id": self.node_id,
            "mode": "read_only_facade",
            "source": str(self.data_dir),
        }

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
        return {
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
            "source": "deterministic_demo_summary",
            "simulation": True,
        }


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


def make_server(
    host: str,
    port: int,
    data_dir: Path | None = None,
    node_id: str = "rhizome_01",
) -> ThreadingHTTPServer:
    class Handler(RhizomeSyncHandler):
        store = RhizomeReadStore(data_dir=data_dir, node_id=node_id)

    return ThreadingHTTPServer((host, port), Handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve Rhizome read endpoints for Pollen.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=13010)
    parser.add_argument("--data-dir", type=Path, default=default_data_dir())
    parser.add_argument("--node-id", default="rhizome_01")
    args = parser.parse_args()

    server = make_server(args.host, args.port, args.data_dir, args.node_id)
    print(
        f"rhizome_sync_facade node_id={args.node_id} listening on http://{args.host}:{args.port}",
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
