"""Testes da lógica do MusicService (subprocess simulado)."""

from backend.services import music as music_mod
from backend.services.music import MusicService


def test_cycle_loop_advances(monkeypatch):
    svc = MusicService()
    monkeypatch.setattr(svc, "_query", lambda *a: "None")
    captured = {}
    monkeypatch.setattr(svc, "_run", lambda *a: captured.update(args=a))
    assert svc.cycle_loop() == {"loop": "Track"}
    assert captured["args"] == ("loop", "Track")


def test_cycle_loop_wraps_to_none(monkeypatch):
    svc = MusicService()
    monkeypatch.setattr(svc, "_query", lambda *a: "Playlist")
    monkeypatch.setattr(svc, "_run", lambda *a: None)
    assert svc.cycle_loop() == {"loop": "None"}


def test_toggle_shuffle_reads_new_state(monkeypatch):
    svc = MusicService()
    monkeypatch.setattr(svc, "_run", lambda *a: None)
    monkeypatch.setattr(svc, "_query", lambda *a: "On")
    assert svc.toggle_shuffle() == {"shuffle": True}


def test_set_volume_clamps_high(monkeypatch):
    captured = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        class R:
            returncode = 0
            stdout = ""
        return R()

    monkeypatch.setattr(music_mod.subprocess, "run", fake_run)
    assert MusicService().set_volume(150) == {"volume": 100}
    assert "100%" in captured["args"]


def test_set_volume_clamps_low(monkeypatch):
    monkeypatch.setattr(music_mod.subprocess, "run",
                        lambda *a, **k: type("R", (), {"returncode": 0, "stdout": ""})())
    assert MusicService().set_volume(-5) == {"volume": 0}
