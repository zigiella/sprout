"""Schema DecisionReceipt."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from .base import BaseSchema, parse_utc_zulu
from .enums import ActionType

WATER_ACTIONS = {ActionType.WATER_A, ActionType.WATER_B, ActionType.WATER_BOTH}


class ExecutionDetails(BaseModel):
    sent_to_esp32_at: datetime
    esp32_ack_at: datetime
    esp32_ack_status: str = Field(min_length=1)
    actual_duration_s: float = Field(ge=0)
    flow_observed_lpm: float = Field(ge=0)
    estimated_liters_actual: float = Field(ge=0)

    @field_validator("sent_to_esp32_at", "esp32_ack_at", mode="before")
    @classmethod
    def validate_datetimes(cls, value: Any) -> datetime:
        return parse_utc_zulu(value)

    @model_validator(mode="after")
    def validate_order(self) -> "ExecutionDetails":
        if self.esp32_ack_at < self.sent_to_esp32_at:
            raise ValueError("esp32_ack_at no puede ser anterior a sent_to_esp32_at")
        return self


class DecisionReceipt(BaseSchema):
    decision_id: str = Field(min_length=1)
    snapshot_id: str = Field(min_length=1)
    active_policy_id: str = Field(min_length=1)
    action: ActionType
    action_params: dict[str, Any]
    rationale_short: str
    rationale_full: str
    policy_refs: list[str] = Field(min_length=1)
    contradictions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    executed: bool
    execution_details: ExecutionDetails | None = None
    blocked_reason: str | None = None

    @field_validator("rationale_short")
    @classmethod
    def validate_rationale_short(cls, value: str) -> str:
        if len(value) > 180:
            raise ValueError("rationale_short no puede superar 180 caracteres")
        return value

    @field_validator("rationale_full")
    @classmethod
    def validate_rationale_full(cls, value: str) -> str:
        if len(value) > 2000:
            raise ValueError("rationale_full no puede superar 2000 caracteres")
        return value

    @model_validator(mode="after")
    def validate_execution_contract(self) -> "DecisionReceipt":
        if self.executed:
            if self.execution_details is None:
                raise ValueError("executed=true exige execution_details")
            if self.blocked_reason is not None:
                raise ValueError("executed=true exige blocked_reason=null")
        else:
            if not self.blocked_reason:
                raise ValueError("executed=false exige blocked_reason no vacio")
            if self.execution_details is not None:
                raise ValueError("executed=false exige execution_details=null")

        required_action_params = {
            ActionType.WATER_A: {"duration_s", "expected_liters"},
            ActionType.WATER_B: {"duration_s", "expected_liters"},
            ActionType.WATER_BOTH: {"duration_s", "expected_liters"},
            ActionType.SKIP: {"next_check_in_s"},
            ActionType.DEFER: {"defer_until", "reason"},
            ActionType.ALERT: {"alert_id"},
            ActionType.BLOCK: {"blocked_action", "reason"},
            ActionType.SHUTDOWN: {"reason", "recoverable"},
        }[self.action]
        missing = required_action_params - self.action_params.keys()
        if missing:
            raise ValueError(f"action_params incompleto para {self.action.value}: faltan {sorted(missing)}")

        if self.action in WATER_ACTIONS and self.executed:
            duration = self.action_params.get("duration_s")
            if not isinstance(duration, int) or duration <= 0:
                raise ValueError("las acciones WATER_* requieren duration_s entero positivo")

        return self
