"""Router REST: `/music/*`.

Endpoints:
- POST /music/play     — play
- POST /music/pause    — pause
- POST /music/next     — skip
- POST /music/prev     — previous
- POST /music/seek     — saltar para posição (segundos)
- GET  /music/controls — estado de volume/shuffle/loop
- POST /music/volume   — definir volume (ALSA, 0-100)
- POST /music/shuffle  — toggle shuffle
- POST /music/repeat   — ciclar repeat (None/Track/Playlist)
- GET  /music/cover    — cover via iTunes Search API (recebe artist+track)
- GET  /music/lyrics   — letra (LRCLIB; recebe artist+track)

`artist`/`track` vêm como query params, fornecidos pelo frontend (que
já os tem a partir do `/status`). Propositadamente NÃO voltamos a
chamar `BluetoothService.get_status()` aqui — isso lançaria de novo
`bluetoothctl`/`playerctl` por cada pedido, o que é lento e pode
atrasar o resto do sistema num dispositivo com pouca CPU.

A capa e a letra usam APIs públicas (iTunes e LRCLIB), nenhuma exige
chave/registo. É a única parte do AveoOS V1 que *precisa* de
internet; o resto funciona offline.
"""

from __future__ import annotations

import logging
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Query
from fastapi.responses import FileResponse, Response

from backend.core import cache
from backend.services import get_music

# Garante que os logs aparecem na consola onde o uvicorn está a correr
# (ou em `journalctl -u <serviço> -f`, se estiver como serviço systemd).
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aveoos.music")

router = APIRouter(prefix="/music", tags=["music"])

# iTunes Search API: pública, sem API key, sem registo.
ITUNES_SEARCH_URL = "https://itunes.apple.com/search"

# LRCLIB: também pública e sem API key. Devolve letra simples
# (plainLyrics) e, quando existe, letra sincronizada por tempo no
# formato LRC (syncedLyrics), ex.: "[00:12.34]Texto da linha".
LRCLIB_URL = "https://lrclib.net/api/get"

# Alguns serviços bloqueiam pedidos sem User-Agent (tratam-nos como
# bot/scraper). Mandamos sempre um, por segurança.
DEFAULT_HEADERS = {"User-Agent": "AveoOS/1.0 (+https://github.com/)"}


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


@router.post("/seek")
def seek(position: float = Query(0, ge=0)):
    """Salta para uma posição absoluta (segundos)."""
    return get_music().seek(position)


@router.get("/controls")
def get_controls():
    """Estado dos controlos secundários (volume/shuffle/loop)."""
    return get_music().get_controls()


@router.post("/volume")
def set_volume(level: int = Query(..., ge=0, le=100)):
    return get_music().set_volume(level)


@router.post("/shuffle")
def shuffle():
    return get_music().toggle_shuffle()


@router.post("/repeat")
def repeat():
    return get_music().cycle_loop()


def _cover_url(artist: str, track: str) -> str:
    """URL local (servida pelo backend) da capa em cache — funciona offline."""
    return "/music/cover/img?" + urlencode({"artist": artist, "track": track})


@router.get("/cover")
async def get_cover(artist: str = "", track: str = ""):
    """Devolve a URL local da capa, garantindo que está em cache.

    Se já estiver em disco, devolve logo (sem rede). Caso contrário procura
    na iTunes Search API, **descarrega os bytes da imagem** e guarda em
    cache — para que nas próximas vezes (e offline) seja servida do disco.
    """
    try:
        if not artist or not track:
            return {"cover": None}

        # Acerto em cache: nada de rede.
        if cache.get_cover(artist, track):
            return {"cover": _cover_url(artist, track)}

        logger.info("A procurar capa: artist=%r track=%r", artist, track)

        async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=5) as client:
            resp = await client.get(
                ITUNES_SEARCH_URL,
                params={
                    "term": f"{artist} {track}",
                    "media": "music",
                    "entity": "song",
                    "limit": 1,
                },
            )
            if resp.status_code != 200:
                logger.warning("iTunes devolveu status=%s", resp.status_code)
                return {"cover": None}

            results = resp.json().get("results", [])
            if not results:
                logger.info("iTunes sem resultados para %r - %r", artist, track)
                return {"cover": None}

            # Vem em 100x100; pedimos uma resolução maior e descarregamos.
            artwork = (results[0].get("artworkUrl100") or "").replace(
                "100x100bb", "600x600bb"
            )
            if not artwork:
                return {"cover": None}

            img = await client.get(artwork)
            if img.status_code != 200 or not img.content:
                return {"cover": None}

        cache.save_cover(artist, track, img.content)
        return {"cover": _cover_url(artist, track)}

    except Exception as e:
        logger.exception("Erro ao obter capa")
        return {"cover": None, "error": f"{type(e).__name__}: {e}"}


@router.get("/cover/img")
def cover_img(artist: str = "", track: str = ""):
    """Serve a capa em cache a partir do disco (offline-friendly)."""
    path = cache.get_cover(artist, track)
    if path:
        return FileResponse(str(path), media_type="image/jpeg")
    return Response(status_code=404)


@router.get("/lyrics")
async def get_lyrics(artist: str = "", track: str = ""):
    """Procura a letra na LRCLIB a partir do artist/track fornecidos
    pelo frontend (que já os tem via `/status`).

    Devolve `synced` (formato LRC, com timestamps por linha) quando
    a LRCLIB tem essa versão disponível, caso contrário só `plain`
    (texto corrido, sem timestamps). Se não encontrar nada, ambos
    vêm `None` e o frontend mostra um placeholder.
    """
    try:
        if not artist or not track:
            logger.info("Sem artist/track ainda — a saltar pedido de letra.")
            return {"synced": None, "plain": None}

        # Acerto em cache: nada de rede (funciona offline).
        cached = cache.get_lyrics(artist, track)
        if cached is not None:
            return cached

        logger.info("A procurar letra: artist=%r track=%r", artist, track)

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                LRCLIB_URL,
                headers=DEFAULT_HEADERS,
                params={"artist_name": artist, "track_name": track},
                timeout=10,
            )

        logger.info("LRCLIB respondeu status=%s", resp.status_code)

        if resp.status_code != 200:
            # LRCLIB devolve 404 quando não tem a letra — não é um erro
            # de código, é só "não encontrado". Registamos o corpo para
            # diagnóstico, mas devolvemos None normalmente.
            logger.info("LRCLIB sem letra (status=%s): %s", resp.status_code, resp.text[:300])
            return {"synced": None, "plain": None}

        data = resp.json()
        synced = data.get("syncedLyrics") or None
        plain = data.get("plainLyrics") or None
        logger.info("Letra encontrada: synced=%s plain=%s", bool(synced), bool(plain))

        result = {"synced": synced, "plain": plain}
        # Só guardamos quando encontramos algo — assim um "miss" volta a
        # tentar mais tarde (a LRCLIB pode passar a ter a letra).
        if synced or plain:
            cache.save_lyrics(artist, track, result)
        return result

    except Exception as e:
        logger.exception("Erro ao obter letra")
        return {"synced": None, "plain": None, "error": f"{type(e).__name__}: {e}"}