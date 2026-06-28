"""Testes dos endpoints via FastAPI TestClient.

Não dependem de hardware: bluetoothctl/playerctl/amixer/vcgencmd não existem
no CI, e os serviços degradam graciosamente (devolvem erro/None sem rebentar).
"""

import warnings

from starlette.testclient import TestClient

from backend.main import app

warnings.filterwarnings("ignore")
client = TestClient(app)


def test_status_has_all_blocks():
    body = client.get("/status").json()
    assert set(body) == {"bluetooth", "music", "system"}


def test_ping():
    assert client.get("/system/ping").json() == {"status": "ok"}


def test_controls_shape():
    assert set(client.get("/music/controls").json()) == {"volume", "shuffle", "loop"}


def test_cover_img_404_when_uncached():
    r = client.get("/music/cover/img", params={"artist": "zzz", "track": "qqq"})
    assert r.status_code == 404


def test_settings_roundtrip():
    assert client.get("/settings").json() == {"theme": "auto"}
    assert client.put("/settings", json={"theme": "day"}).json() == {"theme": "day"}


def test_settings_rejects_invalid_theme():
    assert client.put("/settings", json={"theme": "purple"}).status_code == 422


def test_volume_rejects_out_of_range():
    assert client.post("/music/volume", params={"level": 200}).status_code == 422


# --- Endpoints novos (Sprints 6/12/14/15/16/18/19) — degradam sem hardware ---
def test_power_status_shape():
    assert set(client.get("/power/status").json()) >= {"available", "acc", "ignition"}


def test_obd_status_shape():
    assert set(client.get("/obd/status").json()) >= {"available", "rpm", "speed"}


def test_gps_position_shape():
    assert set(client.get("/gps/position").json()) >= {"available", "lat", "lon"}


def test_audio_source_default():
    body = client.get("/audio/source").json()
    assert body["source"] == "bluetooth"
    assert set(body["available_sources"]) == {"bluetooth", "aux", "usb"}


def test_audio_source_rejects_invalid():
    assert client.post("/audio/source", json={"source": "fm"}).status_code == 422


def test_camera_status_unavailable_off_pi():
    assert client.get("/camera/status").json()["available"] is False


def test_voice_command_maps_intent():
    body = client.post("/voice/command", params={"text": "toca a próxima"}).json()
    assert body["intent"]["action"] == "next"


def test_system_version_has_fields():
    assert set(client.get("/system/version").json()) >= {"version", "date", "branch"}
