"""Testes do SettingsService (ficheiro em tmp via fixture isolate_storage)."""

from backend.services import settings as settings_mod
from backend.services.settings import SettingsService


def test_defaults_when_missing():
    assert SettingsService().get() == {"theme": "auto"}


def test_update_persists():
    svc = SettingsService()
    assert svc.update({"theme": "night"}) == {"theme": "night"}
    assert svc.get()["theme"] == "night"


def test_update_ignores_unknown_keys():
    svc = SettingsService()
    svc.update({"theme": "day", "hacker": "x"})
    assert svc.get() == {"theme": "day"}


def test_corrupt_file_falls_back_to_defaults():
    settings_mod.SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    settings_mod.SETTINGS_FILE.write_text("{nao json", encoding="utf-8")
    assert SettingsService().get() == {"theme": "auto"}
