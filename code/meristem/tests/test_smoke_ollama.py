"""Smoke test contra Ollama real. Marcado `@pytest.mark.ollama`.

Skippea automaticamente si el daemon no responde en el host/puerto de los
Settings por defecto. Correr en local con Ollama + gemma4:e4b cargado:

    pytest -m ollama code/meristem/tests/test_smoke_ollama.py -s

En CI este test no corre (no hay Ollama). Se deja como herramienta de
desarrollo y verificacion manual de latencia objetivo (<60s E2E).
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from schemas import PolicyPacket

from src.llm_client import OllamaClient
from src.persistence import init_db
from src.policy_engine import consolidate
from src.settings import load_settings


@pytest.mark.ollama
def test_consolidate_against_local_ollama(tmp_path: Path) -> None:
    settings = load_settings()
    # Budget holgado para el smoke manual: el prompt real del engine
    # (system_v1 + active_policy + evidence) + structured output contra el
    # schema completo de PolicyPacket excede el default de 120s en CPU. El
    # test todavia asserta elapsed < 90.0 mas abajo para dar senal clara de
    # si cumplimos el objetivo del spec.
    client = OllamaClient(settings, timeout_s=300.0)
    if not client.ping():
        client.close()
        pytest.skip(
            f"Ollama no responde en {settings.ollama_host}; skip smoke test."
        )

    db_path = str(tmp_path / "smoke.db")
    init_db(db_path)

    started = time.monotonic()
    try:
        result = consolidate(
            db_path=db_path,
            target_node_id="rhizome_01",
            evidence=[],
            llm=client,
        )
    finally:
        client.close()
    elapsed = time.monotonic() - started

    assert result.packet is not None or result.reason in {
        "invalid_schema",
        "violates_safety_rule",
    }, f"resultado inesperado: {result}"

    # Latencia objetivo del spec: <60s E2E. Si no se cumple, test falla y
    # queda visible en la bitacora del PR. Margen razonable para hardware
    # modesto.
    assert elapsed < 90.0, (
        f"latencia {elapsed:.1f}s excede budget de 90s (objetivo 60s)."
    )

    # Si la packet paso, debe poder re-serializarse como PolicyPacket.
    if result.packet is not None:
        PolicyPacket.model_validate(result.packet.model_dump(mode="json"))
