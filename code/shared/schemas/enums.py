"""Enums compartidos entre nodos."""

from __future__ import annotations

from enum import Enum


class Mode(str, Enum):
    NORMAL = "normal"
    CONSERVATIVE = "conservative"
    ALERT = "alert"


class ActionType(str, Enum):
    WATER_A = "WATER_A"
    WATER_B = "WATER_B"
    WATER_BOTH = "WATER_BOTH"
    SKIP = "SKIP"
    DEFER = "DEFER"
    ALERT = "ALERT"
    BLOCK = "BLOCK"
    SHUTDOWN = "SHUTDOWN"


class ContradictionType(str, Enum):
    SENSOR_VS_VISION = "sensor_vs_vision"
    POLICY_EXPIRED = "policy_expired"
    DEPOSIT_INCONSISTENT = "deposit_inconsistent"
    FLOW_VS_PUMP = "flow_vs_pump"
    WEATHER_CONFLICT = "weather_conflict"
    TANK_UNDERFLOW = "tank_underflow"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class WeatherProvenance(str, Enum):
    LOCAL_STATION = "local_station"
    FERRIED = "ferried"
    FORECAST_API = "forecast_api"


class PatchOperation(str, Enum):
    REPLACE = "replace"
    ADD = "add"
    REMOVE = "remove"


class DeltaPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
