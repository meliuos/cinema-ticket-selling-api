"""Contact form schemas."""

from pydantic import BaseModel, EmailStr, Field


class ContactRequest(BaseModel):
    """Contact form submission request."""
    
    name: str = Field(..., min_length=2, max_length=100, description="Name of the person contacting")
    email: EmailStr = Field(..., description="Email address for reply")
    subject: str = Field(..., min_length=3, max_length=200, description="Subject of the message")
    message: str = Field(..., min_length=10, max_length=2000, description="Message content")
    phone: str | None = Field(None, max_length=20, description="Optional phone number")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "subject": "Question about ticket booking",
                    "message": "I'm having trouble booking tickets for the upcoming movie. Can you help?",
                    "phone": "+1234567890"
                }
            ]
        }
    }


class ContactResponse(BaseModel):
    """Contact form submission response."""
    
    success: bool
    message: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Your message has been sent successfully. We'll get back to you soon!"
                }
            ]
        }
    }
