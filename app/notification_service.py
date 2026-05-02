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
    related_id: int = None,
    user_type: str = None  # 'job_seeker', 'company', or None for legacy
):
    """Create a new notification - supports all user types"""
    from app.models import JobSeeker, CompanyUser

    # Determine which column to use
    job_seeker_id = None
    company_user_id = None
    legacy_user_id = None

    if user_type == 'job_seeker':
        job_seeker_id = user_id
    elif user_type == 'company':
        company_user_id = user_id
    else:
        # Auto-detect: check which table the user belongs to
        if db.query(JobSeeker).filter(JobSeeker.id == user_id).first():
            job_seeker_id = user_id
        elif db.query(CompanyUser).filter(CompanyUser.id == user_id).first():
            company_user_id = user_id
        else:
            legacy_user_id = user_id

    notification = Notification(
        user_id=legacy_user_id,
        job_seeker_id=job_seeker_id,
        company_user_id=company_user_id,
        title=title,
        message=message,
        notification_type=notification_type,
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
    from app.models import JobSeeker, CompanyUser

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or not job.company:
        return

    # Get applicant name
    applicant_name = "A job seeker"
    applicant = (
        db.query(JobSeeker).filter(JobSeeker.id == applicant_id).first()
        or db.query(User).filter(User.id == applicant_id).first()
    )
    if applicant:
        applicant_name = applicant.name

    # Find the company user who owns this job
    company_user = None
    if job.company.company_user_id:
        company_user = db.query(CompanyUser).filter(
            CompanyUser.id == job.company.company_user_id
        ).first()
    if not company_user and job.company.email:
        company_user = db.query(CompanyUser).filter(
            CompanyUser.email == job.company.email
        ).first()

    if company_user:
        # Store in-app notification using company_user.id
        create_notification(
            db=db,
            user_id=company_user.id,
            title="New Job Application",
            message=f"{applicant_name} applied for {job.title}",
            notification_type="application",
            related_id=job_id
        )


def notify_application_status_change(db: Session, application_id: int, status: str):
    """Notify applicant when their application status changes"""
    application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    
    if application and application.job:
        status_messages = {
            "approved": f"Congratulations! Your application for {application.job.title} has been approved",
            "accepted": f"Congratulations! Your application for {application.job.title} has been accepted",
            "rejected": f"Your application for {application.job.title} was not successful this time",
            "under_review": f"Your application for {application.job.title} is under review",
            "shortlisted": f"Great news! You've been shortlisted for {application.job.title}"
        }
        
        message = status_messages.get(status, f"Your application status for {application.job.title} has been updated")
        
        create_notification(
            db=db,
            user_id=application.user_id,
            title="Application Approved!" if status == "approved" else "Application Status Update",
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

        # Send FCM push notifications to all job seekers
        try:
            from app.fcm_service import send_job_alert_to_all
            company_name = job.company.name if job.company else "a company"
            location = job.location or ""
            sent = send_job_alert_to_all(db, job.title, company_name, job_id, location)
            print(f"   📱 FCM push notifications sent to {sent} devices")
        except Exception as e:
            print(f"   ⚠️  FCM push notification failed: {e}")


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
