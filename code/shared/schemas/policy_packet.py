"""Schema PolicyPacket."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator, field_validator

from .base import BaseSchema, parse_utc_zulu
from .enums import Mode


class WateringWindow(BaseModel):
    start_hour_local: int = Field(ge=0, le=23)
    end_hour_local: int = Field(ge=0, le=23)

    @model_validator(mode="after")
    def validate_window(self) -> "WateringWindow":
        if self.end_hour_local <= self.start_hour_local:
            raise ValueError("la ventana de riego no puede cruzar medianoche en v1.0")
        return self


class MoistureThreshold(BaseModel):
    min_pct: float = Field(ge=0, le=100)
    target_pct: float = Field(ge=0, le=100)

    @model_validator(mode="after")
    def validate_thresholds(self) -> "MoistureThreshold":
        if self.target_pct < self.min_pct:
            raise ValueError("target_pct no puede ser menor que min_pct")
        return self


class SoilMoistureThresholds(BaseModel):
    parcel_a: MoistureThreshold
    parcel_b: MoistureThreshold


class PolicyRules(BaseModel):
    watering_window: WateringWindow
    soil_moisture_thresholds: SoilMoistureThresholds
    max_watering_duration_s: int = Field(gt=0, le=120)
    daily_water_budget_liters: float = Field(gt=0)
    tank_minimum_pct: float = Field(ge=0, le=100)
    require_vision_confirmation: bool
    conservative_triggers: list[str] = Field(default_factory=list)

    @field_validator("tank_minimum_pct")
    @classmethod
    def validate_tank_minimum_pct(cls, value: float) -> float:
        if value < 10.0:
            raise ValueError("tank_minimum_pct no puede bajar del 10%")
        return value


class PolicyPacket(BaseSchema):
    policy_id: str = Field(min_length=1)
    target_node_id: str = Field(min_length=1)
    valid_until: datetime
    version_chain: list[str] = Field(min_length=1)
    mode_default: Mode
    rules: PolicyRules
    rationale: str | None = None
    notes: str | None = None

    @field_validator("valid_until", mode="before")
    @classmethod
    def validate_valid_until(cls, value: Any) -> datetime:
        return parse_utc_zulu(value)

    @model_validator(mode="after")
    def validate_policy(self) -> "PolicyPacket":
        if self.valid_until <= self.created_at:
            raise ValueError("valid_until debe ser posterior a created_at")
        return self
