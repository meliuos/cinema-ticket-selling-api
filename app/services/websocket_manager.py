"""WebSocket connection manager for real-time seat updates."""

from typing import Dict, List, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time seat updates.
    
    Groups connections by screening_id so users watching the same
    screening get real-time updates when seats change status.
    Also tracks user_id per connection for user-specific notifications.
    """
    
    def __init__(self):
        # screening_id -> list of (websocket, user_id) tuples
        self.screening_rooms: Dict[int, List[tuple]] = {}
        # websocket -> (screening_id, user_id) mapping for easy cleanup
        self.connection_mapping: Dict[WebSocket, tuple] = {}
        
    async def connect(self, screening_id: int, websocket: WebSocket, user_id: int = None):
        """
        Connect a user to a screening room.
        
        Args:
            screening_id: ID of the screening to join
            websocket: WebSocket connection
            user_id: Optional user ID for user-specific updates
        """
        await websocket.accept()
        
        # Add to screening room with user_id
        if screening_id not in self.screening_rooms:
            self.screening_rooms[screening_id] = []
        
        self.screening_rooms[screening_id].append((websocket, user_id))
        self.connection_mapping[websocket] = (screening_id, user_id)
        
        logger.info(f"User {user_id} connected to screening {screening_id}. "
                   f"Room now has {len(self.screening_rooms[screening_id])} connections")
        
        # Send initial connection confirmation with user_id
        await self.send_to_connection(websocket, {
            "type": "connection_confirmed",
            "screening_id": screening_id,
            "user_id": user_id,
            "message": "Connected to real-time seat updates"
        })
        
    def disconnect(self, websocket: WebSocket):
        """
        Disconnect a user from their screening room.
        
        Args:
            websocket: WebSocket connection to disconnect
        """
        if websocket in self.connection_mapping:
            screening_id, user_id = self.connection_mapping[websocket]
            
            # Remove from screening room
            if screening_id in self.screening_rooms:
                self.screening_rooms[screening_id] = [
                    (ws, uid) for ws, uid in self.screening_rooms[screening_id] 
                    if ws != websocket
                ]
                logger.info(f"User {user_id} disconnected from screening {screening_id}. "
                          f"Room now has {len(self.screening_rooms[screening_id])} connections")
                
                if not self.screening_rooms[screening_id]:
                    del self.screening_rooms[screening_id]
            
            del self.connection_mapping[websocket]
    
    async def send_to_connection(self, websocket: WebSocket, message: dict):
        """
        Send message to a specific connection.
        
        Args:
            websocket: Target WebSocket connection
            message: Message dictionary to send
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send message to connection: {e}")
            # Connection might be dead, disconnect it
            self.disconnect(websocket)
    
    async def broadcast_to_screening(
        self, 
        screening_id: int, 
        message: dict, 
        exclude_ws: WebSocket = None
    ):
        """
        Broadcast message to all connections in a screening room.
        Automatically adds is_mine flag for each user's connection.
        
        Args:
            screening_id: ID of the screening room
            message: Message dictionary to broadcast
            exclude_ws: Optional WebSocket to exclude from broadcast
        """
        if screening_id not in self.screening_rooms:
            return
        
        # Get list of connections
        connections = self.screening_rooms[screening_id].copy()
        
        logger.info(f"Broadcasting to {len(connections)} connections in screening {screening_id}: {message['type']}")
        
        # Send to all connections with user-specific info
        dead_connections = []
        for websocket, conn_user_id in connections:
            if websocket == exclude_ws:
                continue
            
            # Customize message for each user
            user_message = message.copy()
            
            # If this is a seat update, add is_mine flag for the connection's user
            if conn_user_id:
                if message.get("type") == "seat_update":
                    user_message["is_mine"] = (message.get("reserved_by") == conn_user_id)
                elif message.get("type") == "bulk_seat_update" and "updates" in message:
                    # Clone updates with is_mine flag
                    user_message["updates"] = [
                        {**update, "is_mine": update.get("reserved_by") == conn_user_id}
                        for update in message["updates"]
                    ]
            try:
                await websocket.send_json(user_message)
            except Exception as e:
                logger.warning(f"Failed to send to connection, marking for removal: {e}")
                dead_connections.append(websocket)
        
        # Clean up dead connections
        for dead_ws in dead_connections:
            self.disconnect(dead_ws)
    
    async def broadcast_seat_update(
        self, 
        screening_id: int, 
        seat_id: int, 
        status: str, 
        user_id: int = None,
        expires_at: str = None
    ):
        """
        Broadcast seat status update to all users in screening room.
        
        Args:
            screening_id: ID of the screening
            seat_id: ID of the seat that changed
            status: New status (available, reserved, booked)
            user_id: ID of user who caused the change
            expires_at: ISO timestamp when reservation expires (for reserved status)
        """
        message = {
            "type": "seat_update",
            "seat_id": seat_id,
            "status": status,
            "timestamp": str(datetime.utcnow().isoformat())
        }
        
        if user_id:
            message["reserved_by"] = user_id
            
        if expires_at:
            message["expires_at"] = expires_at
        
        await self.broadcast_to_screening(screening_id, message)
    
    async def broadcast_multiple_seat_updates(
        self, 
        screening_id: int, 
        seat_updates: List[Dict]
    ):
        """
        Broadcast multiple seat updates in a single message.
        
        Args:
            screening_id: ID of the screening
            seat_updates: List of seat update dictionaries
        """
        if not seat_updates:
            logger.warning(f"No seat updates to broadcast for screening {screening_id}")
            return
            
        logger.info(f"Broadcasting {len(seat_updates)} seat updates to screening {screening_id}")
        
        message = {
            "type": "bulk_seat_update",
            "updates": seat_updates,
            "timestamp": str(datetime.utcnow().isoformat())
        }
        
        await self.broadcast_to_screening(screening_id, message)
    
    def get_connection_count(self, screening_id: int = None) -> int:
        """
        Get number of active connections.
        
        Args:
            screening_id: Optional screening ID to get count for specific room
            
        Returns:
            Number of connections
        """
        if screening_id:
            return len(self.screening_rooms.get(screening_id, []))
        
        return sum(len(connections) for connections in self.screening_rooms.values())
    
    def get_active_screenings(self) -> List[int]:
        """
        Get list of screening IDs that have active connections.
        
        Returns:
            List of screening IDs
        """
        return list(self.screening_rooms.keys())


# Global connection manager instance
manager = ConnectionManager()