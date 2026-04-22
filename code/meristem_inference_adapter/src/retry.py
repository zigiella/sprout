"""Retry con backoff para 429 de Gemini (punto 5 de #46).

Obligatorio desde el primer PR, no iteracion posterior. Default: 3 reintentos
con backoff `500ms / 2s / 8s`. Si el ultimo intento falla, `UpstreamRateLimited`
se propaga y el adapter responde 503 al caller con header
`Sprout-Inference-Error: upstream_rate_limited`.

Sin esto, una rafaga del sweep de #47 o una demo en vivo explota por rate
limit del plan Gemini.

Nota: excepciones que NO son rate-limit (ej. 400 por request malformado) se
propagan sin reintento. Solo el predicado `is_rate_limit` decide que cuenta.
"""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")


class UpstreamRateLimited(Exception):
    """Se agotaron los reintentos frente a 429 del upstream."""

    def __init__(self, attempts: int, last_error: BaseException) -> None:
        super().__init__(
            f"upstream rate-limited tras {attempts} intento(s); "
            f"ultima causa: {type(last_error).__name__}: {last_error}"
        )
        self.attempts = attempts
        self.last_error = last_error


async def with_retry(
    op: Callable[[], Awaitable[T]],
    *,
    max_attempts: int,
    backoff_ms: tuple[int, ...],
    is_rate_limit: Callable[[BaseException], bool],
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> T:
    """Ejecuta `op` con reintentos frente a errores considerados rate-limit.

    Args:
        op: coroutine sin argumentos que realiza la llamada upstream.
        max_attempts: numero total de intentos (incluye el primero). Minimo 1.
        backoff_ms: duracion de espera ANTES de los reintentos 2, 3, ...
            Debe tener longitud >= `max_attempts - 1`. Si es mas larga, las
            posiciones extra se ignoran.
        is_rate_limit: predicado que decide si una excepcion cuenta como 429.
            Todo lo demas se propaga sin retry.
        sleep: inyectable para tests (por defecto `asyncio.sleep`).

    Returns:
        El resultado de `op` si algun intento tuvo exito.

    Raises:
        UpstreamRateLimited: si todos los intentos fallaron con rate-limit.
        BaseException: cualquier excepcion no-rate-limit se propaga sin retry.
        ValueError: si la configuracion es invalida.
    """
    if max_attempts < 1:
        raise ValueError(f"max_attempts debe ser >= 1, recibido {max_attempts}")
    if len(backoff_ms) < max_attempts - 1:
        raise ValueError(
            f"backoff_ms debe tener al menos {max_attempts - 1} valores "
            f"para max_attempts={max_attempts}, recibido {len(backoff_ms)}"
        )

    last_error: BaseException | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await op()
        except BaseException as exc:  # noqa: BLE001 — predicado decide
            if not is_rate_limit(exc):
                raise
            last_error = exc
            if attempt >= max_attempts:
                break
            # Esperar backoff_ms[attempt-1] antes del siguiente intento.
            wait_s = backoff_ms[attempt - 1] / 1000.0
            await sleep(wait_s)

    # Si llegamos aqui, todos los intentos fueron rate-limit.
    assert last_error is not None  # invariante: entramos en except al menos 1 vez
    raise UpstreamRateLimited(attempts=max_attempts, last_error=last_error)
