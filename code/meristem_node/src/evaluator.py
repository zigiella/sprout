"""Evaluator — lógica determinística de Meristem-nodo.

Decide qué acción tomar a partir del bundle de Pollen. **La decisión NO
la toma el LLM**. Esto aísla riesgo de drift del modelo de la jerarquía
de seguridad del proyecto. El LLM solo escribe el `rationale` después
de que el Evaluator decida.

Cuatro reglas en orden de precedencia (cortocircuitan en la primera
que se cumpla):

1. **REFUSE — HARD_LIMIT_DOMAIN o JURISDICTION_POLLEN**
   El bundle pide algo que viola la jurisdicción de Meristem.
   - HARD_LIMIT_DOMAIN: intenta relajar un hard limit del firmware
     (bajar tank_minimum_pct, subir max_seconds_per_event, acortar
     alert_latched_persists_until).

     **Equivalencia jurisdiccional con SAFETY_DOWNGRADE (Xilema día 26)**:
     `HARD_LIMIT_DOMAIN` (cómo Meristem nombra el rechazo, perspectiva
     del emisor) y `SAFETY_DOWNGRADE` (cómo Rhizome/Pollen nombran el
     intento de bajar safety, perspectiva del validador) son la misma
     realidad vista desde dos lados — no son duplicados, son
     **equivalentes jurisdiccionales**. Si en futuras visitas un
     `ValidationStamp` de Rhizome trae `reason: SAFETY_DOWNGRADE`,
     Meristem lo interpreta como sinónimo de su propio
     `HARD_LIMIT_DOMAIN` al consolidar evidencia.
   - JURISDICTION_POLLEN: cambio físico puntual reportado por
     operador (ej. "regar 30s extra hoy") → es jurisdicción de Pollen
     vía MissionPatch, no de Meristem vía PolicyPacket.

2. **ALERT_POLICY — PERSISTENT_EMERGENCY**
   El nodo está en emergencia que persiste a través de varios receipts
   o snapshot.mode == "alert" + ALERT_LATCHED activa.
   Meristem afina con mode_default="alert", no bloquea hardware.

3. **CONSERVATIVE_POLICY — EVIDENCE_LOW_CONFIDENCE**
   El bundle muestra disputas (validation_stamps con disputed/caution),
   baja confianza media en receipts, o contradicciones pendientes en
   snapshot. Meristem afina con mode_default="conservative" y
   thresholds más estrictos (ej. soil_dry_threshold_pct 30 → 35).

4. **CONFIRM_POLICY — STABLE_BUNDLE**
   Camino feliz: bundle limpio, sin emergencias, sin disputas, alta
   confianza. Meristem confirma policy activa con valid_until +7d.

Las 4 reglas son testeables unitariamente y cubrirán la mini-batería
v0 (M1-M5) + casos borde.
"""

from __future__ import annotations

import json
from typing import Any

from .schemas import Action, Bundle, EvaluationResult


# ---------------------------------------------------------------------------
# Constantes de las reglas (configurables vía settings post-demo)
# ---------------------------------------------------------------------------

# Confianza media mínima para considerar bundle "fiable" (regla 3 → 4)
CONFIDENCE_THRESHOLD = 0.7

# Receipts con BLOCK consecutivos que disparan ALERT (regla 2)
PERSISTENT_BLOCK_THRESHOLD = 2

# Soil_dry_threshold_pct sube +5 cuando entramos en conservative
SOIL_THRESHOLD_BUMP_CONSERVATIVE = 5

# Reason codes (literales que el operador y el writeup pueden citar)
RC_HARD_LIMIT = "HARD_LIMIT_DOMAIN"
RC_JURISDICTION_POLLEN = "JURISDICTION_POLLEN"
RC_PERSISTENT_EMERGENCY = "PERSISTENT_EMERGENCY"
RC_LOW_CONFIDENCE = "EVIDENCE_LOW_CONFIDENCE"
RC_STABLE = "STABLE_BUNDLE"


# ---------------------------------------------------------------------------
# Helpers (lectura tolerante del bundle)
# ---------------------------------------------------------------------------


def _bundle_requests_hard_limit_relaxation(bundle: Bundle) -> tuple[bool, str | None]:
    """¿El bundle contiene una solicitud de bajar hard limits del firmware?

    Detecta dos canales:

    1. `weather_digest` u otro objeto con campo `requested_policy_override`
       que pide reducir un hard limit.
    2. Un `validation_stamp` con `visit_amendment.policy_override` que
       intenta reducir tank_minimum_pct, subir max_seconds_per_event o
       acortar alert_latched_persists_until.

    Devuelve (True, descripción) si detecta intento. (False, None) si no.

    NOTA: Pydantic Bundle deja estos campos como `dict[str, Any]` porque
    todavía no hemos cerrado los sub-schemas. Esto se aprieta cuando
    Floema entregue los Kotlin equivalentes finales.
    """
    # Canal 1: validation_stamps con visit_amendment hostil
    for stamp in bundle.validation_stamps:
        amendment = stamp.get("visit_amendment") or stamp.get("visitAmendment")
        if not amendment:
            continue
        override = amendment.get("policy_override") or amendment.get("policyOverride")
        if not override:
            continue

        # Detectar intentos de relajación. Heurística simple v0.
        override_str = str(override).lower()
        if "tank_minimum_pct" in override_str:
            # Si el override pide tank_minimum_pct con valor bajo → relax
            if any(
                f"tank_minimum_pct={n}" in override_str.replace(" ", "")
                for n in [str(i) for i in range(0, 20)]
            ):
                return True, f"validation_stamp.visit_amendment intenta tank_minimum_pct < 20: {override}"
        if "max_seconds_per_event" in override_str:
            # Si pide max_seconds_per_event con valor mayor que default (180)
            for n in range(181, 1000):
                if f"max_seconds_per_event={n}" in override_str.replace(" ", ""):
                    return True, f"validation_stamp.visit_amendment intenta max_seconds_per_event > 180: {override}"

    # Canal 2: rhizome_snapshot con flag explícito (futuro v1)
    snap = bundle.rhizome_snapshot
    if snap.get("requested_policy_override"):
        return True, f"snapshot pide override de policy: {snap['requested_policy_override']}"

    return False, None


def _bundle_requests_pollen_jurisdiction(bundle: Bundle) -> tuple[bool, str | None]:
    """¿El bundle pide un cambio físico puntual del operador?

    Casos típicos:
    - operador reporta "regar 30s extra hoy" → es MissionPatch via Pollen,
      no PolicyPacket via Meristem.
    - operador anota "saltar siguiente ciclo" → idem.

    Detección v0: busca campo `operator_request` en snapshot o en algún
    decision_receipt con tag `operator_override`.
    """
    snap = bundle.rhizome_snapshot
    if snap.get("operator_request"):
        return True, f"snapshot.operator_request presente: {snap['operator_request']}"

    for receipt in bundle.decision_receipts:
        tags = receipt.get("tags") or []
        if "operator_override" in tags:
            return True, "decision_receipt con tag operator_override"

    return False, None


def _bundle_in_persistent_emergency(bundle: Bundle) -> tuple[bool, str | None]:
    """¿El nodo está en emergencia persistente?

    Criterios:
    - `snapshot.mode == "alert"` Y `snapshot.alert_latched == True`
    - O al menos N decision_receipts con `action == "BLOCK"` consecutivos
      en la ventana del bundle.
    """
    snap = bundle.rhizome_snapshot
    mode = snap.get("mode")
    alert_latched = snap.get("alert_latched", False)

    if mode == "alert" and alert_latched:
        return True, "snapshot.mode=alert + alert_latched=True"

    block_receipts = [
        r for r in bundle.decision_receipts if str(r.get("action", "")).upper() == "BLOCK"
    ]
    if len(block_receipts) >= PERSISTENT_BLOCK_THRESHOLD:
        reasons = [r.get("blocked_reason", "?") for r in block_receipts]
        return True, f"{len(block_receipts)} receipts con BLOCK ({','.join(reasons[:3])})"

    return False, None


def _bundle_low_confidence(bundle: Bundle) -> tuple[bool, str | None]:
    """¿El bundle es de baja confianza?

    Tres canales independientes:
    - validation_stamps con status disputed o caution.
    - confidence media de receipts < CONFIDENCE_THRESHOLD.
    - snapshot.pending_contradictions no vacío.
    """
    disputed_stamps = [
        s for s in bundle.validation_stamps
        if str(s.get("status", "")).lower() in ("disputed", "caution")
    ]
    if disputed_stamps:
        statuses = [s.get("status") for s in disputed_stamps]
        return True, f"{len(disputed_stamps)} validation_stamps con disputed/caution ({statuses})"

    confidences = [
        r.get("confidence") for r in bundle.decision_receipts
        if r.get("confidence") is not None
    ]
    if confidences:
        avg_conf = sum(confidences) / len(confidences)
        if avg_conf < CONFIDENCE_THRESHOLD:
            return True, f"avg confidence en receipts = {avg_conf:.2f} (umbral {CONFIDENCE_THRESHOLD})"

    snap = bundle.rhizome_snapshot
    contradictions = snap.get("pending_contradictions") or []
    if contradictions:
        return True, f"snapshot.pending_contradictions = {contradictions}"

    return False, None


# ---------------------------------------------------------------------------
# Evaluator principal
# ---------------------------------------------------------------------------


def evaluate(bundle: Bundle) -> EvaluationResult:
    """Aplica las 4 reglas determinísticas en orden y devuelve EvaluationResult.

    El orden importa: REFUSE corta antes de ALERT, ALERT antes de
    CONSERVATIVE, CONSERVATIVE antes de CONFIRM. La primera regla que
    cumpla decide.
    """
    refs = [bundle.bundle_id]

    # Regla 1: REFUSE — HARD_LIMIT_DOMAIN
    is_hard_limit, hard_msg = _bundle_requests_hard_limit_relaxation(bundle)
    if is_hard_limit:
        return EvaluationResult(
            action=Action.REFUSE,
            reason_code=RC_HARD_LIMIT,
            evidence_refs=refs,
            suggested_mode="normal",  # no aplica, REFUSE no emite policy
            suggested_rules={},
            rationale_seed=(
                f"Detectado intento de relajar hard limit del firmware: {hard_msg}. "
                "Meristem rechaza emitir PolicyPacket. La frontera física manda."
            ),
        )

    # Regla 1-bis: REFUSE — JURISDICTION_POLLEN
    is_pollen_jur, pollen_msg = _bundle_requests_pollen_jurisdiction(bundle)
    if is_pollen_jur:
        return EvaluationResult(
            action=Action.REFUSE,
            reason_code=RC_JURISDICTION_POLLEN,
            evidence_refs=refs,
            suggested_mode="normal",
            suggested_rules={},
            rationale_seed=(
                f"El bundle incluye {pollen_msg}. Cambios físicos puntuales son "
                "jurisdicción de Pollen vía MissionPatch, no de Meristem vía "
                "PolicyPacket."
            ),
        )

    # Regla 2: ALERT_POLICY — PERSISTENT_EMERGENCY
    is_emergency, emergency_msg = _bundle_in_persistent_emergency(bundle)
    if is_emergency:
        return EvaluationResult(
            action=Action.ALERT_POLICY,
            reason_code=RC_PERSISTENT_EMERGENCY,
            evidence_refs=refs,
            suggested_mode="alert",
            suggested_rules={
                "alert_until_human_review": True,
                "skip_routine_watering": True,
            },
            rationale_seed=(
                f"Emergencia persistente detectada: {emergency_msg}. "
                "Meristem afina con mode=alert. NO bloquea hardware "
                "(eso es del firmware), solo recomienda al firmware "
                "operar en modo alerta hasta revisión humana."
            ),
        )

    # Regla 3: CONSERVATIVE_POLICY — EVIDENCE_LOW_CONFIDENCE
    is_low_conf, low_conf_msg = _bundle_low_confidence(bundle)
    if is_low_conf:
        # Aprieta thresholds existentes en la policy activa
        suggested_rules = {
            "soil_dry_threshold_pct_bump": SOIL_THRESHOLD_BUMP_CONSERVATIVE,
            "extra_caution_on_disputed_evidence": True,
        }
        return EvaluationResult(
            action=Action.CONSERVATIVE_POLICY,
            reason_code=RC_LOW_CONFIDENCE,
            evidence_refs=refs,
            suggested_mode="conservative",
            suggested_rules=suggested_rules,
            rationale_seed=(
                f"Evidencia de baja confianza: {low_conf_msg}. "
                "Meristem afina con mode=conservative y endurece thresholds "
                f"(+{SOIL_THRESHOLD_BUMP_CONSERVATIVE}pp en soil_dry)."
            ),
        )

    # Regla 4: CONFIRM_POLICY — STABLE_BUNDLE (camino feliz)
    return EvaluationResult(
        action=Action.CONFIRM_POLICY,
        reason_code=RC_STABLE,
        evidence_refs=refs,
        suggested_mode="normal",
        suggested_rules={},
        rationale_seed=(
            "Bundle limpio: sin emergencias, sin disputas, evidencia coherente. "
            "Meristem confirma policy activa con valid_until extendido +7 días."
        ),
    )
