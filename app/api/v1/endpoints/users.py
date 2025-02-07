from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.core.config import settings
import os
from PIL import Image
import shutil
from datetime import datetime

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Get current user"""
    return current_user

@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Update own user profile"""
    if user_in.email and user_in.email != current_user.email:
        if db.query(models.User).filter(models.User.email == user_in.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    if user_in.username and user_in.username != current_user.username:
        if db.query(models.User).filter(models.User.username == user_in.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    for field, value in user_in.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/me/profile-picture", response_model=schemas.User)
async def upload_profile_picture(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Upload profile picture"""
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type"
        )
    
    # Create media directory if it doesn't exist
    os.makedirs(settings.MEDIA_PATH, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"profile_{current_user.id}_{timestamp}.jpg"
    file_path = os.path.join(settings.MEDIA_PATH, filename)
    
    try:
        # Save and process image
        with Image.open(file.file) as img:
            # Resize image if needed
            if img.height > 500 or img.width > 500:
                img.thumbnail((500, 500))
            img.save(file_path, "JPEG")
        
        # Update user profile
        current_user.profile_picture = filename
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        return current_user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not process image"
        )

@router.get("/{username}", response_model=schemas.UserWithFollowInfo)
def get_user_by_username(
    username: str,
    db: Session = Depends(deps.get_db)
) -> Any:
    """Get user by username"""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Add follower counts
    setattr(user, 'followers_count', len(user.followers))
    setattr(user, 'following_count', len(user.following))
    return user

@router.post("/{username}/follow", response_model=schemas.User)
def follow_user(
    username: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Follow a user"""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users cannot follow themselves"
        )
    
    if user in current_user.following:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )
    
    current_user.following.append(user)
    db.commit()
    return user

@router.delete("/{username}/unfollow", response_model=schemas.User)
def unfollow_user(
    username: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Unfollow a user"""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user not in current_user.following:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not following this user"
        )
    
    current_user.following.remove(user)
    db.commit()
    return user