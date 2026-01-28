from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional, Set

from fastapi import WebSocket


class WebSocketManager:
    """
    Very small WS hub:
    - Connections are grouped by screening_id
    - Can broadcast seat updates
    """

    def __init__(self) -> None:
        self._connections: Dict[int, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, screening_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.setdefault(screening_id, set()).add(websocket)
        await self.send_to_connection(
            websocket,
            {"type": "connection_confirmed", "screening_id": screening_id},
        )

    def disconnect(self, screening_id: int, websocket: WebSocket) -> None:
        conns = self._connections.get(screening_id)
        if not conns:
            return
        conns.discard(websocket)
        if not conns:
            self._connections.pop(screening_id, None)

    async def send_to_connection(self, websocket: WebSocket, message: Dict[str, Any]) -> None:
        try:
            await websocket.send_json(message)
        except Exception:
            # ignore broken connections
            pass

    async def broadcast(self, screening_id: int, message: Dict[str, Any]) -> None:
        conns = list(self._connections.get(screening_id, set()))
        for ws in conns:
            await self.send_to_connection(ws, message)

    async def broadcast_seat_update(
        self,
        screening_id: int,
        seat_id: int,
        status: str,
        reserved_by: Optional[int] = None,
        is_mine: Optional[bool] = None,
        expires_at: Optional[str] = None,
    ) -> None:
        await self.broadcast(
            screening_id,
            {
                "type": "seat_update",
                "seat_id": seat_id,
                "status": status,
                "user_id": reserved_by,
                "reserved_by": reserved_by,
                "is_mine": is_mine,
                "expires_at": expires_at,
            },
        )


manager = WebSocketManager()
