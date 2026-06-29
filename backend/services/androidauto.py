"""Android Auto (OpenAuto) — projeta o telemóvel Android no Pi.

O objetivo: metes a rota no Google Maps no telemóvel e vês/navegas no ecrã
do carro. O telemóvel liga por USB em modo Android Auto; o Pi corre o
OpenAuto (`autoapp`), que é uma *head unit* Android Auto e abre uma janela
de ecrã inteiro por cima do kiosk.

REQUER HARDWARE + BUILD: OpenAuto compilado no Pi (ver
`scripts/android-auto/install-openauto.sh`) e um telemóvel Android ligado
por USB. Fora do Pi (ou sem o binário), `available()` é False e o `start()`
devolve um erro explicativo — nada rebenta.
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
from pathlib import Path

from backend.core.runtime import gui_env

# Sítios onde o binário do OpenAuto costuma ficar após o build/instalação.
OPENAUTO_CANDIDATES = [
    "/usr/local/bin/autoapp",
    str(Path.home() / "openauto" / "build" / "autoapp"),
    "/opt/openauto/bin/autoapp",
]


def _binary() -> str | None:
    for candidate in OPENAUTO_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    return shutil.which("autoapp")


class AndroidAutoService:
    def __init__(self) -> None:
        self._proc: subprocess.Popen | None = None

    def available(self) -> bool:
        return _binary() is not None

    def _running(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def status(self) -> dict:
        return {"available": self.available(), "running": self._running()}

    def start(self) -> dict:
        binary = _binary()
        if not binary:
            return {"status": "error",
                    "error": "OpenAuto não instalado — ver scripts/android-auto/"}
        if self._running():
            return {"status": "ok", "running": True}
        try:
            self._proc = subprocess.Popen([binary], env=gui_env())
            return {"status": "ok", "running": True}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def stop(self) -> dict:
        if self._running():
            try:
                self._proc.send_signal(signal.SIGTERM)
                self._proc.wait(timeout=5)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
        self._proc = None
        return {"status": "ok", "running": False}
