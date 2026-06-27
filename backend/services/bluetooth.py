import subprocess
import re

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

            if connected:
                meta = subprocess.run(
                    ["playerctl", "metadata", "--format", "{{status}}|{{artist}}|{{title}}"],
                    capture_output=True, text=True, timeout=3
                )
                if meta.returncode == 0:
                    parts = meta.stdout.strip().split("|")
                    if len(parts) == 3:
                        playing = parts[0] == "Playing"
                        artist = parts[1]
                        track = parts[2]

            return {
                "connected": connected,
                "device": name_match.group(1).strip() if name_match else None,
                "playing": playing,
                "track": track,
                "artist": artist,
            }
        except Exception as e:
            return {"connected": False, "device": None, "playing": False, "error": str(e)}