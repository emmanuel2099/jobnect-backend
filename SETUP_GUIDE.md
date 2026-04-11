# Complete Setup Guide for JobNect Backend

## Step-by-Step Setup Instructions

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database
- Git (optional)

---

## Local Development Setup

### Step 1: Install Python Dependencies

```bash
cd jobnect-backend-python
pip install -r requirements.txt
```

### Step 2: Setup PostgreSQL Database

**Option A: Local PostgreSQL**
1. Install PostgreSQL from https://www.postgresql.org/download/
2. Create database:
```sql
CREATE DATABASE jobnect_db;
```

**Option B: Free Cloud PostgreSQL**
- Render.com: https://render.com (Free tier)
- Railway.app: https://railway.app (Free tier)
- Supabase: https://supabase.com (Free tier)

### Step 3: Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env file with your settings
```

Example `.env` content:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/jobnect_db
SECRET_KEY=your-super-secret-key-at-least-32-characters-long
```

### Step 4: Run the Backend

```bash
python main.py
```

The server will:
- ✅ Create all database tables automatically
- ✅ Seed sample data (categories, cities, companies, jobs)
- ✅ Start on http://localhost:8000

### Step 5: Test the API

Open your browser and visit:
- **API Root**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Connect Flutter App to Backend

### For Android Emulator

The Flutter app is already configured in `urls.dart`:
```dart
static const String _baseUrl = 'http://10.0.2.2:8000/api/v10';
```

This works because:
- `10.0.2.2` is the Android emulator's alias for `localhost`
- Port `8000` is where the backend runs

### For iOS Simulator

Change `urls.dart` to:
```dart
static const String _baseUrl = 'http://localhost:8000/api/v10';
```

### For Physical Device

1. Find your computer's IP address:
   - Windows: `ipconfig` (look for IPv4)
   - Mac/Linux: `ifconfig` or `ip addr`

2. Update `urls.dart`:
```dart
static const String _baseUrl = 'http://YOUR_IP:8000/api/v10';
```

3. Make sure your phone and computer are on the same WiFi network

---

## Deploy to Production (Render.com)

### Step 1: Prepare Your Code

1. Push code to GitHub repository
2. Make sure all files are committed

### Step 2: Create PostgreSQL Database

1. Go to https://render.com
2. Click "New +" → "PostgreSQL"
3. Name: `jobnect-db`
4. Click "Create Database"
5. Copy the "Internal Database URL"

### Step 3: Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `jobnect-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 4: Add Environment Variables

In the "Environment" section, add:
- **DATABASE_URL**: (paste the Internal Database URL from Step 2)
- **SECRET_KEY**: (generate a random 32+ character string)

### Step 5: Deploy

1. Click "Create Web Service"
2. Wait for deployment (2-3 minutes)
3. Your API will be live at: `https://jobnect-api.onrender.com`

### Step 6: Update Flutter App

Update `urls.dart`:
```dart
static const String _baseUrl = 'https://jobnect-api.onrender.com/api/v10';
```

---

## Testing the Backend

### Test Registration

```bash
curl -X POST http://localhost:8000/api/v10/registration \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "phone": "1234567890",
    "password": "password123",
    "password_confirmation": "password123",
    "company": "N/A"
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Registration successful",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "name": "Test User",
      "email": "test@example.com",
      ...
    }
  }
}
```

### Test Login

```bash
curl -X POST http://localhost:8000/api/v10/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Test Protected Endpoint

```bash
# Use the token from registration/login
curl -X GET http://localhost:8000/api/v10/applicant/resume/details \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## API Endpoints Summary

### Authentication (No token required)
- `POST /api/v10/registration` - Register new user
- `POST /api/v10/login` - Login user
- `POST /api/v10/password-reset-email-verification` - Send reset OTP
- `POST /api/v10/reset-password` - Reset password

### Profile & Resume (Token required)
- `GET /api/v10/applicant/resume/details` - Get complete resume
- `POST /api/v10/applicant/profile/update` - Update profile
- `POST /api/v10/applicant/image/update` - Update profile photo
- `POST /api/v10/resume/update/personal-info` - Update personal info
- `POST /api/v10/resume/update/address-info` - Update address
- `POST /api/v10/resume/update/career-info` - Update career info
- Experience: `/resume/experience/store`, `/update`, `/delete/{id}`
- Education: `/resume/education/store`, `/update`, `/delete/{id}`
- Training: `/resume/training/store`, `/update`, `/delete/{id}`
- Language: `/resume/language/store`, `/update`, `/delete/{id}`
- Reference: `/resume/reference/store`, `/update`, `/delete/{id}`

### Jobs (Public + Protected)
- `GET /api/v10/jobs/recent` - Recent jobs (public)
- `GET /api/v10/jobs/popular` - Popular jobs (public)
- `GET /api/v10/jobs-filter` - Filter jobs (public)
- `GET /api/v10/jobs/details/{id}` - Job details (public)
- `GET /api/v10/job/index` - Company's jobs (token required)
- `POST /api/v10/job/store` - Create job (token required)
- `POST /api/v10/job/update` - Update job (token required)
- `DELETE /api/v10/job/delete/{id}` - Delete job (token required)

### Applications (Token required)
- `POST /api/v10/applicant/job-apply` - Apply for job
- `GET /api/v10/applicant/job/applied` - Get applied jobs
- `GET /api/v10/applicant/job/bookmarks` - Get bookmarked jobs
- `POST /api/v10/applicant/job/bookmark/store` - Toggle bookmark

### Companies (Public)
- `GET /api/v10/companies` - All companies
- `GET /api/v10/featured-companies` - Featured companies
- `GET /api/v10/company/details/{id}` - Company details
- `GET /api/v10/company/jobs/{id}` - Company jobs

### Master Data (Public)
- `GET /api/v10/job-category` - Job categories
- `GET /api/v10/cities` - Cities
- `GET /api/v10/skills` - Skills
- `GET /api/v10/designations` - Designations
- `GET /api/v10/job-types` - Job types
- `GET /api/v10/job-levels` - Job levels
- `GET /api/v10/education-levels` - Education levels
- `GET /api/v10/settings` - App settings
- `GET /api/v10/app-sliders` - App banners

---

## Troubleshooting

### Database Connection Error

**Error**: `could not connect to server`

**Solution**:
1. Check PostgreSQL is running
2. Verify DATABASE_URL in .env
3. Test connection: `psql -U username -d jobnect_db`

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
pip install -r requirements.txt
```

### Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Use different port
uvicorn main:app --port 8001
```

### Token Authentication Error

**Error**: `Could not validate credentials`

**Solution**:
1. Check token is included in Authorization header
2. Format: `Authorization: Bearer YOUR_TOKEN`
3. Token might be expired (generate new one by logging in)

---

## Database Schema

The backend creates these tables automatically:

**User Management**
- users
- resumes
- experiences
- educations
- trainings
- languages
- references

**Job Management**
- jobs
- companies
- job_applications
- bookmarks

**Master Data**
- job_categories
- cities
- skills
- designations
- job_types
- job_levels
- education_levels

**Other**
- notifications
- social_links
- kyc
- app_settings
- app_sliders

---

## Sample Data

On first run, the database is populated with:
- ✅ 10 job categories (IT, Marketing, Sales, etc.)
- ✅ 8 cities (New York, London, Tokyo, etc.)
- ✅ 6 job types (Full-time, Part-time, Contract, etc.)
- ✅ 6 job levels (Entry, Junior, Mid, Senior, etc.)
- ✅ 7 education levels (High School, Bachelor's, Master's, etc.)
- ✅ 10 skills (Python, JavaScript, Marketing, etc.)
- ✅ 10 designations (Software Engineer, Manager, etc.)
- ✅ 5 sample companies
- ✅ 10 sample jobs

---

## Next Steps

1. ✅ Backend is running locally
2. ✅ Test API endpoints using Swagger UI
3. ✅ Run Flutter app and test signup/login
4. ✅ Deploy to Render.com for production
5. ✅ Update Flutter app with production URL

---

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the API documentation at `/docs`
3. Check database connection and credentials
4. Verify all dependencies are installed

## Summary

You now have a complete backend API with:
- ✅ 60+ endpoints
- ✅ JWT authentication
- ✅ Complete CRUD operations
- ✅ Auto-seeded database
- ✅ Production-ready code
- ✅ Easy deployment to Render.com

The backend is ready to use with your Flutter app!
