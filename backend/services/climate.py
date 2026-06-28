"""Sprint 17 — climatização por IR.

REQUER HARDWARE: emissor IR + `ir-ctl` (pacote v4l-utils / LIRC). O fluxo é:
aprender uma vez cada botão do comando do A/C (grava o sinal num ficheiro)
e depois reenviar. Fora do Pi, os comandos degradam para erro controlado.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

CODES_DIR = Path.home() / ".config" / "aveoos" / "ir"


class ClimateService:
    def list_commands(self) -> dict:
        try:
            return {"commands": sorted(p.stem for p in CODES_DIR.glob("*.ir"))}
        except Exception:
            return {"commands": []}

    def send(self, command: str) -> dict:
        code = CODES_DIR / f"{command}.ir"
        if not code.exists():
            return {"status": "error", "error": f"código '{command}' não aprendido"}
        try:
            subprocess.run(["ir-ctl", "--send", str(code)],
                           capture_output=True, text=True, timeout=5)
            return {"status": "ok", "command": command}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def learn(self, command: str) -> dict:
        try:
            CODES_DIR.mkdir(parents=True, exist_ok=True)
            code = CODES_DIR / f"{command}.ir"
            subprocess.run(["ir-ctl", "--receive", str(code)],
                           capture_output=True, text=True, timeout=15)
            return {"status": "learned", "command": command}
        except Exception as e:
            return {"status": "error", "error": str(e)}
