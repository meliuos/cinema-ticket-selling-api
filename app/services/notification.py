"""Notification service for movie availability alerts."""

import logging
from datetime import datetime, timezone
from typing import List
from sqlmodel import Session, select, and_

from app.models.movie_notification import MovieNotification
from app.models.movie import Movie, MovieState
from app.models.user import User
from app.config import settings
from app.utils.email import send_email, generate_movie_available_email

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing movie notifications."""
    
    @staticmethod
    def subscribe_to_movie(
        db: Session, 
        user_id: int, 
        movie_id: int
    ) -> tuple[bool, str]:
        """
        Subscribe a user to notifications for a movie.
        
        Args:
            db: Database session
            user_id: ID of the user subscribing
            movie_id: ID of the movie
            
        Returns:
            Tuple of (success, message)
        """
        # Check if movie exists
        movie = db.get(Movie, movie_id)
        if not movie:
            return False, "Movie not found"
        
        # Only allow subscriptions for COMING_SOON movies
        if movie.state != MovieState.COMING_SOON:
            return False, f"Movie is already {movie.state}. Notifications are only available for coming soon movies."
        
        # Check if subscription already exists
        existing = db.exec(
            select(MovieNotification).where(
                and_(
                    MovieNotification.user_id == user_id,
                    MovieNotification.movie_id == movie_id
                )
            )
        ).first()
        
        if existing:
            return True, "Already subscribed to notifications for this movie"
        
        # Create new subscription
        notification = MovieNotification(
            user_id=user_id,
            movie_id=movie_id,
            notified=False
        )
        db.add(notification)
        db.commit()
        
        return True, "Successfully subscribed to notifications"
    
    @staticmethod
    def unsubscribe_from_movie(
        db: Session, 
        user_id: int, 
        movie_id: int
    ) -> tuple[bool, str]:
        """
        Unsubscribe a user from notifications for a movie.
        
        Args:
            db: Database session
            user_id: ID of the user unsubscribing
            movie_id: ID of the movie
            
        Returns:
            Tuple of (success, message)
        """
        notification = db.exec(
            select(MovieNotification).where(
                and_(
                    MovieNotification.user_id == user_id,
                    MovieNotification.movie_id == movie_id
                )
            )
        ).first()
        
        if not notification:
            return False, "No active subscription found"
        
        db.delete(notification)
        db.commit()
        
        return True, "Successfully unsubscribed from notifications"
    
    @staticmethod
    def get_unnotified_subscribers(db: Session, movie_id: int) -> List[tuple[User, MovieNotification]]:
        """
        Get all users who subscribed to a movie but haven't been notified yet.
        
        Args:
            db: Database session
            movie_id: ID of the movie
            
        Returns:
            List of (User, MovieNotification) tuples
        """
        results = db.exec(
            select(User, MovieNotification)
            .join(MovieNotification, User.id == MovieNotification.user_id)
            .where(
                and_(
                    MovieNotification.movie_id == movie_id,
                    MovieNotification.notified == False
                )
            )
        ).all()
        
        return results
    
    @staticmethod
    def mark_as_notified(db: Session, notification_id: int):
        """
        Mark a notification as sent.
        
        Args:
            db: Database session
            notification_id: ID of the notification
        """
        notification = db.get(MovieNotification, notification_id)
        if notification:
            notification.notified = True
            notification.notified_at = datetime.now(timezone.utc)
            db.add(notification)
            db.commit()
    
    @staticmethod
    async def send_availability_email(user_email: str, user_name: str, movie_title: str, movie_id: int):
        """
        Send email notification when a movie becomes available.
        
        Integrates with SMTP to send actual emails.
        Falls back to logging if email is not configured.
        
        Args:
            user_email: Recipient email address
            user_name: Recipient name
            movie_title: Name of the movie
            movie_id: ID of the movie
        """
        try:
            if settings.emails_enabled:
                # Generate email content
                email_data = generate_movie_available_email(
                    email_to=user_email,
                    user_name=user_name,
                    movie_title=movie_title,
                    movie_id=movie_id
                )
                
                # Send the email
                send_email(
                    email_to=user_email,
                    subject=email_data.subject,
                    html_content=email_data.html_content
                )
                
                logger.info(f"📧 Email sent to {user_email} about {movie_title}")
            else:
                # Fallback: Log the notification if email is not configured
                logger.warning("Email not configured. Logging notification instead.")
                logger.info(f"📧 EMAIL NOTIFICATION (Not Sent - Email Not Configured)")
                logger.info(f"To: {user_email}")
                logger.info(f"Subject: 🎬 {movie_title} - Tickets Now Available!")
                logger.info(f"User: {user_name}")
                logger.info(f"Movie: {movie_title}")
                logger.info(f"Message: Showtimes are now live at {settings.front_url}/movies/{movie_id}")
                
        except Exception as e:
            logger.error(f"Failed to send email to {user_email}: {e}")
            raise
    
    @staticmethod
    async def notify_movie_available(db: Session, movie_id: int):
        """
        Notify all subscribed users that a movie is now available.
        
        This should be called when:
        - Movie state changes from COMING_SOON to SHOWING
        - First screening is created for the movie
        
        Args:
            db: Database session
            movie_id: ID of the movie that became available
        """
        movie = db.get(Movie, movie_id)
        if not movie:
            logger.error(f"Movie {movie_id} not found")
            return
        
        # Get all subscribers who haven't been notified
        subscribers = NotificationService.get_unnotified_subscribers(db, movie_id)
        
        if not subscribers:
            logger.info(f"No subscribers to notify for movie {movie.title}")
            return
        
        logger.info(f"Notifying {len(subscribers)} subscribers about {movie.title}")
        
        # Send notifications
        for user, notification in subscribers:
            try:
                # Send email
                await NotificationService.send_availability_email(
                    user_email=user.email,
                    user_name=user.full_name,
                    movie_title=movie.title,
                    movie_id=movie.id
                )
                
                # Mark as notified
                NotificationService.mark_as_notified(db, notification.id)
                
                logger.info(f"Notified user {user.email} about {movie.title}")
                
            except Exception as e:
                logger.error(f"Failed to notify user {user.email}: {e}")
                continue
