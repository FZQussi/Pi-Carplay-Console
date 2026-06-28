"""Router REST: `/settings`.

- GET /settings  — preferências atuais
- PUT /settings  — atualizar (patch parcial validado)
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from backend.services import get_settings

router = APIRouter(tags=["settings"])


class SettingsPatch(BaseModel):
    """Patch parcial. Cada campo é opcional; só os presentes são aplicados.
    O `Literal` rejeita valores inválidos com 422 automaticamente."""

    theme: Literal["auto", "day", "night"] | None = None


@router.get("/settings")
def read_settings():
    return get_settings().get()


@router.put("/settings")
def write_settings(patch: SettingsPatch):
    return get_settings().update(patch.model_dump(exclude_none=True))
