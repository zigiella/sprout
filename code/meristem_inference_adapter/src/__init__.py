"""meristem_inference_adapter — proxy Ollama-compatible.

Expone :11434 con contrato Ollama y reenvia a Gemini API (cloud), Ollama real
en :11435 (local) o a un mock con canned responses (test).

Ver README.md para contratos y puntos 1-11 de los criterios tecnicos de #46.
"""
