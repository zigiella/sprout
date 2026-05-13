from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))

from schemas.decision_receipt import DecisionReceipt
from schemas.rhizome_snapshot import RhizomeSnapshot

from src.rhizome_steward import (
    BoundedJsonlStore,
    ESP32CommandResult,
    FakeESP32Client,
    RhizomeSteward,
    SerialESP32Client,
    StewardConfig,
    Telemetry,
    zulu,
)


def _config(tmp: str, **overrides):
    values = {
        "state_dir": Path(tmp),
        "sync_facade_state_dir": Path(tmp) / "sync_facade",
        "decision_interval_s": 60,
        "cooldown_s": 3600,
        "requested_water_seconds": 8,
        "max_total_bytes": 64 * 1024,
        "retention_days": 30,
    }
    values.update(overrides)
    return StewardConfig(**values)


def _telemetry(*, soil_a_raw=30, tank_level_pct=70.0, flow_pulses=0):
    return Telemetry(
        collected_at=zulu(datetime.now(timezone.utc)),
        soil_a_raw=soil_a_raw,
        soil_b_raw=soil_a_raw,
        tank_level_pct=tank_level_pct,
        flow_pulses=flow_pulses,
        host_link="FRESH",
        host_age_ms=0,
    )


class RhizomeStewardTest(unittest.TestCase):
    def test_dry_soil_executes_water_when_explicitly_enabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(tmp, execute_water=True),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=30)),
            )
            result = steward.run_once()

            receipts = steward.store.iter_jsonl("decision_receipts")
            facade_snapshot_exists = (Path(tmp) / "facade_data" / "rhizome_snapshot.json").exists()
            facade_receipt_exists = (Path(tmp) / "facade_data" / "decision_receipt.json").exists()

        self.assertEqual(result["action"], "WATER_A")
        self.assertTrue(result["executed"])
        self.assertIsNone(result["blocked_reason"])
        self.assertEqual(receipts[-1]["execution_details"]["esp32_ack_status"], "OK")
        self.assertTrue(facade_snapshot_exists)
        self.assertTrue(facade_receipt_exists)

    def test_dry_soil_does_not_water_without_execute_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(tmp, execute_water=False),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=30)),
            )
            result = steward.run_once()

        self.assertEqual(result["action"], "WATER_A")
        self.assertFalse(result["executed"])
        self.assertEqual(result["blocked_reason"], "OBSERVE_MODE_EXECUTE_WATER_FALSE")

    def test_wet_soil_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(tmp, execute_water=True),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=70)),
            )
            result = steward.run_once()

        self.assertEqual(result["action"], "SKIP")
        self.assertFalse(result["executed"])
        self.assertEqual(result["blocked_reason"], "NO_ACTION_NEEDED")

    def test_tank_low_alerts_without_water(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(tmp, execute_water=True),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=20, tank_level_pct=10.0)),
            )
            result = steward.run_once()

        self.assertEqual(result["action"], "ALERT")
        self.assertFalse(result["executed"])
        self.assertEqual(result["blocked_reason"], "TANK_LOW")

    def test_missing_tank_sensor_defers_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(tmp, execute_water=True),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=20, tank_level_pct=None)),
            )
            result = steward.run_once()

        self.assertEqual(result["action"], "DEFER")
        self.assertEqual(result["blocked_reason"], "TANK_SENSOR_UNAVAILABLE")

    def test_minimal_hardware_mode_allows_missing_tank_with_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(tmp, execute_water=True, allow_missing_tank_sensor=True),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=20, tank_level_pct=None, flow_pulses=None)),
            )
            result = steward.run_once()
            snapshot = steward.store.load_json("current_snapshot.json")
            receipt = steward.store.load_json("last_decision_receipt.json")

        self.assertEqual(result["action"], "WATER_A")
        self.assertTrue(result["executed"])
        self.assertIsNotNone(snapshot)
        self.assertIsNotNone(receipt)
        self.assertIn("tank_level_unavailable", snapshot["pending_contradictions"])
        self.assertIn("flow_sensor_unavailable", receipt["contradictions"])
        RhizomeSnapshot.model_validate(snapshot)
        DecisionReceipt.model_validate(receipt)

    def test_strict_flow_mode_defers_when_flow_sensor_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(
                    tmp,
                    execute_water=True,
                    allow_missing_tank_sensor=True,
                    allow_missing_flow_sensor=False,
                ),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=20, tank_level_pct=None, flow_pulses=None)),
            )
            result = steward.run_once()

        self.assertEqual(result["action"], "DEFER")
        self.assertEqual(result["blocked_reason"], "FLOW_SENSOR_UNAVAILABLE")

    def test_cooldown_defers_second_water(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(tmp, execute_water=True),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=20)),
            )
            first = steward.run_once()
            second = steward.run_once()

        self.assertEqual(first["action"], "WATER_A")
        self.assertTrue(first["executed"])
        self.assertEqual(second["action"], "DEFER")
        self.assertEqual(second["blocked_reason"], "COOLDOWN_NOT_MET")

    def test_shadow_skeptic_records_observation_without_changing_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(tmp, execute_water=False),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=30)),
            )
            result = steward.run_once()
            shadow = steward.store.iter_jsonl("shadow_skeptic")

        self.assertEqual(result["action"], "WATER_A")
        self.assertFalse(shadow[-1]["affects_decision"])
        self.assertIn("reviewed_action", shadow[-1])

    def test_unknown_soil_defers(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(tmp, execute_water=True),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=1234)),
            )
            result = steward.run_once()

        self.assertEqual(result["action"], "DEFER")
        self.assertEqual(result["blocked_reason"], "SOIL_UNKNOWN")

    def test_unknown_soil_snapshot_remains_shared_schema_compatible(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(tmp, execute_water=True),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=1234)),
            )
            steward.run_once()
            snapshot = steward.store.load_json("current_snapshot.json")
            receipt = steward.store.load_json("last_decision_receipt.json")

        self.assertIsNotNone(snapshot)
        self.assertIsNotNone(receipt)
        RhizomeSnapshot.model_validate(snapshot)
        DecisionReceipt.model_validate(receipt)
        self.assertIn("soil_a_unavailable_or_uncalibrated", snapshot["pending_contradictions"])

    def test_raw_thresholds_allow_autonomy_with_uncalibrated_sensor_units(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(tmp, execute_water=True, soil_dry_below_raw=1500, soil_wet_above_raw=2600),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=1200)),
            )
            result = steward.run_once()

        self.assertEqual(result["action"], "WATER_A")
        self.assertTrue(result["executed"])

    def test_low_is_wet_raw_threshold_skips_current_wet_soil(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(
                    tmp,
                    execute_water=True,
                    soil_raw_polarity="low_is_wet",
                    soil_wet_below_raw=1300,
                    soil_dry_above_raw=2600,
                ),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=1265)),
            )
            result = steward.run_once()

        self.assertEqual(result["action"], "SKIP")
        self.assertFalse(result["executed"])

    def test_low_is_wet_raw_without_dry_threshold_defers_outside_wet_band(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(
                    tmp,
                    execute_water=True,
                    soil_raw_polarity="low_is_wet",
                    soil_wet_below_raw=1300,
                ),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=1700)),
            )
            result = steward.run_once()

        self.assertEqual(result["action"], "DEFER")
        self.assertFalse(result["executed"])

    def test_low_is_wet_raw_threshold_waters_when_dry_above_xilema_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(
                    tmp,
                    execute_water=True,
                    allow_missing_tank_sensor=True,
                    soil_raw_polarity="low_is_wet",
                    soil_wet_below_raw=1300,
                    soil_dry_above_raw=2200,
                ),
                FakeESP32Client(telemetry=_telemetry(soil_a_raw=2300, tank_level_pct=None)),
            )
            result = steward.run_once()
            snapshot = steward.store.load_json("current_snapshot.json")

        self.assertEqual(result["action"], "WATER_A")
        self.assertTrue(result["executed"])
        self.assertIsNotNone(snapshot)
        RhizomeSnapshot.model_validate(snapshot)
        sensors = snapshot["sensors"]
        self.assertEqual(sensors["soil_moisture_a_raw"], 2300)
        self.assertTrue(sensors["soil_moisture_a_pct_estimated"])
        self.assertEqual(sensors["soil_moisture_calibration"], "demo_raw_index")
        self.assertLessEqual(sensors["soil_moisture_a_pct"], 35.0)

    def test_test_only_ack_is_not_counted_as_physical_execution(self):
        class TestOnlyClient(FakeESP32Client):
            def water(self, plot: str, seconds: int) -> ESP32CommandResult:
                return ESP32CommandResult(
                    ok=True,
                    command=f"PUMP_PULSE {seconds * 1000}",
                    sent_at=zulu(datetime.now(timezone.utc)),
                    received_at=zulu(datetime.now(timezone.utc)),
                    lines=[
                        f"ACK command=PUMP_PULSE duration_ms={seconds * 1000} final_state=OFF execution=TEST_ONLY",
                    ],
                    ack_status="OK",
                )

        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(tmp, execute_water=True),
                TestOnlyClient(telemetry=_telemetry(soil_a_raw=30)),
            )
            result = steward.run_once()
            receipt = steward.store.load_json("last_decision_receipt.json")

        self.assertEqual(result["action"], "WATER_A")
        self.assertFalse(result["executed"])
        self.assertEqual(result["blocked_reason"], "ESP32_TEST_ONLY")
        self.assertIsNotNone(receipt)
        DecisionReceipt.model_validate(receipt)
        self.assertEqual(receipt["blocked_reason"], "ESP32_TEST_ONLY")
        self.assertEqual(receipt["action_params"]["esp32_execution_mode"], "TEST_ONLY")

    def test_test_only_ack_can_be_accepted_after_operator_validation(self):
        class TestOnlyClient(FakeESP32Client):
            def water(self, plot: str, seconds: int) -> ESP32CommandResult:
                return ESP32CommandResult(
                    ok=True,
                    command=f"PUMP_PULSE {seconds * 1000}",
                    sent_at=zulu(datetime.now(timezone.utc)),
                    received_at=zulu(datetime.now(timezone.utc)),
                    lines=[
                        f"ACK command=PUMP_PULSE duration_ms={seconds * 1000} final_state=OFF execution=TEST_ONLY",
                    ],
                    ack_status="OK",
                )

        with tempfile.TemporaryDirectory() as tmp:
            steward = RhizomeSteward(
                _config(
                    tmp,
                    execute_water=True,
                    accept_esp32_test_only_pulse_as_executed=True,
                ),
                TestOnlyClient(telemetry=_telemetry(soil_a_raw=30)),
            )
            result = steward.run_once()
            receipt = steward.store.load_json("last_decision_receipt.json")

        self.assertEqual(result["action"], "WATER_A")
        self.assertTrue(result["executed"])
        self.assertIsNone(result["blocked_reason"])
        self.assertIsNotNone(receipt)
        DecisionReceipt.model_validate(receipt)
        self.assertNotIn("esp32_execution_mode", receipt["action_params"])
        self.assertEqual(
            receipt["execution_details"]["esp32_execution_interpretation"],
            "operator_confirmed_physical_pulse",
        )

    def test_pump_pulse_mode_maps_water_seconds_to_pump_pulse_ms(self):
        class DummySerialClient(SerialESP32Client):
            def __init__(self):
                self.water_command_mode = "pump-pulse"
                self.max_wait_s = 3.0
                self.calls = []

            def command(self, command, max_wait_s=None):
                self.calls.append((command, max_wait_s))
                return ESP32CommandResult(
                    ok=True,
                    command=command,
                    sent_at=zulu(datetime.now(timezone.utc)),
                    received_at=zulu(datetime.now(timezone.utc)),
                    lines=[f"ACK command={command}"],
                    ack_status="OK",
                )

        client = DummySerialClient()
        result = client.water("A", 3)

        self.assertTrue(result.ok)
        self.assertEqual(client.calls[0][0], "PUMP_PULSE 3000")
        self.assertGreaterEqual(client.calls[0][1], 5.0)

    def test_serial_command_waits_for_expected_ack_after_heartbeat_noise(self):
        class NoisySerial:
            def __init__(self):
                self.writes = []
                self.lines = [
                    b"HEARTBEAT state=SAFE_IDLE host_link=FRESH\n",
                    b"",
                    b"ACK command=PUMP_PULSE gpio=16 duration_ms=3000 PUMP_REPORT state=OFF\n",
                    b"",
                ]

            def write(self, data):
                self.writes.append(data)
                return len(data)

            def readline(self):
                if self.lines:
                    return self.lines.pop(0)
                return b""

            def reset_input_buffer(self):
                return None

            def reset_output_buffer(self):
                return None

        client = SerialESP32Client.__new__(SerialESP32Client)
        client.serial = NoisySerial()
        client.quiet_s = 0.0
        client.max_wait_s = 0.2
        client.water_command_mode = "pump-pulse"

        result = client.command("PUMP_PULSE 3000", max_wait_s=0.2)

        self.assertTrue(result.ok)
        self.assertEqual(result.ack_status, "OK")
        self.assertIn("ACK command=PUMP_PULSE", "\n".join(result.lines))

    def test_store_enforces_byte_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = BoundedJsonlStore(Path(tmp), retention_days=30, max_total_bytes=900)
            now = datetime.now(timezone.utc) - timedelta(days=10)
            for index in range(50):
                store.append("telemetry_samples", {"index": index, "payload": "x" * 80}, now + timedelta(days=index))

            total = sum(path.stat().st_size for path in Path(tmp).glob("*/*.jsonl"))

        self.assertLessEqual(total, 900)


if __name__ == "__main__":
    unittest.main()
