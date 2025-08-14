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
        # Check if we're in Railway/production environment
        is_railway = (
            os.getenv("RAILWAY_ENVIRONMENT") or 
            os.getenv("ENVIRONMENT") == "production" or
            os.getenv("RAILWAY_SERVICE_NAME") or
            os.getenv("PORT")  # Railway always sets PORT
        )
        
        if not v:
            if is_railway:
                # In Railway, DATABASE_URL should be provided by Railway
                raise ValueError(
                    "DATABASE_URL is required in Railway. "
                    "Please ensure you have added a PostgreSQL service to your Railway project. "
                    f"Current environment: ENVIRONMENT={os.getenv('ENVIRONMENT')}, "
                    f"RAILWAY_ENVIRONMENT={os.getenv('RAILWAY_ENVIRONMENT')}, "
                    f"PORT={os.getenv('PORT')}"
                )
            else:
                # Fallback to local development
                return "postgresql+asyncpg://repotrackr:repotrackr_dev@localhost:5432/repotrackr" if "DATABASE_URL" in values else "postgresql://repotrackr:repotrackr_dev@localhost:5432/repotrackr"
        
        # Ensure DATABASE_URL uses asyncpg for async operations
        if "DATABASE_URL" in values and v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # Handle Railway's DATABASE_URL format
        if "DATABASE_URL" in values and ("railway.app" in v or is_railway):
            # Railway provides postgresql:// format, convert to asyncpg
            if v.startswith("postgresql://"):
                v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Debug: Print database URL (without password) for troubleshooting
print("🔍 Database Configuration Debug Info:")
print(f"  ENVIRONMENT: {os.getenv('ENVIRONMENT', 'not set')}")
print(f"  RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'not set')}")
print(f"  RAILWAY_SERVICE_NAME: {os.getenv('RAILWAY_SERVICE_NAME', 'not set')}")
print(f"  PORT: {os.getenv('PORT', 'not set')}")
print(f"  Raw DATABASE_URL from env: {'set' if os.getenv('DATABASE_URL') else 'not set'}")

if settings.DATABASE_URL:
    # Mask password in the URL for security
    import re
    masked_url = re.sub(r':([^@]+)@', ':****@', settings.DATABASE_URL)
    print(f"✅ Database URL configured: {masked_url}")
else:
    print("❌ WARNING: DATABASE_URL is not set!")
    print("💡 If you're on Railway, make sure you've added a PostgreSQL service to your project.")
    print("💡 If you're running locally, make sure you have a local PostgreSQL server running.")
