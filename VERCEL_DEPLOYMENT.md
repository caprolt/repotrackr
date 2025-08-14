# Vercel Deployment Guide

This guide will help you deploy your RepoTrackr frontend to Vercel and set up the backend deployment.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Backend Deployment**: Your FastAPI backend needs to be deployed separately (see Backend Deployment section)
3. **Database**: Set up your production database (Supabase recommended)

## Frontend Deployment (Vercel)

### 1. Prepare Your Repository

Your project is already configured for Vercel deployment with the following files:
- `frontend/vercel.json` - Vercel configuration
- `frontend/.env.example` - Environment variables template
- Updated `frontend/next.config.js` - Production-ready configuration

### 2. Deploy to Vercel

#### Option A: Deploy via Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend directory
cd frontend

# Deploy
vercel

# Follow the prompts to link your project
```

#### Option B: Deploy via Vercel Dashboard
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Set the root directory to `frontend`
5. Configure environment variables (see below)

### 3. Configure Environment Variables

In your Vercel project settings, add the following environment variable:

```
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

Replace `your-backend-domain.com` with your actual backend URL.

## Backend Deployment

Since Vercel doesn't support Python backends, you'll need to deploy your FastAPI backend separately. Here are your options:

### Option 1: Railway (Recommended)
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Set the root directory to `backend`
4. Add environment variables from your `.env` file
5. Deploy

### Option 2: Render
1. Go to [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables

### Option 3: Heroku
1. Create a `Procfile` in the backend directory:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
2. Deploy using Heroku CLI or GitHub integration

### Option 4: DigitalOcean App Platform
1. Go to [digitalocean.com](https://digitalocean.com)
2. Create a new App
3. Connect your GitHub repository
4. Configure as a Python app
5. Set environment variables

## Environment Variables for Backend

Make sure to set these environment variables in your backend deployment:

```bash
# Database (use Supabase for production)
DATABASE_URL=postgresql+asyncpg://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
DATABASE_URL_SYNC=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres

# CORS (add your Vercel domain)
BACKEND_CORS_ORIGINS=["https://your-app.vercel.app", "http://localhost:3000"]

# Other settings
DEBUG=false
ENVIRONMENT=production
```

## Post-Deployment Steps

1. **Update CORS**: Add your Vercel domain to the backend's CORS origins
2. **Test API**: Verify your frontend can communicate with the backend
3. **Database Migration**: Run database migrations on your production database
4. **Monitor**: Set up monitoring and logging for both frontend and backend

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure your backend CORS includes your Vercel domain
2. **API Connection**: Verify `NEXT_PUBLIC_API_URL` is set correctly
3. **Database Connection**: Ensure your production database is accessible
4. **Environment Variables**: Check that all required variables are set in Vercel

### Debugging

- Check Vercel deployment logs in the dashboard
- Use browser dev tools to inspect API requests
- Verify environment variables are loaded correctly

## Security Considerations

1. **Environment Variables**: Never commit sensitive data to your repository
2. **CORS**: Only allow necessary origins in your backend CORS configuration
3. **Database**: Use connection pooling and SSL for production databases
4. **API Keys**: Store all API keys as environment variables

## Next Steps

After successful deployment:
1. Set up custom domain (optional)
2. Configure monitoring and analytics
3. Set up CI/CD for automatic deployments
4. Implement proper error handling and logging
