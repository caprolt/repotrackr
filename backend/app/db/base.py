from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()

# Global engine and session factory (lazy initialization)
_engine = None
_async_session_factory = None


def get_database_url() -> str:
    """Get the database URL with proper async driver."""
    database_url = settings.DATABASE_URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        logger.info("Converted DATABASE_URL to use asyncpg driver")
    return database_url


def get_engine():
    """Get the async database engine (lazy initialization)."""
    global _engine
    if _engine is None:
        database_url = get_database_url()
        _engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            future=True,
            pool_pre_ping=True,
            pool_recycle=300,
        )
    return _engine


def get_async_session_factory():
    """Get the async session factory (lazy initialization)."""
    global _async_session_factory
    if _async_session_factory is None:
        engine = get_engine()
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_factory


# Dependency to get database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async_session_factory = get_async_session_factory()
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def close_db_connections():
    """Close database connections on shutdown."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
