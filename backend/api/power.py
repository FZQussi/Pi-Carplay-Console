"""Router REST: `/power/*` (Sprint 6)."""

from fastapi import APIRouter

from backend.services import get_power

router = APIRouter(prefix="/power", tags=["power"])


@router.get("/status")
def status():
    return get_power().get_status()


@router.post("/shutdown")
def shutdown():
    return get_power().graceful_shutdown()
