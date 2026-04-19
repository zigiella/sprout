"""Consolidador de evidencia + emision de PolicyPacket.

Flujo (spec 12 §6):

    evidence + active_policy  ──►  prompt  ──►  Ollama E4B  ──►  JSON raw
                                                                      │
                                                                      ▼
                                                             PolicyPacket.validate
                                                                      │
                                                                      ▼
                                                             safety_rules.check
                                                                 ┌────┴────┐
                                                             OK  │         │ violaciones
                                                                 ▼         ▼
                                                          persist()   log blocked
                                                                      return None

Reglas clave:
- Si el JSON del modelo no valida el schema → no persiste, devuelve None y
  loguea el intento.
- Si valida el schema pero viola §30 → no persiste, loguea el intento en
  `decisions_log` con action="blocked_by_safety" (ver Gap 4 del draft de
  sub-issue 2026-04-18), devuelve None.
- Si todo OK → persiste como policy activa, devuelve la packet.

Este modulo NO esta expuesto como endpoint en este PR. Se invoca desde un
consolidator job (fuera de alcance, PR siguiente) o desde tests.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from schemas import PolicyPacket

from . import safety_rules
from .llm_client import OllamaClient
from .persistence import (
    append_decision_log,
    get_active_policy,
    upsert_policy,
)

logger = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
_SYSTEM_PROMPT_PATH = _PROMPTS_DIR / "system_v1.txt"


@dataclass(frozen=True)
class EngineResult:
    """Resultado de un ciclo de consolidacion."""

    packet: PolicyPacket | None
    reason: str | None  # None si OK; "invalid_schema" / "violates_safety_rule" si no
    violations: list[dict[str, Any]] | None = None


def load_system_prompt() -> str:
    return _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


def build_user_prompt(
    target_node_id: str,
    evidence: list[dict[str, Any]],
    active_policy: dict[str, Any] | None,
) -> str:
    """Formatea el contexto para la llamada al modelo.

    El schema se incluye textualmente para anclar la salida; Ollama lo usa
    tambien como `format` en la llamada HTTP, pero duplicarlo en el prompt
    mejora la coherencia en modelos pequenos (E4B).
    """
    schema_json = json.dumps(PolicyPacket.model_json_schema(), indent=2)
    active_block = (
        json.dumps(active_policy, indent=2)
        if active_policy is not None
        else "null"
    )
    evidence_block = json.dumps(evidence, indent=2)

    return (
        f"Nodo objetivo: {target_node_id}\n\n"
        f"Politica actualmente activa (o null si no hay):\n{active_block}\n\n"
        f"Evidencia reciente ({len(evidence)} items):\n{evidence_block}\n\n"
        f"Schema PolicyPacket v1.0 al que debe ajustarse tu salida:\n{schema_json}\n\n"
        "Emite UN solo JSON que valide contra el schema. Nada mas."
    )


def consolidate(
    db_path: str | Path,
    target_node_id: str,
    evidence: list[dict[str, Any]],
    llm: OllamaClient,
) -> EngineResult:
    """Ejecuta un ciclo de consolidacion para `target_node_id`.

    `evidence` es la lista de payloads crudos ya acumulados por /ingest
    (normalmente ultimos N snapshots + weather packets + alerts). El caller
    decide que subset pasa; aqui se usa tal cual.
    """
    system = load_system_prompt()
    active = get_active_policy(db_path, target_node_id)
    user = build_user_prompt(target_node_id, evidence, active)

    schema = PolicyPacket.model_json_schema()
    raw = llm.generate_json(system=system, user=user, schema=schema)

    try:
        packet = PolicyPacket.model_validate(raw)
    except ValidationError as exc:
        logger.warning(
            "LLM produjo JSON que no valida PolicyPacket: %s", exc.errors()
        )
        append_decision_log(
            db_path,
            origin_node_id="meristem_01",
            action="blocked_invalid_schema",
            payload={"raw_output": raw, "errors": exc.errors()},
        )
        return EngineResult(
            packet=None, reason="invalid_schema", violations=None
        )

    violations = safety_rules.check_policy_packet(packet)
    if violations:
        logger.warning(
            "LLM produjo PolicyPacket que viola §30: %s",
            [v.rule for v in violations],
        )
        append_decision_log(
            db_path,
            origin_node_id="meristem_01",
            action="blocked_by_safety",
            payload={
                "attempted_packet": packet.model_dump(mode="json"),
                "violations": [v.to_dict() for v in violations],
            },
        )
        return EngineResult(
            packet=None,
            reason=safety_rules.REASON_VIOLATES_SAFETY_RULE,
            violations=[v.to_dict() for v in violations],
        )

    upsert_policy(db_path, packet.model_dump(mode="json"))
    return EngineResult(packet=packet, reason=None, violations=None)
