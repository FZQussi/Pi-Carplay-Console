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
# MAC do dispositivo principal. Marcado como TODO para Sprint 9: remover
# hardcode e implementar descoberta via `bluetoothctl`.
DEFAULT_BT_MAC = "14:49:D4:7F:2A:18"

# Nota: as credenciais do Spotify foram removidas — o AveoOS usa a iTunes
# Search API (sem chave) para capas e a LRCLIB para letras. Se algum dia
# voltar a usar-se o Spotify, ler de variáveis de ambiente, nunca hardcoded.
# (As chaves que aqui estavam ficaram expostas no histórico do git e devem
# ser revogadas no painel do Spotify.)
