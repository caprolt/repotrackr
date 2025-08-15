#!/usr/bin/env python3
"""
Startup script for RepoTrackr API with proper async context initialization
"""

import os
import asyncio
import uvicorn
import subprocess
import sys
import time

def load_settings_with_retry():
    """Load settings with retry logic for Railway deployment."""
    max_retries = 10
    retry_delay = 3
    
    for attempt in range(max_retries):
        try:
            print(f"📋 Loading configuration attempt {attempt + 1}/{max_retries}")
            
            # Import settings
            from app.core.config import settings
            
            # Check if DATABASE_URL is available
            if not settings.DATABASE_URL:
                print("⏳ DATABASE_URL not available yet, waiting...")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 1.5  # Gradual backoff
                    continue
                else:
                    raise ValueError("DATABASE_URL not available after all retries")
            
            print("✅ Configuration loaded successfully")
            return settings
            
        except Exception as e:
            print(f"❌ Configuration loading attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
                retry_delay *= 1.5
            else:
                print("❌ All configuration loading attempts failed.")
                raise
    
    raise RuntimeError("Failed to load configuration after all retries")

def run_migrations():
    """Run database migrations before starting the application."""
    print("🔄 Running database migrations...")
    
    # Try multiple times with delays (for containerized environments)
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            print(f"📋 Migration attempt {attempt + 1}/{max_retries}")
            
            # Run alembic upgrade head
            result = subprocess.run(
                ["python", "-m", "alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Database migrations completed successfully")
            if result.stdout.strip():
                print(result.stdout)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Database migration attempt {attempt + 1} failed!")
            print(f"Error: {e}")
            if e.stdout.strip():
                print(f"stdout: {e.stdout}")
            if e.stderr.strip():
                print(f"stderr: {e.stderr}")
            
            if attempt < max_retries - 1:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print("❌ All migration attempts failed.")
                return False
                
        except Exception as e:
            print(f"❌ Unexpected error during migration attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                return False
    
    return False

def test_database_connection():
    """Test database connection before running migrations."""
    print("🔍 Testing database connection...")
    
    try:
        # Run the database connection test
        result = subprocess.run(
            ["python", "test_db_connection.py"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Database connection test passed")
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Database connection test failed!")
        if e.stdout.strip():
            print(f"stdout: {e.stdout}")
        if e.stderr.strip():
            print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during connection test: {e}")
        return False

def main():
    """Start the FastAPI application with proper configuration."""
    print("🚀 Starting RepoTrackr API...")
    
    # Load settings with retry logic
    try:
        settings = load_settings_with_retry()
        print(f"📊 Environment: {settings.ENVIRONMENT}")
        print(f"🔧 Debug mode: {settings.DEBUG}")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        sys.exit(1)
    
    # Test database connection first
    print("🔍 Testing database connectivity...")
    if not test_database_connection():
        print("❌ Database connection test failed. Exiting.")
        sys.exit(1)
    
    # Run database migrations
    if not run_migrations():
        print("❌ Failed to run database migrations. Exiting.")
        sys.exit(1)
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    
    print(f"🌐 Starting server on port {port}...")
    
    # Configure uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
        access_log=True,
    )

if __name__ == "__main__":
    main()
