"""Event bus interno para comunicação entre serviços e o WebSocket.

Sprint 2 (planeado) — atualmente um placeholder vazio. O objetivo é
permitir que `BluetoothService`, `MusicService`, `PowerService`, etc.
emitam eventos tipados (ex: `BT_CONNECTED`, `TRACK_CHANGED`, `ACC_OFF`)
que serão ouvidos pelo `core/ws.py` e enviados para o frontend.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class EventType(str, Enum):
    """Tipos de eventos suportados pelo bus."""

    BT_STATE_CHANGED = "bt-state-changed"
    TRACK_CHANGED = "track-changed"
    ACC_OFF = "acc-off"
    SYSTEM_ERROR = "system-error"


@dataclass
class Event:
    """Envelope genérico para um evento interno."""

    type: EventType
    payload: dict[str, Any]


type Listener = Callable[[Event], None]

_listeners: list[tuple[EventType, Listener]] = []


def subscribe(event_type: EventType, listener: Listener) -> None:
    """Regista uma função *listener* para um dado tipo de evento."""
    _listeners.append((event_type, listener))


def publish(event: Event) -> None:
    """Publica um evento. Todos os listeners registados para o tipo são chamados."""
    for et, listener in _listeners:
        if et == event.type:
            listener(event)
