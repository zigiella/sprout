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


class RhizomeReadStore:
    """Loads contract-shaped JSON objects from a local directory."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or default_data_dir()

    def status(self) -> dict[str, str]:
        return {
            "status": "ready",
            "version": VERSION,
            "node_id": "rhizome_01",
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
                rationale = str(receipt.get("rationale_short") or "").strip()
                return {"explanation": rationale or "DecisionReceipt sin rationale_short."}
        return None


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

        try:
            if path == "/status":
                self._send_json(HTTPStatus.OK, self.store.status())
                return

            if path == "/snapshot/latest":
                self._send_json(HTTPStatus.OK, self.store.latest_snapshot())
                return

            if path == "/receipts":
                since = parse_qs(parsed.query).get("since", [None])[0]
                self._send_json(HTTPStatus.OK, self.store.receipts(since=since))
                return

            prefix = "/explain/decision/"
            if path.startswith(prefix):
                decision_id = unquote(path[len(prefix) :])
                explanation = self.store.explain_decision(decision_id)
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


def make_server(host: str, port: int, data_dir: Path | None = None) -> ThreadingHTTPServer:
    class Handler(RhizomeSyncHandler):
        store = RhizomeReadStore(data_dir=data_dir)

    return ThreadingHTTPServer((host, port), Handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve Rhizome read endpoints for Pollen.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=13010)
    parser.add_argument("--data-dir", type=Path, default=default_data_dir())
    args = parser.parse_args()

    server = make_server(args.host, args.port, args.data_dir)
    print(f"rhizome_sync_facade listening on http://{args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
