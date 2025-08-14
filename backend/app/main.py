from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.base import close_db_connections

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """Initialize database connections on startup."""
    print("🚀 Starting RepoTrackr API...")
    
    # Verify database connection on startup
    try:
        from app.db.base import get_async_session_factory
        from sqlalchemy import text
        
        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            # Test database connection
            result = await session.execute(text("SELECT 1"))
            print("✅ Database connection verified on startup")
            
    except Exception as e:
        print(f"❌ Database connection failed on startup: {e}")
        # Don't raise the exception - let the app start but log the error
        # This allows the health check to still work


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown."""
    print("🛑 Shutting down RepoTrackr API...")
    await close_db_connections()


@app.get("/")
async def root():
    return {
        "message": "Welcome to RepoTrackr API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with database status."""
    try:
        from app.db.base import get_async_session_factory
        from sqlalchemy import text
        
        async_session_factory = get_async_session_factory()
        async with async_session_factory() as session:
            # Test database connection
            result = await session.execute(text("SELECT 1"))
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": "2024-01-01T00:00:00Z"  # You can add proper timestamp if needed
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }
