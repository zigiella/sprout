"""FastAPI app de Meristem-nodo.

Día 15: lógica determinística (Evaluator + persistencia SQLite). Día
16 sustituye el rationale stub por LLM Gemma 4 E4B + tool calling.

Levanta en :13000 por defecto.

Uso:
    cd code/meristem_node
    pip install -r requirements.txt
    python -m src.main

Visitar http://localhost:13000/docs para OpenAPI/Swagger.
"""

from __future__ import annotations

import os
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException

from . import ingest as ingest_service
from . import persistence
from .evaluator import evaluate
from .policy_composer import compose_policy
from .schemas import (
    Action,
    Bundle,
    DecisionRecord,
    PolicyPacket,
    VisitResponse,
    VisitResponsePayload,
)


PORT = int(os.environ.get("MERISTEM_NODE_PORT", "13000"))


# ---------------------------------------------------------------------------
# Stub de rationale del LLM (día 15). Día 16 lo sustituye llamada real.
# ---------------------------------------------------------------------------


def _stub_rationale(rationale_seed: str) -> tuple[str, str]:
    """Genera rationale técnico + prosa al operador desde el seed.

    Día 15: stub determinístico (texto fijo según seed). Día 16: cliente
    al adapter llamacpp con E4B + tool calling.

    Returns:
        (rationale_tecnico, rationale_for_operator)
    """
    if not rationale_seed:
        return ("Policy actualizada.", "Tu Rhizome sigue funcionando bien.")

    seed = rationale_seed.strip()
    seed_lower = seed.lower()
    if "limpio" in seed_lower or "estable" in seed_lower:
        operator = (
            "Tu Rhizome sigue funcionando bien. He extendido la política "
            "activa una semana más."
        )
    elif "conservativ" in seed_lower or "baja confianza" in seed_lower:
        operator = (
            "He notado evidencia ambigua en tu última visita. Pongo el "
            "Rhizome en modo prudente unos días."
        )
    elif "alert" in seed_lower or "emergencia" in seed_lower:
        operator = (
            "Hay alerta persistente en el nodo. Modo ALERTA hasta que "
            "revises a mano. No se ejecutan riegos automáticos."
        )
    else:
        operator = "Política actualizada según los datos de la visita."

    return (seed[:500], operator)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


def _build_app() -> FastAPI:
    persistence.init_db()

    app = FastAPI(
        title="Meristem-nodo (Sprout)",
        version="0.1.0",
        description=(
            "Slow brain doméstico de Sprout. Vive en portátil casero del "
            "agricultor o cooperativa. Ingiere bundles que Pollen trae de "
            "Rhizome y emite PolicyPacket actualizado. Día 15: lógica "
            "determinística + persistencia SQLite. Día 16: LLM Gemma 4 "
            "E4B + tool calling integrado."
        ),
    )

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "version": "0.1.0",
            "port": PORT,
            "stubbed_llm": True,  # día 15: rationale es stub
            "bundles_received_total": persistence.count_bundles(),
            "policies_emitted_total": persistence.count_policies(),
            "decisions_by_rule": persistence.count_decisions_by_rule(),
        }

    @app.post("/visit", response_model=VisitResponse)
    async def visit(bundle: Bundle) -> VisitResponse:
        """Pollen entrega bundle. Pipeline:

        1. Ingest (validación + persistencia)
        2. Evaluator (4 reglas determinísticas)
        3a. Si REFUSE → respuesta envelope sin policy
        3b. Si OK → componer PolicyPacket + rationale + persistir
        4. Devolver VisitResponse
        """
        # 1. Ingest
        ingest_service.ingest(bundle)

        # 2. Evaluator
        evaluation = evaluate(bundle)

        # 3. Branch por action
        if evaluation.action == Action.REFUSE:
            return VisitResponse(
                status="refuse",
                reason_code=evaluation.reason_code,
                payload=None,
            )

        # 3b: componer policy + rationale
        rationale_tecnico, rationale_operador = _stub_rationale(
            evaluation.rationale_seed
        )
        policy = compose_policy(bundle, evaluation, rationale_tecnico)

        # 4. Persistir policy y decision
        persistence.insert_policy(policy, evidence_refs=evaluation.evidence_refs)
        persistence.insert_decision(
            DecisionRecord(
                decision_id=f"dec_{uuid.uuid4().hex[:12]}",
                bundle_id=bundle.bundle_id,
                policy_id=policy.policy_id,
                rule_applied=evaluation.action,
                reason_code=evaluation.reason_code,
                llm_metrics={"stubbed": True, "day": 15},
            )
        )

        return VisitResponse(
            status="ok",
            reason_code=evaluation.reason_code,
            payload=VisitResponsePayload(
                policy_packet=policy,
                rationale_for_operator=rationale_operador,
                evidence_refs=evaluation.evidence_refs,
            ),
        )

    @app.get("/policy/latest", response_model=PolicyPacket | None)
    async def policy_latest() -> PolicyPacket | None:
        """Última policy emitida (debug/demo)."""
        return persistence.get_latest_policy_global()

    @app.get("/policy/{policy_id}", response_model=PolicyPacket)
    async def policy_by_id(policy_id: str) -> PolicyPacket:
        """Trazabilidad: policy concreta por id."""
        policy = persistence.get_policy_by_id(policy_id)
        if not policy:
            raise HTTPException(
                status_code=404, detail=f"policy_id {policy_id!r} not found"
            )
        return policy

    @app.get("/policy/by-target/{target_node_id}", response_model=PolicyPacket | None)
    async def policy_by_target(target_node_id: str) -> PolicyPacket | None:
        """Última policy emitida para un nodo Rhizome concreto.

        Útil para Pollen: cuando va a visitar a Rhizome X, consulta aquí
        si hay policy nueva pendiente de transportar.
        """
        return persistence.get_latest_policy_for(target_node_id)

    return app


app = _build_app()


def main() -> None:
    """Entrypoint CLI: `python -m src.main` levanta uvicorn."""
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=PORT, reload=False)


if __name__ == "__main__":
    main()
