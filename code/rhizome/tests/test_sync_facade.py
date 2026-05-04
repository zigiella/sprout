from __future__ import annotations

import json
import shutil
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from src.rhizome_sync_facade import default_data_dir, make_server


def _stop_server(server) -> None:
    server.shutdown()
    server.server_close()


def _get_json(base_url: str, path: str):
    with urllib.request.urlopen(f"{base_url}{path}", timeout=3) as response:
        assert response.headers["Content-Type"].startswith("application/json")
        return json.loads(response.read().decode("utf-8"))


def _run_server(data_dir: Path):
    server = make_server("127.0.0.1", 0, data_dir)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, f"http://{host}:{port}"


class SyncFacadeTest(unittest.TestCase):
    def test_pollen_read_endpoints_return_contract_shapes(self):
        server, base_url = _run_server(default_data_dir())
        try:
            status = _get_json(base_url, "/status")
            snapshot = _get_json(base_url, "/snapshot/latest")
            receipts = _get_json(base_url, "/receipts")
            explanation = _get_json(base_url, f"/explain/decision/{receipts[0]['decision_id']}")
        finally:
            _stop_server(server)

        self.assertEqual(status["status"], "ready")
        self.assertEqual(status["mode"], "read_only_facade")
        self.assertTrue(snapshot["snapshot_id"])
        self.assertGreaterEqual(snapshot["sensors"]["tank_level_pct"], 0)
        self.assertIsInstance(receipts, list)
        self.assertTrue(receipts[0]["decision_id"])
        self.assertEqual(explanation["explanation"], receipts[0]["rationale_short"])

    def test_receipts_since_filter_uses_created_at(self):
        server, base_url = _run_server(default_data_dir())
        try:
            all_receipts = _get_json(base_url, "/receipts")
            future_receipts = _get_json(base_url, "/receipts?since=2099-01-01T00:00:00Z")
        finally:
            _stop_server(server)

        self.assertGreaterEqual(len(all_receipts), 1)
        self.assertEqual(future_receipts, [])

    def test_explain_missing_decision_returns_structured_404(self):
        server, base_url = _run_server(default_data_dir())
        try:
            try:
                _get_json(base_url, "/explain/decision/not-real")
            except urllib.error.HTTPError as exc:
                payload = json.loads(exc.read().decode("utf-8"))
                status = exc.code
            else:
                raise AssertionError("expected HTTPError")
        finally:
            _stop_server(server)

        self.assertEqual(status, 404)
        self.assertEqual(payload, {"error": "decision_not_found", "decision_id": "not-real"})

    def test_missing_data_file_is_service_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            shutil.copy(default_data_dir() / "decision_receipt.json", data_dir / "decision_receipt.json")
            server, base_url = _run_server(data_dir)
            try:
                try:
                    _get_json(base_url, "/snapshot/latest")
                except urllib.error.HTTPError as exc:
                    payload = json.loads(exc.read().decode("utf-8"))
                    status = exc.code
                else:
                    raise AssertionError("expected HTTPError")
            finally:
                _stop_server(server)

        self.assertEqual(status, 503)
        self.assertEqual(payload["error"], "data_file_missing")
