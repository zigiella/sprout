"""Mock cliente WebSocket Pollen para smoke local del protocolo Variante D.

Útil para:
- Smoke local de Meristem-nodo sin necesidad de Pollen Android real
- Referencia de implementación para Floema (cliente Kotlin/OkHttp)
- Demostración del flujo completo en video si lo grabamos

USO:
    # Pre-requisito: Meristem-nodo levantado en :13000
    cd code/meristem_node
    python -m src.main &  # background

    # Lanzar mock client
    python scripts/mock_pollen_ws_client.py

    # Modo "interactivo" — escucha 60s, responde a comandos
    python scripts/mock_pollen_ws_client.py --interactive --timeout 60

    # Modo "demo" con escenario completo (hello + sleep + heartbeat + push)
    python scripts/mock_pollen_ws_client.py --demo

PROTOCOLO: ver `code/meristem_node/src/ws_schemas.py` y bitácora
`bitacora/2026-05-04_acepto-variante-d-websocket-protocolo_meristem-a-floema.md`
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime

try:
    from websockets.client import connect as ws_connect
except ImportError:
    print("ERROR: instala 'websockets': pip install websockets", file=sys.stderr)
    sys.exit(2)


DEFAULT_URL = "ws://localhost:13000/ws/pollen-sync"


async def send(ws, event: str, payload: dict, trace_id: str | None = None) -> None:
    msg = {
        "event": event,
        "payload": payload,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if trace_id:
        msg["trace_id"] = trace_id
    print(f">> [send] {event}", json.dumps(payload, ensure_ascii=True))
    await ws.send(json.dumps(msg))


async def receive_one(ws) -> dict:
    raw = await ws.recv()
    msg = json.loads(raw)
    print(f"<< [recv] {msg.get('event', '?')}", json.dumps(msg.get("payload", {}), ensure_ascii=True))
    return msg


async def run_demo(url: str, pollen_id: str) -> int:
    """Escenario completo: hello → ready → heartbeat → push → close."""
    async with ws_connect(url) as ws:
        # 1. Hello
        await send(ws, "pollen_hello", {
            "pollen_id": pollen_id,
            "app_version": "0.5.0-demo",
            "bundles_pending_count": 2,
            "policies_to_pickup_target_ids": ["rhizome_01", "rhizome_02"],
        })
        ready = await receive_one(ws)
        assert ready["event"] == "meristem_ready", "esperaba meristem_ready"

        # 2. Heartbeat
        await asyncio.sleep(1)
        await send(ws, "pollen_heartbeat", {})
        ack = await receive_one(ws)
        assert ack["event"] == "meristem_heartbeat_ack", "esperaba ack"

        # 3. Simulamos que la UI Meristem disparó comando push_bundles
        # (en producción esto lo dispara el agricultor con click).
        # Aquí solo escuchamos hasta 5s o hasta recibir el comando.
        try:
            cmd = await asyncio.wait_for(receive_one(ws), timeout=5.0)
            print(f"   [Demo] recibido comando: {cmd.get('payload', {}).get('command')}")
            # Simular que Pollen termina de empujar bundles via HTTP normal
            # y notifica via WS:
            await asyncio.sleep(1)
            await send(ws, "bundles_pushed", {
                "count": 2,
                "bundle_ids": ["b_demo_01", "b_demo_02"],
            }, trace_id=cmd.get("trace_id"))
        except asyncio.TimeoutError:
            print("   [Demo] no llegó comando en 5s (UI no disparó)")

        await asyncio.sleep(1)
        print("   [Demo] cerrando conexión limpiamente")
    return 0


async def run_interactive(url: str, pollen_id: str, timeout: float) -> int:
    """Modo interactivo: hello + escucha continua hasta timeout."""
    async with ws_connect(url) as ws:
        await send(ws, "pollen_hello", {
            "pollen_id": pollen_id,
            "app_version": "0.5.0-mock",
            "bundles_pending_count": 0,
            "policies_to_pickup_target_ids": [],
        })

        async def heartbeat_loop():
            while True:
                await asyncio.sleep(10)
                try:
                    await send(ws, "pollen_heartbeat", {})
                except Exception:
                    return

        async def listen_loop():
            while True:
                try:
                    await receive_one(ws)
                except Exception:
                    return

        try:
            await asyncio.wait_for(
                asyncio.gather(heartbeat_loop(), listen_loop()),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            print(f"   [Interactive] timeout {timeout}s alcanzado, cerrando")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help=f"Default: {DEFAULT_URL}")
    parser.add_argument("--pollen-id", default="pollen_mock_01")
    parser.add_argument(
        "--demo", action="store_true",
        help="Escenario completo (hello + heartbeat + push + close)",
    )
    parser.add_argument(
        "--interactive", action="store_true",
        help="Modo interactivo: escucha continua",
    )
    parser.add_argument(
        "--timeout", type=float, default=60.0,
        help="Timeout para modo interactivo (default 60s)",
    )
    args = parser.parse_args()

    if args.demo:
        return asyncio.run(run_demo(args.url, args.pollen_id))
    if args.interactive:
        return asyncio.run(run_interactive(args.url, args.pollen_id, args.timeout))
    # Por defecto: demo
    return asyncio.run(run_demo(args.url, args.pollen_id))


if __name__ == "__main__":
    sys.exit(main())
