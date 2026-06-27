import subprocess
import re
import os


def _clean_artist(artist):
    """Algumas apps (ex.: Spotify) metem texto extra no campo de artista
    da notificação, tipo "Farruko • Recomendado para ti". Fica só a
    primeira parte, antes do separador "•"."""
    if not artist:
        return artist
    return artist.split("•")[0].strip()


class BluetoothService:
    def get_status(self):
        try:
            result = subprocess.run(
                ["bluetoothctl", "info", "14:49:D4:7F:2A:18"],
                capture_output=True, text=True, timeout=5
            )
            connected = "Connected: yes" in result.stdout
            name_match = re.search(r"Name: (.+)", result.stdout)

            track = None
            artist = None
            playing = False
            duration = 0
            position = 0

            if connected:
                meta = subprocess.run(
                    ["playerctl", "metadata", "--format",
                     "{{status}}|{{artist}}|{{title}}|{{mpris:length}}|{{position}}"],
                    capture_output=True, text=True, timeout=3,
                    env={**os.environ, "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus"}
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
                "connected": connected,
                "device": name_match.group(1).strip() if name_match else None,
                "playing": playing,
                "track": track,
                "artist": artist,
                "duration": duration,   # microssegundos
                "position": position,   # microssegundos
            }
        except Exception as e:
            return {"connected": False, "device": None, "playing": False, "error": str(e)}

    def make_discoverable(self):
        try:
            subprocess.run(["bluetoothctl", "discoverable", "on"], timeout=5)
            subprocess.run(["bluetoothctl", "pairable", "on"], timeout=5)
            return {"status": "discoverable"}
        except Exception as e:
            return {"error": str(e)}

    def disconnect(self):
        try:
            subprocess.run(["bluetoothctl", "disconnect"], timeout=5)
            return {"status": "disconnected"}
        except Exception as e:
            return {"error": str(e)}