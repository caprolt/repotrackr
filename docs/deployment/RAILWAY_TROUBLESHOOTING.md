# Railway Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. Database Connection Errors During Build

**Error**: `psycopg2.OperationalError` during `alembic upgrade head` in Dockerfile

**Cause**: Alembic is trying to run migrations during the Docker build phase when `DATABASE_URL` is not available.

**Solution**: ✅ **FIXED** - Migrations now run at startup instead of build time.

### 2. Configuration Loading Errors

**Error**: `DATABASE_URL is required in Railway` during configuration loading

**Cause**: Pydantic settings validation fails when `DATABASE_URL` is not immediately available.

**Solution**: ✅ **FIXED** - Added retry logic for configuration loading with gradual backoff.

### 3. Git Executable Errors

**Error**: `ImportError: Bad git executable.`

**Cause**: Docker image doesn't have Git installed, but the application uses GitPython for repository operations.

**Solution**: ✅ **FIXED** - Added Git and SSH support to Dockerfile.

### 4. Missing DATABASE_URL Environment Variable

**Error**: `DATABASE_URL is required in Railway`

**Cause**: No PostgreSQL service added to Railway project.

**Solution**:
1. Go to your Railway project dashboard
2. Click "New Service" → "Database" → "PostgreSQL"
3. Railway will automatically inject `DATABASE_URL` into your app service

### 5. Database Connection Timeout

**Error**: Connection timeout or refused during startup

**Cause**: Database service not ready when app starts.

**Solution**: ✅ **FIXED** - Added retry logic with exponential backoff in `start.py`

### 6. Port Configuration Issues

**Error**: App not accessible on Railway

**Solution**: Ensure your app uses the `PORT` environment variable:
```python
port = int(os.getenv("PORT", 8000))
```

### 7. Health Check Failures

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
   - ✅ Git and SSH support installed
   - ✅ Railway environment diagnosed
   - ✅ Database connection tested
   - ✅ Database setup verified

2. **Startup Phase**:
   - ✅ Configuration loaded with retry logic
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

Test Git functionality:
```bash
git --version
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

### Test Git Installation
```bash
git --version
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
6. **Fixed configuration loading** - Added retry logic for settings loading
7. **Separated DATABASE_URL and DATABASE_URL_SYNC validation** - Prevents validation conflicts
8. **Enhanced Alembic configuration** - Better error handling for missing database URLs
9. **Added Git support** - Installed Git and SSH client for repository operations

## Startup Process

The new startup process follows this sequence:

1. **Configuration Loading** (with retry logic)
   - Attempts to load settings up to 10 times
   - Waits for `DATABASE_URL` to become available
   - Uses gradual backoff between attempts

2. **Database Connection Test**
   - Tests connectivity before proceeding
   - Uses the same retry logic for configuration

3. **Database Migrations**
   - Runs Alembic migrations with retry logic
   - Up to 5 attempts with exponential backoff

4. **Application Startup**
   - Starts the FastAPI application
   - Uses the `PORT` environment variable

## System Dependencies

The Docker image now includes:
- **Git** - Required for GitPython repository operations
- **OpenSSH Client** - For SSH-based Git operations
- **CA Certificates** - For HTTPS Git operations
- **GCC** - For compiling Python packages
