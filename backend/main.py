from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
import base64
import subprocess
import os

from backend.services.music import MusicService
from backend.services.bluetooth import BluetoothService

app = FastAPI(title="AveoOS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

music = MusicService()
bluetooth = BluetoothService()

app.mount("/static", StaticFiles(directory="frontend"), name="static")

SPOTIFY_CLIENT_ID = "9d28e91e4abb4bb7b7611165324c507f"
SPOTIFY_CLIENT_SECRET = "c2ae1e031fd84cf0b753bf977a43d712"

async def get_spotify_token():
    credentials = base64.b64encode(
        f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {credentials}"},
            data={"grant_type": "client_credentials"}
        )
        return r.json().get("access_token")

@app.get("/")
def root():
    return FileResponse("frontend/index.html")

@app.get("/status")
def status():
    return {
        "bluetooth": bluetooth.get_status(),
        "music": music.get_current_track()
    }

@app.post("/music/play")
def play():
    return music.play()

@app.post("/music/pause")
def pause():
    return music.pause()

@app.post("/music/next")
def next_track():
    return music.next()

@app.post("/music/prev")
def prev_track():
    return music.prev()

@app.post("/bluetooth/discoverable")
def bluetooth_discoverable():
    return bluetooth.make_discoverable()

@app.post("/bluetooth/disconnect")
def bluetooth_disconnect():
    return bluetooth.disconnect()

@app.get("/music/cover")
async def get_cover():
    try:
        bt_status = bluetooth.get_status()
        artist = bt_status.get("artist", "")
        track = bt_status.get("track", "")

        if not artist or not track:
            return {"cover": None}

        token = await get_spotify_token()

        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://api.spotify.com/v1/search",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "q": f"track:{track} artist:{artist}",
                    "type": "track",
                    "limit": 1
                }
            )
            data = r.json()
            items = data.get("tracks", {}).get("items", [])
            if not items:
                return {"cover": None}

            cover = items[0]["album"]["images"][0]["url"]
            return {"cover": cover}

    except Exception as e:
        return {"cover": None, "error": str(e)}