# Railway Database Connection Troubleshooting

## Issue: "Connection to localhost failed"

If you're seeing this error:
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server at "localhost" (::1), port 5432 failed: Connection refused
```

This means your application is trying to connect to a local PostgreSQL server instead of using Railway's database.

## Root Cause

The `DATABASE_URL` environment variable is not being set properly in Railway, causing the application to fall back to the local development database URL.

## Quick Fix Steps

### 1. Add PostgreSQL Service to Railway

1. Go to your Railway project dashboard
2. Click "New Service"
3. Select "Database" → "PostgreSQL"
4. Railway will automatically create a PostgreSQL database
5. The `DATABASE_URL` environment variable will be automatically injected

### 2. Verify Environment Variables

In your Railway project settings, ensure these variables are set:

```bash
# Railway will automatically provide these:
DATABASE_URL=postgresql://postgres:[password]@[railway-host]:5432/postgres
PORT=8000

# You need to set these manually:
ENVIRONMENT=production
DEBUG=false
BACKEND_CORS_ORIGINS=["https://your-app.vercel.app", "http://localhost:3000"]
```

### 3. Check Railway Project Configuration

- **Root Directory**: Make sure it's set to `backend` in Railway dashboard
- **Build Command**: Should use the configuration files in the backend directory
- **Start Command**: Should be `python start.py`

## Diagnostic Tools

### Run the Diagnostic Script

The application now includes a diagnostic script that will help identify issues:

```bash
python diagnose_railway.py
```

This script will:
- Check if you're running on Railway
- Verify environment variables
- Test database URL format
- Provide specific solutions

### Check Build Logs

Look for these messages in your Railway build logs:

```
🔍 Database Configuration Debug Info:
  ENVIRONMENT: production
  RAILWAY_ENVIRONMENT: production
  PORT: 8000
  Raw DATABASE_URL from env: set
✅ Database URL configured: postgresql+asyncpg://postgres:****@[railway-host]:5432/postgres
```

If you see:
```
❌ WARNING: DATABASE_URL is not set!
```

Then the PostgreSQL service is not properly added to your Railway project.

## Common Scenarios

### Scenario 1: No PostgreSQL Service Added

**Symptoms:**
- `DATABASE_URL` is not set
- Application falls back to localhost
- Connection refused error

**Solution:**
1. Add PostgreSQL service to Railway project
2. Redeploy the application

### Scenario 2: Wrong Root Directory

**Symptoms:**
- Configuration files not found
- Build fails
- Environment variables not loaded

**Solution:**
1. In Railway dashboard, set root directory to `backend`
2. Redeploy the application

### Scenario 3: Environment Variables Not Set

**Symptoms:**
- Application uses development defaults
- CORS errors
- Wrong configuration

**Solution:**
1. Set required environment variables in Railway dashboard
2. Redeploy the application

## Verification Steps

After fixing the issue, verify the deployment:

### 1. Check Health Endpoint

Visit: `https://your-app.up.railway.app/health`

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. Check Build Logs

Look for these success messages:
```
✅ Railway environment detected
✅ DATABASE_URL is set
✅ Database connection successful
✅ All expected tables exist
```

### 3. Test API Endpoints

Visit: `https://your-app.up.railway.app/api/v1/docs`

The API documentation should load without database errors.

## Prevention

To prevent this issue in the future:

1. **Always add PostgreSQL service first** before deploying your application
2. **Use the diagnostic script** during development to catch issues early
3. **Check Railway dashboard** to ensure services are properly connected
4. **Monitor build logs** for any configuration issues

## Debug Commands

If you need to debug locally:

```bash
# Test Railway environment detection
python diagnose_railway.py

# Test database setup
python setup_database.py

# Test deployment verification
python verify_deployment.py

# Check environment variables
echo $DATABASE_URL
echo $RAILWAY_ENVIRONMENT
echo $PORT
```

## Getting Help

If you're still having issues:

1. **Check Railway documentation**: https://docs.railway.app/
2. **Review build logs** in Railway dashboard
3. **Run diagnostic scripts** to identify specific issues
4. **Verify project configuration** matches the deployment guide

## Success Checklist

✅ PostgreSQL service added to Railway project
✅ Root directory set to `backend`
✅ Environment variables configured
✅ Build completes successfully
✅ Health endpoint returns database connected
✅ API endpoints work without errors
