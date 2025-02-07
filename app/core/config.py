from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Base Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Social Media API"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # Media
    MEDIA_PATH: str = os.getenv("MEDIA_PATH")
    ALLOWED_IMAGE_TYPES: set = {"image/jpeg", "image/png", "image/gif"}
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB

    class Config:
        case_sensitive = True

@lru_cache() 
def get_settings():
    return Settings()

settings = get_settings()