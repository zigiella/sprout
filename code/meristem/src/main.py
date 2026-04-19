"""Entrypoint HTTP de Meristem (FastAPI).

Expone:
- `/health`               → liveness + metadata.
- `/ingest`               → Pollen empuja evidencia.
- `/policies/{rhizome_id}`→ policy activa.
- `/deltas/pending/{rhizome_id}` + `/deltas/propose`.

Ver `src/routes.py`.

Shadow (Meristem sombra contra Gemma 4 31B cloud) solo se importa si el
flag `SHADOW_ENABLED` esta activo. Con flag apagado, `google.genai` no debe
entrar nunca en `sys.modules` — ver `tests/test_shadow_off.py`.
"""

from __future__ import annotations

from fastapi import FastAPI

from . import __version__
from .persistence import init_db
from .routes import router as api_router
from .settings import Settings, load_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    init_db(settings.db_path)

    app = FastAPI(title="Sprout Meristem", version=__version__)
    app.state.settings = settings

    if settings.shadow_enabled:
        # Import diferido. Con flag off, no se toca nunca.
        from .shadow import shadow_client  # noqa: F401

    @app.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "version": __version__,
            "model": settings.ollama_model,
            "shadow_enabled": settings.shadow_enabled,
        }

    app.include_router(api_router)
    return app


def main() -> None:
    import uvicorn

    settings = load_settings()
    uvicorn.run(
        "src.main:create_app",
        factory=True,
        host="127.0.0.1",
        port=settings.meristem_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
