"""FastAPI app de Meristem-nodo.

Día 16: pipeline determinístico + LLM Gemma 4 E4B Q4_K_M para rationale
con tool calling. La decisión la toma el Evaluator; el LLM solo
escribe rationale técnico + rationale para operador.

Levanta en :13000 por defecto.

Uso:
    cd code/meristem_node
    pip install -r requirements.txt
    # Asegúrate de tener llama-server :8080 con E4B + adapter :12000
    python -m src.main

Env vars opcionales:
    MERISTEM_USE_LLM=false  → salta LLM, usa stub (para tests/dev)
    MERISTEM_ADAPTER_URL=http://localhost:12000  → adapter llamacpp

Visitar http://localhost:13000/docs para OpenAPI/Swagger.
"""

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import ingest as ingest_service
from . import persistence
from .evaluator import evaluate
from .inference import LLMUnavailableError, compose_rationale_via_llm
from .policy_composer import compose_policy
from .schemas import (
    Action,
    Bundle,
    DecisionRecord,
    EvaluationResult,
    PolicyPacket,
    StatusResponse,
    TargetStatus,
    VisitResponse,
    VisitResponsePayload,
)
from .ws_manager import manager as pollen_manager
from .ws_schemas import (
    CommandPayload,
    MeristemReadyPayload,
    WSEvent,
)


logger = logging.getLogger(__name__)


PORT = int(os.environ.get("MERISTEM_NODE_PORT", "13000"))
USE_LLM = os.environ.get("MERISTEM_USE_LLM", "true").lower() not in (
    "false", "0", "no",
)
ADAPTER_URL = os.environ.get("MERISTEM_ADAPTER_URL", "http://localhost:12000")
MERISTEM_ID = os.environ.get("MERISTEM_ID", "meristem_demo_01")


class CommandRequest(BaseModel):
    """Request body para `POST /pollen/command` (UI → Meristem → Pollen)."""

    command: str  # "push_bundles" | "pull_policies"
    expected_count: int = 0


# ---------------------------------------------------------------------------
# Rationale composer: LLM real si disponible, fallback determinista.
# ---------------------------------------------------------------------------


def _compose_rationale(
    bundle: Bundle, evaluation: EvaluationResult,
) -> tuple[str, str, dict[str, Any]]:
    """Devuelve (rationale_tecnico, rationale_para_operador, llm_metrics).

    Si USE_LLM=true (default) y el adapter llamacpp está vivo en
    ADAPTER_URL, llama a Gemma 4 E4B con tool calling y obtiene rationale.
    Si falla, fallback al stub determinista (no rompe pipeline).
    """
    if USE_LLM:
        try:
            rt, ro, metrics = compose_rationale_via_llm(
                bundle, evaluation, adapter_url=ADAPTER_URL
            )
            metrics["mode"] = "llm"
            return rt, ro, metrics
        except LLMUnavailableError as e:
            logger.warning(
                "LLM no disponible (%s). Fallback a rationale stub.", e
            )
            rt, ro = _stub_rationale(evaluation.rationale_seed)
            return rt, ro, {"mode": "stub_fallback", "reason": str(e)}

    rt, ro = _stub_rationale(evaluation.rationale_seed)
    return rt, ro, {"mode": "stub_disabled"}


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
            "meristem_id": MERISTEM_ID,
            "llm_mode": "real" if USE_LLM else "stub_disabled",
            "adapter_url": ADAPTER_URL if USE_LLM else None,
            "bundles_received_total": persistence.count_bundles(),
            "policies_emitted_total": persistence.count_policies(),
            "decisions_by_rule": persistence.count_decisions_by_rule(),
            "policies_by_scope": persistence.count_policies_by_scope(),
            "targets_known": persistence.list_known_targets(),
            "pollen_connection": pollen_manager.state_snapshot(),
            "ws_events_by_type": persistence.count_ws_events_by_event(),
        }

    @app.get("/status", response_model=StatusResponse)
    async def status() -> StatusResponse:
        """Vista consolidada multi-Rhizome.

        Para cada Rhizome conocido (que ha enviado al menos un bundle),
        devuelve resumen: última policy + modo + reason_code + edad +
        contadores. Pensado para demo MVP donde Meristem gestiona
        rhizome_01 + rhizome_02 simultáneos en el mismo hardware.
        """
        targets_known = persistence.list_known_targets()
        targets: list[TargetStatus] = []
        for t in targets_known:
            summary = persistence.get_target_summary(t)
            if summary is None:
                continue  # defensivo, no debería pasar
            targets.append(TargetStatus(**summary))
        return StatusResponse(targets_known=targets_known, targets=targets)

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

        # 3b: componer rationale (LLM o fallback) + policy
        rationale_tecnico, rationale_operador, llm_metrics = _compose_rationale(
            bundle, evaluation
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
                llm_metrics=llm_metrics,
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

    # -----------------------------------------------------------------------
    # WebSocket endpoint Pollen ↔ Meristem (Variante D, protocolo v1.0)
    # -----------------------------------------------------------------------

    @app.websocket("/ws/pollen-sync")
    async def ws_pollen_sync(websocket: WebSocket) -> None:
        """Endpoint WebSocket para sincronización bidireccional con Pollen.

        Protocolo v1.0 acordado con Floema (PR #81). Pollen es cliente
        WebSocket; Meristem es server. Mensajes JSON con shape uniforme:
        `{event, payload, timestamp, trace_id?}`.

        Flujo:
        1. Pollen abre conexión → `pollen_hello`
        2. Meristem responde con `meristem_ready` (lista policies disponibles)
        3. Loop bidireccional con heartbeat cada 10s
        4. Comandos `push_bundles` / `pull_policies` se disparan desde
           UI Meristem via POST /pollen/command y se entregan por este WS

        El control plane viaja por WebSocket; el data plane (POST /visit,
        GET /policy/by-target/{id}) sigue siendo HTTP REST estándar.
        """
        accepted = await pollen_manager.accept_or_reject(websocket)
        if not accepted:
            return

        logger.info("WS Pollen aceptado, esperando hello...")

        try:
            while True:
                msg = await websocket.receive_json()
                event = msg.get("event", "")
                payload = msg.get("payload", {}) or {}
                trace_id = msg.get("trace_id")

                # Persistir el mensaje recibido (audit trail)
                persistence.log_ws_event(
                    direction="in", event=event, payload=payload, trace_id=trace_id,
                )
                pollen_manager.heartbeat()

                if event == WSEvent.POLLEN_HELLO.value:
                    pollen_id = payload.get("pollen_id", "unknown")
                    app_version = payload.get("app_version", "0.0.0")
                    pollen_manager.register_hello(pollen_id, app_version)
                    logger.info(
                        "Pollen %s v%s conectado. bundles_pending=%d, policies_pickup=%s",
                        pollen_id, app_version,
                        payload.get("bundles_pending_count", 0),
                        payload.get("policies_to_pickup_target_ids", []),
                    )
                    # Construir lista de policies disponibles para retirar
                    pickup = []
                    for tid in payload.get("policies_to_pickup_target_ids", []):
                        pol = persistence.get_latest_policy_for(tid)
                        if pol:
                            pickup.append({
                                "target_node_id": tid,
                                "policy_id": pol.policy_id,
                            })
                    ready_payload = MeristemReadyPayload(
                        meristem_id=MERISTEM_ID,
                        version="0.1.0",
                        policies_ready_for_pickup=pickup,
                    ).model_dump(mode="json")
                    persistence.log_ws_event(
                        direction="out",
                        event=WSEvent.MERISTEM_READY.value,
                        payload=ready_payload,
                    )
                    await pollen_manager.send(WSEvent.MERISTEM_READY, ready_payload)

                elif event == WSEvent.POLLEN_HEARTBEAT.value:
                    ack_payload = {"online": True}
                    persistence.log_ws_event(
                        direction="out",
                        event=WSEvent.MERISTEM_HEARTBEAT_ACK.value,
                        payload=ack_payload,
                    )
                    await pollen_manager.send(
                        WSEvent.MERISTEM_HEARTBEAT_ACK, ack_payload,
                    )

                elif event == WSEvent.BUNDLES_PUSHED.value:
                    logger.info(
                        "Pollen termino de empujar bundles: count=%d ids=%s",
                        payload.get("count", 0),
                        payload.get("bundle_ids", []),
                    )
                    # No hace falta responder; UI Meristem leerá /sync-state.

                elif event == WSEvent.POLICIES_PULLED.value:
                    logger.info(
                        "Pollen termino de retirar policies: count=%d ids=%s",
                        payload.get("count", 0),
                        payload.get("policy_ids", []),
                    )

                else:
                    logger.warning("Evento WS desconocido: %s", event)
                    err_payload = {
                        "code": "UNKNOWN_EVENT",
                        "message_es": f"Evento desconocido: {event!r}",
                    }
                    persistence.log_ws_event(
                        direction="out",
                        event=WSEvent.ERROR.value,
                        payload=err_payload,
                        trace_id=trace_id,
                    )
                    await pollen_manager.send(
                        WSEvent.ERROR, err_payload, trace_id=trace_id,
                    )

        except WebSocketDisconnect:
            logger.info("Pollen %s desconectado limpiamente", pollen_manager.pollen_id)
        except Exception as e:
            logger.exception("Error en loop WS Pollen: %s", e)
        finally:
            await pollen_manager.disconnect()

    # -----------------------------------------------------------------------
    # REST endpoints para la UI Meristem (control plane)
    # -----------------------------------------------------------------------

    @app.post("/pollen/command")
    async def trigger_pollen_command(req: CommandRequest) -> dict[str, Any]:
        """Disparado por click del agricultor en UI Meristem.

        Envía un mensaje `command` por el WS al Pollen conectado. Si no
        hay Pollen conectado, devuelve 409.
        """
        if not pollen_manager.is_connected:
            raise HTTPException(
                status_code=409,
                detail="No hay Pollen conectado en este momento.",
            )
        trace_id = f"cmd_{uuid.uuid4().hex[:8]}"
        cmd_payload = CommandPayload(
            command=req.command,
            expected_count=req.expected_count,
        ).model_dump(mode="json")
        persistence.log_ws_event(
            direction="out",
            event=WSEvent.COMMAND.value,
            payload=cmd_payload,
            trace_id=trace_id,
        )
        ok = await pollen_manager.send(
            WSEvent.COMMAND, cmd_payload, trace_id=trace_id,
        )
        if not ok:
            raise HTTPException(
                status_code=502,
                detail="No se pudo enviar el comando por WebSocket.",
            )
        return {
            "ok": True,
            "trace_id": trace_id,
            "command": req.command,
            "expected_count": req.expected_count,
        }

    # -----------------------------------------------------------------------
    # UI estática para el agricultor (HTML/CSS/JS vanilla servido por FastAPI)
    # -----------------------------------------------------------------------
    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.is_dir():
        app.mount(
            "/ui",
            StaticFiles(directory=str(static_dir), html=True),
            name="ui",
        )

    @app.get("/sync-state")
    async def sync_state() -> dict[str, Any]:
        """Estado actual del sync Pollen-Meristem para la UI.

        Combina:
        - estado de la conexión WS (connected, alive, pollen_id)
        - últimos N eventos WS persistidos (audit/demo visible)

        La UI hace polling cada 1-2s a este endpoint para reflejar
        eventos en pantalla sin abrir su propio WebSocket.
        """
        return {
            "pollen_connection": pollen_manager.state_snapshot(),
            "recent_events": persistence.get_recent_ws_events(limit=20),
            "ws_events_by_type": persistence.count_ws_events_by_event(),
        }

    @app.get("/bundles/recent")
    async def bundles_recent(limit: int = 20) -> dict[str, Any]:
        """Últimos N bundles recibidos vía POST /visit.

        Para zona "Visitas recibidas" de la UI Meristem. Cada item
        incluye `reason_code` y `rule_applied` de la decisión que se
        tomó sobre ese bundle (joineando con `decisions`). Si todavía
        no hay decisión (REFUSE branch o race condition), ambos son
        None.
        """
        capped = max(1, min(int(limit), 200))
        return {
            "limit": capped,
            "items": persistence.list_recent_bundles(limit=capped),
        }

    @app.get("/policies/recent")
    async def policies_recent(limit: int = 20) -> dict[str, Any]:
        """Últimas N policies emitidas (orden DESC).

        Para zona "Políticas emitidas" de la UI Meristem. Cada item
        incluye `policy_id`, `target_node_id`, `mode_default`,
        `valid_until`, rationale técnico recortado a 160 chars.
        """
        capped = max(1, min(int(limit), 200))
        return {
            "limit": capped,
            "items": persistence.list_recent_policies(limit=capped),
        }

    return app


app = _build_app()


def main() -> None:
    """Entrypoint CLI: `python -m src.main` levanta uvicorn."""
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=PORT, reload=False)


if __name__ == "__main__":
    main()
