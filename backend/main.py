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

from backend.api.audio import router as audio_router
from backend.api.bluetooth import router as bluetooth_router
from backend.api.camera import router as camera_router
from backend.api.climate import router as climate_router
from backend.api.gps import router as gps_router
from backend.api.music import router as music_router
from backend.api.obd import router as obd_router
from backend.api.power import router as power_router
from backend.api.settings import router as settings_router
from backend.api.system import router as system_router
from backend.api.voice import router as voice_router
from backend.core.config import FRONTEND_DIR, FRONTEND_PAGES_DIR
from backend.core.ws import manager
from backend.services import get_bluetooth, get_music, get_system

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
        "system": get_system().get_status(),
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


async def power_monitor_loop() -> None:
    """Vigia o ACC: quando a ignição passa a OFF (após ter estado ON), faz
    shutdown seguro. Só atua no Pi — fora dele `available` é False e o loop
    fica inofensivo (nunca desliga a máquina de desenvolvimento)."""
    from backend.services import get_power

    was_on = False
    while True:
        try:
            st = await asyncio.to_thread(get_power().get_status)
            if st.get("available"):
                ignition = bool(st.get("ignition"))
                if was_on and not ignition:
                    logger.info("ACC OFF detetado — a iniciar shutdown seguro")
                    get_power().graceful_shutdown()
                was_on = ignition
        except Exception:
            logger.exception("Erro no monitor de energia")
        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Arranca os loops de monitorização junto com a app e cancela-os no shutdown."""
    tasks = [
        asyncio.create_task(monitor_loop()),
        asyncio.create_task(power_monitor_loop()),
    ]
    try:
        yield
    finally:
        for task in tasks:
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
app.include_router(settings_router)
app.include_router(power_router)
app.include_router(audio_router)
app.include_router(camera_router)
app.include_router(obd_router)
app.include_router(gps_router)
app.include_router(climate_router)
app.include_router(voice_router)


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
