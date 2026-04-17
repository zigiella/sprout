"""Schema ContradictionAlert."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator, model_validator

from .base import BaseSchema, parse_utc_zulu
from .enums import ContradictionType, Severity

CRITICAL_ACTIONS = {"block_watering", "request_policy_review"}
EVIDENCE_REQUIRED_KEYS = {
    ContradictionType.SENSOR_VS_VISION: {"sensor_reading", "vision_reading"},
    ContradictionType.POLICY_EXPIRED: {"policy_id", "expired_at"},
    ContradictionType.DEPOSIT_INCONSISTENT: {"tank_level_pct", "flow_history_summary"},
    ContradictionType.FLOW_VS_PUMP: {"pump_active_from", "flow_rate_observed"},
    ContradictionType.WEATHER_CONFLICT: {"active_policy_id", "conflicting_weather_packet_id"},
    ContradictionType.TANK_UNDERFLOW: {"tank_level_pct", "minimum_threshold_pct"},
}


class ContradictionAlert(BaseSchema):
    alert_id: str = Field(min_length=1)
    target_node_id: str = Field(min_length=1)
    contradiction_type: ContradictionType
    severity: Severity
    observed_at: datetime
    evidence: dict[str, Any]
    recommended_action: str | None = None
    expires_at: datetime
    rationale: str | None = None

    @field_validator("observed_at", "expires_at", mode="before")
    @classmethod
    def validate_datetimes(cls, value: Any) -> datetime:
        return parse_utc_zulu(value)

    @model_validator(mode="after")
    def validate_alert(self) -> "ContradictionAlert":
        required_keys = EVIDENCE_REQUIRED_KEYS[self.contradiction_type]
        missing = required_keys - self.evidence.keys()
        if missing:
            raise ValueError(f"evidence incompleta para {self.contradiction_type.value}: faltan {sorted(missing)}")
        if self.expires_at <= self.created_at:
            raise ValueError("expires_at debe ser posterior a created_at")
        if self.severity == Severity.CRITICAL and self.recommended_action not in CRITICAL_ACTIONS:
            raise ValueError("severity critical exige recommended_action de bloqueo o revision")
        return self
