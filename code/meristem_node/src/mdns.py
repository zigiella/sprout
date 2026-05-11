"""Anuncio mDNS del Meristem-node en la red local.

Permite que Pollen Android (u otros clientes en la misma LAN)
descubran al Meristem por nombre `meristem.local` en lugar de tener
que conocer la IP estática del portátil del agricultor.

Servicio anunciado:
- Tipo: `_http._tcp.local.`
- Nombre: `<MERISTEM_NODE_NAME>._http._tcp.local.` (default `meristem`)
- Puerto: el del Meristem-node (`MERISTEM_NODE_PORT`, default 13000)
- TXT properties: `version`, `service`, `meristem_id`

Lifecycle vía FastAPI lifespan:
- `startup`: registrar servicio + anunciar en multicast 224.0.0.251:5353
- `shutdown`: desregistrar + cerrar Zeroconf instance

Si `MERISTEM_MDNS_ENABLED=false`, todo este modulo es no-op (devuelve
None de `start`). Util para tests + entornos sin multicast.
"""
from __future__ import annotations

import logging
import os
import socket
from typing import Any

logger = logging.getLogger(__name__)


def is_mdns_enabled() -> bool:
    return os.environ.get("MERISTEM_MDNS_ENABLED", "true").lower() not in (
        "false", "0", "no",
    )


def get_node_name() -> str:
    """Nombre del servicio en mDNS, sin sufijo `.local`.

    Por defecto `meristem`, configurable via `MERISTEM_NODE_NAME`.
    """
    return os.environ.get("MERISTEM_NODE_NAME", "meristem").strip().lower()


def get_local_ip() -> str:
    """Devuelve la IP local de la interfaz que sale a internet.

    Truco: abre socket UDP no conectado a 8.8.8.8 (no envía datos)
    para que el OS resuelva la interfaz de salida y nos diga su IP.
    No requiere DNS ni conexión real.

    Si no hay red, devuelve `127.0.0.1` como fallback.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


class MDNSAnnouncer:
    """Wrapper en torno a `zeroconf.Zeroconf` con lifecycle simple.

    Diseño explícito: no levanta el servicio en el constructor; solo
    al llamar `start()`. Esto permite tests que crean el announcer
    sin tocar la red.
    """

    def __init__(
        self,
        node_name: str,
        port: int,
        meristem_id: str = "meristem_demo_01",
        version: str = "0.1.0",
    ) -> None:
        self.node_name = node_name
        self.port = port
        self.meristem_id = meristem_id
        self.version = version
        self._zeroconf: Any = None
        self._service_info: Any = None
        self._registered: bool = False

    @property
    def fqdn(self) -> str:
        """Nombre completo `meristem.local` (con punto final omitido)."""
        return f"{self.node_name}.local"

    def state_snapshot(self) -> dict[str, Any]:
        """Snapshot serializable para `/health` endpoint."""
        return {
            "enabled": True,
            "node_name": self.node_name,
            "fqdn": self.fqdn,
            "port": self.port,
            "registered": self._registered,
        }

    def start(self) -> bool:
        """Registra el servicio mDNS en multicast. Idempotente.

        Returns True si registró nuevo servicio, False si ya estaba.
        """
        if self._registered:
            return False
        # Import local: si zeroconf no está instalado, fallar al
        # llamar start() es mejor que en import time.
        from zeroconf import ServiceInfo, Zeroconf

        ip = get_local_ip()
        info = ServiceInfo(
            type_="_http._tcp.local.",
            name=f"{self.node_name}._http._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=self.port,
            properties={
                "version": self.version,
                "service": "meristem-node",
                "meristem_id": self.meristem_id,
            },
            server=f"{self.node_name}.local.",
        )
        zc = Zeroconf()
        zc.register_service(info)
        self._zeroconf = zc
        self._service_info = info
        self._registered = True
        logger.info(
            "mDNS announced as %s.local (port=%d, ip=%s)",
            self.node_name, self.port, ip,
        )
        return True

    def stop(self) -> None:
        """Desregistra y cierra Zeroconf. Idempotente."""
        if not self._registered:
            return
        try:
            if self._zeroconf is not None and self._service_info is not None:
                self._zeroconf.unregister_service(self._service_info)
                self._zeroconf.close()
        except Exception as e:
            logger.warning("Error parando mDNS: %s", e)
        finally:
            self._zeroconf = None
            self._service_info = None
            self._registered = False
            logger.info("mDNS deregistered")
