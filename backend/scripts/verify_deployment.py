#!/usr/bin/env python3
"""
Deployment verification script for Railway
"""

import os
import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_database_connection():
    """Verify database connection with proper async setup"""
    print("🔍 Verifying Database Connection")
    print("=" * 50)
    
    # Get DATABASE_URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable is not set!")
        return False
    
    # Mask password for security
    import re
    masked_url = re.sub(r':([^@]+)@', ':****@', database_url)
    print(f"📋 Original DATABASE_URL: {masked_url}")
    
    # Ensure we're using asyncpg
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        print("🔄 Converted to asyncpg URL")
    
    masked_async_url = re.sub(r':([^@]+)@', ':****@', database_url)
    print(f"📋 Final DATABASE_URL: {masked_async_url}")
    
    try:
        # Import and use the app's database setup
        from app.db.base import get_async_session_factory
        
        # Get session factory (this will initialize the engine)
        async_session_factory = get_async_session_factory()
        
        # Test connection using the app's session factory
        async with async_session_factory() as session:
            result = await session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Database connection successful! Test result: {row[0]}")
            
            # Test if we can access the database
            result = await session.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"📊 Connected to database: {db_name}")
            
            # Test if tables exist
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Available tables: {tables}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False

async def verify_environment():
    """Verify environment variables"""
    print("\n🔍 Environment Verification")
    print("=" * 50)
    
    env_vars = [
        'DATABASE_URL',
        'ENVIRONMENT',
        'RAILWAY_ENVIRONMENT',
        'PORT',
        'REDIS_URL'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var.upper() or 'KEY' in var.upper() or 'SECRET' in var.upper():
                print(f"✅ {var}: {'*' * 10}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: not set")

async def main():
    """Main verification function"""
    print("🚀 RepoTrackr Deployment Verification")
    print("=" * 60)
    
    # Verify environment
    await verify_environment()
    
    # Verify database connection
    db_success = await verify_database_connection()
    
    print("\n" + "=" * 60)
    if db_success:
        print("✅ Deployment verification successful!")
        print("🎉 Your application should be ready to run!")
        return True
    else:
        print("❌ Deployment verification failed!")
        print("🔧 Please check your DATABASE_URL and environment variables.")
        return False

if __name__ == "__main__":
    asyncio.run(main())
