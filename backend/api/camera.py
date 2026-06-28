"""Router REST: `/camera/*` (Sprint 14) — câmara de marcha-atrás."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

from backend.services import get_camera
from backend.services.camera import reverse_active

router = APIRouter(prefix="/camera", tags=["camera"])


@router.get("/status")
def status():
    return {"available": get_camera().available(), "reverse": reverse_active()}


@router.get("/stream")
def stream():
    cam = get_camera()
    if not cam.available():
        return JSONResponse({"error": "câmara indisponível"}, status_code=503)
    return StreamingResponse(
        cam.mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
