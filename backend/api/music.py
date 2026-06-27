"""Router REST: `/music/*`.

Endpoints:
- POST /music/play     — play
- POST /music/pause    — pause
- POST /music/next     — skip
- POST /music/prev     — previous
- GET  /music/cover    — cover URL do Spotify (procura track+artist)
- GET  /music/lyrics   — letra (LRCLIB; sincronizada quando disponível)

A capa e a letra usam APIs públicas (Spotify e LRCLIB). É a única
parte do AveoOS V1 que *precisa* de internet; o resto funciona offline.
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

# LRCLIB é gratuito e não exige API key/registo. Devolve letra simples
# (plainLyrics) e, quando existe, letra sincronizada por tempo no
# formato LRC (syncedLyrics), ex.: "[00:12.34]Texto da linha".
LRCLIB_URL = "https://lrclib.net/api/get"


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


@router.get("/lyrics")
async def get_lyrics():
    """Procura a letra na LRCLIB a partir do artist/track atual.

    Lê o estado via `BluetoothService`, pela mesma razão do
    `/music/cover`: é onde o `playerctl` reporta track+artist.

    Devolve `synced` (formato LRC, com timestamps por linha) quando
    a LRCLIB tem essa versão disponível, caso contrário só `plain`
    (texto corrido, sem timestamps). Se não encontrar nada, ambos
    vêm `None` e o frontend mostra um placeholder.
    """
    try:
        bt_status = get_bluetooth().get_status()
        artist = bt_status.get("artist", "")
        track = bt_status.get("track", "")

        if not artist or not track:
            return {"synced": None, "plain": None}

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                LRCLIB_URL,
                params={"artist_name": artist, "track_name": track},
            )

        if resp.status_code != 200:
            return {"synced": None, "plain": None}

        data = resp.json()
        return {
            "synced": data.get("syncedLyrics") or None,
            "plain": data.get("plainLyrics") or None,
        }

    except Exception as e:
        return {"synced": None, "plain": None, "error": str(e)}