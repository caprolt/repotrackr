#!/usr/bin/env python3
"""
Startup script for RepoTrackr API with proper async context initialization
"""

import os
import asyncio
import uvicorn
from app.core.config import settings

def main():
    """Start the FastAPI application with proper configuration."""
    print("🚀 Starting RepoTrackr API...")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug mode: {settings.DEBUG}")
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    
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
