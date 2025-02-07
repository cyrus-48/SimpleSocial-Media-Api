from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
from app.api import deps
from app.core.config import settings
import os
from PIL import Image
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=schemas.Post)
def create_post(
    *,
    db: Session = Depends(deps.get_db),
    post_in: schemas.PostCreate,
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Create new post"""
    post = models.Post(
        **post_in.dict(),
        author_id=current_user.id
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@router.post("/{post_id}/image", response_model=schemas.Post)
async def upload_post_image(
    *,
    post_id: int,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Upload image for a post"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post or post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or not owned by user"
        )

    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type"
        )
    
    # Create media directory if it doesn't exist
    os.makedirs(settings.MEDIA_PATH, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"post_{post_id}_{timestamp}.jpg"
    file_path = os.path.join(settings.MEDIA_PATH, filename)
    
    try:
        with Image.open(file.file) as img:
            # Resize if needed while maintaining aspect ratio
            if img.height > 1080 or img.width > 1080:
                img.thumbnail((1080, 1080))
            img.save(file_path, "JPEG")
        
        post.image_url = filename
        db.add(post)
        db.commit()
        db.refresh(post)
        return post
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not process image"
        )

@router.get("/", response_model=List[schemas.PostWithInteractions])
def get_posts(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 20,
    current_user: Optional[models.User] = Depends(deps.get_optional_current_user)
) -> Any:
    """Get all posts with optional pagination"""
    posts = db.query(models.Post)\
        .order_by(models.Post.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    # Add interaction info if user is logged in
    if current_user:
        for post in posts:
            post.user_has_liked = any(like.user_id == current_user.id for like in post.likes)
            post.likes_count = len(post.likes)
            post.comments_count = len(post.comments)
    
    return posts

@router.get("/feed", response_model=List[schemas.PostWithInteractions])
def get_feed(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Get posts from followed users"""
    following_ids = [user.id for user in current_user.following]
    following_ids.append(current_user.id)  # Include own posts
    
    posts = db.query(models.Post)\
        .filter(models.Post.author_id.in_(following_ids))\
        .order_by(models.Post.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    # Add interaction info
    for post in posts:
        post.user_has_liked = any(like.user_id == current_user.id for like in post.likes)
        post.likes_count = len(post.likes)
        post.comments_count = len(post.comments)
    
    return posts

@router.get("/{post_id}", response_model=schemas.PostWithInteractions)
def get_post(
    *,
    post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(deps.get_optional_current_user)
) -> Any:
    """Get post by ID"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if current_user:
        post.user_has_liked = any(like.user_id == current_user.id for like in post.likes)
        post.likes_count = len(post.likes)
        post.comments_count = len(post.comments)
    
    return post

@router.put("/{post_id}", response_model=schemas.Post)
def update_post(
    *,
    post_id: int,
    post_in: schemas.PostUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Update post"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post or post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or not owned by user"
        )
    
    for field, value in post_in.dict(exclude_unset=True).items():
        setattr(post, field, value)
    
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@router.delete("/{post_id}")
def delete_post(
    *,
    post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Delete post"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post or post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or not owned by user"
        )
    
    # Delete post image if exists
    if post.image_url:
        image_path = os.path.join(settings.MEDIA_PATH, post.image_url)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.delete(post)
    db.commit()
    return {"status": "success"}

@router.post("/{post_id}/like", response_model=schemas.Post)
def like_post(
    *,
    post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Like a post"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if already liked
    like = db.query(models.Like).filter(
        models.Like.post_id == post_id,
        models.Like.user_id == current_user.id
    ).first()
    
    if like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already liked"
        )
    
    like = models.Like(post_id=post_id, user_id=current_user.id)
    db.add(like)
    db.commit()
    db.refresh(post)
    return post

@router.delete("/{post_id}/unlike", response_model=schemas.Post)
def unlike_post(
    *,
    post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Unlike a post"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    like = db.query(models.Like).filter(
        models.Like.post_id == post_id,
        models.Like.user_id == current_user.id
    ).first()
    
    if not like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not liked"
        )
    
    db.delete(like)
    db.commit()
    db.refresh(post)
    return post

@router.post("/{post_id}/comments", response_model=schemas.Comment)
def create_comment(
    *,
    post_id: int,
    comment_in: schemas.CommentCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
) -> Any:
    """Create comment on a post"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    comment = models.Comment(
        **comment_in.dict(),
        author_id=current_user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.get("/{post_id}/comments", response_model=List[schemas.Comment])
def get_comments(
    *,
    post_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(deps.get_db)
) -> Any:
    """Get comments for a post"""
    comments = db.query(models.Comment)\
        .filter(models.Comment.post_id == post_id)\
        .order_by(models.Comment.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return comments