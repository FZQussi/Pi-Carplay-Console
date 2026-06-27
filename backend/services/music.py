"""Serviço de música: controla a reprodução via `playerctl`.

O `playerctl` fala com o MPRIS exposto pelo telemóvel ligado por
Bluetooth (via AVRCP) — é o mesmo mecanismo que o `BluetoothService`
já usa para LER o estado (track/artist/playing). Aqui usamo-lo para
EMITIR os comandos de play/pause/next/prev.
"""

import os
import subprocess

# Mesmo D-Bus session bus usado em BluetoothService.get_status() — tem
# de ser igual, senão o playerctl não encontra o player do telemóvel.
PLAYERCTL_ENV = {**os.environ, "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus"}


class MusicService:
    """Controlos de reprodução via `playerctl`."""

    def _run(self, *args):
        try:
            result = subprocess.run(
                ["playerctl", *args],
                capture_output=True,
                text=True,
                timeout=3,
                env=PLAYERCTL_ENV,
            )
            if result.returncode != 0:
                return {"status": "error", "error": result.stderr.strip()}
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def play(self):
        return self._run("play")

    def pause(self):
        return self._run("pause")

    def next(self):
        return self._run("next")

    def prev(self):
        return self._run("previous")

    def get_current_track(self):
        """Mantido por compatibilidade com `/status`.

        O estado real (track/artist/playing) é lido pelo
        `BluetoothService` via `playerctl metadata` — este método
        existe só para o `main.py` não rebentar ao chamá-lo.
        """
        return {"playing": None, "title": None, "artist": None}