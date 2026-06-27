"""Constantes e configuração central do AveoOS.

O `core/config.py` agrega todos os paths, identificadores e segredos que
outras partes do backend precisam de ler. Manter constantes fora dos
módulos de domínio facilita a troca de comportamento sem editar lógica.
"""

from pathlib import Path

# Caminhos ---------------------------------------------------------------
# Repo root = pasta que contém este projeto (parent de "backend").
REPO_ROOT = Path(__file__).resolve().parents[2]

FRONTEND_DIR = REPO_ROOT / "frontend"
FRONTEND_PAGES_DIR = FRONTEND_DIR / "pages"

# Bluetooth --------------------------------------------------------------
# MAC do dispositivo principal. Marcado como TODO para Sprint 2: remover
# hardcode e implementar descoberta via `bluetoothctl`.
DEFAULT_BT_MAC = "14:49:D4:7F:2A:18"

# Spotify ----------------------------------------------------------------
# TODO: mover para variáveis de ambiente / ficheiro .env. Não commitar
# segredos ao git.
SPOTIFY_CLIENT_ID = "9d28e91e4abb4bb7b7611165324c507f"
SPOTIFY_CLIENT_SECRET = "c2ae1e031fd84cf0b753bf977a43d712"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"
