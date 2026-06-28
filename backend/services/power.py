"""Sprint 6 — gestão de energia (ACC) e shutdown seguro.

REQUER HARDWARE: GPIO17 ligado ao sinal ACC via divisor (ver HARDWARE.md).
Fora do Pi, `get_status()` devolve `acc=None` e o monitor não faz nada. A
lógica de *debounce* é pura e está testada em `tests/`.
"""

from __future__ import annotations

import subprocess

ACC_GPIO = 17


def read_acc_raw() -> bool | None:
    """Lê o pino ACC. None se não há GPIO disponível (dev/PC)."""
    try:
        import gpiod  # type: ignore
    except Exception:
        return None
    try:
        chip = gpiod.Chip("gpiochip0")
        line = chip.get_line(ACC_GPIO)
        line.request(consumer="aveoos", type=gpiod.LINE_REQ_DIR_IN)
        try:
            return bool(line.get_value())
        finally:
            line.release()
    except Exception:
        return None


class Debouncer:
    """Estabiliza um sinal booleano: só muda de estado após `threshold`
    leituras consecutivas iguais. Filtra ruído do alternador para não
    desligar o Pi por um pico espúrio."""

    def __init__(self, threshold: int = 3) -> None:
        self.threshold = threshold
        self.state: bool | None = None
        self._candidate: bool | None = None
        self._count = 0

    def update(self, raw: bool) -> bool | None:
        if raw == self.state:
            self._candidate = None
            self._count = 0
            return self.state
        if raw == self._candidate:
            self._count += 1
        else:
            self._candidate = raw
            self._count = 1
        if self._count >= self.threshold:
            self.state = raw
            self._candidate = None
            self._count = 0
        return self.state


class PowerService:
    def __init__(self) -> None:
        self._debouncer = Debouncer()

    def get_status(self) -> dict:
        raw = read_acc_raw()
        if raw is None:
            return {"available": False, "acc": None, "ignition": None}
        ignition = self._debouncer.update(raw)
        return {"available": True, "acc": raw, "ignition": bool(ignition)}

    def graceful_shutdown(self) -> dict:
        """Coordena um shutdown limpo. (O stop dos serviços é feito pelo
        systemd ao apanhar o SIGTERM do `shutdown`.)"""
        try:
            subprocess.Popen(["sudo", "shutdown", "-h", "now"])
            return {"status": "shutting-down"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
