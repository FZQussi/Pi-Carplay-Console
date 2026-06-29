"""Router REST: `/maps/*` — janela do Google Maps (site real)."""

from __future__ import annotations

from fastapi import APIRouter

from backend.services import get_maps

router = APIRouter(prefix="/maps", tags=["maps"])


@router.get("/status")
def status():
    return get_maps().status()


@router.post("/open")
def open_maps():
    return get_maps().open()


@router.post("/hide")
def hide_maps():
    return get_maps().hide()
