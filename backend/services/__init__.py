from functools import lru_cache

from backend.services.music import MusicService
from backend.services.bluetooth import BluetoothService

# Pacote `services`. Re-exporta as classes públicas.
__all__ = ["MusicService", "BluetoothService", "get_music", "get_bluetooth"]


@lru_cache(maxsize=1)
def get_music() -> MusicService:
    """Devolve a instância singleton de MusicService."""
    return MusicService()


@lru_cache(maxsize=1)
def get_bluetooth() -> BluetoothService:
    """Devolve a instância singleton de BluetoothService."""
    return BluetoothService()
