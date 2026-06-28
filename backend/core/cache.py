"""Cache em disco para capas e letras.

Objetivo (Sprint 11): depois de uma música tocar uma vez, a capa e a letra
ficam guardadas localmente — aparecem instantaneamente e **funcionam sem
internet** nas próximas vezes. As APIs externas (iTunes, LRCLIB) passam a
ser só o "primeiro fetch".

- Capas: bytes da imagem em `~/.cache/aveoos/covers/<key>.jpg`
- Letras: JSON `{synced, plain}` em `~/.cache/aveoos/lyrics/<key>.json`

A chave é um hash de `artist|track` normalizado. Cada diretório tem um
limite de ficheiros: ao exceder, apagam-se os mais antigos (LRU por mtime).
Em cada acerto fazemos `touch` para marcar como recente.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

CACHE_ROOT = Path.home() / ".cache" / "aveoos"
COVERS_DIR = CACHE_ROOT / "covers"
LYRICS_DIR = CACHE_ROOT / "lyrics"

# Limites de LRU. Capas rondam dezenas de KB; 300 ≈ poucos MB. Letras são
# texto, praticamente irrelevantes em tamanho.
MAX_COVERS = 300
MAX_LYRICS = 500

# As letras não mudam, mas usamos um TTL para limitar staleness e permitir
# reaver eventuais correções na LRCLIB. 30 dias é folgado.
LYRICS_TTL_S = 30 * 24 * 3600


def _key(artist: str, track: str) -> str:
    raw = f"{(artist or '').lower().strip()}|{(track or '').lower().strip()}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _trim(directory: Path, max_files: int) -> None:
    """Mantém no máximo `max_files`, apagando os mais antigos (por mtime)."""
    try:
        files = sorted(directory.glob("*"), key=lambda p: p.stat().st_mtime)
    except OSError:
        return
    excess = len(files) - max_files
    for p in files[:excess] if excess > 0 else []:
        try:
            p.unlink()
        except OSError:
            pass


# --- Capas ------------------------------------------------------------------
def cover_path(artist: str, track: str) -> Path:
    return COVERS_DIR / f"{_key(artist, track)}.jpg"


def get_cover(artist: str, track: str) -> Path | None:
    """Caminho da capa em cache, ou None. Faz `touch` (LRU) em caso de acerto."""
    p = cover_path(artist, track)
    if p.exists():
        try:
            p.touch()
        except OSError:
            pass
        return p
    return None


def save_cover(artist: str, track: str, data: bytes) -> Path:
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    p = cover_path(artist, track)
    p.write_bytes(data)
    _trim(COVERS_DIR, MAX_COVERS)
    return p


# --- Letras -----------------------------------------------------------------
def get_lyrics(artist: str, track: str) -> dict | None:
    """Letra em cache (dentro do TTL), ou None."""
    p = LYRICS_DIR / f"{_key(artist, track)}.json"
    try:
        if p.exists() and time.time() - p.stat().st_mtime < LYRICS_TTL_S:
            p.touch()
            return json.loads(p.read_text(encoding="utf-8"))
    except OSError:
        return None
    except (ValueError, UnicodeDecodeError):
        # ficheiro corrompido — trata como miss
        return None
    return None


def save_lyrics(artist: str, track: str, payload: dict) -> None:
    LYRICS_DIR.mkdir(parents=True, exist_ok=True)
    p = LYRICS_DIR / f"{_key(artist, track)}.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    _trim(LYRICS_DIR, MAX_LYRICS)
