"""Meristem sombra.

Validacion de desarrollo contra Gemma 4 31B via Google AI Studio. **Nunca
en produccion ni en el demo grabado.**

Reglas duras (docs/12_meristem_spec.md §2.4):
- Vive detras de SHADOW_ENABLED=false por defecto.
- Requiere GEMINI_API_KEY para funcionar.
- El codigo vive aislado en este subpaquete.

Este `__init__` esta intencionadamente vacio. Importar `meristem.src.shadow`
no debe tirar de `google.genai`. El import se hace explicito al importar
`meristem.src.shadow.shadow_client`, que a su vez solo se importa cuando
`SHADOW_ENABLED=true` (ver `src/main.py`).
"""
