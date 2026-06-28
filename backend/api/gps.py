"""Router REST: `/gps/*` (Sprint 16)."""

from fastapi import APIRouter

from backend.services import get_gps

router = APIRouter(prefix="/gps", tags=["gps"])


@router.get("/position")
def position():
    return get_gps().get_position()
