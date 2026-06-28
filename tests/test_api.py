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
