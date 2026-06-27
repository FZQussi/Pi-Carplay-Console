"""Router REST: `/music/*`.

Endpoints:
- POST /music/play     — play
- POST /music/pause    — pause
- POST /music/next     — skip
- POST /music/prev     — previous
- GET  /music/cover    — cover URL do Spotify (procura track+artist)

A capa usa a API pública do Spotify. É a única parte do AveoOS V1 que
*precisa* de internet; o resto funciona offline.
"""

from __future__ import annotations

import base64

import httpx
from fastapi import APIRouter

from backend.core.config import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_SEARCH_URL,
    SPOTIFY_TOKEN_URL,
)
from backend.services import get_bluetooth, get_music

router = APIRouter(prefix="/music", tags=["music"])


@router.post("/play")
def play():
    return get_music().play()


@router.post("/pause")
def pause():
    return get_music().pause()


@router.post("/next")
def next_track():
    return get_music().next()


@router.post("/prev")
def prev_track():
    return get_music().prev()


@router.get("/cover")
async def get_cover():
    """Procura a capa na Spotify a partir do artist/track atual.

    Lê o estado via `BluetoothService` (e não do `MusicService` mock)
    porque o `playerctl` que reporta track+artist vive no mesmo escopo
    do estado Bluetooth.
    """
    try:
        bt_status = get_bluetooth().get_status()
        artist = bt_status.get("artist", "")
        track = bt_status.get("track", "")

        if not artist or not track:
            return {"cover": None}

        credentials = base64.b64encode(
            f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
        ).decode()

        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                SPOTIFY_TOKEN_URL,
                headers={"Authorization": f"Basic {credentials}"},
                data={"grant_type": "client_credentials"},
            )
            token = token_resp.json().get("access_token")

            search_resp = await client.get(
                SPOTIFY_SEARCH_URL,
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "q": f"track:{track} artist:{artist}",
                    "type": "track",
                    "limit": 1,
                },
            )
            items = search_resp.json().get("tracks", {}).get("items", [])
            if not items:
                return {"cover": None}

            return {"cover": items[0]["album"]["images"][0]["url"]}

    except Exception as e:
        return {"cover": None, "error": str(e)}
