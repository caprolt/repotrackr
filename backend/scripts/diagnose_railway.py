#!/usr/bin/env python3
"""
Railway deployment diagnostic script
"""

import os
import sys

def diagnose_railway_environment():
    """Diagnose Railway environment setup"""
    print("🔍 Railway Environment Diagnosis")
    print("=" * 50)
    
    # Check Railway-specific environment variables
    railway_vars = {
        'RAILWAY_ENVIRONMENT': os.getenv('RAILWAY_ENVIRONMENT'),
        'RAILWAY_SERVICE_NAME': os.getenv('RAILWAY_SERVICE_NAME'),
        'RAILWAY_PROJECT_ID': os.getenv('RAILWAY_PROJECT_ID'),
        'PORT': os.getenv('PORT'),
        'ENVIRONMENT': os.getenv('ENVIRONMENT'),
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'REDIS_URL': os.getenv('REDIS_URL'),
    }
    
    print("📋 Environment Variables:")
    for var, value in railway_vars.items():
        if value:
            if 'PASSWORD' in var.upper() or 'KEY' in var.upper() or 'SECRET' in var.upper():
                print(f"  ✅ {var}: {'*' * 10}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            if var in ['DATABASE_URL', 'PORT']:
                print(f"  ❌ {var}: not set (REQUIRED)")
            else:
                print(f"  ⚠️  {var}: not set (optional)")
    
    # Determine if we're on Railway
    is_railway = any([
        railway_vars['RAILWAY_ENVIRONMENT'],
        railway_vars['RAILWAY_SERVICE_NAME'],
        railway_vars['RAILWAY_PROJECT_ID'],
        railway_vars['PORT']  # Railway always sets PORT
    ])
    
    print(f"\n🚂 Railway Detection: {'✅ Yes' if is_railway else '❌ No'}")
    
    if is_railway:
        print("✅ This appears to be a Railway environment")
        
        if not railway_vars['DATABASE_URL']:
            print("❌ DATABASE_URL is missing!")
            print("💡 Solution: Add a PostgreSQL service to your Railway project")
            print("   1. Go to your Railway project dashboard")
            print("   2. Click 'New Service'")
            print("   3. Select 'Database' → 'PostgreSQL'")
            print("   4. Railway will automatically inject DATABASE_URL")
            return False
        else:
            print("✅ DATABASE_URL is set")
            
            # Check if it looks like a Railway database URL
            if 'railway.app' in railway_vars['DATABASE_URL']:
                print("✅ DATABASE_URL appears to be a Railway PostgreSQL URL")
            else:
                print("⚠️  DATABASE_URL doesn't look like a Railway URL")
                print(f"   URL format: {railway_vars['DATABASE_URL'][:50]}...")
            
            return True
    else:
        print("❌ This doesn't appear to be a Railway environment")
        print("💡 If you're trying to deploy to Railway:")
        print("   1. Make sure you're running this on Railway")
        print("   2. Check that your Railway project is properly configured")
        print("   3. Verify the root directory is set to 'backend'")
        return False

def diagnose_database_connection():
    """Diagnose database connection"""
    print("\n🔍 Database Connection Diagnosis")
    print("=" * 50)
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    # Mask password for security
    import re
    masked_url = re.sub(r':([^@]+)@', ':****@', database_url)
    print(f"📋 DATABASE_URL: {masked_url}")
    
    # Check URL format
    if database_url.startswith('postgresql://'):
        print("✅ URL format: postgresql:// (sync)")
        print("💡 Will be converted to postgresql+asyncpg:// for async operations")
    elif database_url.startswith('postgresql+asyncpg://'):
        print("✅ URL format: postgresql+asyncpg:// (async)")
    else:
        print("⚠️  Unknown URL format")
    
    # Check if it's localhost (problematic on Railway)
    if 'localhost' in database_url or '127.0.0.1' in database_url:
        print("❌ WARNING: URL contains localhost!")
        print("💡 This will not work on Railway. You need a Railway PostgreSQL service.")
        return False
    
    return True

def main():
    """Main diagnostic function"""
    print("🚀 Railway Deployment Diagnostic Tool")
    print("=" * 60)
    
    # Check Railway environment
    railway_ok = diagnose_railway_environment()
    
    # Check database connection
    db_ok = diagnose_database_connection()
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS SUMMARY:")
    
    if railway_ok and db_ok:
        print("✅ Environment looks good for Railway deployment!")
        print("🎉 Your application should work properly on Railway.")
        return True
    elif railway_ok and not db_ok:
        print("⚠️  Railway environment detected but database issues found.")
        print("🔧 Fix the database connection issues above.")
        return False
    elif not railway_ok:
        print("❌ Railway environment not properly detected.")
        print("🔧 Make sure you're deploying to Railway correctly.")
        return False
    else:
        print("❌ Multiple issues detected.")
        print("🔧 Fix the issues above before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
