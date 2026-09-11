import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Smart Medicine Identification & Verification Platform"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database configuration
    # Default to local SQLite for instant, zero-setup hackathon development
    # Override with PostgreSQL URI via DATABASE_URL env var (e.g. Supabase, Neon, Render)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./medicine_platform.db")
    
    # Authentication & JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "smart-medicine-hackathon-super-secret-key-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days for hackathon ease
    
    # CORS settings (Allows Next.js web admin & Flutter mobile client)
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "*"
    ]
    
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")


settings = Settings()
