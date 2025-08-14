#!/usr/bin/env python3
"""
Database connection test script for debugging Railway deployment
"""

import os
import asyncio
from sqlalchemy import create_engine, text
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
        # Create async engine
        engine = create_async_engine(database_url, echo=True)
        
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Async connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Async connection failed: {e}")
        return False

def test_sync_connection():
    """Test sync database connection"""
    print("Testing sync database connection...")
    
    # Get DATABASE_URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set!")
        return False
    
    # Convert async URL to sync URL
    if database_url.startswith('postgresql+asyncpg://'):
        sync_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
    else:
        sync_url = database_url
    
    # Mask password for security
    import re
    masked_url = re.sub(r':([^@]+)@', ':****@', sync_url)
    print(f"Using sync DATABASE_URL: {masked_url}")
    
    try:
        # Create sync engine
        engine = create_engine(sync_url, echo=True)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Sync connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Sync connection failed: {e}")
        return False

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
    
    # Test connections
    sync_success = test_sync_connection()
    async_success = await test_async_connection()
    
    print("\n" + "=" * 40)
    if sync_success and async_success:
        print("✅ All database connections successful!")
        return True
    else:
        print("❌ Some database connections failed!")
        return False

if __name__ == "__main__":
    asyncio.run(main())
