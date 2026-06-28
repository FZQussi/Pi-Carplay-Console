"""Testes do SystemService (com sysfs/subprocess simulados)."""

from backend.services import system
from backend.services.system import SystemService


def test_cpu_temp_reads_sysfs(tmp_path, monkeypatch):
    f = tmp_path / "temp"
    f.write_text("48500")
    monkeypatch.setattr(system, "_THERMAL", f)
    assert SystemService().get_cpu_temp() == 48.5


def test_cpu_temp_missing_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(system, "_THERMAL", tmp_path / "nao-existe")
    assert SystemService().get_cpu_temp() is None


def test_throttled_parses_bits(monkeypatch):
    class FakeResult:
        stdout = "throttled=0x50005"  # bit0 (undervoltage) + bit2 (throttled)

    monkeypatch.setattr(system.subprocess, "run", lambda *a, **k: FakeResult())
    assert SystemService()._read_throttled() == {"undervoltage": True, "throttled": True}


def test_status_warning_undervoltage(monkeypatch):
    svc = SystemService()
    monkeypatch.setattr(svc, "get_cpu_temp", lambda: 55.0)
    monkeypatch.setattr(svc, "get_throttled", lambda: {"undervoltage": True, "throttled": False})
    assert svc.get_status()["warning"] == "undervoltage"


def test_status_warning_high_temp(monkeypatch):
    svc = SystemService()
    monkeypatch.setattr(svc, "get_cpu_temp", lambda: 85.0)
    monkeypatch.setattr(svc, "get_throttled", lambda: {})
    assert svc.get_status()["warning"] == "throttled"


def test_status_no_warning(monkeypatch):
    svc = SystemService()
    monkeypatch.setattr(svc, "get_cpu_temp", lambda: 50.0)
    monkeypatch.setattr(svc, "get_throttled", lambda: {})
    assert svc.get_status()["warning"] is None
