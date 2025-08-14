# Railway Deployment Guide

This guide will help you deploy your RepoTrackr FastAPI backend to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Railway CLI** (optional): `npm install -g @railway/cli`

## Step-by-Step Deployment

### 1. Create a New Railway Project

1. Go to [railway.app/dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Set the root directory to `backend`

### 2. Add PostgreSQL Database

1. In your Railway project dashboard, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a PostgreSQL database
4. The `DATABASE_URL` environment variable will be automatically injected

### 3. Add Redis (Optional)

If you want to use Redis for job queues and caching:

1. Click "New Service" again
2. Select "Database" → "Redis"
3. Railway will automatically create a Redis instance
4. The `REDIS_URL` environment variable will be automatically injected

### 4. Configure Environment Variables

In your Railway project settings, add these environment variables:

```bash
# Application settings
APP_NAME=RepoTrackr
DEBUG=false
ENVIRONMENT=production

# API settings
API_V1_STR=/api/v1
PROJECT_NAME=RepoTrackr
VERSION=0.1.0

# CORS settings (replace with your actual Vercel frontend domain)
# The frontend (Vercel) makes requests to this backend (Railway)
BACKEND_CORS_ORIGINS=["https://your-app.vercel.app", "http://localhost:3000"]

# Optional: GitHub integration
# GITHUB_TOKEN=your_github_token
# GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Optional: Supabase (if using for auth)
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your_service_role_key
# SUPABASE_ANON_KEY=your_anon_key
```

### 5. Deploy

1. Railway will automatically detect your Python project
2. It will use the `nixpacks.toml` configuration for building
3. The deployment will run:
   - `pip install -r requirements.txt`
   - `python -m alembic upgrade head` (database migrations)
   - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 6. Get Your Backend URL

1. After deployment, go to your service dashboard
2. Copy the generated domain (e.g., `https://your-app-production.up.railway.app`)
3. This is your backend URL for the frontend configuration

## Configuration Files

Your project includes these Railway-specific files:

- `railway.toml` - Railway deployment configuration
- `nixpacks.toml` - Build system configuration
- `Procfile` - Alternative deployment configuration
- `runtime.txt` - Python version specification

## Environment Variables Reference

### Automatic Variables (Railway provides these)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string (if Redis service added)
- `PORT` - Port number for the application

### Required Manual Variables
- `BACKEND_CORS_ORIGINS` - CORS origins (include your Vercel frontend domain)
- `DEBUG` - Set to `false` for production
- `ENVIRONMENT` - Set to `production`

### CORS Configuration Explained
Since you're deploying:
- **Backend** → Railway (`https://your-app-production.up.railway.app`)
- **Frontend** → Vercel (`https://your-app.vercel.app`)

The `BACKEND_CORS_ORIGINS` should include your **Vercel domain** because that's where the API requests originate from.

### Optional Variables
- `GITHUB_TOKEN` - For GitHub API access
- `GITHUB_WEBHOOK_SECRET` - For GitHub webhooks
- `SUPABASE_URL` - For Supabase integration
- `SUPABASE_KEY` - Supabase service role key
- `SUPABASE_ANON_KEY` - Supabase anonymous key

## Post-Deployment Steps

### 1. Update Frontend Configuration

In your Vercel project, update the environment variable:
```
NEXT_PUBLIC_API_URL=https://your-app-production.up.railway.app
```

### 2. Test the API

1. Visit your Railway app URL
2. Check the health endpoint: `https://your-app-production.up.railway.app/health`
3. View API docs: `https://your-app-production.up.railway.app/api/v1/docs`

### 3. Monitor Deployment

- Check Railway dashboard for deployment logs
- Monitor application health
- Set up alerts if needed

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Railway build logs
   - Verify `requirements.txt` is in the backend directory
   - Ensure Python version compatibility

2. **"pip: command not found" Error**
   - Railway might not be detecting Python properly
   - Try redeploying with the updated configuration files
   - Check that `nixpacks.toml` and `railway.toml` are in the backend directory
   - Ensure the root directory is set to `backend` in Railway dashboard

3. **Database Connection Error (localhost)**
   - The app is trying to connect to localhost instead of Railway's database
   - Check that `DATABASE_URL` environment variable is set in Railway
   - Verify the PostgreSQL service is added to your Railway project
   - The updated config will now fail fast with a clear error message if DATABASE_URL is missing

2. **Database Connection Issues**
   - Verify `DATABASE_URL` is set correctly
   - Check if PostgreSQL service is running
   - Ensure database migrations completed successfully

3. **CORS Errors**
   - Verify `BACKEND_CORS_ORIGINS` includes your Vercel domain
   - Check the format: `["https://domain.com", "http://localhost:3000"]`

4. **Port Issues**
   - Railway automatically sets the `PORT` environment variable
   - Your app should use `$PORT` in the start command

### Debugging Commands

```bash
# View deployment logs
railway logs

# Check environment variables
railway variables

# Restart the service
railway service restart

# Connect to the service shell
railway shell
```

## Scaling and Performance

### Railway Plans
- **Free Tier**: Limited resources, good for development
- **Pro Plan**: More resources, better for production
- **Team Plan**: Collaboration features

### Performance Tips
1. Use connection pooling for database connections
2. Implement caching with Redis
3. Monitor resource usage in Railway dashboard
4. Set up proper logging and monitoring

## Security Considerations

1. **Environment Variables**: Never commit sensitive data
2. **CORS**: Only allow necessary origins
3. **Database**: Use SSL connections
4. **API Keys**: Store all keys as environment variables
5. **Secrets**: Use Railway's secrets management

## Next Steps

After successful Railway deployment:
1. Deploy your frontend to Vercel
2. Set up custom domain (optional)
3. Configure monitoring and alerts
4. Set up CI/CD for automatic deployments
5. Implement proper error handling and logging
