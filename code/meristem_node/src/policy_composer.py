"""PolicyComposer — construye PolicyPacket válido a partir de decisión + rationale.

Responsabilidad única: dado un Bundle, una EvaluationResult del Evaluator y
un texto de rationale (escrito por el LLM o stub), construir un PolicyPacket
con todos los campos requeridos. **No decide nada**, solo combina.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .schemas import (
    Action,
    Bundle,
    EvaluationResult,
    PolicyPacket,
)


# ---------------------------------------------------------------------------
# Defaults de policy v0 (configurable post-demo)
# ---------------------------------------------------------------------------

VALID_DAYS_DEFAULT = 7
PLACEHOLDER_SIGNATURE = "<placeholder-meristem-v0>"


def compose_policy(
    bundle: Bundle,
    evaluation: EvaluationResult,
    rationale: str,
) -> PolicyPacket:
    """Construye PolicyPacket válido. Nunca devuelve None.

    Args:
        bundle: el bundle entrante (para target_node_id)
        evaluation: decisión del Evaluator (para mode + rules + reason_code)
        rationale: prosa breve generada por el LLM (o stub determinista)

    Returns:
        PolicyPacket listo para serializar y entregar a Pollen.

    Raises:
        ValueError: si evaluation.action == REFUSE (no se compone policy
            cuando el Evaluator rechazó). El caller debe manejar REFUSE
            antes de llamar a esta función.
    """
    if evaluation.action == Action.REFUSE:
        raise ValueError(
            f"compose_policy llamado con action=REFUSE "
            f"(reason_code={evaluation.reason_code!r}). El caller debe "
            f"manejar REFUSE sin componer policy."
        )

    valid_until = datetime.now(timezone.utc) + timedelta(days=VALID_DAYS_DEFAULT)
    policy_id = f"pkt_meristem_{int(valid_until.timestamp())}"

    rules: dict[str, Any] = {}
    rules.update(evaluation.suggested_rules)
    # Marcador de la regla aplicada para trazabilidad post-mortem.
    rules["_evaluator_rule"] = evaluation.action.value
    rules["_reason_code"] = evaluation.reason_code

    return PolicyPacket(
        policy_id=policy_id,
        target_node_id=bundle.target_rhizome_id,
        valid_until=valid_until,
        mode_default=evaluation.suggested_mode,
        rules=rules,
        rationale=rationale,
        signature=PLACEHOLDER_SIGNATURE,
    )
