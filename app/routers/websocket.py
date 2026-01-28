"""WebSocket routes for real-time seat updates."""

from __future__ import annotations

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from typing import Optional

from app.database import get_session
from app.services.auth import get_current_user_from_token
from app.services.websocket_manager import manager

router = APIRouter()


@router.websocket("/ws/screenings/{screening_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    screening_id: int,
    token: Optional[str] = Query(None),
):
    """
    URL: ws://host:8000/ws/screenings/{screening_id}?token=<JWT>

    If token is invalid/missing we still accept connection (read-only updates).
    """
    user_id = None
    if token:
        try:
            session = next(get_session())
            user = await get_current_user_from_token(token, session)
            user_id = user.id if user else None
        except Exception:
            user_id = None
        finally:
            try:
                session.close()
            except Exception:
                pass

    # For now we don't use user_id in the WS manager; it’s here for parity / future.
    await manager.connect(screening_id, websocket)

    try:
        while True:
            # Keep connection alive. Client may send pings; ignore content.
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Normal client disconnect (code 1000 etc.) — don't treat as server error.
        pass
    finally:
        manager.disconnect(screening_id, websocket)
