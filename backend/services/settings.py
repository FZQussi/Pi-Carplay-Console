"""Serviço de definições persistentes.

Guarda preferências do utilizador em `~/.config/aveoos/settings.json`. Por
agora só o tema (auto/dia/noite), mas é o sítio óbvio para crescer (ordem da
grelha, presets, etc.).

Defensivo por defeito: se o ficheiro não existir ou estiver corrompido,
devolve os valores por omissão sem rebentar.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SETTINGS_DIR = Path.home() / ".config" / "aveoos"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

# Valores por omissão. Só chaves aqui presentes são aceites num update — um
# patch com chaves desconhecidas é ignorado (evita lixo no ficheiro).
DEFAULTS: dict[str, Any] = {
    "theme": "auto",  # "auto" | "day" | "night"
}


class SettingsService:
    def get(self) -> dict[str, Any]:
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                data = {}
        except Exception:
            data = {}
        return {**DEFAULTS, **{k: data[k] for k in DEFAULTS if k in data}}

    def update(self, patch: dict[str, Any]) -> dict[str, Any]:
        data = self.get()
        for key in DEFAULTS:
            if key in patch and patch[key] is not None:
                data[key] = patch[key]
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps(data), encoding="utf-8")
        return data
