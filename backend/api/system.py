"""Router REST: `/system/*`.

- GET  /system/ping    — health check simples
- GET  /system/health  — saúde detalhada do Pi (temp, throttle, uptime, disco)
- GET  /system/version — versão atual (git)
- POST /system/update  — atualização OTA (git pull + restart)
"""

from fastapi import APIRouter

from backend.services import get_system, get_update

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/ping")
def ping():
    """Health check simples."""
    return {"status": "ok"}


@router.get("/health")
def health():
    """Estado detalhado do sistema (ver `SystemService.get_health`)."""
    return get_system().get_health()


@router.get("/version")
def version():
    """Versão atual (Sprint 19)."""
    return get_update().get_version()


@router.post("/update")
def update():
    """Atualização OTA (Sprint 19)."""
    return get_update().update()
