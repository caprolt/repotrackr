# Railway Database Deployment Checklist

## Pre-Deployment Database Setup ✅

### 1. Railway Project Configuration
- [ ] Create new Railway project
- [ ] Connect GitHub repository
- [ ] Set root directory to `backend`
- [ ] Ensure `railway.toml` is in the backend directory

### 2. PostgreSQL Database Service
- [ ] Add PostgreSQL service to Railway project
- [ ] Verify `DATABASE_URL` is automatically injected
- [ ] Check that the database service is running
- [ ] Note the database connection details

### 3. Environment Variables Setup
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Set `BACKEND_CORS_ORIGINS` with your Vercel frontend domain
- [ ] Verify `DATABASE_URL` is available (auto-injected by Railway)
- [ ] Set `REDIS_URL` if using Redis (optional)

### 4. Code Configuration Files
- [ ] Verify `railway.toml` includes database setup steps
- [ ] Check `nixpacks.toml` has correct build phases
- [ ] Ensure `requirements.txt` includes all database dependencies
- [ ] Verify `alembic.ini` is properly configured

## Database Migration and Setup ✅

### 1. Initial Migration
- [ ] Verify `alembic/versions/5f05349437be_initial_migration.py` exists
- [ ] Check that all tables are defined in the migration:
  - [ ] `projects` table
  - [ ] `tasks` table
  - [ ] `progress_snapshots` table
  - [ ] `skills` table
- [ ] Verify all indexes are created
- [ ] Check that foreign key relationships are defined

### 2. Database Models
- [ ] Verify all models in `app/db/models.py`:
  - [ ] Project model with proper fields
  - [ ] Task model with status enum
  - [ ] ProgressSnapshot model with decimal fields
  - [ ] Skill model with confidence scoring
- [ ] Check that UUID primary keys are used
- [ ] Verify enum types are properly defined
- [ ] Ensure indexes are created for performance

### 3. Database Configuration
- [ ] Check `app/core/config.py` handles Railway DATABASE_URL
- [ ] Verify async/sync URL conversion works
- [ ] Test database URL validation
- [ ] Ensure fallback to local development works

## Deployment Process ✅

### 1. Build Phase
- [ ] `pip install -r requirements.txt` - Install dependencies
- [ ] `python -m alembic upgrade head` - Run database migrations
- [ ] `python setup_database.py` - Verify database setup
- [ ] `python verify_deployment.py` - Final deployment verification

### 2. Runtime Configuration
- [ ] Verify `start.py` uses correct port configuration
- [ ] Check that `app/main.py` includes database health checks
- [ ] Ensure proper startup/shutdown database handling
- [ ] Test health endpoint includes database status

## Post-Deployment Verification ✅

### 1. Database Connection Tests
- [ ] Test `/health` endpoint returns database status
- [ ] Verify database tables exist
- [ ] Check that indexes are created
- [ ] Test basic CRUD operations

### 2. API Endpoints
- [ ] Test `/api/v1/projects` endpoint
- [ ] Verify project creation works
- [ ] Check that relationships work properly
- [ ] Test error handling for database issues

### 3. Monitoring and Logs
- [ ] Check Railway deployment logs
- [ ] Verify database connection logs
- [ ] Monitor application startup logs
- [ ] Check for any database-related errors

## Troubleshooting Database Issues ✅

### Common Problems and Solutions

#### 1. "DATABASE_URL not set" Error
- **Cause**: PostgreSQL service not added to Railway project
- **Solution**: Add PostgreSQL service in Railway dashboard

#### 2. "Connection refused" Error
- **Cause**: Database service not running or wrong URL
- **Solution**: Check Railway dashboard for database service status

#### 3. "Table does not exist" Error
- **Cause**: Migrations not run or failed
- **Solution**: Check build logs for migration errors

#### 4. "asyncpg not found" Error
- **Cause**: Missing asyncpg dependency
- **Solution**: Verify `asyncpg>=0.29.0` in requirements.txt

#### 5. "SSL connection required" Error
- **Cause**: Railway requires SSL for database connections
- **Solution**: Ensure DATABASE_URL includes SSL parameters

## Database Performance and Optimization ✅

### 1. Connection Pooling
- [ ] Verify connection pooling is configured
- [ ] Check pool size settings
- [ ] Monitor connection usage

### 2. Indexes
- [ ] Verify all necessary indexes are created
- [ ] Check index usage in queries
- [ ] Monitor query performance

### 3. Monitoring
- [ ] Set up database monitoring
- [ ] Monitor slow queries
- [ ] Check connection pool status

## Security Considerations ✅

### 1. Database Security
- [ ] Verify SSL connections are used
- [ ] Check that credentials are not logged
- [ ] Ensure proper access controls

### 2. Environment Variables
- [ ] Verify sensitive data is in environment variables
- [ ] Check that DATABASE_URL is not exposed in logs
- [ ] Ensure proper secret management

## Quick Commands for Database Management

```bash
# Check database connection
python setup_database.py

# Run migrations
python -m alembic upgrade head

# Create new migration
python -m alembic revision --autogenerate -m "description"

# Check migration status
python -m alembic current

# Rollback migration
python -m alembic downgrade -1

# Verify deployment
python verify_deployment.py
```

## URLs to Test After Deployment

- Health check: `https://your-app.up.railway.app/health`
- API docs: `https://your-app.up.railway.app/api/v1/docs`
- Projects endpoint: `https://your-app.up.railway.app/api/v1/projects`

## Success Indicators

✅ **Database deployment is successful when:**
- Health endpoint returns `{"status": "healthy", "database": "connected"}`
- All API endpoints respond without database errors
- Database tables exist and are accessible
- Migrations completed successfully
- No database-related errors in Railway logs
