from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Feedback, User, Company, Job
from app.schemas import FeedbackCreate, FeedbackResponse, FeedbackListResponse, StandardResponse
from app.auth import get_current_user

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.post("/", response_model=StandardResponse)
def create_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create feedback for a company (job seekers only)
    """
    # Verify user is a job seeker
    if current_user.user_type != "applicant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can submit feedback"
        )
    
    # Verify company exists
    company = db.query(Company).filter(Company.id == feedback_data.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # If job_id is provided, verify job exists and belongs to the company
    if feedback_data.job_id:
        job = db.query(Job).filter(
            Job.id == feedback_data.job_id,
            Job.company_id == feedback_data.company_id
        ).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found or does not belong to this company"
            )
    
    # Validate rating
    if feedback_data.rating < 1 or feedback_data.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    # Check if user has already submitted feedback for this company/job combination
    existing_feedback = db.query(Feedback).filter(
        Feedback.job_seeker_id == current_user.id,
        Feedback.company_id == feedback_data.company_id,
        Feedback.job_id == feedback_data.job_id
    ).first()
    
    if existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted feedback for this company/job"
        )
    
    # Create feedback
    feedback = Feedback(
        job_seeker_id=current_user.id,
        company_id=feedback_data.company_id,
        job_id=feedback_data.job_id,
        rating=feedback_data.rating,
        feedback_text=feedback_data.feedback_text,
        feedback_type=feedback_data.feedback_type,
        is_anonymous=feedback_data.is_anonymous,
        is_public=feedback_data.is_public
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return StandardResponse(
        success=True,
        message="Feedback submitted successfully",
        data={"feedback_id": feedback.id}
    )

@router.get("/my-feedback", response_model=FeedbackListResponse)
def get_my_feedback(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get feedback submitted by the current user (job seekers only)
    """
    if current_user.user_type != "applicant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can view their feedback"
        )
    
    offset = (page - 1) * per_page
    
    feedbacks = db.query(Feedback).filter(
        Feedback.job_seeker_id == current_user.id
    ).order_by(Feedback.created_at.desc()).offset(offset).limit(per_page).all()
    
    total = db.query(Feedback).filter(Feedback.job_seeker_id == current_user.id).count()
    
    return FeedbackListResponse(
        feedbacks=feedbacks,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/company/{company_id}", response_model=FeedbackListResponse)
def get_company_feedback(
    company_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    include_private: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get feedback for a company (companies can see all their feedback, others see only public)
    """
    # Verify company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    offset = (page - 1) * per_page
    
    # Build query based on user permissions
    if current_user.user_type == "company":
        # Check if current user owns this company
        user_company = db.query(Company).filter(
            Company.id == company_id,
            Company.user_id == current_user.id
        ).first()
        
        if user_company:
            # Company owners can see all feedback for their company
            feedbacks = db.query(Feedback).filter(
                Feedback.company_id == company_id
            ).order_by(Feedback.created_at.desc()).offset(offset).limit(per_page).all()
            
            total = db.query(Feedback).filter(Feedback.company_id == company_id).count()
        else:
            # Other companies can only see public feedback
            feedbacks = db.query(Feedback).filter(
                Feedback.company_id == company_id,
                Feedback.is_public == True,
                Feedback.status == "approved"
            ).order_by(Feedback.created_at.desc()).offset(offset).limit(per_page).all()
            
            total = db.query(Feedback).filter(
                Feedback.company_id == company_id,
                Feedback.is_public == True,
                Feedback.status == "approved"
            ).count()
    else:
        # Job seekers can only see public, approved feedback
        feedbacks = db.query(Feedback).filter(
            Feedback.company_id == company_id,
            Feedback.is_public == True,
            Feedback.status == "approved"
        ).order_by(Feedback.created_at.desc()).offset(offset).limit(per_page).all()
        
        total = db.query(Feedback).filter(
            Feedback.company_id == company_id,
            Feedback.is_public == True,
            Feedback.status == "approved"
        ).count()
    
    return FeedbackListResponse(
        feedbacks=feedbacks,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/job/{job_id}", response_model=FeedbackListResponse)
def get_job_feedback(
    job_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get feedback for a specific job (public only)
    """
    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    offset = (page - 1) * per_page
    
    # Only show public, approved feedback for jobs
    feedbacks = db.query(Feedback).filter(
        Feedback.job_id == job_id,
        Feedback.is_public == True,
        Feedback.status == "approved"
    ).order_by(Feedback.created_at.desc()).offset(offset).limit(per_page).all()
    
    total = db.query(Feedback).filter(
        Feedback.job_id == job_id,
        Feedback.is_public == True,
        Feedback.status == "approved"
    ).count()
    
    return FeedbackListResponse(
        feedbacks=feedbacks,
        total=total,
        page=page,
        per_page=per_page
    )

@router.put("/{feedback_id}", response_model=StandardResponse)
def update_feedback(
    feedback_id: int,
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update feedback (only by original author)
    """
    if current_user.user_type != "applicant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can update feedback"
        )
    
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # Check if user owns this feedback
    if feedback.job_seeker_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own feedback"
        )
    
    # Validate rating
    if feedback_data.rating < 1 or feedback_data.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    # Update feedback
    feedback.rating = feedback_data.rating
    feedback.feedback_text = feedback_data.feedback_text
    feedback.feedback_type = feedback_data.feedback_type
    feedback.is_anonymous = feedback_data.is_anonymous
    feedback.is_public = feedback_data.is_public
    
    db.commit()
    
    return StandardResponse(
        success=True,
        message="Feedback updated successfully"
    )

@router.delete("/{feedback_id}", response_model=StandardResponse)
def delete_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete feedback (only by original author)
    """
    if current_user.user_type != "applicant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only job seekers can delete feedback"
        )
    
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # Check if user owns this feedback
    if feedback.job_seeker_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own feedback"
        )
    
    db.delete(feedback)
    db.commit()
    
    return StandardResponse(
        success=True,
        message="Feedback deleted successfully"
    )
