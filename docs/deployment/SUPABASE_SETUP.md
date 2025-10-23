# Supabase Database Setup Guide

## Overview
This guide explains how to migrate from the local PostgreSQL database to Supabase, eliminating the need for Docker containers.

## Benefits of Using Supabase
- ✅ No local database management required
- ✅ Built-in authentication system
- ✅ Automatic backups and scaling
- ✅ Real-time subscriptions (future feature)
- ✅ Easy database management dashboard
- ✅ No Docker containers needed for database

## Setup Steps

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign up/Login and create a new project
3. Choose a region close to your users
4. Wait for the project to be provisioned (2-3 minutes)

### 2. Get Database Connection Details
1. In your Supabase dashboard, go to **Settings** → **Database**
2. Copy the following values:
   - **Host**: `db.[project-ref].supabase.co`
   - **Database name**: `postgres`
   - **Port**: `5432`
   - **User**: `postgres`
   - **Password**: (found in the connection string)

### 3. Configure Environment Variables
Create or update your `.env` file in the `backend/` directory:

```env
# Supabase Configuration
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_KEY=[your-service-role-key]
SUPABASE_ANON_KEY=[your-anon-key]

# Database URLs (Supabase)
DATABASE_URL=postgresql+asyncpg://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
DATABASE_URL_SYNC=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres

# Optional: Keep Redis local for now
REDIS_URL=redis://localhost:6379/0
```

### 4. Run Database Migrations
```bash
cd backend
python -m alembic upgrade head
```

### 5. Update Startup Scripts
The startup scripts have been updated to support Supabase mode. You can now:

**Option A: Use Supabase (Recommended)**
```bash
# No need to start Docker containers!
cd backend
python start.py
```

**Option B: Use Local Database (Legacy)**
```bash
# Start Docker containers
docker-compose up -d postgres redis
cd backend
python start.py
```

## Database Schema
The existing Alembic migrations will work with Supabase. The schema includes:
- `projects` table
- `skills` table  
- `jobs` table (for background processing)
- All necessary indexes and constraints

## Migration from Local Database
If you have existing data in your local database:

1. **Export local data**:
   ```bash
   pg_dump -h localhost -U repotrackr -d repotrackr > local_backup.sql
   ```

2. **Import to Supabase**:
   ```bash
   psql "postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres" < local_backup.sql
   ```

## Environment-Specific Configuration

### Development
- Use Supabase for consistent development environment
- No need to manage local Docker containers
- Easy to share database state with team members

### Production
- Supabase handles scaling automatically
- Built-in monitoring and alerting
- Automatic backups and point-in-time recovery

## Troubleshooting

### Connection Issues
- Verify your Supabase project is active
- Check that your IP is not blocked (check Supabase dashboard)
- Ensure connection string format is correct

### Migration Issues
- Make sure you're using the latest Alembic migrations
- Check that all required extensions are enabled in Supabase
- Verify database user has necessary permissions

### Performance
- Supabase provides good performance for most use cases
- Consider connection pooling for high-traffic applications
- Monitor query performance through Supabase dashboard

## Next Steps
1. Set up Supabase authentication (optional)
2. Configure real-time subscriptions (optional)
3. Set up monitoring and alerting
4. Configure backup retention policies

## Cost Considerations
- Supabase has a generous free tier
- Pay-as-you-go pricing for additional usage
- No infrastructure management costs
- Automatic scaling reduces operational overhead
