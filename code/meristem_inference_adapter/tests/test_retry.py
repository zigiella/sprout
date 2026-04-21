"""Tests de `retry.with_retry` — punto 5 de #46.

Verifica:
- Exito en 1er intento no espera ni reintenta.
- Rate-limit en primeros intentos + exito final → devuelve resultado.
- Agotar intentos → UpstreamRateLimited.
- Excepcion no-rate-limit se propaga sin retry.
- Sleep inyectable: verifica la secuencia exacta de waits.
- Config invalida rechazada.
"""

from __future__ import annotations

import pytest

from src.retry import UpstreamRateLimited, with_retry


class _FakeRateLimit(Exception):
    pass


class _FakeServerError(Exception):
    pass


def _is_rl(exc: BaseException) -> bool:
    return isinstance(exc, _FakeRateLimit)


async def _always_ok():
    return "ok"


def _make_flaky(fail_times: int, then: str = "ok"):
    """Op que falla con _FakeRateLimit `fail_times` veces, luego devuelve `then`."""
    state = {"n": 0}

    async def op():
        state["n"] += 1
        if state["n"] <= fail_times:
            raise _FakeRateLimit(f"attempt {state['n']}")
        return then

    return op, state


class _SleepRecorder:
    def __init__(self) -> None:
        self.waits: list[float] = []

    async def __call__(self, seconds: float) -> None:
        self.waits.append(seconds)


@pytest.mark.asyncio
async def test_exito_primer_intento_no_espera():
    sleep = _SleepRecorder()
    result = await with_retry(
        _always_ok,
        max_attempts=3,
        backoff_ms=(500, 2000),
        is_rate_limit=_is_rl,
        sleep=sleep,
    )
    assert result == "ok"
    assert sleep.waits == []


@pytest.mark.asyncio
async def test_reintentos_con_backoff_exacto():
    op, state = _make_flaky(fail_times=2, then="final")
    sleep = _SleepRecorder()
    result = await with_retry(
        op,
        max_attempts=3,
        backoff_ms=(500, 2000),
        is_rate_limit=_is_rl,
        sleep=sleep,
    )
    assert result == "final"
    assert state["n"] == 3
    # Espero 500ms antes del 2o intento, 2000ms antes del 3er intento.
    assert sleep.waits == [0.5, 2.0]


@pytest.mark.asyncio
async def test_agotar_intentos_levanta_upstream_rate_limited():
    op, state = _make_flaky(fail_times=10)  # nunca tiene exito
    sleep = _SleepRecorder()
    with pytest.raises(UpstreamRateLimited) as ei:
        await with_retry(
            op,
            max_attempts=3,
            backoff_ms=(500, 2000, 8000),
            is_rate_limit=_is_rl,
            sleep=sleep,
        )
    assert ei.value.attempts == 3
    assert isinstance(ei.value.last_error, _FakeRateLimit)
    assert state["n"] == 3
    # 3 intentos ⇒ 2 esperas entre ellos. El backoff[2]=8000 no se consume.
    assert sleep.waits == [0.5, 2.0]


@pytest.mark.asyncio
async def test_default_de_46_tres_intentos_500_2000_8000():
    # Valores del comentario tecnico de #46.
    op, state = _make_flaky(fail_times=99)
    sleep = _SleepRecorder()
    with pytest.raises(UpstreamRateLimited):
        await with_retry(
            op,
            max_attempts=3,
            backoff_ms=(500, 2000, 8000),
            is_rate_limit=_is_rl,
            sleep=sleep,
        )
    assert state["n"] == 3
    assert sleep.waits == [0.5, 2.0]


@pytest.mark.asyncio
async def test_no_rate_limit_se_propaga_sin_retry():
    state = {"n": 0}

    async def op():
        state["n"] += 1
        raise _FakeServerError("boom")

    sleep = _SleepRecorder()
    with pytest.raises(_FakeServerError):
        await with_retry(
            op,
            max_attempts=3,
            backoff_ms=(500, 2000),
            is_rate_limit=_is_rl,
            sleep=sleep,
        )
    assert state["n"] == 1  # solo 1 intento
    assert sleep.waits == []


@pytest.mark.asyncio
async def test_max_attempts_cero_rechazado():
    with pytest.raises(ValueError, match="max_attempts"):
        await with_retry(
            _always_ok,
            max_attempts=0,
            backoff_ms=(),
            is_rate_limit=_is_rl,
        )


@pytest.mark.asyncio
async def test_backoff_demasiado_corto_rechazado():
    with pytest.raises(ValueError, match="backoff_ms"):
        await with_retry(
            _always_ok,
            max_attempts=3,
            backoff_ms=(500,),  # deberia tener al menos 2
            is_rate_limit=_is_rl,
        )


@pytest.mark.asyncio
async def test_max_attempts_uno_sin_reintentos():
    op, state = _make_flaky(fail_times=99)
    sleep = _SleepRecorder()
    with pytest.raises(UpstreamRateLimited) as ei:
        await with_retry(
            op,
            max_attempts=1,
            backoff_ms=(),
            is_rate_limit=_is_rl,
            sleep=sleep,
        )
    assert ei.value.attempts == 1
    assert state["n"] == 1
    assert sleep.waits == []
