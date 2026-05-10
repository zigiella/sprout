"""Cliente al `meristem_inference_adapter` para Meristem-nodo.

Llama al adapter en `:12000` (que reenvía al `llama-server` en `:8080`
con Gemma 4 E4B Q4_K_M) y devuelve el rationale técnico + rationale
para operador.

Loop de tool calling:
1. POST inicial con `tools` → modelo decide si llama tool
2. Si emite `tool_calls`: ejecutar tool (stub determinista) + POST
   continuación con tool_result en messages
3. Repetir hasta finish_reason="stop" o max_iterations

Errores → fallback a stub determinístico (no rompe pipeline).
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from .prompts import (
    MERISTEM_SYSTEM_PROMPT_ES,
    TOOL_DEFINITIONS,
    build_user_message,
    call_tool,
)
from .schemas import Bundle, EvaluationResult


logger = logging.getLogger(__name__)


# Configuración por defecto. Override por env si toca.
ADAPTER_URL_DEFAULT = "http://localhost:12000"
MAX_TOOL_ITERATIONS = 3
HTTP_TIMEOUT_S = 600.0  # E4B + tool calling + num_ctx grande puede tardar bastante


class LLMUnavailableError(Exception):
    """Error genérico al hablar con el adapter. Caller debe fallback."""


DEFAULT_NUM_CTX = 4096
# num_predict reducido de 1024 -> 256 tras mini-experimento dia 24
# (linea C). Reduce latencia ~53% sin perder validez del rationale: la
# regla de brevedad de Xilema limita rationale_para_operador a 240
# chars de todos modos. Override puntual via header X-Meristem-Num-Predict
# si una alerta especifica necesita mas detalle.
DEFAULT_NUM_PREDICT = 256


def _post_chat(
    adapter_url: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None,
    num_ctx: int = DEFAULT_NUM_CTX,
    num_predict: int = DEFAULT_NUM_PREDICT,
) -> dict[str, Any]:
    """POST a /api/chat del adapter. Devuelve respuesta Ollama-format.

    `num_ctx` y `num_predict` son configurables para experimentos
    (mini-experimento contexto día 23).
    """
    payload: dict[str, Any] = {
        "model": "gemma4:e4b",  # alias resuelto por config.py del adapter
        "messages": messages,
        "options": {
            "temperature": 0.3,
            "num_ctx": num_ctx,
            "num_predict": num_predict,
        },
        "stream": False,
        "think": True,  # Meristem es slow brain, thinking ON
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    try:
        with httpx.Client(timeout=HTTP_TIMEOUT_S) as client:
            r = client.post(f"{adapter_url}/api/chat", json=payload)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPError as e:
        raise LLMUnavailableError(f"adapter HTTP error: {e}") from e


def _parse_rationale_json(content: str) -> tuple[str, str] | None:
    """Extrae (rationale_tecnico, rationale_para_operador) del JSON emitido.

    El system prompt pide JSON compacto sin Markdown fences. Si llega
    con fences (modelo no respetó), recortamos defensivamente.
    """
    text = content.strip()
    if not text:
        return None
    if text.startswith("```"):
        # Recortar fence si lo hay
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace > first_brace:
            text = text[first_brace : last_brace + 1]
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return None
    # Parser tolerante: el LLM a veces traduce las keys al inglés.
    # Aceptamos variantes; preferimos castellano si están las dos.
    rt = (
        obj.get("rationale_tecnico")
        or obj.get("technical_rationale")
        or obj.get("rationaleTecnico")
        or obj.get("technicalRationale")
    )
    ro = (
        obj.get("rationale_para_operador")
        or obj.get("rationale_operador")
        or obj.get("user_friendly_rationale")
        or obj.get("operator_rationale")
        or obj.get("rationaleParaOperador")
        or obj.get("userFriendlyRationale")
    )
    if not isinstance(rt, str) or not isinstance(ro, str):
        return None
    return rt.strip(), ro.strip()


def compose_rationale_via_llm(
    bundle: Bundle,
    evaluation: EvaluationResult,
    *,
    adapter_url: str = ADAPTER_URL_DEFAULT,
    use_tools: bool = True,
    num_ctx: int = DEFAULT_NUM_CTX,
    num_predict: int = DEFAULT_NUM_PREDICT,
) -> tuple[str, str, dict[str, Any]]:
    """Devuelve (rationale_tecnico, rationale_operador, llm_metrics).

    Loop tool calling (max 3 iteraciones). Si el modelo cumple regla de
    brevedad y emite JSON limpio, parseamos y devolvemos. Si emite tool
    call, ejecutamos stub y continuamos. Si nada de esto funciona en
    3 iteraciones, raise para que caller fallback a stub.

    `llm_metrics` se persiste en `decisions.llm_metrics` para audit.
    """
    bundle_json = bundle.model_dump(mode="json")
    evaluation_json = evaluation.model_dump(mode="json")
    user_message = build_user_message(bundle_json, evaluation_json)

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": MERISTEM_SYSTEM_PROMPT_ES},
        {"role": "user", "content": user_message},
    ]
    tools = TOOL_DEFINITIONS if use_tools else None

    metrics: dict[str, Any] = {
        "tool_iterations": 0,
        "tool_calls_log": [],
        "finish_reasons": [],
    }

    for iteration in range(MAX_TOOL_ITERATIONS):
        response = _post_chat(
            adapter_url, messages, tools,
            num_ctx=num_ctx, num_predict=num_predict,
        )
        msg = (response.get("message") or {})
        content = msg.get("content") or ""
        thinking = msg.get("thinking") or ""
        tool_calls = msg.get("tool_calls") or []
        finish_reason = response.get("done_reason", "stop")

        metrics["finish_reasons"].append(finish_reason)
        metrics["tool_iterations"] = iteration + 1
        metrics[f"tokens_in_iter_{iteration}"] = response.get("prompt_eval_count")
        metrics[f"tokens_out_iter_{iteration}"] = response.get("eval_count")
        metrics[f"thinking_chars_iter_{iteration}"] = len(thinking)

        # Si emitió tool_calls, ejecutamos y continuamos.
        if tool_calls:
            assistant_msg: dict[str, Any] = {"role": "assistant"}
            if content:
                assistant_msg["content"] = content
            assistant_msg["tool_calls"] = tool_calls
            messages.append(assistant_msg)

            for tc in tool_calls:
                fn = tc.get("function") or {}
                name = fn.get("name", "")
                raw_args = fn.get("arguments", "{}")
                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except json.JSONDecodeError:
                    args = {}
                tool_result = call_tool(name, args)
                metrics["tool_calls_log"].append({"name": name, "args": args})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", ""),
                    "name": name,
                    "content": tool_result,
                })
            continue  # otro round con tool_results en el contexto

        # Sin tool_calls → modelo respondió. Intentamos parsear JSON.
        parsed = _parse_rationale_json(content)
        if parsed:
            metrics["parsed_ok"] = True
            metrics["final_content_len"] = len(content)
            return parsed[0], parsed[1], metrics

        # Si el contenido está vacío pero hay thinking (split de Gemma 4
        # vía llama.cpp), intentamos parsear el thinking.
        if not content and thinking:
            parsed_t = _parse_rationale_json(thinking)
            if parsed_t:
                metrics["parsed_from_thinking"] = True
                return parsed_t[0], parsed_t[1], metrics

        metrics["parsed_ok"] = False
        metrics["raw_content_excerpt"] = content[:300]
        break  # JSON inválido: rompemos sin reintentar (no resuelve)

    raise LLMUnavailableError(
        f"LLM no produjo JSON válido tras {metrics['tool_iterations']} iteraciones. "
        f"Último finish_reason={metrics['finish_reasons'][-1] if metrics['finish_reasons'] else '?'}"
    )


# ---------------------------------------------------------------------------
# Chat conversacional read-only (fase 3 plan IA dia 19, linea B dia 24)
# ---------------------------------------------------------------------------


def compose_chat_response(
    operator_message: str,
    conversation_history: list[dict[str, Any]] | None = None,
    *,
    adapter_url: str = ADAPTER_URL_DEFAULT,
    use_tools: bool = True,
    num_ctx: int = DEFAULT_NUM_CTX,
    num_predict: int = 512,  # respuestas chat un poco mas largas que rationale
) -> tuple[str, dict[str, Any]]:
    """Devuelve (answer_es, llm_metrics) para una pregunta del operador.

    Distinto de `compose_rationale_via_llm`:
    - Usa MERISTEM_CHAT_SYSTEM_PROMPT_ES (no el de /visit)
    - El output es texto libre en castellano (no JSON estructurado)
    - Acepta `conversation_history` (list of {role, content}) para
      continuidad
    - Incluye `evidence_refs` extraidos del texto si el modelo cito
      policy_id o decision_id

    Loop de tool calling hasta MAX_TOOL_ITERATIONS. Si LLM falla,
    raise para que caller fallback con respuesta generica.
    """
    # Import circular evitado con import local (chat usa el mismo
    # MERISTEM_CHAT_SYSTEM_PROMPT_ES que vive en prompts.py)
    from .prompts import (
        MERISTEM_CHAT_SYSTEM_PROMPT_ES,
        TOOL_DEFINITIONS,
        call_tool,
    )

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": MERISTEM_CHAT_SYSTEM_PROMPT_ES},
    ]
    if conversation_history:
        for msg in conversation_history:
            role = msg.get("role")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
    # Mensaje actual del operador
    messages.append({"role": "user", "content": operator_message})

    tools = TOOL_DEFINITIONS if use_tools else None

    metrics: dict[str, Any] = {
        "tool_iterations": 0,
        "tool_calls_log": [],
        "finish_reasons": [],
    }

    for iteration in range(MAX_TOOL_ITERATIONS):
        response = _post_chat(
            adapter_url, messages, tools,
            num_ctx=num_ctx, num_predict=num_predict,
        )
        msg = (response.get("message") or {})
        content = msg.get("content") or ""
        thinking = msg.get("thinking") or ""
        tool_calls = msg.get("tool_calls") or []
        finish_reason = response.get("done_reason", "stop")

        metrics["finish_reasons"].append(finish_reason)
        metrics["tool_iterations"] = iteration + 1
        metrics[f"tokens_in_iter_{iteration}"] = response.get("prompt_eval_count")
        metrics[f"tokens_out_iter_{iteration}"] = response.get("eval_count")
        metrics[f"thinking_chars_iter_{iteration}"] = len(thinking)

        if tool_calls:
            assistant_msg: dict[str, Any] = {"role": "assistant"}
            if content:
                assistant_msg["content"] = content
            assistant_msg["tool_calls"] = tool_calls
            messages.append(assistant_msg)

            for tc in tool_calls:
                fn = tc.get("function") or {}
                name = fn.get("name", "")
                raw_args = fn.get("arguments", "{}")
                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except json.JSONDecodeError:
                    args = {}
                tool_result = call_tool(name, args)
                metrics["tool_calls_log"].append({"name": name, "args": args})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", ""),
                    "name": name,
                    "content": tool_result,
                })
            continue  # otra ronda

        # Sin tool_calls -> respuesta del modelo
        if content:
            metrics["parsed_ok"] = True
            metrics["final_content_len"] = len(content)
            return content.strip(), metrics

        # Si content vacio pero hay thinking, usamos thinking como fallback
        if not content and thinking:
            metrics["parsed_from_thinking"] = True
            return thinking.strip(), metrics

        metrics["parsed_ok"] = False
        break

    raise LLMUnavailableError(
        f"LLM no produjo respuesta de chat tras {metrics['tool_iterations']} "
        f"iteraciones. finish_reason="
        f"{metrics['finish_reasons'][-1] if metrics['finish_reasons'] else '?'}"
    )


def extract_evidence_refs(answer: str) -> list[str]:
    """Extrae policy_id / decision_id mencionados en la respuesta del chat.

    Heuristica simple: busca patrones tipo `pkt_meristem_xxx` y
    `dec_xxx` en el texto. Si no encuentra, devuelve lista vacia.
    El operador puede verificar haciendo GET /policy/{policy_id}.
    """
    import re
    pattern = r"(pkt_meristem_[a-zA-Z0-9_]+|dec_[a-zA-Z0-9_]+)"
    matches = re.findall(pattern, answer)
    # Dedup preservando orden
    seen = set()
    out = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out
