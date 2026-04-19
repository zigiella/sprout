"""Simulador de ESP32 para CI y desarrollo sin hardware real.

Sigue `docs/30_safety_rules.md` v1.0 lo bastante de cerca como para:
- validar los 15 tests de safety del sprint
- probar el protocolo UART con CRC-8/DVB-S2
- generar un `DecisionReceipt` bloqueado para demo o writeup

No intenta modelar timings de hardware a nivel de microsegundo ni acceso
real a GPIO/NVS; la meta aqui es fidelidad de contrato, no emulacion fisica.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
import argparse
import json
import sys
from typing import Iterable

SHARED_ROOT = Path(__file__).resolve().parents[3] / "shared"
if str(SHARED_ROOT) not in sys.path:
    sys.path.insert(0, str(SHARED_ROOT))

from schemas import DecisionReceipt  # type: ignore  # noqa: E402
from schemas.enums import ActionType  # type: ignore  # noqa: E402

FIRMWARE_VERSION = "1.0"
CRC8_POLY = 0xD5
MAX_UART_MESSAGE_LEN = 128
BOOT_SILENCE_MS = 2_000
HEARTBEAT_INTERVAL_MS = 5_000
HEARTBEAT_TIMEOUT_MS = 10_000
WATCHDOG_TIMEOUT_MS = 8_000
WATCHDOG_RESET_MS = 2_000
MAX_WATER_DURATION_S = 60
MIN_ZONE_INTERVAL_MS = 30_000
MAX_OPENINGS_PER_HOUR = 8
MAX_OPENINGS_PER_DAY = 48
TANK_MINIMUM_PCT = 20.0
FLOW_CONFIRMATION_DEADLINE_MS = 3_000
MAX_COMMANDS_PER_SECOND = 10
LOG_BUFFER_BYTES = 4 * 1024
VOLTAGE_MIN_V = 10.5
VOLTAGE_MAX_V = 13.5
SIMULATION_EPOCH = datetime(2026, 4, 19, 12, 0, 0, tzinfo=UTC)


class Esp32State(str, Enum):
    BOOT = "BOOT"
    SAFE = "SAFE"
    ACTIVE = "ACTIVE"
    ALERT = "ALERT"
    DEGRADED = "DEGRADED"


class Command(str, Enum):
    WATER_A = "WATER_A"
    WATER_B = "WATER_B"
    STOP = "STOP"
    STATUS = "STATUS"
    RESET_ALERT = "RESET_ALERT"
    DUMP_LOG = "DUMP_LOG"


class RejectReason(str, Enum):
    DEPOSITO_BAJO = "DEPOSITO_BAJO"
    DURATION_OVER_MAX = "DURATION_OVER_MAX"
    DURATION_ZERO = "DURATION_ZERO"
    RATE_LIMIT_HOUR = "RATE_LIMIT_HOUR"
    RATE_LIMIT_DAY = "RATE_LIMIT_DAY"
    MIN_INTERVAL = "MIN_INTERVAL"
    STATE_ALERT = "STATE_ALERT"
    STATE_DEGRADED = "STATE_DEGRADED"
    STATE_BOOT = "STATE_BOOT"
    ZONE_IN_USE = "ZONE_IN_USE"
    FLOW_FAULT = "FLOW_FAULT"
    RESET_NOT_ALLOWED = "RESET_NOT_ALLOWED"


class EventCode(str, Enum):
    HEARTBEAT_LOST = "HEARTBEAT_LOST"
    FLOW_INTERRUPTED = "FLOW_INTERRUPTED"
    STATE_CHANGE = "STATE_CHANGE"
    ALERT_ENTERED = "ALERT_ENTERED"
    ALERT_CLEARED = "ALERT_CLEARED"
    TEMP_HIGH = "TEMP_HIGH"
    VOLTAGE_OUT_RANGE = "VOLTAGE_OUT_RANGE"
    BOOT_LOOP_DETECTED = "BOOT_LOOP_DETECTED"


class Zone(str, Enum):
    A = "A"
    B = "B"


@dataclass(slots=True)
class ParsedFrame:
    message_type: str
    seq: int
    payload: tuple[str, ...]
    crc_hex: str
    raw: str


@dataclass(slots=True)
class ActiveWatering:
    zone: Zone
    seq: int
    started_ms: int
    duration_ms: int
    requested_duration_s: int
    flow_confirmed: bool = False
    flow_lpm: float = 0.0


@dataclass(slots=True)
class RelayOutputs:
    pump: bool = False
    valve_a: bool = False
    valve_b: bool = False


@dataclass(slots=True)
class SensorInputs:
    tank_level_pct: float = 100.0
    temperature_c: float = 24.0
    voltage_v: float = 12.0
    tank_sensor_ok: bool = True
    flow_sensor_ok: bool = True


def crc8_dvb_s2(payload: str | bytes) -> int:
    data = payload.encode("ascii") if isinstance(payload, str) else payload
    crc = 0
    for value in data:
        crc ^= value
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ CRC8_POLY) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


def build_frame(message_type: str, seq: int, *payload_parts: object) -> str:
    body_tokens = [message_type, str(seq), *[str(part) for part in payload_parts]]
    body = " ".join(token for token in body_tokens if token != "")
    frame = f"{body} {crc8_dvb_s2(body):02X}\n"
    if len(frame) > MAX_UART_MESSAGE_LEN:
        raise ValueError("frame supera el maximo de 128 bytes")
    return frame


def parse_frame(raw: str) -> ParsedFrame:
    if len(raw) > MAX_UART_MESSAGE_LEN:
        raise ValueError("frame demasiado largo")
    if not raw.endswith("\n"):
        raise ValueError("frame sin terminador")
    stripped = raw.rstrip("\n")
    try:
        body, crc_hex = stripped.rsplit(" ", 1)
    except ValueError as exc:
        raise ValueError("frame sin CRC") from exc
    computed_crc = f"{crc8_dvb_s2(body):02X}"
    if computed_crc != crc_hex:
        raise ValueError("CRC mismatch")
    tokens = body.split(" ")
    if len(tokens) < 2:
        raise ValueError("frame incompleto")
    try:
        seq = int(tokens[1])
    except ValueError as exc:
        raise ValueError("seq invalido") from exc
    return ParsedFrame(
        message_type=tokens[0],
        seq=seq,
        payload=tuple(tokens[2:]),
        crc_hex=crc_hex,
        raw=raw,
    )


class MockESP32:
    """Simula el comportamiento observable del firmware ESP32 v1.0."""

    def __init__(self) -> None:
        self.state = Esp32State.BOOT
        self.outputs = RelayOutputs()
        self.sensors = SensorInputs()
        self.alert_reason: str | None = None
        self.active: ActiveWatering | None = None
        self.time_ms = 0
        self.boot_started_ms = 0
        self.last_host_message_ms: int | None = None
        self.last_host_seq: int | None = None
        self.next_device_seq = 1
        self.next_heartbeat_ms: int | None = None
        self.zone_start_history: dict[Zone, deque[int]] = {Zone.A: deque(), Zone.B: deque()}
        self.last_zone_start_ms: dict[Zone, int | None] = {Zone.A: None, Zone.B: None}
        self.reboot_times_ms: deque[int] = deque()
        self.command_timestamps_ms: deque[int] = deque()
        self.log_lines: deque[str] = deque()
        self.log_bytes = 0
        self.outbox: list[str] = []
        self._log("REBOOT", "cause=power_on")
        self._log("STATE_CHANGE", "from=BOOT to=BOOT reason=power_on")

    @property
    def uptime_s(self) -> int:
        return self.time_ms // 1000

    def iso_now(self) -> str:
        moment = SIMULATION_EPOCH + timedelta(milliseconds=self.time_ms)
        return moment.strftime("%Y-%m-%dT%H:%M:%SZ")

    def drain_outbox(self) -> list[str]:
        frames = self.outbox[:]
        self.outbox.clear()
        return frames

    def set_tank_level(self, tank_level_pct: float) -> None:
        self.sensors.tank_level_pct = tank_level_pct

    def set_temperature(self, temperature_c: float) -> None:
        self.sensors.temperature_c = temperature_c

    def set_voltage(self, voltage_v: float) -> None:
        self.sensors.voltage_v = voltage_v

    def confirm_flow(self, flow_lpm: float = 3.2) -> None:
        if self.active is not None:
            self.active.flow_confirmed = True
            self.active.flow_lpm = flow_lpm

    def reboot(self, cause: str = "manual_reset") -> None:
        self._close_outputs()
        self.active = None
        self.alert_reason = None
        self.reboot_times_ms.append(self.time_ms)
        while self.reboot_times_ms and self.time_ms - self.reboot_times_ms[0] > 60_000:
            self.reboot_times_ms.popleft()
        self._log("REBOOT", f"cause={cause}")
        self.state = Esp32State.BOOT
        self.boot_started_ms = self.time_ms
        self.next_heartbeat_ms = None
        self._log("STATE_CHANGE", f"from={Esp32State.ACTIVE.value} to={Esp32State.BOOT.value} reason={cause}")

    def advance_time(self, milliseconds: int) -> list[str]:
        if milliseconds < 0:
            raise ValueError("milliseconds debe ser >= 0")

        target_ms = self.time_ms + milliseconds
        while self.time_ms < target_ms:
            next_points = [target_ms]
            if self.state == Esp32State.BOOT:
                next_points.append(self.boot_started_ms + BOOT_SILENCE_MS)
            if self.next_heartbeat_ms is not None:
                next_points.append(self.next_heartbeat_ms)
            if self.active is not None:
                next_points.append(self.active.started_ms + self.active.duration_ms)
                if not self.active.flow_confirmed:
                    next_points.append(self.active.started_ms + FLOW_CONFIRMATION_DEADLINE_MS)
            if self.active is not None and self.last_host_message_ms is not None:
                next_points.append(self.last_host_message_ms + HEARTBEAT_TIMEOUT_MS)

            next_time = min(point for point in next_points if point > self.time_ms)
            self.time_ms = next_time
            self._maybe_finish_boot()
            self._maybe_emit_heartbeat()
            self._maybe_trip_runtime_guards()
            self._maybe_finish_watering()

        return self.drain_outbox()

    def receive_line(self, raw_line: str) -> list[str]:
        if len(raw_line) > MAX_UART_MESSAGE_LEN or not raw_line.endswith("\n"):
            return []

        try:
            frame = parse_frame(raw_line)
        except ValueError:
            self._log("CMD_RX", "crc_ok=false")
            return []

        self._log("CMD_RX", f"seq={frame.seq} crc_ok=true raw={raw_line.rstrip()}")
        self._record_host_activity(frame.seq)

        if frame.message_type != "CMD":
            self._enqueue_ack(frame.seq, "MALFORMED")
            return self.drain_outbox()

        if self._is_replay(frame.seq):
            self._log("CMD_REPLAY", f"seq={frame.seq}")
            return []

        self.last_host_seq = frame.seq
        self.last_host_message_ms = self.time_ms

        if self._rate_limit_host_commands():
            self._log("CMD_DROP", f"seq={frame.seq} reason=rate_limit_cps")
            return []

        if self.state == Esp32State.BOOT:
            self._reject(frame.seq, RejectReason.STATE_BOOT)
            return self.drain_outbox()

        if not frame.payload:
            self._enqueue_ack(frame.seq, "MALFORMED")
            return self.drain_outbox()

        command_name = frame.payload[0]
        parameters = frame.payload[1:]

        try:
            command = Command(command_name)
        except ValueError:
            self._enqueue_ack(frame.seq, "MALFORMED")
            return self.drain_outbox()

        if self.state == Esp32State.ALERT and command not in {Command.STATUS, Command.STOP, Command.RESET_ALERT, Command.DUMP_LOG}:
            self._reject(frame.seq, RejectReason.STATE_ALERT)
            return self.drain_outbox()

        if self.state == Esp32State.DEGRADED and command not in {Command.STATUS, Command.DUMP_LOG}:
            self._reject(frame.seq, RejectReason.STATE_DEGRADED)
            return self.drain_outbox()

        if command in {Command.WATER_A, Command.WATER_B}:
            self._handle_water_command(frame.seq, command, parameters)
        elif command == Command.STOP:
            self._handle_stop(frame.seq)
        elif command == Command.STATUS:
            self._handle_status(frame.seq)
        elif command == Command.RESET_ALERT:
            self._handle_reset_alert(frame.seq)
        elif command == Command.DUMP_LOG:
            self._handle_dump_log(frame.seq)

        return self.drain_outbox()

    def build_blocked_receipt(
        self,
        *,
        decision_id: str,
        snapshot_id: str,
        active_policy_id: str,
        attempted_action: ActionType,
        attempted_duration_s: int,
        expected_liters: float,
        rejected_reason: RejectReason,
        contradictions: Iterable[str] | None = None,
        confidence: float = 0.99,
    ) -> DecisionReceipt:
        human_reason = {
            RejectReason.DEPOSITO_BAJO: "Deposito por debajo del minimo duro del firmware.",
            RejectReason.MIN_INTERVAL: "El firmware impone 30 s entre aperturas de la misma zona.",
            RejectReason.RATE_LIMIT_HOUR: "El firmware alcanzo el maximo de aperturas por hora.",
            RejectReason.RATE_LIMIT_DAY: "El firmware alcanzo el maximo de aperturas por dia.",
            RejectReason.STATE_ALERT: "El firmware esta en ALERT y no acepta nuevas aperturas.",
            RejectReason.STATE_DEGRADED: "El firmware esta en DEGRADED y no puede verificar sensores criticos.",
            RejectReason.STATE_BOOT: "El firmware aun esta dentro de la ventana de boot segura.",
            RejectReason.ZONE_IN_USE: "Ya hay otra zona activa; la concurrencia esta prohibida.",
            RejectReason.DURATION_OVER_MAX: "La duracion excede el limite duro de 60 s.",
            RejectReason.DURATION_ZERO: "La duracion debe ser positiva.",
            RejectReason.FLOW_FAULT: "No se puede garantizar caudal valido.",
            RejectReason.RESET_NOT_ALLOWED: "La condicion que disparo ALERT sigue presente.",
        }[rejected_reason]
        attempted_params = {"duration_s": attempted_duration_s, "expected_liters": expected_liters}
        return DecisionReceipt(
            created_at=self.iso_now(),
            origin_node_id="rhizome_01",
            decision_id=decision_id,
            snapshot_id=snapshot_id,
            active_policy_id=active_policy_id,
            action=ActionType.BLOCK,
            action_params={
                "blocked_action": attempted_action.value,
                "reason": rejected_reason.value,
                "attempted_params": attempted_params,
            },
            rationale_short=f"Firmware bloqueo {attempted_action.value}: {rejected_reason.value}.",
            rationale_full=(
                f"Rhizome intento ejecutar {attempted_action.value} con {attempted_params}, "
                f"pero el ESP32 respondio REJECTED {rejected_reason.value}. {human_reason}"
            ),
            policy_refs=["rules.tank_minimum_pct", "rules.max_watering_duration_s"],
            contradictions=list(contradictions or []),
            confidence=confidence,
            executed=False,
            execution_details=None,
            blocked_reason=rejected_reason.value.lower(),
        )

    def demo_low_tank_block(self) -> dict[str, object]:
        self.advance_time(BOOT_SILENCE_MS)
        self.set_tank_level(11.0)
        command = build_frame("CMD", 42, Command.WATER_A.value, 10)
        responses = self.receive_line(command)
        receipt = self.build_blocked_receipt(
            decision_id="rec_demo_low_tank_block",
            snapshot_id="snap_demo_low_tank_block",
            active_policy_id="pkt_demo_policy",
            attempted_action=ActionType.WATER_A,
            attempted_duration_s=10,
            expected_liters=0.6,
            rejected_reason=RejectReason.DEPOSITO_BAJO,
        )
        return {
            "command": command.rstrip(),
            "responses": [response.rstrip() for response in responses],
            "receipt": receipt.model_dump(mode="json"),
        }

    def _record_host_activity(self, seq: int) -> None:
        _ = seq

    def _rate_limit_host_commands(self) -> bool:
        self.command_timestamps_ms.append(self.time_ms)
        while self.command_timestamps_ms and self.time_ms - self.command_timestamps_ms[0] >= 1_000:
            self.command_timestamps_ms.popleft()
        return len(self.command_timestamps_ms) > MAX_COMMANDS_PER_SECOND

    def _is_replay(self, seq: int) -> bool:
        if self.last_host_seq is None:
            return False
        diff = (seq - self.last_host_seq) & 0xFFFF
        return diff == 0 or diff > 32_768

    def _maybe_finish_boot(self) -> None:
        if self.state != Esp32State.BOOT:
            return
        if self.time_ms - self.boot_started_ms < BOOT_SILENCE_MS:
            return

        sensor_failure = (
            not self.sensors.tank_sensor_ok
            or not self.sensors.flow_sensor_ok
            or self.sensors.voltage_v < VOLTAGE_MIN_V
            or self.sensors.voltage_v > VOLTAGE_MAX_V
        )
        if len(self.reboot_times_ms) > 3:
            self.state = Esp32State.DEGRADED
            self._enqueue_event(EventCode.BOOT_LOOP_DETECTED)
        elif sensor_failure:
            self.state = Esp32State.DEGRADED
        else:
            self.state = Esp32State.SAFE
        self.next_heartbeat_ms = self.time_ms
        self._log("STATE_CHANGE", f"from=BOOT to={self.state.value} reason=boot_complete")
        self._maybe_emit_heartbeat(force=True)

    def _maybe_emit_heartbeat(self, force: bool = False) -> None:
        if self.next_heartbeat_ms is None:
            return
        if not force and self.time_ms < self.next_heartbeat_ms:
            return
        while self.next_heartbeat_ms is not None and self.time_ms >= self.next_heartbeat_ms:
            self._enqueue_heartbeat()
            self.next_heartbeat_ms += HEARTBEAT_INTERVAL_MS
            if force:
                break

    def _maybe_trip_runtime_guards(self) -> None:
        if self.sensors.temperature_c > 80.0:
            self._enter_alert("TEMP_HIGH")
            self._enqueue_event(EventCode.TEMP_HIGH, f"celsius={self.sensors.temperature_c:.1f}")
            return

        if self.sensors.voltage_v < VOLTAGE_MIN_V or self.sensors.voltage_v > VOLTAGE_MAX_V:
            if self.state != Esp32State.ACTIVE:
                self._transition(Esp32State.DEGRADED, "voltage_out_of_range")
                self._enqueue_event(EventCode.VOLTAGE_OUT_RANGE, f"volts={self.sensors.voltage_v:.2f}")
                return

        if self.active is None:
            return

        if self.last_host_message_ms is not None and self.time_ms - self.last_host_message_ms >= HEARTBEAT_TIMEOUT_MS:
            self._enter_alert(EventCode.HEARTBEAT_LOST.value)
            self._enqueue_event(EventCode.HEARTBEAT_LOST)
            return

        if self.sensors.tank_level_pct < TANK_MINIMUM_PCT:
            self._enter_alert(RejectReason.DEPOSITO_BAJO.value)
            return

        if not self.active.flow_confirmed and self.time_ms - self.active.started_ms >= FLOW_CONFIRMATION_DEADLINE_MS:
            offending_seq = self.active.seq
            self._enter_alert(RejectReason.FLOW_FAULT.value)
            self._enqueue_event(EventCode.FLOW_INTERRUPTED, f"cmd={offending_seq}")

    def _maybe_finish_watering(self) -> None:
        if self.active is None:
            return
        if self.state != Esp32State.ACTIVE:
            return
        if self.time_ms < self.active.started_ms + self.active.duration_ms:
            return
        self._close_outputs()
        self.active = None
        self._transition(Esp32State.SAFE, "watering_complete")

    def _handle_water_command(self, seq: int, command: Command, parameters: tuple[str, ...]) -> None:
        if len(parameters) != 1:
            self._enqueue_ack(seq, "MALFORMED")
            return

        try:
            duration_s = int(parameters[0])
        except ValueError:
            self._enqueue_ack(seq, "MALFORMED")
            return

        if duration_s <= 0:
            self._reject(seq, RejectReason.DURATION_ZERO)
            return
        if duration_s > MAX_WATER_DURATION_S:
            self._reject(seq, RejectReason.DURATION_OVER_MAX)
            return
        if self.sensors.tank_level_pct < TANK_MINIMUM_PCT:
            self._reject(seq, RejectReason.DEPOSITO_BAJO)
            return

        zone = Zone.A if command == Command.WATER_A else Zone.B
        if self.active is not None:
            self._reject(seq, RejectReason.ZONE_IN_USE)
            return

        if self._opening_count(zone, 3_600_000) >= MAX_OPENINGS_PER_HOUR:
            self._reject(seq, RejectReason.RATE_LIMIT_HOUR)
            return
        if self._opening_count(zone, 86_400_000) >= MAX_OPENINGS_PER_DAY:
            self._reject(seq, RejectReason.RATE_LIMIT_DAY)
            return

        last_start_ms = self.last_zone_start_ms[zone]
        if last_start_ms is not None and self.time_ms - last_start_ms < MIN_ZONE_INTERVAL_MS:
            self._reject(seq, RejectReason.MIN_INTERVAL)
            return

        self.active = ActiveWatering(
            zone=zone,
            seq=seq,
            started_ms=self.time_ms,
            duration_ms=duration_s * 1_000,
            requested_duration_s=duration_s,
        )
        self.zone_start_history[zone].append(self.time_ms)
        self.last_zone_start_ms[zone] = self.time_ms
        self.outputs.pump = True
        self.outputs.valve_a = zone == Zone.A
        self.outputs.valve_b = zone == Zone.B
        self._transition(Esp32State.ACTIVE, f"{command.value.lower()}_accepted")
        self._enqueue_ack(seq, "OK", f"zone={zone.value}", f"duration_s={duration_s}")

    def _handle_stop(self, seq: int) -> None:
        self._close_outputs()
        self.active = None
        if self.state == Esp32State.ACTIVE:
            self._transition(Esp32State.SAFE, "stop")
        self._enqueue_ack(seq, "OK", f"state={self.state.value}")

    def _handle_status(self, seq: int) -> None:
        self._enqueue_ack(
            seq,
            "OK",
            f"state={self.state.value}",
            f"tank_pct={self.sensors.tank_level_pct:.1f}",
            f"temp_c={self.sensors.temperature_c:.1f}",
            f"uptime_s={self.uptime_s}",
        )

    def _handle_reset_alert(self, seq: int) -> None:
        if self.state != Esp32State.ALERT:
            self._reject(seq, RejectReason.RESET_NOT_ALLOWED)
            return
        if self._alert_condition_active():
            self._reject(seq, RejectReason.RESET_NOT_ALLOWED)
            return
        self.alert_reason = None
        self._transition(Esp32State.SAFE, "reset_alert")
        self._enqueue_event(EventCode.ALERT_CLEARED)
        self._enqueue_ack(seq, "OK", "state=SAFE")

    def _handle_dump_log(self, seq: int) -> None:
        self._enqueue_ack(seq, "OK", f"entries={len(self.log_lines)}")

    def _alert_condition_active(self) -> bool:
        if self.alert_reason == RejectReason.DEPOSITO_BAJO.value:
            return self.sensors.tank_level_pct < TANK_MINIMUM_PCT
        if self.alert_reason == EventCode.HEARTBEAT_LOST.value:
            return self.last_host_message_ms is None or self.time_ms - self.last_host_message_ms >= HEARTBEAT_TIMEOUT_MS
        if self.alert_reason == RejectReason.FLOW_FAULT.value:
            return self.active is not None and not self.active.flow_confirmed
        if self.alert_reason == "TEMP_HIGH":
            return self.sensors.temperature_c > 80.0
        return False

    def _opening_count(self, zone: Zone, window_ms: int) -> int:
        history = self.zone_start_history[zone]
        while history and self.time_ms - history[0] > window_ms:
            history.popleft()
        return len(history)

    def _enter_alert(self, reason: str) -> None:
        if self.state == Esp32State.ALERT:
            return
        self._close_outputs()
        self.active = None
        self.alert_reason = reason
        self._transition(Esp32State.ALERT, reason)
        self._enqueue_event(EventCode.ALERT_ENTERED, f"reason={reason}")

    def _transition(self, new_state: Esp32State, reason: str) -> None:
        if self.state == new_state:
            return
        previous = self.state
        self.state = new_state
        self._log("STATE_CHANGE", f"from={previous.value} to={new_state.value} reason={reason}")
        self._enqueue_event(EventCode.STATE_CHANGE, f"from={previous.value}", f"to={new_state.value}")

    def _close_outputs(self) -> None:
        self.outputs = RelayOutputs()

    def _reject(self, seq: int, reason: RejectReason) -> None:
        self._log("CMD_REJECTED", f"seq={seq} reason={reason.value}")
        self._enqueue_ack(seq, "REJECTED", reason.value)

    def _enqueue_ack(self, seq: int, status: str, *payload_parts: object) -> None:
        self.outbox.append(build_frame("ACK", seq, status, *payload_parts))

    def _enqueue_event(self, event: EventCode, *payload_parts: object) -> None:
        seq = self._next_device_sequence()
        self.outbox.append(build_frame("EVT", seq, event.value, *payload_parts))

    def _enqueue_heartbeat(self) -> None:
        seq = self._next_device_sequence()
        self.outbox.append(build_frame("HBT", seq, f"uptime={self.uptime_s}", f"state={self.state.value}"))

    def _next_device_sequence(self) -> int:
        seq = self.next_device_seq
        self.next_device_seq = (self.next_device_seq + 1) & 0xFFFF
        return seq

    def _log(self, entry_type: str, payload: str) -> None:
        line = f"{self.time_ms},{entry_type},{self.state.value},{payload}"
        encoded_size = len(line.encode("utf-8")) + 1
        while self.log_lines and self.log_bytes + encoded_size > LOG_BUFFER_BYTES:
            dropped = self.log_lines.popleft()
            self.log_bytes -= len(dropped.encode("utf-8")) + 1
        self.log_lines.append(line)
        self.log_bytes += encoded_size


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Demo del mock ESP32 de safety rules.")
    parser.add_argument(
        "--scenario",
        choices=["low_tank_block"],
        default="low_tank_block",
        help="Escenario de demo a ejecutar.",
    )
    args = parser.parse_args(argv)

    firmware = MockESP32()
    if args.scenario == "low_tank_block":
        result = firmware.demo_low_tank_block()
    else:
        raise ValueError(f"escenario no soportado: {args.scenario}")

    print("=== COMMAND ===")
    print(result["command"])
    print("=== RESPONSES ===")
    for response in result["responses"]:
        print(response)
    print("=== DECISION RECEIPT ===")
    print(json.dumps(result["receipt"], indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
