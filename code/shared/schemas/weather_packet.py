"""Schema WeatherPacket."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator, field_validator

from .base import BaseSchema, parse_utc_zulu
from .enums import WeatherProvenance


class WeatherLocation(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    altitude_m: float | None = None
    label: str | None = None


class WeatherMeasurements(BaseModel):
    temperature_c: float | None = None
    humidity_rel_pct: float | None = Field(default=None, ge=0, le=100)
    pressure_hpa: float | None = None
    rain_last_1h_mm: float | None = Field(default=None, ge=0)
    rain_last_24h_mm: float | None = Field(default=None, ge=0)
    wind_speed_kmh: float | None = Field(default=None, ge=0)
    wind_direction_deg: float | None = Field(default=None, ge=0, le=360)
    solar_radiation_wm2: float | None = Field(default=None, ge=0)
    uv_index: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_at_least_one_measurement(self) -> "WeatherMeasurements":
        if not any(value is not None for value in self.model_dump().values()):
            raise ValueError("measurements debe incluir al menos una medida")
        return self


class WeatherPacket(BaseSchema):
    packet_id: str = Field(min_length=1)
    observed_at: datetime
    observed_by_node_id: str = Field(min_length=1)
    provenance: WeatherProvenance
    valid_until: datetime
    location: WeatherLocation
    measurements: WeatherMeasurements
    confidence: float = Field(ge=0, le=1)
    notes: str | None = None

    @field_validator("observed_at", "valid_until", mode="before")
    @classmethod
    def validate_datetimes(cls, value: Any) -> datetime:
        return parse_utc_zulu(value)

    @model_validator(mode="after")
    def validate_packet(self) -> "WeatherPacket":
        if self.observed_at > self.created_at:
            raise ValueError("observed_at no puede estar en el futuro respecto a created_at")
        if self.valid_until <= self.created_at:
            raise ValueError("valid_until debe ser posterior a created_at")
        if self.provenance == WeatherProvenance.LOCAL_STATION and self.observed_by_node_id != self.origin_node_id:
            raise ValueError("local_station exige observed_by_node_id == origin_node_id")
        return self
