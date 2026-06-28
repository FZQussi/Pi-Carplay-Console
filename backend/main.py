"""AveoOS backend — entrypoint FastAPI.

Responsabilidades:
- Montar a aplicação com CORS permissivo (kiosk local)
- Servir o frontend (SPA vanilla) em `/`
- Servir assets estáticos em `/static/...`
- Incluir routers REST por recurso (music, bluetooth, system)
- Disponibilizar `/status` (resumo consolidado do estado)
- Push de estado em tempo real via WebSocket (`/ws`)

O `/status` continua a existir como *fallback* para quando o WebSocket
não está disponível. O caminho normal é: um loop em segundo plano lê o
estado do sistema e faz broadcast para os clientes WS sempre que muda —
ver `monitor_loop()` e `docs/FEATURE-PLAN.md` (Sprint 7).

Mais detalhes em `docs/ARCHITECTURE.md`. Workflow de dev em
`docs/DEVELOPMENT.md`.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.bluetooth import router as bluetooth_router
from backend.api.music import router as music_router
from backend.api.system import router as system_router
from backend.core.config import FRONTEND_DIR, FRONTEND_PAGES_DIR
from backend.core.ws import manager
from backend.services import get_bluetooth, get_music

logger = logging.getLogger("aveoos.main")

# Cadência do loop de monitorização. 1s dá uma barra de progresso fluida
# sem martelar os subprocessos (bluetoothctl/playerctl) ao ponto de pesar
# na CPU de um Pi.
MONITOR_INTERVAL_S = 1.0


def build_status() -> dict:
    """Estado consolidado do sistema.

    Chama os subprocessos (bluetoothctl/playerctl) via os serviços, por
    isso é *bloqueante* — quem chamar de dentro do event loop deve usar
    `asyncio.to_thread`.
    """
    return {
        "bluetooth": get_bluetooth().get_status(),
        "music": get_music().get_current_track(),
    }


async def monitor_loop() -> None:
    """Lê o estado periodicamente e faz broadcast só quando muda.

    Centraliza o polling no backend (um lado só corre os subprocessos) e
    empurra para o(s) cliente(s) — em vez de cada cliente bater no
    `/status`. Em idle (sem música, sem mudanças) não há tráfego nem
    trabalho extra além da leitura.
    """
    last: dict | None = None
    while True:
        try:
            status = await asyncio.to_thread(build_status)
            if status != last:
                last = status
                await manager.broadcast(status)
        except Exception:
            logger.exception("Erro no loop de monitorização")
        await asyncio.sleep(MONITOR_INTERVAL_S)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Arranca o loop de monitorização junto com a app e cancela-o no shutdown."""
    task = asyncio.create_task(monitor_loop())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title="AveoOS", lifespan=lifespan)

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
    """Estado consolidado. Fallback para quando o WebSocket não está ativo."""
    return build_status()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Canal de push do estado. Envia o estado atual ao ligar e fica à
    escuta; o `monitor_loop` trata dos updates seguintes via broadcast."""
    await manager.connect(websocket)
    try:
        # Estado inicial para o ecrã arrancar já preenchido, sem esperar
        # pelo primeiro tick do monitor.
        await websocket.send_json(await asyncio.to_thread(build_status))
        # Mantém a coroutine viva; só serve para detetar a desconexão.
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        logger.exception("Erro na ligação WebSocket")
        manager.disconnect(websocket)
