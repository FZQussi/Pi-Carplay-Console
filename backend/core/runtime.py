"""Descoberta de ambiente em runtime (sem constantes hardcoded).

Antes o DBus de sessão estava fixo em `uid 1000`. Aqui descobrimo-lo a
partir de `/run/user/<uid>/bus`, preferindo um uid não-root (o utilizador
que tem o PulseAudio/MPRIS). Fora do Linux devolve o ambiente atual.
"""

from __future__ import annotations

import glob
import os

# O caminho do bus de sessão não muda durante a vida do processo, mas
# dbus_session_env() é chamado a cada tick do monitor (playerctl, 1x/s).
# Guardamos o resultado para não fazer glob+stat a /run/user/* todo o
# segundo. Só cacheamos quando encontramos um bus — assim, se o backend
# arrancar antes da sessão do utilizador, tentamos de novo no próximo tick.
_cached_bus: str | None = None


def dbus_session_env() -> dict[str, str]:
    global _cached_bus
    if _cached_bus is None:
        buses = sorted(glob.glob("/run/user/*/bus"))
        non_root = [b for b in buses if "/run/user/0/" not in b]
        chosen = non_root or buses
        if not chosen:
            return dict(os.environ)
        _cached_bus = chosen[0]
    return {**os.environ, "DBUS_SESSION_BUS_ADDRESS": f"unix:path={_cached_bus}"}
