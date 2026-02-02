"""Email testing routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from app.config import settings
from app.models.user import User
from app.services.auth import get_current_active_user
from app.utils.email import send_email, generate_test_email, generate_movie_available_email

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/test-email", tags=["Email Testing"])


class TestEmailRequest(BaseModel):
    """Request model for test email."""
    email: EmailStr


@router.post("/send-test")
async def send_test_email(
    request: TestEmailRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Send a test email to verify email configuration.
    Requires authentication.
    """
    if not settings.emails_enabled:
        raise HTTPException(
            status_code=400,
            detail="Email is not configured. Please set SMTP settings in environment variables."
        )
    
    try:
        email_data = generate_test_email(request.email)
        send_email(
            email_to=request.email,
            subject=email_data.subject,
            html_content=email_data.html_content
        )
        
        return {
            "success": True,
            "message": f"Test email sent successfully to {request.email}",
            "email_configured": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )


@router.post("/send-movie-notification-test")
async def send_movie_notification_test(
    request: TestEmailRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Send a test movie availability notification email.
    Requires authentication.
    """
    if not settings.emails_enabled:
        raise HTTPException(
            status_code=400,
            detail="Email is not configured. Please set SMTP settings in environment variables."
        )
    
    try:
        email_data = generate_movie_available_email(
            email_to=request.email,
            user_name=current_user.full_name,
            movie_title="Dune Part III (Test Movie)"
        )
        
        send_email(
            email_to=request.email,
            subject=email_data.subject,
            html_content=email_data.html_content
        )
        
        return {
            "success": True,
            "message": f"Movie notification test email sent to {request.email}",
            "email_configured": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )


@router.get("/status")
async def email_status():
    """Check email configuration status."""
    return {
        "emails_enabled": settings.emails_enabled,
        "smtp_host": settings.SMTP_HOST,
        "smtp_port": settings.SMTP_PORT,
        "smtp_tls": settings.SMTP_TLS,
        "smtp_ssl": settings.SMTP_SSL,
        "from_email": settings.EMAILS_FROM_EMAIL,
        "from_name": settings.EMAILS_FROM_NAME,
        "message": "Email is configured and ready" if settings.emails_enabled else "Email is not configured. Set SMTP_HOST and EMAILS_FROM_EMAIL to enable."
    }
