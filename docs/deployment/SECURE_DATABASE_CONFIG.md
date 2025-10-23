# Secure Database Configuration

This document explains the secure approach used for database configuration in RepoTrackr.

## Security Improvements

### Before (Insecure)
- Hardcoded database credentials in multiple files
- Credentials visible in source code
- Risk of accidental commit to version control

### After (Secure)
- Environment variables for all database components
- No hardcoded credentials in source code
- `.env` file excluded from version control

## Configuration Structure

### Environment Variables
The application now uses individual environment variables for database configuration:

```bash
# Database components (recommended approach)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=repotrackr
DB_USER=repotrackr
DB_PASSWORD=repotrackr_dev

# Alternative: Direct URLs (still supported)
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
DATABASE_URL_SYNC=postgresql://user:pass@host:port/db
```

### Files Updated

1. **`app/core/config.py`**
   - Removed hardcoded credentials
   - Added environment variable fallbacks
   - Dynamic URL construction from components

2. **`alembic/env.py`**
   - Removed hardcoded credentials
   - Uses environment variables for database URL

3. **`alembic.ini`**
   - Removed hardcoded URL
   - URL now set dynamically by `env.py`

4. **Setup Scripts**
   - Updated to not hardcode credentials
   - Use dynamic configuration

## Setup Instructions

### 1. Create Environment File
```bash
cd backend
cp .env.example .env
```

### 2. Configure Database
Edit `.env` file with your database settings:

```bash
# For local development
DB_HOST=localhost
DB_PORT=5432
DB_NAME=repotrackr
DB_USER=repotrackr
DB_PASSWORD=your_secure_password

# For production (Railway/Supabase)
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
```

### 3. Run Setup
```bash
# Use the setup script
./scripts/setup.sh

# Or manually
docker-compose up -d
cd backend
python -m alembic upgrade head
```

## Security Best Practices

### ✅ Do
- Use environment variables for all sensitive data
- Keep `.env` files out of version control
- Use strong, unique passwords
- Rotate credentials regularly
- Use different credentials for different environments

### ❌ Don't
- Hardcode credentials in source code
- Commit `.env` files to version control
- Use the same credentials across environments
- Use weak passwords
- Share credentials in logs or error messages

## Environment-Specific Configuration

### Local Development
- Uses individual DB_* environment variables
- Defaults to localhost PostgreSQL
- Credentials stored in `.env` file

### Production (Railway)
- Uses `DATABASE_URL` environment variable
- Provided by Railway platform
- No local `.env` file needed

### Production (Supabase)
- Uses `DATABASE_URL` environment variable
- Configured in Supabase dashboard
- Secure connection with SSL

## Troubleshooting

### Database Connection Issues
1. Check that `.env` file exists and is properly configured
2. Verify database service is running (`docker-compose ps`)
3. Check environment variable values
4. Review logs for connection errors

### Migration Issues
1. Ensure `DATABASE_URL_SYNC` is properly set
2. Check Alembic configuration
3. Verify database permissions

### Security Concerns
1. Ensure `.env` is in `.gitignore`
2. Check for any remaining hardcoded credentials
3. Verify environment variable usage
4. Review access logs for unauthorized attempts

## Migration from Old Configuration

If you're upgrading from the old hardcoded configuration:

1. **Backup your data** (if any)
2. **Create new `.env` file** with your database settings
3. **Update any deployment scripts** to use environment variables
4. **Test the new configuration** thoroughly
5. **Remove any remaining hardcoded credentials**

The application will automatically use the new secure configuration once the `.env` file is in place.
