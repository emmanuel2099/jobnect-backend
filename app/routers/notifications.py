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
    """Get user notifications"""
    
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
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
