"""
Review System Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)  # Job reviews (by job seekers)
    company_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Company reviews (by job seekers)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(200), nullable=False)
    comment = Column(Text, nullable=False)
    is_verified = Column(Boolean, default=False)  # Admin verified
    is_helpful = Column(Integer, default=0)  # Number of people who found it helpful
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    reviewed_user = relationship("User", foreign_keys=[reviewed_user_id], back_populates="reviews_received")
    job = relationship("Job", foreign_keys=[job_id], back_populates="reviews")
    company = relationship("User", foreign_keys=[company_id], back_populates="company_reviews")

class ReviewResponse(Base):
    __tablename__ = "review_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    responder_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    review = relationship("Review", foreign_keys=[review_id], back_populates="responses")
    responder = relationship("User", foreign_keys=[responder_id], back_populates="review_responses")
