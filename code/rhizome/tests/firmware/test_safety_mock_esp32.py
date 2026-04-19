"""Tests del simulador de firmware ESP32 segun docs/30_safety_rules.md."""

from __future__ import annotations

from .mock_esp32 import (
    BOOT_SILENCE_MS,
    HEARTBEAT_TIMEOUT_MS,
    MIN_ZONE_INTERVAL_MS,
    ActionType,
    Command,
    Esp32State,
    MockESP32,
    RejectReason,
    build_frame,
    parse_frame,
)


def _boot_ready(controller: MockESP32) -> None:
    controller.advance_time(BOOT_SILENCE_MS)
    controller.drain_outbox()


def _ack_payload(responses: list[str]) -> tuple[str, ...]:
    for response in responses:
        frame = parse_frame(response)
        if frame.message_type == "ACK":
            return frame.payload
    raise AssertionError("no se encontro ningun ACK en la respuesta")


def _water_ok(controller: MockESP32, seq: int, zone: Command, duration_s: int = 1) -> None:
    responses = controller.receive_line(build_frame("CMD", seq, zone.value, duration_s))
    assert _ack_payload(responses)[0] == "OK"
    controller.confirm_flow()
    controller.advance_time(duration_s * 1_000)
    controller.drain_outbox()


def test_duration_over_max() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    responses = controller.receive_line(build_frame("CMD", 1, Command.WATER_A.value, 61))
    assert parse_frame(responses[0]).payload == ("REJECTED", RejectReason.DURATION_OVER_MAX.value)


def test_duration_zero() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    responses = controller.receive_line(build_frame("CMD", 2, Command.WATER_A.value, 0))
    assert parse_frame(responses[0]).payload == ("REJECTED", RejectReason.DURATION_ZERO.value)


def test_deposit_low() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    controller.set_tank_level(19.0)
    responses = controller.receive_line(build_frame("CMD", 3, Command.WATER_A.value, 10))
    assert parse_frame(responses[0]).payload == ("REJECTED", RejectReason.DEPOSITO_BAJO.value)


def test_rate_limit_hour() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    for seq in range(10, 18):
        _water_ok(controller, seq, Command.WATER_A)
        controller.advance_time(MIN_ZONE_INTERVAL_MS)
        controller.drain_outbox()
    responses = controller.receive_line(build_frame("CMD", 18, Command.WATER_A.value, 1))
    assert parse_frame(responses[0]).payload == ("REJECTED", RejectReason.RATE_LIMIT_HOUR.value)


def test_min_interval() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    _water_ok(controller, 20, Command.WATER_A)
    controller.advance_time(MIN_ZONE_INTERVAL_MS - 10_000)
    controller.drain_outbox()
    responses = controller.receive_line(build_frame("CMD", 21, Command.WATER_A.value, 1))
    assert parse_frame(responses[0]).payload == ("REJECTED", RejectReason.MIN_INTERVAL.value)


def test_zone_concurrent() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    responses = controller.receive_line(build_frame("CMD", 30, Command.WATER_A.value, 10))
    assert _ack_payload(responses)[0] == "OK"
    responses = controller.receive_line(build_frame("CMD", 31, Command.WATER_B.value, 10))
    assert _ack_payload(responses) == ("REJECTED", RejectReason.ZONE_IN_USE.value)


def test_heartbeat_loss() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    controller.receive_line(build_frame("CMD", 40, Command.WATER_A.value, 20))
    controller.confirm_flow()
    responses = controller.advance_time(HEARTBEAT_TIMEOUT_MS + 5_000)
    event_types = [parse_frame(frame).payload[0] for frame in responses if frame.startswith("EVT")]
    assert "HEARTBEAT_LOST" in event_types
    assert controller.state == Esp32State.ALERT
    assert controller.outputs.pump is False
    assert controller.outputs.valve_a is False


def test_flow_fault() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    controller.receive_line(build_frame("CMD", 50, Command.WATER_A.value, 10))
    responses = controller.advance_time(3_500)
    event_types = [parse_frame(frame).payload[0] for frame in responses if frame.startswith("EVT")]
    assert "FLOW_INTERRUPTED" in event_types
    assert controller.state == Esp32State.ALERT


def test_crc_mismatch() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    good = build_frame("CMD", 60, Command.WATER_A.value, 10)
    corrupted = good[:-3] + "00\n"
    assert controller.receive_line(corrupted) == []


def test_malformed() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    responses = controller.receive_line(build_frame("CMD", 70, "WATER_X", 10))
    assert parse_frame(responses[0]).payload == ("MALFORMED",)


def test_replay() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    command = build_frame("CMD", 80, Command.STATUS.value)
    first = controller.receive_line(command)
    second = controller.receive_line(command)
    assert parse_frame(first[0]).payload[0] == "OK"
    assert second == []


def test_boot_guard() -> None:
    controller = MockESP32()
    responses = controller.receive_line(build_frame("CMD", 90, Command.WATER_A.value, 10))
    assert parse_frame(responses[0]).payload == ("REJECTED", RejectReason.STATE_BOOT.value)


def test_alert_stuck() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    controller.set_tank_level(25.0)
    controller.receive_line(build_frame("CMD", 100, Command.WATER_A.value, 10))
    controller.confirm_flow()
    controller.set_tank_level(15.0)
    controller.advance_time(1_000)
    controller.drain_outbox()
    responses = controller.receive_line(build_frame("CMD", 101, Command.RESET_ALERT.value))
    assert parse_frame(responses[0]).payload == ("REJECTED", RejectReason.RESET_NOT_ALLOWED.value)


def test_alert_recovery() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    controller.set_tank_level(25.0)
    controller.receive_line(build_frame("CMD", 110, Command.WATER_A.value, 10))
    controller.confirm_flow()
    controller.set_tank_level(15.0)
    controller.advance_time(1_000)
    controller.drain_outbox()
    controller.set_tank_level(40.0)
    responses = controller.receive_line(build_frame("CMD", 111, Command.RESET_ALERT.value))
    assert parse_frame(responses[-1]).payload == ("OK", "state=SAFE")
    assert controller.state == Esp32State.SAFE


def test_reboot_safe() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    controller.receive_line(build_frame("CMD", 120, Command.WATER_A.value, 10))
    controller.confirm_flow()
    controller.reboot()
    assert controller.outputs.pump is False
    assert controller.outputs.valve_a is False
    controller.advance_time(BOOT_SILENCE_MS)
    controller.drain_outbox()
    assert controller.state == Esp32State.SAFE


def test_blocked_receipt_for_low_tank() -> None:
    controller = MockESP32()
    _boot_ready(controller)
    receipt = controller.build_blocked_receipt(
        decision_id="rec_low_tank",
        snapshot_id="snap_low_tank",
        active_policy_id="pkt_policy",
        attempted_action=ActionType.WATER_A,
        attempted_duration_s=10,
        expected_liters=0.6,
        rejected_reason=RejectReason.DEPOSITO_BAJO,
    )
    assert receipt.action == ActionType.BLOCK
    assert receipt.executed is False
    assert receipt.blocked_reason == "deposito_bajo"
    assert receipt.action_params["blocked_action"] == "WATER_A"
    assert receipt.action_params["reason"] == RejectReason.DEPOSITO_BAJO.value


def test_demo_low_tank_block_returns_transcript_and_receipt() -> None:
    controller = MockESP32()
    result = controller.demo_low_tank_block()
    assert "CMD 42 WATER_A 10" in result["command"]
    assert any("REJECTED DEPOSITO_BAJO" in response for response in result["responses"])
    assert result["receipt"]["blocked_reason"] == "deposito_bajo"
