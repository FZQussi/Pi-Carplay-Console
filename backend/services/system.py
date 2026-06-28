"""Serviço de sistema: saúde do Raspberry Pi.

Lê temperatura do CPU, throttling/undervoltage, uptime e armazenamento.
Tudo degrada graciosamente fora do Pi (dev em Windows/macOS): os valores
ficam `None` e nenhuma exceção sobe — o frontend simplesmente não mostra
o que não existe.
"""

import shutil
import subprocess
import time
from pathlib import Path

# Temperatura do CPU em milicelsius. Leitura de ficheiro (barata, sem
# subprocess) — pode ser lida a cada tick do monitor sem pesar.
_THERMAL = Path("/sys/class/thermal/thermal_zone0/temp")

# Bits de `vcgencmd get_throttled`. Doc oficial:
# https://www.raspberrypi.com/documentation/computers/os.html#get_throttled
_UNDERVOLT_NOW = 0x1
_THROTTLED_NOW = 0x4

# Acima desta temperatura o Pi 4 começa a fazer throttle térmico.
_TEMP_WARN_C = 80

# `vcgencmd` é um subprocess; não vale a pena corrê-lo a cada segundo.
# Um cache curto chega de sobra para um aviso de undervoltage/throttle.
_THROTTLE_TTL_S = 10


class SystemService:
    """Saúde do Pi. Métodos individuais para o endpoint detalhado; o
    `get_status()` devolve o bloco compacto usado no push em tempo real."""

    def __init__(self) -> None:
        self._throttle_cache: dict | None = None
        self._throttle_ts = 0.0

    def get_cpu_temp(self) -> float | None:
        """Temperatura do CPU em °C, ou None fora do Pi."""
        try:
            return round(int(_THERMAL.read_text()) / 1000, 1)
        except Exception:
            return None

    def _read_throttled(self) -> dict | None:
        """Lê os bits de throttle/undervoltage via vcgencmd (subprocess)."""
        try:
            out = subprocess.run(
                ["vcgencmd", "get_throttled"],
                capture_output=True, text=True, timeout=3,
            ).stdout.strip()
            value = int(out.split("=")[1], 16)  # ex.: "throttled=0x50000"
            return {
                "undervoltage": bool(value & _UNDERVOLT_NOW),
                "throttled": bool(value & _THROTTLED_NOW),
            }
        except Exception:
            return None

    def get_throttled(self) -> dict | None:
        """Estado de throttle/undervoltage, com cache curto (TTL)."""
        now = time.monotonic()
        if self._throttle_cache is None or now - self._throttle_ts > _THROTTLE_TTL_S:
            self._throttle_cache = self._read_throttled()
            self._throttle_ts = now
        return self._throttle_cache

    def get_uptime(self) -> int | None:
        """Uptime em segundos, ou None fora do Linux."""
        try:
            return int(float(Path("/proc/uptime").read_text().split()[0]))
        except Exception:
            return None

    def get_storage(self) -> float | None:
        """Uso do disco da raiz em percentagem, ou None se indisponível."""
        try:
            total, used, _ = shutil.disk_usage("/")
            return round(used / total * 100, 1)
        except Exception:
            return None

    def get_status(self) -> dict:
        """Bloco compacto para o push em tempo real (barra de topo).

        Inclui um `warning` agregado ("undervoltage" | "throttled" | None)
        para o frontend mostrar um aviso sem ter de interpretar bits.
        """
        temp = self.get_cpu_temp()
        throttled = self.get_throttled() or {}
        warning = None
        if throttled.get("undervoltage"):
            warning = "undervoltage"
        elif throttled.get("throttled") or (temp is not None and temp >= _TEMP_WARN_C):
            warning = "throttled"
        return {"cpu_temp": temp, "warning": warning}

    def get_health(self) -> dict:
        """Estado detalhado para o endpoint `/system/health`."""
        return {
            **self.get_status(),
            "throttle": self.get_throttled(),
            "uptime": self.get_uptime(),
            "storage_pct": self.get_storage(),
        }
