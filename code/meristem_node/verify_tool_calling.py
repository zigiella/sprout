"""Verifica que llama-server con Gemma 4 soporta tool calling vía OpenAI-compat.

Tool calling es la pieza estratégica para el Special Technology Track de
llama.cpp del Hackathon Gemma 4 Good ($10k):
- Para validar candidatura en function calling explícito (pieza B3)
- Para mostrar dominio del modelo, no solo uso de texto

Test: define una herramienta `get_weather_history(plot)` y le pedimos
al modelo que decida si necesita llamarla. Si emite `tool_calls` en la
respuesta con el formato OpenAI esperado, tool calling funciona. Si no,
descartamos la pieza B3 limpiamente.

Uso:
    python verify_tool_calling.py
"""

import json
import sys

import httpx

LLAMA_SERVER = "http://127.0.0.1:8080"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather_history",
            "description": (
                "Devuelve el histórico de precipitaciones (mm) y "
                "temperaturas medias (°C) de la última semana para una "
                "parcela concreta de Sprout."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "plot_id": {
                        "type": "string",
                        "description": "Id de la parcela. Ej: 'plot-A'.",
                    }
                },
                "required": ["plot_id"],
            },
        },
    }
]


def main() -> int:
    payload = {
        "model": "gemma-4-E2B-it",  # el cargado actualmente
        "messages": [
            {
                "role": "system",
                "content": (
                    "Eres Meristem, el agente slow brain de Sprout. "
                    "Si necesitas datos meteorológicos históricos para "
                    "evaluar una policy, llama a la herramienta "
                    "get_weather_history. Si no los necesitas, responde "
                    "directo en JSON."
                ),
            },
            {
                "role": "user",
                "content": (
                    "He recibido un bundle de la parcela A. Para decidir "
                    "si la policy activa sigue siendo apropiada, ¿puedes "
                    "consultar el histórico de la última semana?"
                ),
            },
        ],
        "tools": TOOLS,
        "tool_choice": "auto",
        "max_tokens": 500,
        "temperature": 0.3,
        "stream": False,
    }

    print(f"POST {LLAMA_SERVER}/v1/chat/completions con tools array")
    try:
        r = httpx.post(
            f"{LLAMA_SERVER}/v1/chat/completions",
            json=payload,
            timeout=120.0,
        )
        r.raise_for_status()
    except httpx.HTTPError as e:
        print(f"FALLO HTTP: {e}")
        return 1

    data = r.json()
    print()
    print("=== RESPUESTA ===")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
    print()

    choices = data.get("choices") or []
    if not choices:
        print("FAIL: no choices en respuesta")
        return 2

    msg = choices[0].get("message") or {}
    finish = choices[0].get("finish_reason")
    tool_calls = msg.get("tool_calls")

    print(f"finish_reason: {finish}")
    print(f"message.content: {msg.get('content', '')[:200]!r}")
    print(f"message.tool_calls: {tool_calls}")
    print()

    if tool_calls:
        print("✅ PASS: el modelo emitió tool_calls.")
        print("    Tool calling con Gemma 4 + llama-server FUNCIONA.")
        print("    Pieza B3 (tool calling) entra al alcance Meristem-nodo.")
        return 0
    else:
        print("⚠️  AMBIGUO: no hay tool_calls explícitos.")
        print("    Posibilidades:")
        print("    - El modelo respondió texto en vez de llamar tool")
        print("    - El binding de llama-server no traduce el formato de Gemma 4")
        print("    - Hay que afinar el prompt/temperature")
        print("    Revisar response completa antes de descartar.")
        return 3


if __name__ == "__main__":
    sys.exit(main())
