"""Testes de parsing BT (Sprint 9) e descoberta de DBus (core/runtime)."""

from backend.core import runtime
from backend.services.bluetooth import parse_devices


def test_parse_devices():
    out = (
        "Device 14:49:D4:7F:2A:18 Pixel 7\n"
        "Device AA:BB:CC:DD:EE:FF JBL Speaker\n"
        "linha de lixo sem device\n"
    )
    assert parse_devices(out) == [
        {"mac": "14:49:D4:7F:2A:18", "name": "Pixel 7"},
        {"mac": "AA:BB:CC:DD:EE:FF", "name": "JBL Speaker"},
    ]


def test_parse_devices_empty():
    assert parse_devices("") == []


def test_dbus_prefers_non_root(monkeypatch):
    monkeypatch.setattr(runtime.glob, "glob",
                        lambda p: ["/run/user/0/bus", "/run/user/1000/bus"])
    env = runtime.dbus_session_env()
    assert env["DBUS_SESSION_BUS_ADDRESS"] == "unix:path=/run/user/1000/bus"


def test_dbus_fallback_when_none(monkeypatch):
    monkeypatch.setattr(runtime.glob, "glob", lambda p: [])
    assert isinstance(runtime.dbus_session_env(), dict)  # não rebenta
