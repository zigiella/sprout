"""System prompt + tool definitions de Meristem-nodo.

El prompt vive aquí (no en `code/tuning/system_prompts.yaml`) porque
es prompt de **producción** del Meristem-nodo. El yaml de tuning es
para experimentos. Cuando cerremos prompt v1 definitivo (post-Jetson
+ post-Xilema), se sincroniza si Xilema lo pide.

Origen: `code/meristem_node/draft_system_prompt_meristem_es.md`
(borrador día 14 + ajustes día 15) con barandilla `HARD_LIMIT_DOMAIN`,
4 reglas obligatorias, sobre común JSON, regla de brevedad de Xilema.
"""

from __future__ import annotations

import json
from typing import Any


# ---------------------------------------------------------------------------
# System prompt único Meristem-nodo (castellano, thinking ON, tool calling)
# ---------------------------------------------------------------------------

MERISTEM_SYSTEM_PROMPT_ES = """\
Eres Meristem, el cerebro lento doméstico del ecosistema Sprout. Vives
en un portátil casero del agricultor o de la cooperativa, no en data
center, no en hardware especializado. Tu trabajo es slow brain: redactar
una explicación clara para el operador a partir de los datos que Pollen
ha traído de la última visita a Rhizome y de la decisión que el
Evaluator ya ha tomado.

Jerarquía explícita del sistema (no la rompas nunca):
- Lo físico manda: el firmware ESP32 tiene hard limits inviolables
- Rhizome arbitra: decisiones locales en el campo, autoridad inmediata
- Pollen media: transporte físico entre Meristem y Rhizome
- Meristem afina: consolida evidencia, redacta y propone policy con calma

CONTEXTO DE TU TURNO. Recibes:
1. Un bundle (snapshot Rhizome + decision_receipts + weather_digest +
   validation_stamps) que Pollen acaba de traer.
2. Una decisión ya tomada por el Evaluator determinístico
   (CONFIRM_POLICY / CONSERVATIVE_POLICY / ALERT_POLICY / REFUSE) con
   reason_code y rationale_seed.

TU TAREA es ÚNICA: producir dos textos cortos en castellano que
expliquen la decisión:
- `rationale_tecnico`: 1-3 frases factuales con datos concretos del
  bundle. Para auditoría y trazabilidad.
- `rationale_para_operador`: 1-2 frases amables (máximo 240 caracteres)
  que el agricultor verá en su portátil. Sin jerga, sin alarmismo
  innecesario, sin disculpas. Cuenta lo que ves y por qué la policy
  nueva.

NO decides. La acción ya está fijada por el Evaluator. Tu redacción
NO debe contradecir la decisión, ni introducir matices que la
relativicen. Si el Evaluator dijo ALERT, el operador ve ALERT.

TIENES HERRAMIENTAS DISPONIBLES (function calling):
- `get_weather_history(plot_id)`: devuelve histórico meteorológico de
  los últimos 7 días para una parcela. Úsala SOLO si el bundle no
  incluye weather_digest reciente y la decisión depende del clima.
- `compare_with_previous_policy(policy_id)`: devuelve diff con la
  última policy emitida. Úsala SOLO si el operador podría querer
  saber qué cambió respecto a la anterior.

NO inventes herramientas adicionales. Si necesitas un dato que no
puedes obtener, simplemente no lo cites en el rationale.

BARANDILLA DE SEGURIDAD CRÍTICA (sólo si llegas a ver un caso REFUSE).
Si el bundle pidió relajar un hard limit (tank_minimum_pct, max_seconds_per_event,
alert_latched_persists_until) y el Evaluator decidió REFUSE con reason_code
HARD_LIMIT_DOMAIN, tu rationale debe **explicar al operador** que ese
límite es jurisdicción del firmware físico, no de Meristem. El
mensaje al operador es claro y sin disculpas: la frontera física
manda. Lo mismo si reason_code es JURISDICTION_POLLEN: cambios
puntuales se hacen vía Pollen + MissionPatch, no aquí.

FORMATO DE SALIDA ESTRICTO. Devuelve un único objeto JSON compacto
con esta forma:

{"rationale_tecnico": "...", "rationale_para_operador": "..."}

Sin Markdown fences, sin texto fuera del JSON, sin análisis previo.
Cierra el objeto JSON y termina inmediatamente."""


# ---------------------------------------------------------------------------
# Tool definitions (formato OpenAI / llama-server compatible)
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_weather_history",
            "description": (
                "Devuelve el histórico meteorológico (precipitaciones mm + "
                "temperatura media °C) de los últimos 7 días para una "
                "parcela concreta de Sprout. Usar solo si el bundle no "
                "incluye weather_digest reciente y la decisión depende "
                "del clima."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "plot_id": {
                        "type": "string",
                        "description": "Id de la parcela. Ej: 'plot-A', 'plot-B'.",
                    }
                },
                "required": ["plot_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_with_previous_policy",
            "description": (
                "Devuelve el diff entre la policy especificada y la anterior "
                "policy emitida para el mismo nodo Rhizome. Usar solo si el "
                "operador querría saber explícitamente qué cambió."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "policy_id": {
                        "type": "string",
                        "description": "Id de la policy actual.",
                    }
                },
                "required": ["policy_id"],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def build_user_message(bundle_json: dict[str, Any], evaluation_json: dict[str, Any]) -> str:
    """Construye el user message con bundle resumido + decisión del Evaluator.

    Mantenemos el bundle al alcance del modelo pero ya con la decisión
    determinística pre-resuelta. Eso evita que el modelo intente decidir
    (y elimina riesgo de drift).
    """
    return (
        "BUNDLE RECIBIDO:\n"
        f"{json.dumps(bundle_json, indent=2, ensure_ascii=False)}\n\n"
        "DECISIÓN DEL EVALUATOR (ya tomada, no la cuestiones):\n"
        f"{json.dumps(evaluation_json, indent=2, ensure_ascii=False)}\n\n"
        "Tu tarea: emitir el JSON con rationale_tecnico + "
        "rationale_para_operador. Solo eso."
    )


# ---------------------------------------------------------------------------
# Stub tool implementations (para v0 demo)
# ---------------------------------------------------------------------------


def call_tool(tool_name: str, args: dict[str, Any]) -> str:
    """Ejecuta una tool stub y devuelve el resultado como string JSON.

    En v0, las tools son stubs deterministas con datos plausibles. Para
    demo en directo eso basta. Post-demo se conectan a fuentes reales
    (servicio meteo + tabla de policies).
    """
    if tool_name == "get_weather_history":
        plot_id = args.get("plot_id", "?")
        return json.dumps({
            "plot_id": plot_id,
            "days": 7,
            "rain_mm_total": 4.2,
            "temp_avg_c": 18.5,
            "rain_distribution": [0.0, 0.0, 1.2, 0.5, 0.0, 2.5, 0.0],
            "note": "stub-deterministic-v0",
        })
    if tool_name == "compare_with_previous_policy":
        policy_id = args.get("policy_id", "?")
        return json.dumps({
            "current_policy_id": policy_id,
            "previous_policy_id": "pkt_meristem_previous_stub",
            "diff": {
                "mode_default": {"from": "normal", "to": "conservative"},
                "soil_dry_threshold_pct_bump": {"from": 0, "to": 5},
            },
            "note": "stub-deterministic-v0",
        })
    return json.dumps({"error": f"tool {tool_name!r} not implemented"})
