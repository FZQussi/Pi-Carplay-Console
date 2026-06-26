from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AveoOS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "AveoOS running"}

@app.get("/status")
def status():
    return {
        "bluetooth": "unknown",
        "music": "unknown",
        "gps": "disabled"
    }