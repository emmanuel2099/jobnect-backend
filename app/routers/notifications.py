from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models import Notification, User
from app.auth import get_current_user

router = APIRouter()

@router.get("/notifications")
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications - works for job seekers, companies, and legacy users"""
    from app.models import JobSeeker, CompanyUser

    # Determine the correct user_id to query
    user_id = current_user.id

    notifications = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(desc(Notification.created_at)).limit(50).all()

    notifications_data = [{
        "id": notif.id,
        "title": notif.title,
        "message": notif.message,
        "type": notif.notification_type,
        "isRead": notif.is_read,
        "createdAt": notif.created_at.isoformat() if notif.created_at else None
    } for notif in notifications]

    return {
        "success": True,
        "message": "Notifications retrieved",
        "data": {"notifications": notifications_data}
    }

@router.post("/notifications/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        return {
            "success": False,
            "message": "Notification not found",
            "data": {}
        }
    
    notification.is_read = True
    db.commit()
    
    return {
        "success": True,
        "message": "Notification marked as read",
        "data": {}
    }

@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {
        "success": True,
        "message": "All notifications marked as read",
        "data": {}
    }

@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        return {
            "success": False,
            "message": "Notification not found",
            "data": {}
        }
    
    db.delete(notification)
    db.commit()
    
    return {
        "success": True,
        "message": "Notification deleted",
        "data": {}
    }

@router.get("/notifications/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {
        "success": True,
        "message": "Unread count retrieved",
        "data": {"unreadCount": count}
    }


# FCM Token endpoints
from pydantic import BaseModel

class FCMTokenRequest(BaseModel):
    fcm_token: str

@router.post("/fcm-token")
async def update_fcm_token(
    request: FCMTokenRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's FCM token for push notifications."""
    from app.models import JobSeeker, CompanyUser

    if isinstance(current_user, JobSeeker) or (hasattr(current_user, 'user_type') and current_user.user_type == 'applicant'):
        user = db.query(JobSeeker).filter(JobSeeker.id == current_user.id).first()
    else:
        user = db.query(CompanyUser).filter(CompanyUser.id == current_user.id).first()

    if user:
        user.fcm_token = request.fcm_token
        db.commit()
        return {"success": True, "message": "FCM token updated"}
    return {"success": False, "message": "User not found"}


@router.post("/send-test-notification")
async def send_test_notification(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a test push notification to the current user."""
    from app.models import JobSeeker, CompanyUser
    from app.fcm_service import send_notification_to_token

    if isinstance(current_user, JobSeeker) or (hasattr(current_user, 'user_type') and current_user.user_type == 'applicant'):
        user = db.query(JobSeeker).filter(JobSeeker.id == current_user.id).first()
    else:
        user = db.query(CompanyUser).filter(CompanyUser.id == current_user.id).first()

    if not user or not user.fcm_token:
        raise HTTPException(status_code=400, detail="No FCM token found. Open the app first.")

    success = send_notification_to_token(
        user.fcm_token,
        "Test Notification",
        "Eagle's Pride push notifications are working!",
        {"type": "test"}
    )
    return {"success": success, "message": "Notification sent" if success else "Failed to send"}
