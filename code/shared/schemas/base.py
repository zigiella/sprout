"""Tipos y validaciones comunes para los contratos de datos."""

from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

UTC_ZULU_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SIGNATURE_RE = re.compile(r"^[0-9a-f]{64}$")


def parse_utc_zulu(value: Any) -> datetime:
    """Parsea un timestamp ISO-8601 UTC con sufijo Z."""

    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
            raise ValueError("el timestamp debe ser UTC explicito")
        return value.astimezone(timezone.utc)

    if not isinstance(value, str) or not UTC_ZULU_RE.fullmatch(value):
        raise ValueError("el timestamp debe seguir el formato ISO-8601 UTC con sufijo Z")

    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


class BaseSchema(BaseModel):
    """Base comun para todos los mensajes que viajan entre nodos."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    schema_version: str = Field(default="1.0")
    created_at: datetime
    origin_node_id: str = Field(min_length=1)
    signature: str | None = None

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, value: str) -> str:
        if value != "1.0":
            raise ValueError("schema_version debe ser '1.0'")
        return value

    @field_validator("created_at", mode="before")
    @classmethod
    def validate_created_at(cls, value: Any) -> datetime:
        return parse_utc_zulu(value)

    @field_validator("origin_node_id")
    @classmethod
    def validate_origin_node_id(cls, value: str) -> str:
        if not value:
            raise ValueError("origin_node_id no puede estar vacio")
        return value

    @field_validator("signature")
    @classmethod
    def validate_signature(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not SIGNATURE_RE.fullmatch(value):
            raise ValueError("signature debe ser un HMAC-SHA256 hex de 64 chars")
        return value
