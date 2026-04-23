from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import User, Conversation, Message
from app.auth import get_current_user
from app.notification_service import notify_new_message
from pydantic import BaseModel

router = APIRouter(prefix="/api/v10/chat", tags=["chat"])


class SendMessageRequest(BaseModel):
    conversation_id: int
    message: str


class CreateConversationRequest(BaseModel):
    other_user_id: int


@router.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user"""
    try:
        # Get conversations where user is either user1 or user2
        conversations = db.query(Conversation).filter(
            or_(
                Conversation.user1_id == current_user.id,
                Conversation.user2_id == current_user.id
            )
        ).order_by(Conversation.updated_at.desc()).all()

        result = []
        for conv in conversations:
            # Determine the other user
            other_user_id = conv.user2_id if conv.user1_id == current_user.id else conv.user1_id
            other_user = db.query(User).filter(User.id == other_user_id).first()

            # Get last message
            last_message = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(Message.created_at.desc()).first()

            # Count unread messages
            unread_count = db.query(Message).filter(
                and_(
                    Message.conversation_id == conv.id,
                    Message.receiver_id == current_user.id,
                    Message.is_read == False
                )
            ).count()

            result.append({
                "id": conv.id,
                "user1_id": conv.user1_id,
                "user2_id": conv.user2_id,
                "other_user": {
                    "id": other_user.id,
                    "name": other_user.name,
                    "email": other_user.email,
                    "profile_photo": other_user.profile_photo,
                    "company_logo": other_user.company_logo,
                    "company": other_user.company,
                    "user_type": "company" if other_user.company and other_user.company != "N/A" else "applicant"
                } if other_user else None,
                "last_message": {
                    "id": last_message.id,
                    "message": last_message.message,
                    "sender_id": last_message.sender_id,
                    "created_at": last_message.created_at.isoformat() if last_message.created_at else None
                } if last_message else None,
                "unread_count": unread_count,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
            })

        return {"conversations": result}

    except Exception as e:
        print(f"Error fetching conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{conversation_id}")
async def get_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages for a conversation"""
    try:
        # Verify user is part of the conversation
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this conversation")

        # Get messages
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()

        # Mark messages as read
        db.query(Message).filter(
            and_(
                Message.conversation_id == conversation_id,
                Message.receiver_id == current_user.id,
                Message.is_read == False
            )
        ).update({"is_read": True})
        db.commit()

        result = [{
            "id": msg.id,
            "conversation_id": msg.conversation_id,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "message": msg.message,
            "is_read": msg.is_read,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
            "updated_at": msg.updated_at.isoformat() if msg.updated_at else None
        } for msg in messages]

        return {"messages": result}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send")
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in a conversation"""
    try:
        # Verify conversation exists and user is part of it
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Determine receiver
        receiver_id = conversation.user2_id if conversation.user1_id == current_user.id else conversation.user1_id

        # Create message
        new_message = Message(
            conversation_id=request.conversation_id,
            sender_id=current_user.id,
            receiver_id=receiver_id,
            message=request.message,
            is_read=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(new_message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(new_message)
        
        # Send notification to receiver
        try:
            notify_new_message(db, current_user.id, receiver_id, request.message)
        except Exception as notif_error:
            print(f"Failed to send message notification: {notif_error}")

        return {
            "message": {
                "id": new_message.id,
                "conversation_id": new_message.conversation_id,
                "sender_id": new_message.sender_id,
                "receiver_id": new_message.receiver_id,
                "message": new_message.message,
                "is_read": new_message.is_read,
                "created_at": new_message.created_at.isoformat() if new_message.created_at else None,
                "updated_at": new_message.updated_at.isoformat() if new_message.updated_at else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation/create")
async def create_conversation(
    request: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation or return existing one"""
    try:
        # Check if conversation already exists
        existing_conversation = db.query(Conversation).filter(
            or_(
                and_(
                    Conversation.user1_id == current_user.id,
                    Conversation.user2_id == request.other_user_id
                ),
                and_(
                    Conversation.user1_id == request.other_user_id,
                    Conversation.user2_id == current_user.id
                )
            )
        ).first()

        if existing_conversation:
            return {"conversation": {
                "id": existing_conversation.id,
                "user1_id": existing_conversation.user1_id,
                "user2_id": existing_conversation.user2_id,
                "created_at": existing_conversation.created_at.isoformat() if existing_conversation.created_at else None
            }}

        # Create new conversation
        new_conversation = Conversation(
            user1_id=current_user.id,
            user2_id=request.other_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)

        return {"conversation": {
            "id": new_conversation.id,
            "user1_id": new_conversation.user1_id,
            "user2_id": new_conversation.user2_id,
            "created_at": new_conversation.created_at.isoformat() if new_conversation.created_at else None
        }}

    except Exception as e:
        db.rollback()
        print(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-read/{conversation_id}")
async def mark_messages_as_read(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all messages in a conversation as read"""
    try:
        db.query(Message).filter(
            and_(
                Message.conversation_id == conversation_id,
                Message.receiver_id == current_user.id,
                Message.is_read == False
            )
        ).update({"is_read": True})

        db.commit()

        return {"success": True, "message": "Messages marked as read"}

    except Exception as e:
        db.rollback()
        print(f"Error marking messages as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))
