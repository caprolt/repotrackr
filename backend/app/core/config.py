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
    
    # Database - Support both local and Railway/Supabase
    DATABASE_URL: str = ""
    DATABASE_URL_SYNC: str = ""
    
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
        """Validate and ensure database URLs are properly set"""
        if not v:
            # Check if we're in production (Railway)
            if os.getenv("ENVIRONMENT") == "production" or os.getenv("RAILWAY_ENVIRONMENT"):
                raise ValueError("DATABASE_URL is required in production. Please set it in Railway environment variables.")
            else:
                # Fallback to local development
                return "postgresql+asyncpg://repotrackr:repotrackr_dev@localhost:5432/repotrackr" if "DATABASE_URL" in values else "postgresql://repotrackr:repotrackr_dev@localhost:5432/repotrackr"
        
        # Ensure DATABASE_URL uses asyncpg for async operations
        if "DATABASE_URL" in values and v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Debug: Print database URL (without password) for troubleshooting
if settings.DATABASE_URL:
    # Mask password in the URL for security
    import re
    masked_url = re.sub(r':([^@]+)@', ':****@', settings.DATABASE_URL)
    print(f"Database URL configured: {masked_url}")
else:
    print("WARNING: DATABASE_URL is not set!")
    print(f"Environment variables: DATABASE_URL={os.getenv('DATABASE_URL')}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'not set')}")
    print(f"Railway Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'not set')}")
