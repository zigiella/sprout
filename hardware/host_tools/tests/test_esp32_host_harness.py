from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import esp32_host_harness as harness


class FakeSerial:
    def __init__(
        self,
        responses_by_command: dict[str, list[str]],
        *,
        initial_lines: list[str] | None = None,
    ) -> None:
        self.responses_by_command = responses_by_command
        self.pending = [f"{line}\n".encode("utf-8") for line in (initial_lines or [])]
        self.written: list[str] = []
        self.timeout = 0.01

    def write(self, data: bytes) -> int:
        command = data.decode("utf-8").strip()
        self.written.append(command)
        for line in self.responses_by_command.get(command, []):
            self.pending.append(f"{line}\n".encode("utf-8"))
        return len(data)

    def readline(self) -> bytes:
        if self.pending:
            return self.pending.pop(0)
        return b""

    def reset_input_buffer(self) -> None:
        return None

    def reset_output_buffer(self) -> None:
        return None

    def close(self) -> None:
        return None


def test_bundled_scenarios_include_guardian_demo() -> None:
    scenarios = harness.bundled_scenarios()
    assert "guardian_demo" in scenarios
    assert "telemetry_stub_roundtrip" in scenarios


def test_run_scenario_saves_success_artifacts(tmp_path: Path) -> None:
    serial_port = FakeSerial(
        {
            "STATUS": ["STATUS_REPORT state=SAFE_IDLE"],
            "WATER A 12": ["REJECT reason=HEARTBEAT_PERDIDO cmd=WATER A 12"],
        },
        initial_lines=["HELLO fw=0.1.0 state=SAFE_IDLE"],
    )
    scenario = {
        "id": "unit_demo",
        "description": "Escenario de prueba",
        "startup_capture_s": 0.0,
        "steps": [
            {
                "type": "command",
                "name": "status",
                "send": "STATUS",
                "expect_all": ["STATUS_REPORT state=SAFE_IDLE"],
            },
            {
                "type": "command",
                "name": "water",
                "send": "WATER A 12",
                "expect_all": ["REJECT reason=HEARTBEAT_PERDIDO cmd=WATER A 12"],
            },
        ],
    }

    transcript, results, success = harness.run_scenario(
        serial_port,
        scenario,
        quiet_s=0.0,
        max_wait_s=0.0,
        sleep_fn=lambda _seconds: None,
    )

    assert success is True
    assert [result.ok for result in results] == [True, True]

    log_path, json_path = harness.save_artifacts(
        tmp_path,
        "unit_demo",
        port="COM5",
        baud=115200,
        scenario_path=tmp_path / "unit_demo.json",
        scenario=scenario,
        transcript=transcript,
        results=results,
        success=success,
    )

    assert log_path.exists()
    assert json_path.exists()
    assert "STATUS_REPORT state=SAFE_IDLE" in log_path.read_text(encoding="utf-8")
    assert '"success": true' in json_path.read_text(encoding="utf-8")


def test_run_scenario_reports_missing_expectation() -> None:
    serial_port = FakeSerial({"STATUS": ["STATUS_REPORT state=SAFE_IDLE"]})
    scenario = {
        "id": "unit_failure",
        "steps": [
            {
                "type": "command",
                "name": "status",
                "send": "STATUS",
                "expect_all": ["alert_code=NONE"],
            }
        ],
    }

    _transcript, results, success = harness.run_scenario(
        serial_port,
        scenario,
        quiet_s=0.0,
        max_wait_s=0.0,
        sleep_fn=lambda _seconds: None,
    )

    assert success is False
    assert results[0].missing_expectations == ["alert_code=NONE"]
