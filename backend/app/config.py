import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "EcoMind AI"
    TAGLINE: str = "Evidence-Grounded AI for Biodiversity Intelligence"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ecomind.db")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./knowledge/processed/chroma_db")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
