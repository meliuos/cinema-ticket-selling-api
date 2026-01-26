"""Review routes for movie reviews."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func
from typing import Optional
from datetime import datetime

from app.config import settings
from app.database import get_session
from app.models.review import Review, ReviewReactionModel
from app.models.movie import Movie
from app.models.user import User
from app.schemas.review import (
    ReviewCreate,
    ReviewRead,
    ReviewUpdate,
    ReviewReaction,
    ReviewReactionResponse,
    ReviewSummary,
    ReviewListResponse
)
from app.services.auth import get_current_active_user

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/movies", tags=["Reviews"])


@router.post("/{movie_id}/reviews", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(
    movie_id: int,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a new review for a movie."""
    # Check if movie exists
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    # Check if user already reviewed this movie
    existing_review = session.exec(
        select(Review).where(
            Review.user_id == current_user.id,
            Review.movie_id == movie_id,
            Review.is_deleted == False
        )
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this movie. Use PUT to update your review."
        )
    
    # Create new review
    review = Review(
        user_id=current_user.id,
        movie_id=movie_id,
        **review_data.model_dump()
    )
    
    session.add(review)
    session.commit()
    session.refresh(review)
    
    return ReviewRead(
        id=review.id,
        user_id=review.user_id,
        movie_id=review.movie_id,
        rating=review.rating,
        title=review.title,
        comment=review.comment,
        reviewerName=current_user.full_name,
        reviewerAvatar=current_user.profile_picture_url,
        likes=review.likes,
        dislikes=review.dislikes,
        created_at=review.created_at,
        updated_at=review.updated_at
    )


@router.get("/{movie_id}/reviews", response_model=ReviewListResponse)
async def get_movie_reviews(
    movie_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort by: created_at, rating, likes"),
    order: str = Query("desc", description="Order: asc or desc"),
    session: Session = Depends(get_session)
):
    """Get paginated reviews for a movie."""
    # Check if movie exists
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    # Build query with user join
    query = select(Review, User.full_name, User.profile_picture_url).join(
        User, Review.user_id == User.id
    ).where(
        Review.movie_id == movie_id,
        Review.is_deleted == False
    )
    
    # Apply sorting
    if sort_by == "rating":
        query = query.order_by(Review.rating.desc() if order == "desc" else Review.rating.asc())
    elif sort_by == "likes":
        query = query.order_by(Review.likes.desc() if order == "desc" else Review.likes.asc())
    else:  # created_at
        query = query.order_by(Review.created_at.desc() if order == "desc" else Review.created_at.asc())
    
    # Get total count
    count_query = select(func.count()).select_from(Review).where(
        Review.movie_id == movie_id,
        Review.is_deleted == False
    )
    total = session.exec(count_query).one()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    reviews_data = session.exec(query).all()
    
    # Convert to ReviewRead objects with reviewer information
    reviews = []
    for review, reviewer_name, reviewer_avatar in reviews_data:
        reviews.append(ReviewRead(
            id=review.id,
            user_id=review.user_id,
            movie_id=review.movie_id,
            rating=review.rating,
            title=review.title,
            comment=review.comment,
            reviewerName=reviewer_name,
            reviewerAvatar=reviewer_avatar,
            likes=review.likes,
            dislikes=review.dislikes,
            created_at=review.created_at,
            updated_at=review.updated_at
        ))
    
    return ReviewListResponse(
        reviews=reviews,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + len(reviews)) < total
    )


@router.get("/{movie_id}/reviews/summary", response_model=ReviewSummary)
async def get_movie_reviews_summary(
    movie_id: int,
    session: Session = Depends(get_session)
):
    """Get review summary with rating breakdown for a movie."""
    # Check if movie exists
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    # Get all reviews for this movie
    reviews = session.exec(
        select(Review).where(
            Review.movie_id == movie_id,
            Review.is_deleted == False
        )
    ).all()
    
    if not reviews:
        return ReviewSummary(
            movie_id=movie_id,
            total_reviews=0,
            average_rating=0.0,
            rating_breakdown={1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        )
    
    # Calculate statistics
    total_reviews = len(reviews)
    total_rating = sum(review.rating for review in reviews)
    average_rating = round(total_rating / total_reviews, 2)
    
    # Calculate rating breakdown
    rating_breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating_breakdown[review.rating] += 1
    
    return ReviewSummary(
        movie_id=movie_id,
        total_reviews=total_reviews,
        average_rating=average_rating,
        rating_breakdown=rating_breakdown
    )


@router.get("/reviews/{review_id}", response_model=ReviewRead)
async def get_review(
    review_id: int,
    session: Session = Depends(get_session)
):
    """Get a single review by ID."""
    # Query with user join
    result = session.exec(
        select(Review, User.full_name, User.profile_picture_url).join(
            User, Review.user_id == User.id
        ).where(
            Review.id == review_id,
            Review.is_deleted == False
        )
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    review, reviewer_name, reviewer_avatar = result
    
    return ReviewRead(
        id=review.id,
        user_id=review.user_id,
        movie_id=review.movie_id,
        rating=review.rating,
        title=review.title,
        comment=review.comment,
        reviewerName=reviewer_name,
        reviewerAvatar=reviewer_avatar,
        likes=review.likes,
        dislikes=review.dislikes,
        created_at=review.created_at,
        updated_at=review.updated_at
    )


@router.put("/reviews/{review_id}", response_model=ReviewRead)
async def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update a review (only by the review author)."""
    review = session.get(Review, review_id)
    
    if not review or review.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check if current user is the author
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own reviews"
        )
    
    # Update review fields
    update_data = review_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    review.updated_at = datetime.utcnow()
    session.add(review)
    session.commit()
    session.refresh(review)
    
    return ReviewRead(
        id=review.id,
        user_id=review.user_id,
        movie_id=review.movie_id,
        rating=review.rating,
        title=review.title,
        comment=review.comment,
        reviewerName=current_user.full_name,
        reviewerAvatar=current_user.profile_picture_url,
        likes=review.likes,
        dislikes=review.dislikes,
        created_at=review.created_at,
        updated_at=review.updated_at
    )


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Delete a review (soft delete, only by author)."""
    review = session.get(Review, review_id)
    
    if not review or review.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check if current user is the author
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )
    
    # Soft delete
    review.is_deleted = True
    review.updated_at = datetime.utcnow()
    session.add(review)
    session.commit()
    
    return None


@router.post("/reviews/{review_id}/react", response_model=ReviewReactionResponse)
async def react_to_review(
    review_id: int,
    reaction: ReviewReaction,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Add a like or dislike reaction to a review. User can only react once (like OR dislike)."""
    review = session.get(Review, review_id)
    
    if not review or review.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Validate reaction type
    if reaction.reaction_type not in ["like", "dislike"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reaction_type must be 'like' or 'dislike'"
        )
    
    # Check if user already reacted to this review
    existing_reaction = session.exec(
        select(ReviewReactionModel).where(
            ReviewReactionModel.user_id == current_user.id,
            ReviewReactionModel.review_id == review_id
        )
    ).first()
    
    message = ""
    
    if existing_reaction:
        # User already reacted
        if existing_reaction.reaction_type == reaction.reaction_type:
            # Same reaction - remove it (toggle off)
            if existing_reaction.reaction_type == "like":
                review.likes = max(0, review.likes - 1)
            else:
                review.dislikes = max(0, review.dislikes - 1)
            
            session.delete(existing_reaction)
            message = f"Removed your {reaction.reaction_type}"
            user_reaction = None
        else:
            # Different reaction - switch it
            if existing_reaction.reaction_type == "like":
                review.likes = max(0, review.likes - 1)
                review.dislikes += 1
            else:
                review.dislikes = max(0, review.dislikes - 1)
                review.likes += 1
            
            existing_reaction.reaction_type = reaction.reaction_type
            existing_reaction.created_at = datetime.utcnow()
            session.add(existing_reaction)
            message = f"Changed your reaction to {reaction.reaction_type}"
            user_reaction = reaction.reaction_type
    else:
        # New reaction
        new_reaction = ReviewReactionModel(
            user_id=current_user.id,
            review_id=review_id,
            reaction_type=reaction.reaction_type
        )
        
        if reaction.reaction_type == "like":
            review.likes += 1
        else:
            review.dislikes += 1
        
        session.add(new_reaction)
        message = f"Added {reaction.reaction_type} to review"
        user_reaction = reaction.reaction_type
    
    review.updated_at = datetime.utcnow()
    session.add(review)
    session.commit()
    session.refresh(review)
    
    # Get user information for reviewer fields
    user = session.get(User, review.user_id)
    
    review_read = ReviewRead(
        id=review.id,
        user_id=review.user_id,
        movie_id=review.movie_id,
        rating=review.rating,
        title=review.title,
        comment=review.comment,
        reviewerName=user.full_name if user else "Unknown",
        reviewerAvatar=user.profile_picture_url if user else None,
        likes=review.likes,
        dislikes=review.dislikes,
        created_at=review.created_at,
        updated_at=review.updated_at
    )
    
    return ReviewReactionResponse(
        message=message,
        review=review_read,
        user_reaction=user_reaction
    )
