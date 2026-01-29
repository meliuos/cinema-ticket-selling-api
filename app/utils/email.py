"""Email utilities for sending notifications."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from jinja2 import Template
import emails
from emails.template import JinjaTemplate

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    """Email data structure."""
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    """
    Render an email template with the given context.
    
    Args:
        template_name: Name of the template file
        context: Dictionary of variables to render in the template
        
    Returns:
        Rendered HTML content
    """
    template_path = Path(__file__).parent / "email-templates" / template_name
    
    # If template file doesn't exist, use inline template
    if not template_path.exists():
        logger.warning(f"Template {template_name} not found, using inline template")
        return _get_inline_template(template_name, context)
    
    template_str = template_path.read_text()
    html_content = Template(template_str).render(context)
    return html_content


def _get_inline_template(template_name: str, context: dict[str, Any]) -> str:
    """Fallback inline templates when template files don't exist."""
    
    if "movie_available" in template_name:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .movie-title {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                    margin: 20px 0;
                }}
                .cta-button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    margin-top: 20px;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎬 Tickets Now Available!</h1>
            </div>
            <div class="content">
                <p>Hi {context.get('user_name', 'Movie Fan')},</p>
                
                <p>Great news! The movie you've been waiting for is now showing!</p>
                
                <div class="movie-title">🎬 {context.get('movie_title', 'Movie')}</div>
                
                <p>Showtimes are now live and tickets are available for booking.</p>
                
                <p><strong>Don't miss out! Book now before it sells out! 🍿</strong></p>
                
                <div style="text-align: center;">
                    <a href="{context.get('front_url', settings.front_url)}/movies/{context.get('movie_id', '')}" class="cta-button">
                        Book Your Tickets Now
                    </a>
                </div>
                
                <p style="margin-top: 30px;">Thank you for choosing {settings.PROJECT_NAME}!</p>
            </div>
            <div class="footer">
                <p>You received this email because you subscribed to notifications for this movie.</p>
                <p>&copy; 2026 {settings.PROJECT_NAME}. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
    
    # Default template
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>{context.get('subject', 'Notification')}</h2>
        <p>{context.get('message', '')}</p>
        <hr>
        <p style="color: #666; font-size: 12px;">
            {settings.PROJECT_NAME}
        </p>
    </body>
    </html>
    """


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    """
    Send an email.
    
    Args:
        email_to: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        
    Raises:
        AssertionError: If email configuration is not available
    """
    assert settings.emails_enabled, "No provided configuration for email variables"
    
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME or settings.PROJECT_NAME, settings.EMAILS_FROM_EMAIL),
    )
    
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
        
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    
    try:
        response = message.send(to=email_to, smtp=smtp_options)
        logger.info(f"Email sent to {email_to}: {response}")
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {e}")
        raise


def generate_movie_available_email(
    *,
    email_to: str,
    user_name: str,
    movie_title: str,
    movie_id: int,
) -> EmailData:
    """
    Generate email data for movie availability notification.
    
    Args:
        email_to: Recipient email address
        user_name: Name of the user
        movie_title: Title of the movie
        movie_id: ID of the movie
        
    Returns:
        EmailData with subject and HTML content
    """
    subject = f"🎬 {movie_title} - Tickets Now Available!"
    
    html_content = render_email_template(
        template_name="movie_available.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "user_name": user_name,
            "movie_title": movie_title,
            "movie_id": movie_id,
            "front_url": settings.front_url,
            "email": email_to,
        },
    )
    
    return EmailData(html_content=html_content, subject=subject)


def generate_test_email(email_to: str) -> EmailData:
    """
    Generate a test email.
    
    Args:
        email_to: Recipient email address
        
    Returns:
        EmailData with subject and HTML content
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test Email"
    
    html_content = render_email_template(
        template_name="test_email.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "email": email_to,
            "message": "This is a test email from the cinema booking system.",
        },
    )
    
    return EmailData(html_content=html_content, subject=subject)


def generate_contact_form_email(
    *,
    name: str,
    email: str,
    subject: str,
    message: str,
    phone: str | None = None,
) -> EmailData:
    """
    Generate email data for contact form submission.
    
    Args:
        name: Name of the person contacting
        email: Email address of the person contacting
        subject: Subject of the message
        message: Message content
        phone: Optional phone number
        
    Returns:
        EmailData with subject and HTML content
    """
    email_subject = f"Contact Form: {subject}"
    
    # Create inline template for contact form
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .container {{
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .content {{
                padding: 30px;
            }}
            .field {{
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 1px solid #eee;
            }}
            .field-label {{
                font-weight: bold;
                color: #667eea;
                display: block;
                margin-bottom: 5px;
            }}
            .field-value {{
                color: #333;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            .message-box {{
                background: #f9f9f9;
                padding: 15px;
                border-left: 4px solid #667eea;
                border-radius: 4px;
                margin-top: 10px;
            }}
            .footer {{
                text-align: center;
                color: #666;
                padding: 20px;
                font-size: 12px;
                background: #f9f9f9;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1> New Contact Form Submission</h1>
            </div>
            <div class="content">
                <div class="field">
                    <span class="field-label">From:</span>
                    <span class="field-value">{name}</span>
                </div>
                
                <div class="field">
                    <span class="field-label">Email:</span>
                    <span class="field-value">
                        <a href="mailto:{email}">{email}</a>
                    </span>
                </div>
                
                {f'''<div class="field">
                    <span class="field-label">Phone:</span>
                    <span class="field-value">{phone}</span>
                </div>''' if phone else ''}
                
                <div class="field">
                    <span class="field-label">Subject:</span>
                    <span class="field-value">{subject}</span>
                </div>
                
                <div class="field" style="border-bottom: none;">
                    <span class="field-label">Message:</span>
                    <div class="message-box">
                        {message}
                    </div>
                </div>
            </div>
            <div class="footer">
                <p>This message was sent via {settings.PROJECT_NAME} contact form</p>
                <p>&copy; 2026 {settings.PROJECT_NAME}. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return EmailData(html_content=html_content, subject=email_subject)
