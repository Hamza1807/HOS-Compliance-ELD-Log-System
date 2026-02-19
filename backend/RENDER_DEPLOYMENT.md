# Deploy Django Backend to Render

## Step-by-Step Deployment Guide

### 1. Prepare Your Repository

Make sure all changes are committed and pushed:

```bash
git add .
git commit -m "Prepare backend for Render deployment"
git push
```

### 2. Create a Render Account

1. Go to https://render.com
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### 3. Create a New Web Service

1. Click **"New +"** button in the top right
2. Select **"Web Service"**
3. Connect your GitHub repository
4. Select your repository from the list

### 4. Configure Your Web Service

Fill in the following settings:

**Basic Settings:**
- **Name**: `hos-backend` (or any name you prefer)
- **Region**: Choose the closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn hos_project.wsgi:application`

**Instance Type:**
- Select **"Free"** for testing (it will spin down after inactivity)
- Or **"Starter"** ($7/month) for better performance

### 5. Add Environment Variables

Click **"Advanced"** and add these environment variables:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `SECRET_KEY` | Generate a secure key (see below) |
| `DEBUG` | `False` |
| `VERCEL_DOMAIN` | `your-app.vercel.app` (from Vercel) |

**To generate a SECRET_KEY**, run in your terminal:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Create a PostgreSQL Database (Optional but Recommended)

Render offers a free PostgreSQL database:

1. From your dashboard, click **"New +"** → **"PostgreSQL"**
2. Name it: `hos-database`
3. Select **"Free"** tier
4. Click **"Create Database"**
5. Once created, go back to your Web Service
6. Click **"Environment"** tab
7. Add environment variable:
   - Key: `DATABASE_URL`
   - Value: Copy the **"Internal Database URL"** from your PostgreSQL database

**Note**: Free PostgreSQL databases are deleted after 90 days of inactivity.

### 7. Deploy

1. Click **"Create Web Service"**
2. Render will automatically start building and deploying
3. Wait for the build to complete (5-10 minutes)
4. Your backend URL will be: `https://hos-backend.onrender.com`

### 8. Verify Deployment

Once deployed, test your API:
- Visit: `https://your-backend.onrender.com/api/` (should see DRF browsable API)
- Test endpoint: `https://your-backend.onrender.com/api/calculate-trip/`

### 9. Update Frontend Environment Variable

Update your Vercel deployment:

1. Go to Vercel Dashboard
2. Select your frontend project
3. Go to **Settings** → **Environment Variables**
4. Add:
   - Key: `REACT_APP_API_URL`
   - Value: `https://your-backend.onrender.com`
5. Redeploy your frontend

### 10. Update Frontend Code to Use Environment Variable

You'll need to update your frontend API calls to use this environment variable instead of hardcoded localhost.

---

## Important Notes

### Free Tier Limitations:
- **Spins down after 15 minutes of inactivity**
- First request after spin-down takes 50+ seconds
- 750 hours/month free compute time

### Troubleshooting:

**Build fails?**
- Check build logs for errors
- Verify `build.sh` has correct line endings (Unix-style)
- Ensure all dependencies are in `requirements.txt`

**502 Bad Gateway?**
- Check if start command is correct
- View logs: Click "Logs" tab in your service
- Verify environment variables are set

**CORS errors?**
- Make sure `VERCEL_DOMAIN` environment variable is set correctly
- Check Django logs for CORS-related messages

**Static files not loading?**
- Verify `collectstatic` ran successfully in build logs
- Check `STATIC_ROOT` and `STATIC_URL` settings

---

## Next Steps

After successful deployment:
1. ✅ Update frontend to use production API URL
2. ✅ Test all endpoints from your deployed frontend
3. ✅ Set up monitoring (Render provides basic monitoring)
4. ✅ Consider upgrading to paid tier if you need 24/7 uptime

Need help? Check Render's documentation: https://render.com/docs/web-services
