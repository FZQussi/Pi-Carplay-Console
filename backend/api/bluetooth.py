"""Router REST: `/bluetooth/*`.

Endpoints:
- POST /bluetooth/discoverable — tornar o Pi visível e emparelhável
- POST /bluetooth/disconnect   — desligar do dispositivo atual
"""

from fastapi import APIRouter

from backend.services import get_bluetooth

router = APIRouter(prefix="/bluetooth", tags=["bluetooth"])


@router.post("/discoverable")
def discoverable():
    return get_bluetooth().make_discoverable()


@router.post("/disconnect")
def disconnect():
    return get_bluetooth().disconnect()
