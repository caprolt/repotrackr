# Railway Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. Database Connection Errors During Build

**Error**: `psycopg2.OperationalError` during `alembic upgrade head` in Dockerfile

**Cause**: Alembic is trying to run migrations during the Docker build phase when `DATABASE_URL` is not available.

**Solution**: ✅ **FIXED** - Migrations now run at startup instead of build time.

### 2. Missing DATABASE_URL Environment Variable

**Error**: `DATABASE_URL is required in Railway`

**Cause**: No PostgreSQL service added to Railway project.

**Solution**:
1. Go to your Railway project dashboard
2. Click "New Service" → "Database" → "PostgreSQL"
3. Railway will automatically inject `DATABASE_URL` into your app service

### 3. Database Connection Timeout

**Error**: Connection timeout or refused during startup

**Cause**: Database service not ready when app starts.

**Solution**: ✅ **FIXED** - Added retry logic with exponential backoff in `start.py`

### 4. Port Configuration Issues

**Error**: App not accessible on Railway

**Solution**: Ensure your app uses the `PORT` environment variable:
```python
port = int(os.getenv("PORT", 8000))
```

### 5. Health Check Failures

**Error**: Railway health checks failing

**Solution**: Health check endpoint is available at `/health` and returns:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Deployment Checklist

### Before Deploying

- [ ] PostgreSQL service added to Railway project
- [ ] Root directory set to `backend` in Railway
- [ ] Environment variables configured (if needed)
- [ ] Health check path set to `/health`

### During Deployment

1. **Build Phase**: 
   - ✅ Dependencies installed
   - ✅ Railway environment diagnosed
   - ✅ Database connection tested
   - ✅ Database setup verified

2. **Startup Phase**:
   - ✅ Database connection tested
   - ✅ Migrations run with retry logic
   - ✅ Application starts on correct port

### Verification Commands

Test database connection:
```bash
python test_db_connection.py
```

Run diagnostics:
```bash
python diagnose_railway.py
```

## Environment Variables

Railway automatically provides:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Port to bind the application to
- `RAILWAY_ENVIRONMENT` - Railway environment name
- `RAILWAY_SERVICE_NAME` - Service name

## Debugging Commands

### Check Environment
```bash
python diagnose_railway.py
```

### Test Database Connection
```bash
python test_db_connection.py
```

### Run Migrations Manually
```bash
python -m alembic upgrade head
```

### Start Application
```bash
python start.py
```

## Common Railway Commands

### View Logs
```bash
railway logs
```

### Connect to Database
```bash
railway connect
```

### Check Service Status
```bash
railway status
```

## Support

If you're still experiencing issues:

1. Check Railway logs: `railway logs`
2. Verify database service is running
3. Ensure all environment variables are set
4. Check the health endpoint: `https://your-app.railway.app/health`

## Recent Fixes Applied

1. **Moved migrations from build to runtime** - Fixed database connection during build
2. **Added retry logic** - Handles database startup delays
3. **Enhanced error reporting** - Better debugging information
4. **Improved health checks** - More robust health endpoint
5. **Added connection testing** - Validates database connectivity before startup
