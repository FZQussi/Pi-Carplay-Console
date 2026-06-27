from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.services.music import MusicService
from backend.services.bluetooth import BluetoothService
import httpx
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

        # Procura na MusicBrainz
        search_url = f"https://musicbrainz.org/ws/2/recording/?query=recording:{track}+artist:{artist}&fmt=json&limit=1"
        async with httpx.AsyncClient() as client:
            r = await client.get(search_url, headers={"User-Agent": "AveoOS/1.0"})
            data = r.json()

            recordings = data.get("recordings", [])
            if not recordings:
                return {"cover": None}

            release_id = recordings[0].get("releases", [{}])[0].get("id")
            if not release_id:
                return {"cover": None}

            cover_url = f"https://coverartarchive.org/release/{release_id}/front"
            return {"cover": cover_url}

    except Exception as e:
        return {"cover": None, "error": str(e)}