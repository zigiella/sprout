"""Schema RhizomeSnapshot."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .base import BaseSchema, parse_utc_zulu
from .enums import Mode


class SnapshotSensors(BaseModel):
    soil_moisture_a_pct: float = Field(ge=0, le=100)
    soil_moisture_b_pct: float = Field(ge=0, le=100)
    tank_level_pct: float = Field(ge=0, le=100)
    flow_rate_lpm: float = Field(ge=0)
    last_reading_at: datetime

    @field_validator("last_reading_at", mode="before")
    @classmethod
    def validate_last_reading_at(cls, value: Any) -> datetime:
        return parse_utc_zulu(value)


class SnapshotVision(BaseModel):
    last_capture_at: datetime | None = None
    parcel_a_status: str | None = None
    parcel_b_status: str | None = None
    visual_notes: str | None = Field(default=None, max_length=500)

    @field_validator("last_capture_at", mode="before")
    @classmethod
    def validate_last_capture_at(cls, value: Any) -> datetime | None:
        if value is None:
            return None
        return parse_utc_zulu(value)


class SnapshotHealth(BaseModel):
    cpu_temp_c: float
    cpu_load_pct: float = Field(ge=0, le=100)
    ram_used_gb: float = Field(ge=0)
    ram_total_gb: float = Field(gt=0)
    esp32_heartbeat_ok: bool
    last_esp32_ack_at: datetime | None = None

    @field_validator("cpu_temp_c")
    @classmethod
    def validate_cpu_temp_c(cls, value: float) -> float:
        if not -20 <= value <= 120:
            raise ValueError("cpu_temp_c fuera de rango razonable")
        return value

    @field_validator("last_esp32_ack_at", mode="before")
    @classmethod
    def validate_last_esp32_ack_at(cls, value: Any) -> datetime | None:
        if value is None:
            return None
        return parse_utc_zulu(value)


class RhizomeSnapshot(BaseSchema):
    snapshot_id: str = Field(min_length=1)
    mode: Mode
    active_policy_id: str = Field(min_length=1)
    active_policy_expires_at: datetime
    sensors: SnapshotSensors
    vision: SnapshotVision
    health: SnapshotHealth
    last_decision_id: str | None = None
    pending_contradictions: list[str] = Field(default_factory=list)

    @field_validator("active_policy_expires_at", mode="before")
    @classmethod
    def validate_active_policy_expires_at(cls, value: Any) -> datetime:
        return parse_utc_zulu(value)
