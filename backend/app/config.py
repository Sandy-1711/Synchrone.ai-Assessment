"""
Configuration settings for Contract Intelligence System
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    
    MONGO_URL: str = "mongodb://contract_user:secure_password_123@mongodb:27017/contract_intelligence?authSource=admin"
    MONGO_DB: str = "contract_intelligence"
    
    REDIS_URL: str = "redis://redis:6379"
    
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-pro"
    
    MAX_FILE_SIZE: int = 52428800  # 50MB
    ALLOWED_EXTENSIONS: list = ["pdf"]
    UPLOAD_DIR: str = "/app/uploads"
    
    EXTRACTION_TIMEOUT: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()