"""FastAPI app de Meristem-nodo.

Día 14: esqueleto stubeado. Endpoints reales con lógica e integración
LLM se construyen día 15-17. Demo-ready día 18.

Levanta en :13000 por defecto (puerto distinto al adapter de tuning
en :12000 y al llama-server :8080 para que coexistan en demo si toca).

Uso:
    cd code/meristem_node
    pip install -r requirements.txt
    python -m src.main

Visitar http://localhost:13000/docs para OpenAPI/Swagger.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import FastAPI, HTTPException

from .schemas import (
    Bundle,
    PolicyPacket,
    VisitResponse,
    VisitResponsePayload,
)


PORT = int(os.environ.get("MERISTEM_NODE_PORT", "13000"))

app = FastAPI(
    title="Meristem-nodo (Sprout)",
    version="0.1.0-dev",
    description=(
        "Slow brain doméstico de Sprout. Vive en portátil casero del "
        "agricultor o cooperativa. Ingiere bundles que Pollen trae de "
        "Rhizome y emite PolicyPacket actualizado. Día 14 esqueleto "
        "stubeado; lógica real día 15-17."
    ),
)


# In-memory storage stub (día 14). Día 15 sustituido por SQLite.
_LATEST_POLICY: PolicyPacket | None = None
_BUNDLES_RECEIVED: list[Bundle] = []


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": "0.1.0-dev",
        "port": PORT,
        "stubbed": True,
        "bundles_received_total": len(_BUNDLES_RECEIVED),
        "latest_policy_emitted": _LATEST_POLICY.policy_id if _LATEST_POLICY else None,
    }


@app.post("/visit", response_model=VisitResponse)
async def visit(bundle: Bundle) -> VisitResponse:
    """Pollen entrega bundle, recibe PolicyPacket actualizado.

    Día 14 stub: persiste bundle en memoria, devuelve placeholder
    PolicyPacket con `mode_default=normal` y rationale fijo. Día 15-17
    sustituido por flujo real:

      1. IngestService valida y persiste bundle (SQLite)
      2. Evaluator aplica regla determinista (4 reglas)
      3. LLM Gemma 4 E4B emite rationale (con tool calling si aplica)
      4. PolicyComposer construye PolicyPacket válido
      5. Persiste policy + responde
    """
    _BUNDLES_RECEIVED.append(bundle)

    # STUB: confirma policy activa con valid_until +7 días
    valid_until = datetime.now(timezone.utc) + timedelta(days=7)
    new_policy_id = f"pkt_meristem_{int(valid_until.timestamp())}"

    policy = PolicyPacket(
        policy_id=new_policy_id,
        target_node_id=bundle.target_rhizome_id,
        valid_until=valid_until,
        mode_default="normal",
        rules={"placeholder": True},
        rationale=(
            "[STUB día 14] Policy activa confirmada con valid_until +7 días. "
            "Lógica real arranca día 15."
        ),
    )

    global _LATEST_POLICY
    _LATEST_POLICY = policy

    return VisitResponse(
        status="ok",
        reason_code=None,
        payload=VisitResponsePayload(
            policy_packet=policy,
            rationale_for_operator=(
                "Tu Rhizome sigue funcionando bien. He extendido la "
                "política activa una semana más."
            ),
            evidence_refs=[bundle.bundle_id],
        ),
    )


@app.get("/policy/latest", response_model=PolicyPacket | None)
async def policy_latest() -> PolicyPacket | None:
    """Devuelve la última policy emitida (debug/demo)."""
    return _LATEST_POLICY


@app.get("/policy/{policy_id}", response_model=PolicyPacket)
async def policy_by_id(policy_id: str) -> PolicyPacket:
    """Trazabilidad: consulta policy por id (día 14 stub: solo la última)."""
    if _LATEST_POLICY and _LATEST_POLICY.policy_id == policy_id:
        return _LATEST_POLICY
    raise HTTPException(status_code=404, detail=f"policy_id {policy_id!r} not found")


def main() -> None:
    """Entrypoint CLI: `python -m src.main` levanta uvicorn."""
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=PORT, reload=False)


if __name__ == "__main__":
    main()
