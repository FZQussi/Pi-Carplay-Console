"""AveoOS backend — entrypoint FastAPI.

Responsabilidades:
- Montar a aplicação com CORS permissivo (kiosk local)
- Servir o frontend (SPA vanilla) em `/`
- Servir assets estáticos em `/static/...`
- Incluir routers REST por recurso (music, bluetooth, system)
- Disponibilizar `/status` (resumo consolidado do estado)

Mais detalhes em `docs/ARCHITECTURE.md`. Workflow de dev em
`docs/DEVELOPMENT.md`.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.bluetooth import router as bluetooth_router
from backend.api.music import router as music_router
from backend.api.system import router as system_router
from backend.core.config import FRONTEND_DIR, FRONTEND_PAGES_DIR
from backend.services import get_bluetooth, get_music

app = FastAPI(title="AveoOS")

# CORS permissivo: o kiosk acede em localhost e nada mais. Para acesso
# remoto usar um reverse proxy autenticado (fora do scope da V1).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# StaticFiles serve a árvore inteira de frontend/. Os ficheiros ficam
# disponíveis em /static/dirs/etc.css etc.
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# Routers por recurso
app.include_router(music_router)
app.include_router(bluetooth_router)
app.include_router(system_router)


@app.get("/")
def root():
    """Serve o SPA vanilla. Todas as screens vivem dentro deste HTML."""
    return FileResponse(str(FRONTEND_PAGES_DIR / "index.html"))


@app.get("/status")
def status():
    """Estado consolidado, usado pelo polling de 2 segundos no frontend."""
    return {
        "bluetooth": get_bluetooth().get_status(),
        "music": get_music().get_current_track(),
    }
