"""Backends del adapter.

Un backend implementa el Protocol `InferenceBackend` (ver `base.py`) y encapsula
el reenvio al upstream (Gemini / Ollama real / mock).

El selector vive en `main.py` y lee `INFERENCE_BACKEND` de Settings.
"""
