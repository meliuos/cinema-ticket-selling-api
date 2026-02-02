"""Background tasks for seat reservation cleanup."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Session
from app.database import get_session
from app.services.seat_reservation import SeatReservationService

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """Manages background tasks for the application."""
    
    def __init__(self):
        self.cleanup_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    async def start_cleanup_task(self, interval_minutes: int = 1):
        """
        Start the periodic cleanup task for expired reservations.
        
        Args:
            interval_minutes: How often to run cleanup (in minutes)
        """
        if self.is_running:
            return
        
        self.is_running = True
        
        while self.is_running:
            try:
                await self.cleanup_expired_reservations()
                await asyncio.sleep(interval_minutes * 60)  # Convert to seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def cleanup_expired_reservations(self):
        """
        Clean up expired reservations and broadcast updates.
        
        This runs in a separate database session to avoid interfering
        with ongoing requests.
        """
        try:
            # Get a new database session for this background task
            session = next(get_session())
            
            try:
                # Clean up expired reservations
                count, seat_updates = SeatReservationService.cleanup_expired_reservations(session)
                
                if count > 0:
                    # Commit the cleanup changes
                    session.commit()
                    
                    # Broadcast seat updates
                    from app.services.websocket_manager import manager
                    for screening_id, updates in seat_updates.items():
                        try:
                            await manager.broadcast_multiple_seat_updates(screening_id, updates)
                        except Exception as e:
                            pass
                    
            finally:
                session.close()
                
        except Exception:
            pass
    
    def stop_cleanup_task(self):
        """Stop the cleanup task."""
        self.is_running = False
        
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
    
    async def manual_cleanup(self) -> dict:
        """
        Manually trigger a cleanup operation.
        
        Returns:
            Dictionary with cleanup results
        """
        try:
            session = next(get_session())
            
            try:
                start_time = datetime.utcnow()
                count, seat_updates = SeatReservationService.cleanup_expired_reservations(session)
                
                if count > 0:
                    # Commit the cleanup changes
                    session.commit()
                    
                    # Broadcast seat updates
                    from app.services.websocket_manager import manager
                    for screening_id, updates in seat_updates.items():
                        try:
                            await manager.broadcast_multiple_seat_updates(screening_id, updates)
                        except Exception as e:
                            pass
                
                end_time = datetime.utcnow()
                
                return {
                    "success": True,
                    "cleaned_count": count,
                    "timestamp": start_time.isoformat(),
                    "duration_seconds": (end_time - start_time).total_seconds()
                }
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Manual cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global background task manager
background_manager = BackgroundTaskManager()