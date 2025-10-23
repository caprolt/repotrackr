#!/usr/bin/env python3
"""
Database setup and verification script for Railway deployment
"""

import os
import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_database():
    """Set up and verify database connection and schema"""
    print("🔧 Setting up database for Railway deployment...")
    print("=" * 60)
    
    # Get DATABASE_URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable is not set!")
        print("💡 Make sure you've added a PostgreSQL service to your Railway project.")
        return False
    
    # Mask password for security
    import re
    masked_url = re.sub(r':([^@]+)@', ':****@', database_url)
    print(f"📋 DATABASE_URL: {masked_url}")
    
    # Ensure we're using asyncpg
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        print("🔄 Converted to asyncpg URL")
    
    try:
        # Import and use the app's database setup
        from app.db.base import get_async_session_factory
        
        # Get session factory (this will initialize the engine)
        async_session_factory = get_async_session_factory()
        
        # Test connection using the app's session factory
        async with async_session_factory() as session:
            # Test basic connection
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
            
            # Check if our expected tables exist
            expected_tables = ['projects', 'tasks', 'progress_snapshots', 'skills']
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                print(f"⚠️  Missing tables: {missing_tables}")
                print("💡 Run 'python -m alembic upgrade head' to create missing tables")
                return False
            else:
                print("✅ All expected tables exist!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
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
    
    all_good = True
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var.upper() or 'KEY' in var.upper() or 'SECRET' in var.upper():
                print(f"✅ {var}: {'*' * 10}")
            else:
                print(f"✅ {var}: {value}")
        else:
            if var in ['DATABASE_URL', 'PORT']:
                print(f"❌ {var}: not set (REQUIRED)")
                all_good = False
            else:
                print(f"⚠️  {var}: not set (optional)")
    
    return all_good

async def main():
    """Main setup function"""
    print("🚀 RepoTrackr Database Setup for Railway")
    print("=" * 60)
    
    # Verify environment
    env_success = await verify_environment()
    
    if not env_success:
        print("\n❌ Environment verification failed!")
        print("💡 Please check your Railway environment variables.")
        return False
    
    # Set up database
    db_success = await setup_database()
    
    print("\n" + "=" * 60)
    if db_success:
        print("✅ Database setup successful!")
        print("🎉 Your database is ready for Railway deployment!")
        return True
    else:
        print("❌ Database setup failed!")
        print("🔧 Please check your DATABASE_URL and run migrations.")
        return False

if __name__ == "__main__":
    asyncio.run(main())
