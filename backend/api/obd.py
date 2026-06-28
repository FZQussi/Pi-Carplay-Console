"""Router REST: `/obd/*` (Sprint 15)."""

from fastapi import APIRouter

from backend.services import get_obd

router = APIRouter(prefix="/obd", tags=["obd"])


@router.get("/status")
def status():
    return get_obd().get_data()
