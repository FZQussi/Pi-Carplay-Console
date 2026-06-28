from functools import lru_cache

from backend.services.music import MusicService
from backend.services.bluetooth import BluetoothService
from backend.services.system import SystemService

# Pacote `services`. Re-exporta as classes públicas.
__all__ = [
    "MusicService", "BluetoothService", "SystemService",
    "get_music", "get_bluetooth", "get_system",
]


@lru_cache(maxsize=1)
def get_music() -> MusicService:
    """Devolve a instância singleton de MusicService."""
    return MusicService()


@lru_cache(maxsize=1)
def get_bluetooth() -> BluetoothService:
    """Devolve a instância singleton de BluetoothService."""
    return BluetoothService()


@lru_cache(maxsize=1)
def get_system() -> SystemService:
    """Devolve a instância singleton de SystemService."""
    return SystemService()
