"""Serviço Bluetooth — wrapper sobre `bluetoothctl` + `playerctl`.

Sprint 9: o MAC deixou de estar hardcoded. O dispositivo é descoberto
dinamicamente (`bluetoothctl devices Connected`) e o DBus de sessão é
resolvido em runtime (ver `core/runtime.py`), em vez de assumir uid 1000.
"""

import os
import re
import subprocess

from backend.core.runtime import dbus_session_env

_MAC_RE = re.compile(r"([0-9A-Fa-f:]{17})")


def _clean_artist(artist):
    """Algumas apps (ex.: Spotify) metem texto extra no campo de artista
    da notificação, tipo "Farruko • Recomendado para ti". Fica só a
    primeira parte, antes do separador "•"."""
    if not artist:
        return artist
    return artist.split("•")[0].strip()


def parse_devices(output):
    """Parse de `bluetoothctl devices [...]` → [{mac, name}]. Pura/testável."""
    devices = []
    for line in output.splitlines():
        line = line.strip()
        m = re.match(r"Device\s+([0-9A-Fa-f:]{17})\s+(.+)", line)
        if m:
            devices.append({"mac": m.group(1), "name": m.group(2).strip()})
    return devices


class BluetoothService:
    def _run(self, *args, timeout=5):
        return subprocess.run(["bluetoothctl", *args],
                              capture_output=True, text=True, timeout=timeout)

    def _connected_mac(self):
        """MAC do dispositivo atualmente ligado, ou None."""
        try:
            out = self._run("devices", "Connected").stdout
            devs = parse_devices(out)
            if devs:
                return devs[0]["mac"]
        except Exception:
            pass
        return None

    def get_status(self):
        try:
            # `devices Connected` já devolve "Device <MAC> <Nome>" e, por
            # definição, o que aparece aqui está ligado. Isso torna o antigo
            # `bluetoothctl info <mac>` redundante — evitamos um subprocesso
            # por tick do monitor (de 3 para 2 spawns/segundo no Pi).
            connected = parse_devices(self._run("devices", "Connected").stdout)
            if not connected:
                return {"connected": False, "device": None, "playing": False,
                        "track": None, "artist": None, "duration": 0, "position": 0}
            device = connected[0]

            track = artist = None
            playing = False
            duration = position = 0

            meta = subprocess.run(
                ["playerctl", "metadata", "--format",
                 "{{status}}|{{artist}}|{{title}}|{{mpris:length}}|{{position}}"],
                capture_output=True, text=True, timeout=3,
                env=dbus_session_env(),
            )
            if meta.returncode == 0:
                parts = meta.stdout.strip().split("|")
                if len(parts) == 5:
                    playing = parts[0] == "Playing"
                    artist = _clean_artist(parts[1])
                    track = parts[2]
                    duration = int(parts[3]) if parts[3].strip().lstrip("-").isdigit() else 0
                    position = int(parts[4]) if parts[4].strip().lstrip("-").isdigit() else 0

            return {
                "connected": True,
                "device": device["name"],
                "playing": playing,
                "track": track,
                "artist": artist,
                "duration": duration,   # microssegundos
                "position": position,   # microssegundos
            }
        except Exception as e:
            return {"connected": False, "device": None, "playing": False, "error": str(e)}

    def list_devices(self):
        """Dispositivos conhecidos (emparelhados), com flag de ligado."""
        try:
            known = parse_devices(self._run("devices").stdout)
            connected_macs = {d["mac"] for d in parse_devices(self._run("devices", "Connected").stdout)}
            for d in known:
                d["connected"] = d["mac"] in connected_macs
            return {"devices": known}
        except Exception as e:
            return {"devices": [], "error": str(e)}

    def connect(self, mac):
        if not _MAC_RE.fullmatch(mac or ""):
            return {"status": "error", "error": "MAC inválido"}
        try:
            self._run("connect", mac, timeout=15)
            return {"status": "ok", "mac": mac}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def forget(self, mac):
        if not _MAC_RE.fullmatch(mac or ""):
            return {"status": "error", "error": "MAC inválido"}
        try:
            self._run("remove", mac)
            return {"status": "forgotten", "mac": mac}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def make_discoverable(self):
        try:
            self._run("discoverable", "on")
            self._run("pairable", "on")
            return {"status": "discoverable"}
        except Exception as e:
            return {"error": str(e)}

    def disconnect(self):
        try:
            self._run("disconnect")
            return {"status": "disconnected"}
        except Exception as e:
            return {"error": str(e)}
