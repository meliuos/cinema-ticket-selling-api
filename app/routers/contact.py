"""Contact form router."""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.contact import ContactRequest, ContactResponse
from app.config import settings
from app.utils.email import send_email, generate_contact_form_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/contact", tags=["Contact"])


@router.post("", response_model=ContactResponse)
async def submit_contact_form(
    contact_data: ContactRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a contact form message.
    
    Sends an email to the support team with the contact form details.
    This endpoint is public and doesn't require authentication.
    
    Args:
        contact_data: Contact form data (name, email, subject, message, phone)
        background_tasks: FastAPI background tasks for async email sending
        
    Returns:
        ContactResponse with success status and message
        
    Raises:
        HTTPException: If email is not configured or sending fails
    """
    try:
        # Check if email is configured
        if not settings.emails_enabled:
            logger.warning("Contact form submitted but email is not configured")
            raise HTTPException(
                status_code=503,
                detail="Email service is currently unavailable. Please try again later."
            )
        
        # Generate email content
        email_data = generate_contact_form_email(
            name=contact_data.name,
            email=contact_data.email,
            subject=contact_data.subject,
            message=contact_data.message,
            phone=contact_data.phone
        )
        
        # Send email in background
        background_tasks.add_task(
            send_email,
            email_to=settings.SUPPORT_EMAIL,
            subject=email_data.subject,
            html_content=email_data.html_content
        )
        
        logger.info(f"Contact form submitted by {contact_data.name} ({contact_data.email})")
        
        return ContactResponse(
            success=True,
            message="Your message has been sent successfully. We'll get back to you soon!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process contact form: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to send your message. Please try again later."
        )


@router.get("/status")
async def get_contact_status():
    """
    Check if contact form is available.
    
    Returns information about the contact form service status.
    """
    return {
        "available": settings.emails_enabled,
        "support_email": settings.SUPPORT_EMAIL if settings.emails_enabled else None,
        "message": "Contact form is available" if settings.emails_enabled else "Contact form is currently unavailable"
    }
