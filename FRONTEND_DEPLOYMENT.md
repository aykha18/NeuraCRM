# Frontend Deployment Guide

## Quick Deploy to Railway

### Step 1: Deploy Frontend to Railway
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. **IMPORTANT**: Set the root directory to `frontend/`
6. Railway will automatically detect it's a Node.js project

### Step 2: Configure Environment Variables
In your Railway frontend service, add these environment variables:
- `VITE_API_URL=https://neuracrm.up.railway.app`

### Step 3: Deploy
Railway will automatically:
- Install dependencies (`npm install`)
- Build the project (`npm run build`)
- Start the preview server (`npm run preview`)

## Alternative: Build and Serve from Backend

If you prefer to serve the frontend from the same domain as your API:

1. Build the frontend:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. Copy the `dist` folder to your backend
3. The backend will automatically serve the frontend files

## Testing

After deployment, you should be able to access:
- Frontend: `https://your-frontend-url.railway.app`
- API: `https://neuracrm.up.railway.app`

The frontend will automatically connect to your deployed API.
