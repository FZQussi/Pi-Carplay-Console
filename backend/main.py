from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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