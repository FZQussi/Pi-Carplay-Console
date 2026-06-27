"""Gestor de ligações WebSocket para push de eventos ao frontend.

Planeado para Sprint 2. O esquema será:

    Cliente liga-se a `ws://host:8000/ws`
    `connection_manager.connect(ws)` regista e envia estado atual.
    Quando um serviço publica um evento em `core/events.py`, este módulo
    faz broadcast para todas as ligações abertas.

Por agora o ficheiro existe apenas para definir a interface que o
resto do código vai usar quando a sprint arrancar.
"""

from typing import Any
from fastapi import WebSocket


class ConnectionManager:
    """Mantém a lista de WebSockets abertos e faz broadcast."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        for connection in list(self._connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()
