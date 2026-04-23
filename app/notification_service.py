"""
Notification Service - Creates notifications for various events
"""
from sqlalchemy.orm import Session
from app.models import Notification, User, Job, JobApplication, Message
from datetime import datetime


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
    related_id: int = None
):
    """Create a new notification"""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        related_id=related_id,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()
    return notification


def notify_new_message(db: Session, sender_id: int, receiver_id: int, message_text: str):
    """Notify user when they receive a new message"""
    sender = db.query(User).filter(User.id == sender_id).first()
    if sender:
        create_notification(
            db=db,
            user_id=receiver_id,
            title="New Message",
            message=f"{sender.name} sent you a message: {message_text[:50]}...",
            notification_type="message",
            related_id=sender_id
        )


def notify_job_application(db: Session, job_id: int, applicant_id: int):
    """Notify company when someone applies for their job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    applicant = db.query(User).filter(User.id == applicant_id).first()
    
    if job and applicant and job.company:
        # Notify the company owner
        company_owner = db.query(User).filter(User.company == job.company.name).first()
        if company_owner:
            create_notification(
                db=db,
                user_id=company_owner.id,
                title="New Job Application",
                message=f"{applicant.name} applied for {job.title}",
                notification_type="application",
                related_id=job_id
            )


def notify_application_status_change(db: Session, application_id: int, status: str):
    """Notify applicant when their application status changes"""
    application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    
    if application and application.job:
        status_messages = {
            "accepted": f"Congratulations! Your application for {application.job.title} has been accepted",
            "rejected": f"Your application for {application.job.title} was not successful this time",
            "under_review": f"Your application for {application.job.title} is under review",
            "shortlisted": f"Great news! You've been shortlisted for {application.job.title}"
        }
        
        message = status_messages.get(status, f"Your application status for {application.job.title} has been updated")
        
        create_notification(
            db=db,
            user_id=application.user_id,
            title="Application Status Update",
            message=message,
            notification_type="application_status",
            related_id=application.job_id
        )


def notify_new_job_posted(db: Session, job_id: int):
    """Notify all job seekers when a new job is posted"""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if job:
        # Get all job seekers (users without company)
        job_seekers = db.query(User).filter(
            (User.company == None) | (User.company == 'N/A')
        ).all()
        
        for seeker in job_seekers:
            create_notification(
                db=db,
                user_id=seeker.id,
                title="New Job Posted",
                message=f"New opportunity: {job.title} at {job.company.name if job.company else 'a company'}",
                notification_type="new_job",
                related_id=job_id
            )


def notify_interview_scheduled(db: Session, application_id: int, interview_date: str):
    """Notify applicant when interview is scheduled"""
    application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    
    if application and application.job:
        create_notification(
            db=db,
            user_id=application.user_id,
            title="Interview Scheduled",
            message=f"Interview scheduled for {application.job.title} on {interview_date}",
            notification_type="interview",
            related_id=application.job_id
        )
