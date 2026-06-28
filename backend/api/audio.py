"""Router REST: `/audio/*` (Sprint 12) — fontes e estado de chamada."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from backend.services import get_audio

router = APIRouter(prefix="/audio", tags=["audio"])


class SourcePatch(BaseModel):
    source: Literal["bluetooth", "aux", "usb"]


@router.get("/source")
def get_source():
    return get_audio().get_source()


@router.post("/source")
def set_source(body: SourcePatch):
    return get_audio().set_source(body.source)


@router.get("/call")
def call_state():
    return get_audio().call_state()
