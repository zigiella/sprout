"""Schema PolicyDelta."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from .base import BaseSchema
from .enums import DeltaPriority, PatchOperation

ALLOWED_POLICY_PATHS = {
    "valid_until",
    "mode_default",
    "rules.watering_window.start_hour_local",
    "rules.watering_window.end_hour_local",
    "rules.soil_moisture_thresholds.parcel_a.min_pct",
    "rules.soil_moisture_thresholds.parcel_a.target_pct",
    "rules.soil_moisture_thresholds.parcel_b.min_pct",
    "rules.soil_moisture_thresholds.parcel_b.target_pct",
    "rules.max_watering_duration_s",
    "rules.daily_water_budget_liters",
    "rules.tank_minimum_pct",
    "rules.require_vision_confirmation",
    "rules.conservative_triggers",
    "rationale",
    "notes",
}


class PolicyPatch(BaseModel):
    op: PatchOperation
    path: str = Field(min_length=1)
    value: Any | None = None

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        if value not in ALLOWED_POLICY_PATHS:
            raise ValueError("patch path no soportado por el schema v1.0")
        return value

    @model_validator(mode="after")
    def validate_value_presence(self) -> "PolicyPatch":
        if self.op == PatchOperation.REMOVE and self.value is not None:
            raise ValueError("remove no admite value")
        if self.op in {PatchOperation.REPLACE, PatchOperation.ADD} and self.value is None:
            raise ValueError("replace/add requieren value")
        return self


class PolicyDelta(BaseSchema):
    delta_id: str = Field(min_length=1)
    target_node_id: str = Field(min_length=1)
    base_policy_id: str = Field(min_length=1)
    patches: list[PolicyPatch] = Field(min_length=1)
    rationale: str | None = None
    ttl_seconds: int = Field(ge=60, le=604800)
    priority: DeltaPriority

    @field_validator("base_policy_id")
    @classmethod
    def validate_base_policy_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("base_policy_id no puede estar vacio")
        return value
