"""Router REST: `/bluetooth/*`.

Endpoints:
- GET  /bluetooth/devices      — dispositivos emparelhados (+ flag ligado)
- POST /bluetooth/connect      — ligar a um MAC
- POST /bluetooth/forget       — esquecer (remover) um MAC
- POST /bluetooth/discoverable — tornar o Pi visível e emparelhável
- POST /bluetooth/disconnect   — desligar do dispositivo atual
"""

from fastapi import APIRouter

from backend.services import get_bluetooth

router = APIRouter(prefix="/bluetooth", tags=["bluetooth"])


@router.get("/devices")
def devices():
    return get_bluetooth().list_devices()


@router.post("/connect")
def connect(mac: str):
    return get_bluetooth().connect(mac)


@router.post("/forget")
def forget(mac: str):
    return get_bluetooth().forget(mac)


@router.post("/discoverable")
def discoverable():
    return get_bluetooth().make_discoverable()


@router.post("/disconnect")
def disconnect():
    return get_bluetooth().disconnect()
