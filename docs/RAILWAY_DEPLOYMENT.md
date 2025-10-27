# Railway Deployment Guide

## Prerequisites
1. Railway account (https://railway.app)
2. GitHub repository connected to Railway
3. PostgreSQL database (Railway provides this)

## Step-by-Step Deployment

### 1. Connect Repository to Railway
1. Go to Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

### 2. Set Up Database
1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically provide a `DATABASE_URL` environment variable

### 3. Deploy Backend
1. Railway will automatically detect the Python backend
2. The `railway.toml` and `Procfile` will configure the deployment
3. Railway will use the `DATABASE_URL` environment variable automatically

### 4. Environment Variables (Optional)
You can set additional environment variables in Railway dashboard:
- `DATABASE_URL` (automatically provided by Railway PostgreSQL)
- `PORT` (automatically provided by Railway)

### 5. Deploy Frontend (Separate Service)
For the frontend, you'll need to:
1. Create a new service in Railway
2. Set the root directory to `frontend/`
3. Configure build settings for React/Vite

## Troubleshooting

### Common Issues:

1. **Database Connection Error**
   - Ensure `DATABASE_URL` is set correctly
   - Check that the database URL format is correct (postgresql:// not postgres://)

2. **CORS Errors**
   - The CORS configuration has been updated to allow Railway domains
   - Check browser console for specific CORS errors

3. **Port Issues**
   - Railway automatically provides the `PORT` environment variable
   - The app is configured to use `$PORT` in the start command

4. **Build Failures**
   - Check Railway logs for specific error messages
   - Ensure all dependencies are in `requirements.txt`

### Checking Logs:
1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Deployments" tab
4. Click on the latest deployment to view logs

## Database Migration
After deployment, you may need to run database migrations:
1. Connect to your Railway service via SSH or use Railway CLI
2. Run: `alembic upgrade head`

## Frontend Deployment
For the React frontend, consider:
1. Deploying to Vercel (recommended for React apps)
2. Or configure Railway to build the frontend as a separate service
3. Update API endpoints in frontend to point to your Railway backend URL
