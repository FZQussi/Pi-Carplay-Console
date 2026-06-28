"""Fixtures partilhados da suite.

`isolate_storage` (autouse) redireciona a cache de capas/letras e o ficheiro
de definições para um diretório temporário — assim os testes nunca tocam no
`~/.cache` / `~/.config` reais nem dependem de estado entre execuções.
"""

import pytest

from backend.core import cache
from backend.services import settings as settings_mod


@pytest.fixture(autouse=True)
def isolate_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_ROOT", tmp_path / "cache")
    monkeypatch.setattr(cache, "COVERS_DIR", tmp_path / "cache" / "covers")
    monkeypatch.setattr(cache, "LYRICS_DIR", tmp_path / "cache" / "lyrics")
    monkeypatch.setattr(settings_mod, "SETTINGS_DIR", tmp_path / "config")
    monkeypatch.setattr(settings_mod, "SETTINGS_FILE", tmp_path / "config" / "settings.json")
    yield
