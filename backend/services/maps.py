"""Mapas — abre o Google Maps (site real) numa janela Chromium própria.

A `maps.google.com` recusa ser embebida (X-Frame-Options), por isso em vez
de um iframe lançamos uma janela Chromium dedicada por cima do dashboard.
Modelado em `androidauto.py`: lança um subprocesso GUI com o DISPLAY da
sessão, segue o `Popen` para garantir instância única, e usa o `wmctrl`
para levantar/baixar a janela.

REQUER um window manager na sessão do kiosk (ver `scripts/kiosk/`): sem WM
não há stacking entre janelas. Fora do Pi (sem chromium/wmctrl) `available()`
é False e nada rebenta.
"""

from __future__ import annotations

import shutil
import subprocess

from backend.core.runtime import gui_env

MAPS_URL = "https://www.google.com/maps"

# Classes WM estáveis para o wmctrl distinguir as janelas. A do dashboard
# tem de bater certo com a passada ao chromium no script do kiosk.
DASH_CLASS = "aveoos-dash"
MAPS_CLASS = "aveoos-maps"

# Altura da barra de topo do dashboard (px). A janela do Maps arranca por
# baixo dela para a barra ficar sempre visível e tocável (é onde mora o
# botão "Voltar ao painel").
# ponytail: barra/geometria é um botão de calibração — afinar no Pi.
BAR_H = 48


def _chromium() -> str | None:
    return shutil.which("chromium") or shutil.which("chromium-browser")


class MapsService:
    def __init__(self) -> None:
        self._proc: subprocess.Popen | None = None

    def available(self) -> bool:
        return _chromium() is not None

    def _running(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def _raise(self, wm_class: str) -> None:
        """Levanta a janela pela classe WM. Silencioso se o wmctrl faltar."""
        if shutil.which("wmctrl"):
            subprocess.run(["wmctrl", "-x", "-a", wm_class],
                           env=gui_env(), capture_output=True, timeout=5)

    def status(self) -> dict:
        return {"available": self.available(), "open": self._running()}

    def open(self) -> dict:
        binary = _chromium()
        if not binary:
            return {"status": "error", "error": "chromium não instalado"}
        if self._running():
            self._raise(MAPS_CLASS)          # instância única: só levanta
            return {"status": "ok", "open": True}
        try:
            self._proc = subprocess.Popen(
                [binary,
                 f"--app={MAPS_URL}",
                 f"--class={MAPS_CLASS}",
                 f"--window-position=0,{BAR_H}",
                 "--noerrdialogs", "--disable-infobars"],
                env=gui_env(),
            )
            self._raise(MAPS_CLASS)
            return {"status": "ok", "open": True}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def hide(self) -> dict:
        """Volta ao dashboard sem fechar o Maps (só levanta o dashboard)."""
        self._raise(DASH_CLASS)
        return {"status": "ok", "open": self._running()}
