"""Router REST: `/phone/*` — telefone mãos-livres (HFP)."""

from __future__ import annotations

from fastapi import APIRouter

from backend.services import get_phone

router = APIRouter(prefix="/phone", tags=["phone"])


@router.get("/status")
def status():
    return get_phone().status()


@router.get("/contacts")
def contacts():
    return get_phone().contacts()


@router.post("/answer")
def answer():
    return get_phone().answer()


@router.post("/hangup")
def hangup():
    return get_phone().hangup()


@router.post("/dial")
def dial(number: str):
    return get_phone().dial(number)


@router.post("/mute")
def mute():
    return get_phone().mute()
