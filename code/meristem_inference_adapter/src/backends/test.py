"""Backend `test` — mock con canned responses (punto 11 de Cambium).

Obligatorio en el primer PR para desacoplar el CI de Gemini y de Ollama real.
No hace I/O de red. Devuelve respuestas fijas con contadores plausibles y
duraciones sintetizadas desde `time.perf_counter_ns()`.

## Como funciona

- El backend se inicializa con un dict `{selector: CannedResponse}`. Si no se
  pasa ninguno, usa `DEFAULT_CANNED` que incluye tres fixtures basicos.
- El request puede seleccionar un fixture explicitamente via
  `options["test_fixture"] = "<selector>"`. Si no lo hace, se usa `"default"`.
- Si el selector pedido no existe, el backend levanta `KeyError` para que la
  mala configuracion del test sea ruidosa.

## Por que canned en vez de generado

El caller de este backend es el CI y los tests unitarios, no un usuario. La
gracia es tener respuestas bit-a-bit estables — si el formato cambiara y el
caller parseara mal, lo queremos detectar sin depender de LLMs no-deterministas.

## Inspeccion desde tests

El backend guarda el ultimo request recibido en `last_chat_request` y
`last_generate_request` para que los tests puedan hacer assertions sobre que
se envio (utiles en parity tests y en unit tests de `main.py`).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from ..headers import InferenceMetrics


@dataclass(frozen=True)
class CannedResponse:
    """Una respuesta fija para el backend test.

    Se dimensiona como lo que Gemini/Ollama devolverian: content, thinking
    opcional, y contadores de tokens (in/out/thinking). Los contadores se
    exponen tal cual en los headers y en el body Ollama-format.
    """

    model: str
    content: str
    thinking: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    thinking_tokens: int = 0


DEFAULT_CANNED: dict[str, CannedResponse] = {
    "default": CannedResponse(
        model="gemma-4-26b-a4b",
        content="ok",
        thinking="",
        tokens_in=10,
        tokens_out=2,
        thinking_tokens=0,
    ),
    "with_thinking": CannedResponse(
        model="gemma-4-26b-a4b",
        content="respuesta final",
        thinking="razonando sobre el problema y llegando a una conclusion",
        tokens_in=20,
        tokens_out=5,
        thinking_tokens=15,
    ),
    "empty": CannedResponse(
        model="gemma-4-26b-a4b",
        content="",
        thinking="",
        tokens_in=0,
        tokens_out=0,
        thinking_tokens=0,
    ),
}


def _pick_selector(request: dict[str, Any]) -> str:
    options = request.get("options") or {}
    selector = options.get("test_fixture")
    return selector if isinstance(selector, str) and selector else "default"


def _split_duration_ns(total_ns: int, tokens_in: int, tokens_out: int) -> tuple[int, int]:
    """Reparte `total_ns` entre prompt_eval y eval proporcional a tokens.

    Sin tokens (tokens_in==tokens_out==0), devuelve mitad-mitad para evitar 0
    en algun campo (que podria disparar divisions por cero en el caller).
    """
    total = tokens_in + tokens_out
    if total == 0:
        half = total_ns // 2
        return half, total_ns - half
    prompt_ns = (total_ns * tokens_in) // total
    return prompt_ns, total_ns - prompt_ns


class TestBackend:
    """Mock con respuestas predefinidas por selector.

    Implementa el Protocol `InferenceBackend` (chat + generate) sin I/O de red.
    Emite headers `Sprout-Inference-*` con `backend="test"` y `cost_eur=0.0`.
    """

    # El prefijo `Test` en el nombre hace que pytest intente recolectar esta
    # clase como test class. No es un test class. Renombrarla a `MockBackend`
    # perderia la simetria con `INFERENCE_BACKEND=test` (Cambium, punto 11).
    # `__test__ = False` es el opt-out documentado de pytest.
    __test__ = False

    def __init__(self, canned: dict[str, CannedResponse] | None = None) -> None:
        self._canned: dict[str, CannedResponse] = (
            dict(canned) if canned is not None else dict(DEFAULT_CANNED)
        )
        if "default" not in self._canned:
            raise ValueError(
                "canned debe contener al menos la clave 'default' "
                "(fallback cuando el request no especifica test_fixture)."
            )
        self.last_chat_request: dict[str, Any] | None = None
        self.last_generate_request: dict[str, Any] | None = None

    def _resolve(self, request: dict[str, Any]) -> CannedResponse:
        selector = _pick_selector(request)
        if selector not in self._canned:
            raise KeyError(
                f"canned selector {selector!r} no definido. "
                f"Disponibles: {sorted(self._canned.keys())}"
            )
        return self._canned[selector]

    async def chat(
        self, request: dict[str, Any]
    ) -> tuple[dict[str, Any], InferenceMetrics]:
        self.last_chat_request = request
        t0 = time.perf_counter_ns()
        canned = self._resolve(request)
        # El backend test no hace I/O real; el perf_counter aqui solo mide
        # overhead de dispatch. Eso esta bien: queremos duraciones pequenas
        # pero no-cero para que el caller pueda calcular tok/s sin dividir
        # por cero en pruebas.
        t1 = time.perf_counter_ns()
        total_ns = max(t1 - t0, 1_000)  # suelo de 1 microsegundo
        prompt_ns, eval_ns = _split_duration_ns(
            total_ns, canned.tokens_in, canned.tokens_out + canned.thinking_tokens
        )
        model = request.get("model", canned.model)
        body = {
            "model": model,
            "created_at": "1970-01-01T00:00:00Z",  # deterministico
            "message": {
                "role": "assistant",
                "content": canned.content,
                "thinking": canned.thinking,
            },
            "done": True,
            "done_reason": "stop",
            "prompt_eval_count": canned.tokens_in,
            # Ojo: eval_count incluye thinking, por contrato Ollama. El desglose
            # defendible va por headers (ver headers.py docstring, punto 4).
            "eval_count": canned.tokens_out + canned.thinking_tokens,
            "prompt_eval_duration": prompt_ns,
            "eval_duration": eval_ns,
            "total_duration": total_ns,
        }
        metrics = InferenceMetrics(
            backend="test",
            model=model,
            tokens_in=canned.tokens_in,
            tokens_out=canned.tokens_out,
            thinking_tokens=canned.thinking_tokens,
            duration_ms=max(total_ns // 1_000_000, 1),
            cost_eur=0.0,
        )
        return body, metrics

    async def generate(
        self, request: dict[str, Any]
    ) -> tuple[dict[str, Any], InferenceMetrics]:
        self.last_generate_request = request
        t0 = time.perf_counter_ns()
        canned = self._resolve(request)
        t1 = time.perf_counter_ns()
        total_ns = max(t1 - t0, 1_000)
        prompt_ns, eval_ns = _split_duration_ns(
            total_ns, canned.tokens_in, canned.tokens_out + canned.thinking_tokens
        )
        model = request.get("model", canned.model)
        body = {
            "model": model,
            "created_at": "1970-01-01T00:00:00Z",
            # /api/generate usa `response` en vez de `message`.
            "response": canned.content,
            "thinking": canned.thinking,
            "done": True,
            "done_reason": "stop",
            "prompt_eval_count": canned.tokens_in,
            "eval_count": canned.tokens_out + canned.thinking_tokens,
            "prompt_eval_duration": prompt_ns,
            "eval_duration": eval_ns,
            "total_duration": total_ns,
        }
        metrics = InferenceMetrics(
            backend="test",
            model=model,
            tokens_in=canned.tokens_in,
            tokens_out=canned.tokens_out,
            thinking_tokens=canned.thinking_tokens,
            duration_ms=max(total_ns // 1_000_000, 1),
            cost_eur=0.0,
        )
        return body, metrics
