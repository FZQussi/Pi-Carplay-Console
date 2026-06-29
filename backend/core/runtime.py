"""Descoberta de ambiente em runtime (sem constantes hardcoded).

Antes o DBus de sessão estava fixo em `uid 1000`. Aqui descobrimo-lo a
partir de `/run/user/<uid>/bus`, preferindo um uid não-root (o utilizador
que tem o PulseAudio/MPRIS). Fora do Linux devolve o ambiente atual.
"""

from __future__ import annotations

import glob
import os
from pathlib import Path


def dbus_session_env() -> dict[str, str]:
    buses = sorted(glob.glob("/run/user/*/bus"))
    non_root = [b for b in buses if "/run/user/0/" not in b]
    chosen = non_root or buses
    if chosen:
        return {**os.environ, "DBUS_SESSION_BUS_ADDRESS": f"unix:path={chosen[0]}"}
    return dict(os.environ)


def gui_env() -> dict[str, str]:
    """Ambiente para lançar uma app GUI (cliente X) a partir do serviço.
    Precisa do DISPLAY (e do XAUTHORITY) da sessão do kiosk."""
    env = dict(os.environ)
    env.setdefault("DISPLAY", ":0")
    xauth = Path.home() / ".Xauthority"
    if xauth.exists():
        env.setdefault("XAUTHORITY", str(xauth))
    return env
