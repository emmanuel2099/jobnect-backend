from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import uuid
from pathlib import Path

from app.database import get_db
from app.models import User
from app.auth import get_current_user

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload/profile-photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile photo"""
    
    # Validate file type by content_type and extension
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    allowed_extensions = ["jpg", "jpeg", "png", "webp"]
    
    file_extension = file.filename.split(".")[-1].lower() if file.filename else ""
    
    # Check both content_type and extension
    if file.content_type not in allowed_types and file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Only JPG, PNG, and WEBP are allowed. Received: {file.content_type}, extension: {file_extension}"
        )
    
    # Validate file size (5MB max)
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Update user profile photo URL
    photo_url = f"https://jobnect-backend.onrender.com/static/uploads/{unique_filename}"
    current_user.profile_photo = photo_url
    db.commit()
    
    return {
        "success": True,
        "message": "Profile photo uploaded successfully",
        "data": {
            "photoUrl": photo_url
        }
    }

@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload any image and return URL"""
    
    # Validate file type by content_type and extension
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    allowed_extensions = ["jpg", "jpeg", "png", "webp"]
    
    file_extension = file.filename.split(".")[-1].lower() if file.filename else ""
    
    # Check both content_type and extension
    if file.content_type not in allowed_types and file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Only JPG, PNG, and WEBP are allowed. Received: {file.content_type}, extension: {file_extension}"
        )
    
    # Validate file size (5MB max)
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Return URL
    image_url = f"https://jobnect-backend.onrender.com/static/uploads/{unique_filename}"
    
    return {
        "success": True,
        "message": "Image uploaded successfully",
        "data": {
            "imageUrl": image_url
        }
    }

@router.post("/upload/company-logo")
async def upload_company_logo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload company logo"""
    
    # Validate file type by content_type and extension
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    allowed_extensions = ["jpg", "jpeg", "png", "webp"]
    
    file_extension = file.filename.split(".")[-1].lower() if file.filename else ""
    
    # Check both content_type and extension
    if file.content_type not in allowed_types and file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Only JPG, PNG, and WEBP are allowed. Received: {file.content_type}, extension: {file_extension}"
        )
    
    # Validate file size (5MB max)
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Update user company logo URL
    logo_url = f"https://jobnect-backend.onrender.com/static/uploads/{unique_filename}"
    current_user.company_logo = logo_url
    db.commit()
    
    return {
        "success": True,
        "message": "Company logo uploaded successfully",
        "data": {
            "logoUrl": logo_url
        }
    }
