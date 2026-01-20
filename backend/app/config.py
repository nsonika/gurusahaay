"""
Application configuration loaded from environment variables.
Uses pydantic-settings for type-safe config management.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/gurusahaay"
    
    # JWT Authentication
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # Gemini API (optional - for summarization/translation only)
    gemini_api_key: str = ""
    
    # Whisper model size
    whisper_model_size: str = "base"
    
    # Cloudinary (for file uploads)
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance to avoid re-reading env on every request."""
    return Settings()
