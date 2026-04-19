"""Pre-emit validador de limites duros del firmware sobre PolicyPacket y
PolicyDelta.

Filosofia (docs/30_safety_rules.md §3): el firmware ESP32 impone limites
hardcoded que no se pueden relajar desde Python. Si Meristem emite una
politica con `max_watering_duration_s=120`, el firmware la ignora y corta a
60s igual. Este modulo se anticipa a ese rechazo: bloquea la emision en
origen y deja rastro auditable del intento, evitando ruido en el tablero de
alertas y DecisionReceipts de `BLOCK`.

Los schemas v1.0 permiten rangos mas amplios que §30 (ej: schema permite
`tank_minimum_pct>=10`, §30 exige 20). Este modulo implementa la version
estricta de §30 — es lo que Cambium llamo "piso politico con suelo duro" en
su mensaje de 2026-04-19 cerrando los 4 gaps detectados.

Cobertura:
- `rules.max_watering_duration_s <= 60`                   [§3.1]
- `rules.tank_minimum_pct >= 20.0`                        [§3.2]
- Rate limits (8/h, 48/dia)  → NO expresable en v1.0     [Gap 2]
- Concurrencia zonas          → NO expresable en v1.0     [Gap 3]

Gap 2 y 3 se consolidan post-hoc via `REJECTED RATE_LIMIT_*` y
`REJECTED ZONE_IN_USE` observados en DecisionReceipts (fuera del scope de
este PR). Ver bitacora 2026-04-18_drafts-subissue-30-gaps_meristem.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from schemas import PolicyDelta, PolicyPacket
from schemas.enums import PatchOperation

# Limites espejo de docs/30_safety_rules.md §3. Si §30 cambia, esto tambien.
# No se lee de config — son limites fisicos del firmware.
FIRMWARE_MAX_WATERING_DURATION_S: int = 60
FIRMWARE_TANK_MINIMUM_PCT: float = 20.0

# Rason unica que se expone al cliente cuando el validador bloquea. Cambium
# (2026-04-19 Gap 4): el rechazo se devuelve como 422 con esta reason; no se
# emite ContradictionAlert porque los tipos canonicos no cubren el caso.
REASON_VIOLATES_SAFETY_RULE: str = "violates_safety_rule"


@dataclass(frozen=True)
class SafetyViolation:
    """Un parametro de politica que excede un limite duro del firmware."""

    rule: str
    proposed_value: Any
    firmware_limit: Any
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "proposed_value": self.proposed_value,
            "firmware_limit": self.firmware_limit,
            "detail": self.detail,
        }


def check_policy_packet(packet: PolicyPacket) -> list[SafetyViolation]:
    """Valida un PolicyPacket contra §30. Lista vacia si todo esta bien."""
    violations: list[SafetyViolation] = []

    duration = packet.rules.max_watering_duration_s
    if duration > FIRMWARE_MAX_WATERING_DURATION_S:
        violations.append(
            SafetyViolation(
                rule="rules.max_watering_duration_s",
                proposed_value=duration,
                firmware_limit=FIRMWARE_MAX_WATERING_DURATION_S,
                detail=(
                    f"El firmware corta a {FIRMWARE_MAX_WATERING_DURATION_S}s "
                    f"por §30.1; la politica pide {duration}s."
                ),
            )
        )

    tank_min = packet.rules.tank_minimum_pct
    if tank_min < FIRMWARE_TANK_MINIMUM_PCT:
        violations.append(
            SafetyViolation(
                rule="rules.tank_minimum_pct",
                proposed_value=tank_min,
                firmware_limit=FIRMWARE_TANK_MINIMUM_PCT,
                detail=(
                    f"El firmware exige >= {FIRMWARE_TANK_MINIMUM_PCT}% "
                    f"por §30.2; la politica pide {tank_min}%."
                ),
            )
        )

    # Rate limits §30.1 (8/h, 48/dia) y concurrencia §30.2: no-op en v1.0.
    # PolicyPacket no modela scheduling ni cadencia. Ver Gap 2 y Gap 3.

    return violations


def check_delta_against_base(
    delta: PolicyDelta, base: PolicyPacket
) -> list[SafetyViolation]:
    """Proyecta el delta sobre la packet base y valida la proyeccion.

    Es la forma correcta de validar un delta: un patch puede parecer inocuo
    visto solo ("replace rules.max_watering_duration_s = 120") pero la
    proyeccion resultante es la que termina llegando al firmware.
    """
    projected = project_delta(delta, base)
    return check_policy_packet(projected)


def project_delta(delta: PolicyDelta, base: PolicyPacket) -> PolicyPacket:
    """Aplica los patches del delta sobre la packet base y devuelve una
    PolicyPacket nueva (re-validada por pydantic).

    No muta `base`. Revalida: si algun patch produce una packet invalida
    segun el schema (ej: target_pct < min_pct), se levanta ValidationError.
    """
    data = base.model_dump(mode="json")
    for patch in delta.patches:
        _apply_patch(data, patch.op, patch.path, patch.value)
    return PolicyPacket.model_validate(data)


def _apply_patch(
    data: dict[str, Any],
    op: PatchOperation,
    path: str,
    value: Any,
) -> None:
    parts = path.split(".")
    cursor: Any = data
    for key in parts[:-1]:
        cursor = cursor[key]
    last = parts[-1]

    if op == PatchOperation.REPLACE:
        cursor[last] = value
    elif op == PatchOperation.ADD:
        existing = cursor.get(last)
        if isinstance(existing, list):
            # Convencion: "add" sobre lista = append (no reemplaza la lista).
            existing.append(value)
        else:
            cursor[last] = value
    elif op == PatchOperation.REMOVE:
        cursor.pop(last, None)
    else:  # pragma: no cover - enum exhaustivo
        raise ValueError(f"operacion de patch no soportada: {op}")
