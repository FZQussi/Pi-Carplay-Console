"""Router REST: `/system/*`.

- GET /system/ping    — health check simples
- GET /system/health  — saúde detalhada do Pi (temp, throttle, uptime, disco)
"""

from fastapi import APIRouter

from backend.services import get_system

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/ping")
def ping():
    """Health check simples."""
    return {"status": "ok"}


@router.get("/health")
def health():
    """Estado detalhado do sistema (ver `SystemService.get_health`)."""
    return get_system().get_health()
