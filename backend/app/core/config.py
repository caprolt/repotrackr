from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "RepoTrackr"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RepoTrackr"
    VERSION: str = "0.1.0"
    
    # Database - Support both local and Supabase
    DATABASE_URL: str = "postgresql+asyncpg://repotrackr:repotrackr_dev@localhost:5432/repotrackr"
    DATABASE_URL_SYNC: str = "postgresql://repotrackr:repotrackr_dev@localhost:5432/repotrackr"
    
    # Supabase Configuration (optional)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # GitHub (for future use)
    GITHUB_TOKEN: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("DATABASE_URL", "DATABASE_URL_SYNC", pre=True)
    def validate_database_url(cls, v, values):
        """Validate and potentially override database URLs with Supabase"""
        # If Supabase URL is provided, construct the database URL
        if values.get("SUPABASE_URL"):
            # Extract database connection details from Supabase URL
            # Supabase format: postgresql://postgres:[password]@[host]:5432/postgres
            # We'll use environment variables for the actual connection
            pass
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
