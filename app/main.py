from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, users, posts
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
import os

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Create media directory if it doesn't exist
os.makedirs(settings.MEDIA_PATH, exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentication"]
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["users"]
)

app.include_router(
    posts.router,
    prefix=f"{settings.API_V1_STR}/posts",
    tags=["posts"]
)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}