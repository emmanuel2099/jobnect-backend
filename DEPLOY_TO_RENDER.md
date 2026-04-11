# 🚀 Deploy JobNect Backend to Render

## Prerequisites
- GitHub account
- Render account (already have)
- Your code in a GitHub repository

## Step 1: Push Code to GitHub

### Option A: Create New Repository on GitHub
1. Go to https://github.com/new
2. Create a new repository named `jobnect-backend`
3. Don't initialize with README (we already have files)

### Option B: Use Existing Repository
If you already have a repo, skip to Step 2

## Step 2: Initialize Git and Push

Open terminal in `jobnect-backend-python` folder:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - JobNect FastAPI backend"

# Add your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/jobnect-backend.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Deploy on Render

### Method 1: Using render.yaml (Automatic)

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Select the `jobnect-backend` repository
5. Render will detect `render.yaml` and set everything up automatically
6. Click **"Apply"**

### Method 2: Manual Setup

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `jobnect-api`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

5. Add Environment Variables:
   - Click **"Advanced"** → **"Add Environment Variable"**
   - Add:
     ```
     DATABASE_URL = postgresql://jobnect_db_user:ftYcP25S34SsTiRqHWLFvggRdVgx4VXP@dpg-d7d0cpq8qa3s73bdai7g-a.oregon-postgres.render.com/jobnect_db
     SECRET_KEY = jobnect-secret-key-12345678901234567890abcdefghijklmnop
     PYTHON_VERSION = 3.11.0
     ```

6. Click **"Create Web Service"**

## Step 4: Wait for Deployment

- Render will build and deploy your app (takes 2-5 minutes)
- Watch the logs for any errors
- Once deployed, you'll get a URL like: `https://jobnect-api.onrender.com`

## Step 5: Test Your Live API

Use Postman to test:

### Test Registration
**POST** `https://jobnect-api.onrender.com/api/v10/registration`

Body (JSON):
```json
{
  "name": "Test User",
  "email": "test@example.com",
  "phone": "1234567890",
  "password": "password123",
  "password_confirmation": "password123",
  "company": "Test Company"
}
```

### View All Users
**GET** `https://jobnect-api.onrender.com/api/v10/users/list`

### Check API Status
**GET** `https://jobnect-api.onrender.com/`

## Step 6: Update Flutter App

Update your Flutter app's API URL in `api_caller.dart`:

```dart
static const String baseUrl = "https://jobnect-api.onrender.com/api/v10";
```

## Troubleshooting

### Build Fails
- Check Python version in requirements.txt
- Ensure all dependencies are listed
- Check Render logs for specific errors

### Database Connection Issues
- Verify DATABASE_URL is correct
- Check if database is in same region
- Ensure database is active

### App Crashes on Startup
- Check environment variables are set
- Review startup logs in Render dashboard
- Verify SECRET_KEY is set

## Important Notes

⚠️ **Free Tier Limitations:**
- App sleeps after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- 750 hours/month free (enough for one service)

💡 **Keep App Awake:**
- Use a service like UptimeRobot to ping your API every 10 minutes
- Or upgrade to paid plan ($7/month)

## Next Steps

1. ✅ Deploy backend to Render
2. ✅ Test all endpoints with Postman
3. ✅ Update Flutter app with live URL
4. ✅ Test registration from mobile app
5. ✅ Monitor logs and fix any issues

## Support

If you encounter issues:
1. Check Render logs: Dashboard → Your Service → Logs
2. Check database connection: Dashboard → jobnect-db → Info
3. Test endpoints individually in Postman
4. Review error messages in logs

---

**Your Live API will be at:** `https://jobnect-api.onrender.com`

**API Documentation:** `https://jobnect-api.onrender.com/docs`
