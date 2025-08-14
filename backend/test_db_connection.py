#!/usr/bin/env python3
"""
Database connection test script for debugging Railway deployment
"""

import os
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def test_async_connection():
    """Test async database connection"""
    print("Testing async database connection...")
    
    # Get DATABASE_URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set!")
        return False
    
    # Mask password for security
    import re
    masked_url = re.sub(r':([^@]+)@', ':****@', database_url)
    print(f"Using DATABASE_URL: {masked_url}")
    
    try:
        # Import and use the app's database setup
        from app.db.base import get_async_session_factory
        
        # Get session factory (this will initialize the engine)
        async_session_factory = get_async_session_factory()
        
        # Test connection using the app's session factory
        async with async_session_factory() as session:
            result = await session.execute(text("SELECT 1"))
            print("✅ Async connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Async connection failed: {e}")
        return False

def test_sync_connection():
    """Test sync database connection (disabled - using async only)"""
    print("Testing sync database connection...")
    print("⚠️  Sync connection test disabled - using async only")
    return True

def print_environment_info():
    """Print environment information for debugging"""
    print("=== Environment Information ===")
    print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT', 'not set')}")
    print(f"RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'not set')}")
    print(f"PORT: {os.getenv('PORT', 'not set')}")
    print(f"DATABASE_URL: {'set' if os.getenv('DATABASE_URL') else 'not set'}")
    print(f"REDIS_URL: {'set' if os.getenv('REDIS_URL') else 'not set'}")
    print("================================")

async def main():
    """Main test function"""
    print("🔍 Database Connection Test")
    print("=" * 40)
    
    # Print environment info
    print_environment_info()
    
    # Test async connection only
    async_success = await test_async_connection()
    
    print("\n" + "=" * 40)
    if async_success:
        print("✅ Async database connection successful!")
        return True
    else:
        print("❌ Async database connection failed!")
        return False

if __name__ == "__main__":
    asyncio.run(main())
