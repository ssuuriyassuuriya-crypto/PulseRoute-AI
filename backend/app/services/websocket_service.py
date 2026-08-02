import asyncio

from fastapi import WebSocket


class DashboardConnectionManager:
    """Maintains authenticated dashboard sockets and broadcasts one state snapshot."""

    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    @property
    def connection_count(self) -> int:
        return len(self._connections)

    async def connect(self, socket: WebSocket) -> None:
        await socket.accept()
        async with self._lock:
            self._connections.add(socket)

    async def disconnect(self, socket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(socket)

    async def broadcast(self, payload: dict[str, object]) -> None:
        async with self._lock:
            connections = list(self._connections)
        failed: list[WebSocket] = []
        for socket in connections:
            try:
                await socket.send_json(payload)
            except Exception:
                failed.append(socket)
        for socket in failed:
            await self.disconnect(socket)
