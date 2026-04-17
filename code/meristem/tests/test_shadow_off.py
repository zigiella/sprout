"""Test negativo del sombra: con SHADOW_ENABLED=false, `google.genai` jamas
debe entrar en `sys.modules` al arrancar Meristem.

Cambium lo pidio verificable por construccion, no por inspeccion de codigo.
El test corre un subproceso Python limpio con el flag apagado, importa la
app y comprueba que los modulos de shadow (incluido `google.genai`) no se
cargan.

Nota sobre `google`: el paquete namespace `google` puede aparecer en
`sys.modules` por side-effects de otras libs (protobuf, grpcio) sin que
nada de Meristem lo haya tocado. Lo critico por seguridad es que ni
`google.genai` ni el subpaquete `src.shadow.shadow_client` se carguen.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


_MERISTEM_ROOT = Path(__file__).resolve().parents[1]
_SHARED = _MERISTEM_ROOT.parent / "shared"


def test_shadow_not_loaded_when_flag_off(tmp_path: Path) -> None:
    script = (
        "import os, sys;\n"
        "assert os.environ.get('SHADOW_ENABLED') == 'false';\n"
        "from src.main import create_app;\n"
        "from src.settings import load_settings;\n"
        "create_app(load_settings());\n"
        "forbidden = ("
        "'google.genai', "
        "'src.shadow.shadow_client', "
        "'src.shadow.compare'"
        ");\n"
        "leaked = [m for m in forbidden if m in sys.modules];\n"
        "assert not leaked, "
        "f'shadow cargado con SHADOW_ENABLED=false: {leaked}';\n"
        "print('OK')\n"
    )

    env = os.environ.copy()
    env["SHADOW_ENABLED"] = "false"
    env["DB_PATH"] = str(tmp_path / "meristem.db")
    # El subproceso debe encontrar `src` y `schemas`.
    existing_pp = env.get("PYTHONPATH", "")
    extra = os.pathsep.join(
        p for p in (str(_MERISTEM_ROOT), str(_SHARED)) if Path(p).exists()
    )
    env["PYTHONPATH"] = (
        os.pathsep.join([extra, existing_pp]) if existing_pp else extra
    )

    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(_MERISTEM_ROOT),
    )
    assert result.returncode == 0, (
        f"subproceso fallo.\nstdout={result.stdout}\nstderr={result.stderr}"
    )
    assert "OK" in result.stdout
