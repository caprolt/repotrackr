# Railway Deployment Checklist

## Pre-Deployment ✅

- [ ] Railway account created
- [ ] GitHub repository ready
- [ ] All configuration files added:
  - [ ] `railway.toml`
  - [ ] `nixpacks.toml`
  - [ ] `Procfile`
  - [ ] `runtime.txt`
  - [ ] `requirements.txt`

## Railway Setup ✅

- [ ] Create new Railway project
- [ ] Connect GitHub repository
- [ ] Set root directory to `backend`
- [ ] Add PostgreSQL service
- [ ] Add Redis service (optional)

## Environment Variables ✅

- [ ] `APP_NAME=RepoTrackr`
- [ ] `DEBUG=false`
- [ ] `ENVIRONMENT=production`
- [ ] `API_V1_STR=/api/v1`
- [ ] `PROJECT_NAME=RepoTrackr`
- [ ] `VERSION=0.1.0`
- [ ] `BACKEND_CORS_ORIGINS=["https://your-app.vercel.app", "http://localhost:3000"]` (Vercel frontend domain)

## Automatic Variables (Railway provides) ✅

- [ ] `DATABASE_URL` - Auto-injected by PostgreSQL service
- [ ] `REDIS_URL` - Auto-injected by Redis service (if added)
- [ ] `PORT` - Auto-injected by Railway

## Deployment ✅

- [ ] Deploy the service
- [ ] Check build logs for any errors
- [ ] Verify database migrations completed
- [ ] Test health endpoint: `/health`
- [ ] Test API docs: `/api/v1/docs`

## Post-Deployment ✅

- [ ] Copy Railway app URL
- [ ] Update Vercel environment variable: `NEXT_PUBLIC_API_URL`
- [ ] Test frontend-backend communication
- [ ] Verify CORS is working
- [ ] Check application logs

## Troubleshooting ✅

- [ ] Build failures - Check logs and requirements.txt
- [ ] Database connection - Verify DATABASE_URL
- [ ] CORS errors - Check BACKEND_CORS_ORIGINS format
- [ ] Port issues - Ensure using $PORT variable

## Quick Commands

```bash
# Deploy via Railway CLI (optional)
railway login
railway link
railway up

# Check logs
railway logs

# View variables
railway variables

# Restart service
railway service restart
```

## URLs to Test

- Health check: `https://your-app.up.railway.app/health`
- API docs: `https://your-app.up.railway.app/api/v1/docs`
- Root endpoint: `https://your-app.up.railway.app/`
