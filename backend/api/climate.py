"""Router REST: `/climate/*` (Sprint 17) — IR do A/C."""

from fastapi import APIRouter

from backend.services import get_climate

router = APIRouter(prefix="/climate", tags=["climate"])


@router.get("/commands")
def commands():
    return get_climate().list_commands()


@router.post("/send")
def send(command: str):
    return get_climate().send(command)


@router.post("/learn")
def learn(command: str):
    return get_climate().learn(command)
