"""Serviço de música: controla a reprodução via `playerctl`.

O `playerctl` fala com o MPRIS exposto pelo telemóvel ligado por
Bluetooth (via AVRCP) — é o mesmo mecanismo que o `BluetoothService`
já usa para LER o estado (track/artist/playing). Aqui usamo-lo para
EMITIR os comandos de play/pause/next/prev.
"""

import re
import subprocess

from backend.core.runtime import dbus_session_env

# Ordem de ciclo do repeat (MPRIS LoopStatus).
_LOOP_ORDER = ["None", "Track", "Playlist"]


class MusicService:
    """Controlos de reprodução via `playerctl` (+ volume via ALSA `amixer`)."""

    def _run(self, *args):
        try:
            result = subprocess.run(
                ["playerctl", *args],
                capture_output=True,
                text=True,
                timeout=3,
                env=dbus_session_env(),
            )
            if result.returncode != 0:
                return {"status": "error", "error": result.stderr.strip()}
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _query(self, *args):
        """Como `_run` mas devolve o stdout (string) — para LER estado
        (shuffle/loop). Devolve None se o comando falhar."""
        try:
            result = subprocess.run(
                ["playerctl", *args],
                capture_output=True,
                text=True,
                timeout=3,
                env=dbus_session_env(),
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None

    def play(self):
        return self._run("play")

    def pause(self):
        return self._run("pause")

    def next(self):
        return self._run("next")

    def prev(self):
        return self._run("previous")

    def seek(self, position_s):
        """Salta para uma posição absoluta (em segundos)."""
        return self._run("position", str(max(0, int(position_s))))

    # --- Volume (ALSA, não MPRIS) ---------------------------------------
    # Num carro o volume relevante é o da saída ALSA (Master), não o do
    # player do telemóvel. Por isso usamos `amixer`, não `playerctl volume`.
    def get_volume(self):
        try:
            result = subprocess.run(
                ["amixer", "get", "Master"],
                capture_output=True, text=True, timeout=3,
            )
            m = re.search(r"\[(\d+)%\]", result.stdout)
            return {"volume": int(m.group(1)) if m else None}
        except Exception as e:
            return {"volume": None, "error": str(e)}

    def set_volume(self, level):
        level = max(0, min(100, int(level)))
        try:
            subprocess.run(
                ["amixer", "set", "Master", f"{level}%"],
                capture_output=True, text=True, timeout=3,
            )
            return {"volume": level}
        except Exception as e:
            return {"volume": None, "error": str(e)}

    # --- Shuffle / Repeat ------------------------------------------------
    def toggle_shuffle(self):
        self._run("shuffle", "Toggle")
        return {"shuffle": self._query("shuffle") == "On"}

    def cycle_loop(self):
        """Cicla None → Track → Playlist → None."""
        current = self._query("loop") or "None"
        nxt = _LOOP_ORDER[(_LOOP_ORDER.index(current) + 1) % len(_LOOP_ORDER)] \
            if current in _LOOP_ORDER else "None"
        self._run("loop", nxt)
        return {"loop": nxt}

    def get_controls(self):
        """Estado dos controlos secundários (volume/shuffle/loop).

        Fica FORA do `/status` (e do push de 1s) de propósito: são 3
        subprocessos e mudam só por ação do utilizador. O frontend busca
        isto quando entra no ecrã de música e após cada toggle.
        """
        return {
            "volume": self.get_volume().get("volume"),
            "shuffle": self._query("shuffle") == "On",
            "loop": self._query("loop") or "None",
        }

    def get_current_track(self):
        """Mantido por compatibilidade com `/status`.

        O estado real (track/artist/playing) é lido pelo
        `BluetoothService` via `playerctl metadata` — este método
        existe só para o `main.py` não rebentar ao chamá-lo.
        """
        return {"playing": None, "title": None, "artist": None}