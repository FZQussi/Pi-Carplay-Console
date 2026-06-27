import subprocess
import re

class BluetoothService:
    def get_status(self):
        try:
            result = subprocess.run(
                ["bluetoothctl", "info"],
                capture_output=True, text=True, timeout=5
            )
            output = result.stdout

            if "Device" in output:
                name_match = re.search(r"Name: (.+)", output)
                device_match = re.search(r"Device ([0-9A-F:]+)", output)
                connected_match = re.search(r"Connected: (\w+)", output)

                return {
                    "connected": connected_match.group(1) == "yes" if connected_match else False,
                    "device": name_match.group(1).strip() if name_match else "Desconhecido",
                    "address": device_match.group(1) if device_match else None
                }
            else:
                return {"connected": False, "device": None, "address": None}

        except Exception as e:
            return {"connected": False, "device": None, "error": str(e)}

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