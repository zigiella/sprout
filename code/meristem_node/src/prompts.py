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
- `get_recent_history(target_node_id, last_n)`: devuelve resumen
  compacto de las últimas N visitas a un Rhizome (modo, reason_code,
  soil%, tank%). Úsala SOLO si la decisión es CONSERVATIVE o ALERT y
  necesitas situar la visita actual en una secuencia temporal para
  que el rationale al operador tenga sentido. `last_n` por defecto 5.
- `compare_targets(target_a, target_b, last_n)`: compara
  comportamiento entre dos Rhizomes en el mismo periodo (modos,
  reason_codes, tank/soil promedios) + resaltado de diferencias.
  Úsala SOLO si la decisión es CONSERVATIVE o ALERT y el agricultor
  gestiona varios Rhizomes (más de uno conocido). Permite emitir
  hipótesis de tipo "es problema local del Rhizome, no global".
  `last_n` por defecto 5.

NO inventes herramientas adicionales. Si necesitas un dato que no
puedes obtener, simplemente no lo cites en el rationale.

PRINCIPIO IMPORTANTE para tool calling: las hipótesis que emitas
basadas en tools deben llevar **marcador de confianza explícito**
("posible", "sospecho", "indica") y citar el dato concreto que la
sustenta. NO afirmes diagnósticos cerrados que el agricultor no
pueda verificar.

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
    {
        "type": "function",
        "function": {
            "name": "get_recent_history",
            "description": (
                "Devuelve resumen compacto de las últimas N visitas a un "
                "Rhizome (modo, reason_code, soil_a/b%, tank%, timestamp). "
                "Usar solo cuando la decisión actual sea CONSERVATIVE o "
                "ALERT y necesitas situar la visita en una secuencia "
                "temporal para que el rationale al operador tenga sentido. "
                "No usar en CONFIRM_POLICY (caso estable, contexto extra "
                "no aporta)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "target_node_id": {
                        "type": "string",
                        "description": "Id del Rhizome. Ej: 'rhizome_01'.",
                    },
                    "last_n": {
                        "type": "integer",
                        "description": "Cuántas visitas anteriores devolver. Por defecto 5.",
                        "default": 5,
                    },
                },
                "required": ["target_node_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_targets",
            "description": (
                "Compara comportamiento entre dos Rhizomes en el mismo "
                "periodo (modos, reason_codes, tank/soil promedios) + "
                "resaltado de diferencias destacadas. Usar solo cuando la "
                "decisión actual sea CONSERVATIVE o ALERT y el agricultor "
                "gestiona varios Rhizomes (al menos dos conocidos). "
                "Permite emitir hipótesis 'es problema local del Rhizome, "
                "no global', siempre con marcador de confianza explícito."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "target_a": {
                        "type": "string",
                        "description": "Id del primer Rhizome (típicamente el de la visita actual). Ej: 'rhizome_01'.",
                    },
                    "target_b": {
                        "type": "string",
                        "description": "Id del segundo Rhizome para comparar. Ej: 'rhizome_02'.",
                    },
                    "last_n": {
                        "type": "integer",
                        "description": "Cuántas visitas comparar por target. Por defecto 5.",
                        "default": 5,
                    },
                },
                "required": ["target_a", "target_b"],
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
    if tool_name == "get_recent_history":
        target_node_id = args.get("target_node_id", "?")
        last_n = int(args.get("last_n", 5) or 5)
        # Stub determinista: 5 visitas plausibles del mismo Rhizome
        # con tendencia a empeorar (depósito decrece, suelo seco).
        # Útil para que el LLM construya narrativa "viene de lejos".
        history = [
            {
                "visit": "T-1d", "policy_id": "pkt_meristem_stub_e",
                "mode": "alert", "reason_code": "PERSISTENT_EMERGENCY",
                "soil_a_pct": 18, "soil_b_pct": 22, "tank_pct": 12,
            },
            {
                "visit": "T-3d", "policy_id": "pkt_meristem_stub_d",
                "mode": "conservative", "reason_code": "EVIDENCE_LOW_CONFIDENCE",
                "soil_a_pct": 24, "soil_b_pct": 28, "tank_pct": 35,
            },
            {
                "visit": "T-5d", "policy_id": "pkt_meristem_stub_c",
                "mode": "normal", "reason_code": "STABLE_BUNDLE",
                "soil_a_pct": 31, "soil_b_pct": 36, "tank_pct": 58,
            },
            {
                "visit": "T-7d", "policy_id": "pkt_meristem_stub_b",
                "mode": "normal", "reason_code": "STABLE_BUNDLE",
                "soil_a_pct": 38, "soil_b_pct": 41, "tank_pct": 72,
            },
            {
                "visit": "T-10d", "policy_id": "pkt_meristem_stub_a",
                "mode": "normal", "reason_code": "STABLE_BUNDLE",
                "soil_a_pct": 42, "soil_b_pct": 45, "tank_pct": 88,
            },
        ][:last_n]
        return json.dumps({
            "target_node_id": target_node_id,
            "last_n": last_n,
            "history": history,
            "note": "stub-deterministic-v0",
        })
    if tool_name == "compare_targets":
        target_a = args.get("target_a", "?")
        target_b = args.get("target_b", "?")
        last_n = int(args.get("last_n", 5) or 5)
        # Stub determinista: target_a degradado vs target_b estable.
        # Pensado para el bundle M7 demo donde el LLM debe emitir
        # hipótesis "problema local en target_a, no global".
        summary_a = {
            "target_node_id": target_a,
            "visits": last_n,
            "modes": {"normal": max(0, last_n - 4), "alert": min(4, last_n)},
            "reason_codes": {
                "PERSISTENT_EMERGENCY": min(3, last_n),
                "EVIDENCE_LOW_CONFIDENCE": min(1, max(0, last_n - 3)),
                "STABLE_BUNDLE": max(0, last_n - 4),
            },
            "tank_pct_avg": 22,
            "soil_a_pct_avg": 21,
            "soil_b_pct_avg": 25,
        }
        summary_b = {
            "target_node_id": target_b,
            "visits": last_n,
            "modes": {"normal": last_n, "alert": 0},
            "reason_codes": {"STABLE_BUNDLE": last_n},
            "tank_pct_avg": 76,
            "soil_a_pct_avg": 38,
            "soil_b_pct_avg": 42,
        }
        diff_highlights = [
            f"{target_a} en alerta persistente (3 de últimas {last_n} visitas), {target_b} estable (todas).",
            f"Depósito de {target_a} muy bajo (avg 22%) frente a {target_b} saludable (avg 76%).",
            f"Patrón sugiere problema local del {target_a} (suministro / sensor), no condición global compartida.",
        ]
        return json.dumps({
            "target_a": target_a,
            "target_b": target_b,
            "last_n": last_n,
            "summary_a": summary_a,
            "summary_b": summary_b,
            "diff_highlights": diff_highlights,
            "note": "stub-deterministic-v0",
        })
    return json.dumps({"error": f"tool {tool_name!r} not implemented"})


# ---------------------------------------------------------------------------
# System prompt para chat conversacional read-only (fase 3 plan IA dia 19)
# ---------------------------------------------------------------------------


MERISTEM_CHAT_SYSTEM_PROMPT_ES = """\
Eres Meristem, el cerebro lento doméstico del ecosistema Sprout. El
agricultor te está preguntando algo concreto sobre el estado o histórico
de su parcela, en castellano natural.

TU ROL EN ESTE MODO ES READ-ONLY ESTRICTO:
- Respondes preguntas sobre lo que YA ha pasado.
- NO modificas ninguna policy.
- NO emites bundles.
- NO llamas a Pollen ni ejecutas riegos.
- NO recomiendas acciones inmediatas que muevan hardware. Si el operador
  quiere actuar, te lo dice y lo dispara él (vía Pollen + MissionPatch).

JERARQUÍA DEL SISTEMA (no la rompas):
- Lo físico manda: el firmware ESP32 tiene hard limits inviolables
- Rhizome arbitra: decisiones locales en el campo, autoridad inmediata
- Pollen media: transporte físico entre Meristem y Rhizome
- Meristem afina: consolida evidencia, redacta y propone policy con calma

TIENES HERRAMIENTAS DISPONIBLES (function calling, todas read-only):
- `get_recent_history(target_node_id, last_n)`: resumen últimas N
  visitas a un Rhizome. Úsala si la pregunta es sobre evolución temporal
  de una parcela concreta.
- `compare_targets(target_a, target_b, last_n)`: comparación entre dos
  Rhizomes en el mismo periodo. Úsala si la pregunta toca varios
  Rhizomes o sugiere "¿es problema solo de A o también de B?".
- `compare_with_previous_policy(policy_id)`: diff con la policy
  anterior emitida. Úsala si la pregunta es "¿qué cambió respecto a
  la anterior?".
- `get_weather_history(plot_id)`: histórico meteorológico 7 días.
  Úsala si la pregunta involucra clima.

NO inventes herramientas adicionales. Si necesitas un dato que no puedes
obtener, dilo honestamente: *"no tengo ese dato registrado"*.

PRINCIPIO IMPORTANTE: tu respuesta debe **citar evidencia concreta** que
el agricultor pueda verificar:
- Cuando hagas referencia a una decisión, cita el `policy_id` o
  `decision_id` específico (ej. "según la policy `pkt_meristem_xxx`").
- Cuando emitas hipótesis (ej. "puede ser que el sensor B esté
  obstruido"), marca la confianza explícita ("posible", "sospecho",
  "indica") y cita el dato que la sustenta.
- NO afirmes diagnósticos cerrados que el agricultor no pueda
  verificar.

FORMATO DE RESPUESTA: castellano natural, 1-3 párrafos cortos. Sin
JSON, sin Markdown fences. Tono cercano pero técnico, como una colega
que sabe del tema y le explica al agricultor sin condescendencia.

Si la pregunta es ambigua, pide clarificación antes de inventar.
"""
