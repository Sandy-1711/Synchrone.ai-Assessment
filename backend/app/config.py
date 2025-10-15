"""
Configuration settings for Contract Intelligence System
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
from typing import Tuple

print(os.getenv("ALLOWED_EXTENSIONS"))


class Settings(BaseSettings):
    MONGO_URL: str
    MONGO_DB: str

    REDIS_URL: str = "redis://redis:6379"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-2"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-pro"

    MAX_FILE_SIZE: int = 52428800  # 50MB
    ALLOWED_EXTENSIONS: str = "pdf"
    UPLOAD_DIR: str = "/app/uploads"

    EXTRACTION_TIMEOUT: int = 300  # 5 minutes

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
