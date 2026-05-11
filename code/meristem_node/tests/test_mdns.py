"""Tests del modulo mdns (anuncio de meristem.local en LAN).

Linea respuesta a Floema dia 24: usar mDNS en lugar de IP estatica
para que Pollen pueda conectarse a `meristem.local:13000`.

Cubre:
- is_mdns_enabled() respeta env var
- get_node_name() respeta env var
- get_local_ip() devuelve IP no vacia
- MDNSAnnouncer inicializa sin tocar red (lazy)
- state_snapshot devuelve shape esperado
- start() y stop() son idempotentes
- start() registra de verdad y stop() limpia (smoke con red)

Tests con red real (start/stop) se saltan si MERISTEM_MDNS_NETWORK_TESTS
no esta seteado, para no requerir multicast en CI.
"""
from __future__ import annotations

import os

import pytest

from src.mdns import (
    MDNSAnnouncer,
    get_local_ip,
    get_node_name,
    is_mdns_enabled,
)


def test_is_mdns_enabled_default_true(monkeypatch):
    """Default sin env var = enabled."""
    monkeypatch.delenv("MERISTEM_MDNS_ENABLED", raising=False)
    assert is_mdns_enabled() is True


def test_is_mdns_enabled_false_variants(monkeypatch):
    """false / 0 / no desactivan."""
    for v in ("false", "False", "0", "no", "NO"):
        monkeypatch.setenv("MERISTEM_MDNS_ENABLED", v)
        assert is_mdns_enabled() is False, f"failed for {v!r}"


def test_is_mdns_enabled_true_variants(monkeypatch):
    """Cualquier valor que no sea false/0/no es enabled."""
    for v in ("true", "1", "yes", "anything"):
        monkeypatch.setenv("MERISTEM_MDNS_ENABLED", v)
        assert is_mdns_enabled() is True, f"failed for {v!r}"


def test_get_node_name_default(monkeypatch):
    monkeypatch.delenv("MERISTEM_NODE_NAME", raising=False)
    assert get_node_name() == "meristem"


def test_get_node_name_env_override(monkeypatch):
    monkeypatch.setenv("MERISTEM_NODE_NAME", "Meristem-cooperativa")
    # Lowercase + strip
    assert get_node_name() == "meristem-cooperativa"


def test_get_local_ip_returns_string():
    """No falla, devuelve algo. Puede ser 127.0.0.1 si no hay red."""
    ip = get_local_ip()
    assert isinstance(ip, str)
    assert len(ip) >= 7  # min '0.0.0.0'


def test_announcer_init_does_not_touch_network():
    """Constructor NO debe tocar red — solo state."""
    a = MDNSAnnouncer(node_name="test-node", port=13000)
    assert a.node_name == "test-node"
    assert a.port == 13000
    assert a.fqdn == "test-node.local"
    assert a._registered is False


def test_announcer_state_snapshot_shape():
    a = MDNSAnnouncer(node_name="meristem", port=13000)
    snap = a.state_snapshot()
    assert snap == {
        "enabled": True,
        "node_name": "meristem",
        "fqdn": "meristem.local",
        "port": 13000,
        "registered": False,
    }


def test_announcer_stop_before_start_is_noop():
    """stop() sin start() previo no debe fallar."""
    a = MDNSAnnouncer(node_name="test", port=13000)
    a.stop()  # no levanta excepcion
    assert a._registered is False


@pytest.mark.skipif(
    not os.environ.get("MERISTEM_MDNS_NETWORK_TESTS"),
    reason="Tests con multicast real desactivados; setea "
           "MERISTEM_MDNS_NETWORK_TESTS=1 para activar",
)
def test_announcer_start_stop_idempotent_with_real_zeroconf():
    """Smoke con multicast real. Saltado por defecto en CI/dev."""
    a = MDNSAnnouncer(node_name="meristem-test", port=13000)
    assert a.start() is True
    assert a._registered is True
    # Llamar start() de nuevo no debe re-anunciar
    assert a.start() is False
    a.stop()
    assert a._registered is False
    # Llamar stop() de nuevo no falla
    a.stop()
