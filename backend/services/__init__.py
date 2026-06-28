from functools import lru_cache

from backend.services.music import MusicService
from backend.services.bluetooth import BluetoothService
from backend.services.system import SystemService
from backend.services.settings import SettingsService
from backend.services.power import PowerService
from backend.services.audio import AudioService
from backend.services.camera import CameraService
from backend.services.obd import OBDService
from backend.services.gps import GPSService
from backend.services.climate import ClimateService
from backend.services.voice import VoiceService
from backend.services.update import UpdateService

# Pacote `services`. Re-exporta as classes públicas e os singletons.
__all__ = [
    "MusicService", "BluetoothService", "SystemService", "SettingsService",
    "PowerService", "AudioService", "CameraService", "OBDService",
    "GPSService", "ClimateService", "VoiceService", "UpdateService",
    "get_music", "get_bluetooth", "get_system", "get_settings",
    "get_power", "get_audio", "get_camera", "get_obd", "get_gps",
    "get_climate", "get_voice", "get_update",
]


@lru_cache(maxsize=1)
def get_music() -> MusicService:
    return MusicService()


@lru_cache(maxsize=1)
def get_bluetooth() -> BluetoothService:
    return BluetoothService()


@lru_cache(maxsize=1)
def get_system() -> SystemService:
    return SystemService()


@lru_cache(maxsize=1)
def get_settings() -> SettingsService:
    return SettingsService()


@lru_cache(maxsize=1)
def get_power() -> PowerService:
    return PowerService()


@lru_cache(maxsize=1)
def get_audio() -> AudioService:
    return AudioService()


@lru_cache(maxsize=1)
def get_camera() -> CameraService:
    return CameraService()


@lru_cache(maxsize=1)
def get_obd() -> OBDService:
    return OBDService()


@lru_cache(maxsize=1)
def get_gps() -> GPSService:
    return GPSService()


@lru_cache(maxsize=1)
def get_climate() -> ClimateService:
    return ClimateService()


@lru_cache(maxsize=1)
def get_voice() -> VoiceService:
    return VoiceService()


@lru_cache(maxsize=1)
def get_update() -> UpdateService:
    return UpdateService()
