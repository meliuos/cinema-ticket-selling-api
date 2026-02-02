"""FAQ routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.config import settings
from app.database import get_session
from app.models.faq import FAQ as FAQModel
from app.models.user import User
from app.schemas.faq import FAQ, FAQBase
from app.services.auth import get_current_admin_user


router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/faqs", tags=["FAQs"])


@router.get("/", response_model=list[FAQ])
def get_faqs(db: Session = Depends(get_session)):
    """Get all FAQs."""
    faqs = db.exec(select(FAQModel)).all()
    return faqs


@router.post("/", response_model=FAQ)
def create_faq(
    faq_data: FAQBase,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """Create a new FAQ (Admin only)."""
    faq = FAQModel(**faq_data.model_dump())
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


@router.delete("/{faq_id}")
def delete_faq(
    faq_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session)
):
    """Delete an FAQ by ID (Admin only)."""
    faq = db.get(FAQModel, faq_id)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    
    db.delete(faq)
    db.commit()
    return {"message": "FAQ deleted successfully"}