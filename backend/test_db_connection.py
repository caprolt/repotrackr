#!/usr/bin/env python3
"""
Simple database connection test script
"""

import os
import sys
import asyncio
import asyncpg
from app.core.config import settings

async def test_database_connection():
    """Test database connection using asyncpg directly."""
    print("🔍 Testing database connection...")
    
    # Get database URL
    database_url = settings.DATABASE_URL
    if not database_url:
        print("❌ DATABASE_URL is not set!")
        return False
    
    # Convert to sync URL for testing
    sync_url = database_url
    if sync_url.startswith('postgresql+asyncpg://'):
        sync_url = sync_url.replace('postgresql+asyncpg://', 'postgresql://', 1)
    
    print(f"📋 Testing connection to: {sync_url.split('@')[1] if '@' in sync_url else sync_url}")
    
    try:
        # Test connection
        conn = await asyncpg.connect(sync_url)
        print("✅ Database connection successful!")
        
        # Test a simple query
        result = await conn.fetchval('SELECT version()')
        print(f"📊 PostgreSQL version: {result}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Database Connection Test")
    print("=" * 40)
    
    # Print environment info
    print(f"Environment: {os.getenv('ENVIRONMENT', 'not set')}")
    print(f"Railway Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'not set')}")
    print(f"Port: {os.getenv('PORT', 'not set')}")
    
    # Test connection
    success = asyncio.run(test_database_connection())
    
    if success:
        print("\n✅ Database connection test passed!")
        sys.exit(0)
    else:
        print("\n❌ Database connection test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
