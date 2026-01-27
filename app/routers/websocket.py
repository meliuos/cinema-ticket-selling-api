"""WebSocket routes for real-time seat updates."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional
import logging

from app.services.websocket_manager import manager
from app.services.auth import get_current_user_from_token
from app.database import get_session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/screenings/{screening_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    screening_id: int,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time seat updates.
    
    Connects user to a screening room where they'll receive real-time
    updates when seats change status (reserved, booked, available).
    
    URL: ws://localhost:8000/ws/screenings/{screening_id}?token=your_jwt_token
    
    Events sent to client:
    - connection_confirmed: Sent when connection is established
    - seat_update: Single seat status change
    - bulk_seat_update: Multiple seat status changes
    - reservation_expired: When user's own reservations expire
    """
    user_id = None
    if token:
        try:
            # Validate token and get user info
            session = next(get_session())
            user = await get_current_user_from_token(token, session)
            if user:
                user_id = user.id
                logger.info(f"WebSocket connected: User {user.email} joined screening {screening_id}")
            session.close()
        except Exception as e:
            logger.warning(f"Invalid token in WebSocket connection: {e}")
    
    try:
        # Connect to screening room
        await manager.connect(screening_id, websocket, user_id)
        
        # Keep connection alive and listen for any client messages
        while True:
            try:
                # Receive any client messages 
                data = await websocket.receive_text()
                
                # Handle client messages if needed
                try:
                    import json
                    message = json.loads(data)
                    
                    if message.get("type") == "ping":
                        await manager.send_to_connection(websocket, {
                            "type": "pong",
                            "timestamp": str(datetime.utcnow().isoformat())
                        })
                        
                except json.JSONDecodeError:
                    # Invalid JSON, ignore
                    pass
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        manager.disconnect(websocket)


@router.get("/ws/stats")
async def websocket_stats():
    """
    Get WebSocket connection statistics.
    Useful for monitoring and debugging.
    """
    return {
        "total_connections": manager.get_connection_count(),
        "active_screenings": manager.get_active_screenings(),
        "screening_details": {
            screening_id: manager.get_connection_count(screening_id)
            for screening_id in manager.get_active_screenings()
        }
    }


# Import datetime for timestamps
from datetime import datetime