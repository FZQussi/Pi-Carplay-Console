"""Sprint 19 — OTA: versão atual e atualização via git.

`get_version()` funciona em qualquer sítio com git. `update()` faz
`git pull` + reinstala deps + reinicia o serviço systemd — só faz sentido
no Pi em produção, mas degrada com erro controlado em qualquer lado.
"""

from __future__ import annotations

import subprocess

from backend.core.config import REPO_ROOT


def _git(*args, timeout=10) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(REPO_ROOT), *args],
                           capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


class UpdateService:
    def get_version(self) -> dict:
        return {
            "version": _git("rev-parse", "--short", "HEAD"),
            "date": _git("log", "-1", "--format=%cd", "--date=short"),
            "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        }

    def update(self) -> dict:
        try:
            pull = subprocess.run(
                ["git", "-C", str(REPO_ROOT), "pull", "--ff-only"],
                capture_output=True, text=True, timeout=120,
            )
            if pull.returncode != 0:
                return {"status": "error", "stage": "pull", "error": pull.stderr.strip()}

            # Reinstalar deps (best-effort) e reiniciar o serviço.
            pip = REPO_ROOT / ".venv" / "bin" / "pip"
            if pip.exists():
                subprocess.run([str(pip), "install", "-r", str(REPO_ROOT / "requirements.txt")],
                               capture_output=True, text=True, timeout=300)
            subprocess.Popen(["sudo", "systemctl", "restart", "aveoos-backend"])
            return {"status": "updating", "output": pull.stdout.strip()}
        except Exception as e:
            return {"status": "error", "error": str(e)}
