from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.database import get_db
from app.models import User, Company, Job, Review
from app.schemas import ReviewCreate, ReviewResponse, ReviewListResponse
from typing import List, Optional

router = APIRouter(prefix="/reviews", tags=["Reviews"])

# Create a review
@router.post("/")
def create_review(
    request: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new review"""
    
    # Check if user is job seeker (reviewing company/job)
    if current_user.user_type != "applicant":
        raise HTTPException(status_code=403, detail="Only job seekers can write reviews")
    
    # Validate rating
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5 stars")
    
    try:
        # Create review
        review = Review(
            company_id=request.company_id,
            user_id=current_user.id,
            job_id=request.job_id,
            rating=request.rating,
            title=request.title,
            content=request.content,
            pros=request.pros,
            cons=request.cons,
            is_anonymous=request.is_anonymous,
            is_verified=False  # Initially unverified
        )
        
        db.add(review)
        db.commit()
        
        return {
            "success": True,
            "message": "Review submitted successfully",
            "data": {
                "review_id": review.id,
                "status": "pending_verification"
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create review: {str(e)}")

# Get reviews for company
@router.get("/company/{company_id}")
def get_company_reviews(
    company_id: int,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get all reviews for a specific company"""
    
    try:
        # Get total count
        total = db.query(Review).filter(Review.company_id == company_id).count()
        
        # Get paginated reviews
        reviews = db.query(Review).filter(Review.company_id == company_id)\
            .order_by(Review.created_at.desc())\
            .offset((page - 1) * limit)\
            .limit(limit)\
            .all()
        
        # Convert to response format
        review_responses = []
        for review in reviews:
            review_responses.append({
                "id": review.id,
                "user_id": review.user_id,
                "job_id": review.job_id,
                "rating": review.rating,
                "title": review.title,
                "content": review.content,
                "pros": review.pros,
                "cons": review.cons,
                "is_anonymous": review.is_anonymous,
                "is_verified": review.is_verified,
                "created_at": review.created_at.isoformat(),
                "updated_at": review.updated_at.isoformat() if review.updated_at else review.created_at.isoformat()
            })
        
        return {
            "success": True,
            "message": "Reviews retrieved successfully",
            "data": {
                "reviews": review_responses,
                "total": total,
                "page": page,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reviews: {str(e)}")

# Get reviews for job
@router.get("/job/{job_id}")
def get_job_reviews(
    job_id: int,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get all reviews for a specific job"""
    
    try:
        # Get total count
        total = db.query(Review).filter(Review.job_id == job_id).count()
        
        # Get paginated reviews
        reviews = db.query(Review).filter(Review.job_id == job_id)\
            .order_by(Review.created_at.desc())\
            .offset((page - 1) * limit)\
            .limit(limit)\
            .all()
        
        # Convert to response format
        review_responses = []
        for review in reviews:
            review_responses.append({
                "id": review.id,
                "user_id": review.user_id,
                "company_id": review.company_id,
                "job_id": review.job_id,
                "rating": review.rating,
                "title": review.title,
                "content": review.content,
                "pros": review.pros,
                "cons": review.cons,
                "is_anonymous": review.is_anonymous,
                "is_verified": review.is_verified,
                "created_at": review.created_at.isoformat(),
                "updated_at": review.updated_at.isoformat() if review.updated_at else review.created_at.isoformat()
            })
        
        return {
            "success": True,
            "message": "Reviews retrieved successfully",
            "data": {
                "reviews": review_responses,
                "total": total,
                "page": page,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reviews: {str(e)}")

# Get company's average rating
@router.get("/company/{company_id}/rating")
def get_company_rating(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Get company's average rating"""
    
    try:
        # Calculate average rating
        reviews = db.query(Review).filter(Review.company_id == company_id).all()
        
        if not reviews:
            return {
                "success": True,
                "message": "No reviews found",
                "data": {
                    "average_rating": 0,
                    "total_reviews": 0
                }
            }
        
        total_rating = sum(review.rating for review in reviews)
        average_rating = total_rating / len(reviews)
        
        return {
            "success": True,
            "message": "Company rating retrieved successfully",
            "data": {
                "average_rating": round(average_rating, 2),
                "total_reviews": len(reviews)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get rating: {str(e)}")

# Verify review (company action)
@router.put("/{review_id}/verify")
def verify_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify a review (company only)"""
    
    # Check if user is from company
    if current_user.user_type != "company":
        raise HTTPException(status_code=403, detail="Only companies can verify reviews")
    
    try:
        # Get review
        review = db.query(Review).filter(Review.id == review_id).first()
        
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Check if review belongs to user's company
        company = db.query(Company).filter(Company.id == review.company_id).first()
        if not company or company.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only verify reviews for your company")
        
        # Update verification status
        review.is_verified = True
        db.commit()
        
        return {
            "success": True,
            "message": "Review verified successfully",
            "data": {
                "review_id": review.id,
                "is_verified": True
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to verify review: {str(e)}")

# Get user's reviews
@router.get("/my-reviews")
def get_my_reviews(
    current_user: User = Depends(get_current_user),
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get current user's reviews"""
    
    try:
        # Get total count
        total = db.query(Review).filter(Review.user_id == current_user.id).count()
        
        # Get paginated reviews
        reviews = db.query(Review).filter(Review.user_id == current_user.id)\
            .order_by(Review.created_at.desc())\
            .offset((page - 1) * limit)\
            .limit(limit)\
            .all()
        
        # Convert to response format
        review_responses = []
        for review in reviews:
            review_responses.append({
                "id": review.id,
                "company_id": review.company_id,
                "job_id": review.job_id,
                "rating": review.rating,
                "title": review.title,
                "content": review.content,
                "pros": review.pros,
                "cons": review.cons,
                "is_anonymous": review.is_anonymous,
                "is_verified": review.is_verified,
                "created_at": review.created_at.isoformat(),
                "updated_at": review.updated_at.isoformat() if review.updated_at else review.created_at.isoformat()
            })
        
        return {
            "success": True,
            "message": "Your reviews retrieved successfully",
            "data": {
                "reviews": review_responses,
                "total": total,
                "page": page,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reviews: {str(e)}")
