"""Router REST: `/system/*`.

Placeholder. Será expandido quando os serviços de sistema (uptime,
temperatura, saúde do SD) forem implementados no Sprint 1+.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/ping")
def ping():
    """Health check simples."""
    return {"status": "ok"}
