from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from .user import User

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: int

class Comment(CommentBase):
    id: int
    post_id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: User

    class Config:
        from_attributes = True

class LikeBase(BaseModel):
    post_id: int

class Like(LikeBase):
    id: int
    user_id: int
    created_at: datetime
    user: User

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    content: str
    image_url: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    content: Optional[str] = None
    image_url: Optional[str] = None

class Post(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: User
    comments: List[Comment] = []
    likes: List[Like] = []
    likes_count: int = 0
    comments_count: int = 0

    class Config:
        from_attributes = True

class PostWithInteractions(Post):
    user_has_liked: bool = False