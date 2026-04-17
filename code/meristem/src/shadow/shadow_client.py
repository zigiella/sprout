"""Cliente del Meristem sombra (Gemma 4 31B via Google AI Studio).

Solo se importa cuando SHADOW_ENABLED=true. Si este modulo se importa sin
`google-genai` instalado, el `ImportError` es intencional — indica que el
flag esta mal configurado en el entorno (flag on sin dependencia opcional).
"""

from __future__ import annotations

from google import genai  # type: ignore[import-not-found]

from ..settings import Settings


class ShadowClient:
    """Wrapper minimo sobre google-genai para el modelo sombra."""

    def __init__(self, settings: Settings) -> None:
        if not settings.shadow_enabled:
            raise RuntimeError(
                "ShadowClient instanciado con SHADOW_ENABLED=false. "
                "Esto jamas debe pasar en produccion."
            )
        if not settings.gemini_api_key:
            raise RuntimeError(
                "SHADOW_ENABLED=true pero GEMINI_API_KEY vacia."
            )
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.shadow_model

    @property
    def model(self) -> str:
        return self._model
