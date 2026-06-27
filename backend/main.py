from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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