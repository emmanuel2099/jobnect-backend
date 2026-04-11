# JobNect Python Backend API

Complete REST API backend for JobNect mobile application built with **FastAPI** and **PostgreSQL**.

## 🚀 Features

✅ Complete Authentication System (JWT)
✅ User Profile & Resume Management
✅ Job Posting & Management
✅ Job Applications & Bookmarks
✅ Company Profiles
✅ Master Data (Categories, Cities, Skills, etc.)
✅ Auto-populated Sample Data
✅ Interactive API Documentation (Swagger UI)

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT (python-jose)
- **Password Hashing:** Passlib with bcrypt

## 📦 Quick Start

### 1. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Database

Create a PostgreSQL database:
```sql
CREATE DATABASE jobnect_db;
```

Or use free PostgreSQL hosting:
- [Render.com](https://render.com) - Free PostgreSQL
- [Railway.app](https://railway.app) - Free PostgreSQL
- [Supabase](https://supabase.com) - Free PostgreSQL

### 3. Configure Environment

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and add your database URL:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/jobnect_db
SECRET_KEY=your-super-secret-key-min-32-characters
```

### 4. Run the Server

```bash
# Development mode (auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start on `http://localhost:8000`

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🗄️ Database Auto-Setup

On first run, the API will automatically:
1. Create all database tables
2. Insert default master data:
   - 10 job categories
   - 8 cities
   - 6 job types
   - 6 job levels
   - 7 education levels
   - 10 skills
   - 10 designations

## 📱 Connect Flutter App

The Flutter app's `urls.dart` is already configured:

**For local testing (Android emulator):**
```dart
static const String _baseUrl = 'http://10.0.2.2:8000/api/v10';
```

**For production:**
```dart
static const String _baseUrl = 'https://your-app.onrender.com/api/v10';
```

## 🧪 Test the API

### Test Registration
```bash
curl -X POST http://localhost:8000/api/v10/registration \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "password": "password123",
    "password_confirmation": "password123",
    "company": "N/A"
  }'
```

### Test Login
```bash
curl -X POST http://localhost:8000/api/v10/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

## 🌐 Deploy to Render (Free)

1. Push code to GitHub
2. Go to [Render.com](https://render.com)
3. Create PostgreSQL database (free)
4. Create Web Service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `DATABASE_URL` (from PostgreSQL)
   - `SECRET_KEY` (random string)
6. Deploy!

## 📁 Project Structure

```
jobnect-backend-python/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration
│   ├── database.py        # Database connection
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── auth.py            # Authentication utilities
│   └── routers/           # API routes
│       ├── auth.py
│       ├── profile.py
│       ├── jobs.py
│       ├── applications.py
│       ├── companies.py
│       └── master_data.py
└── README.md
```

## 🔑 API Endpoints

### Authentication
- POST `/api/v10/registration` - User signup
- POST `/api/v10/login` - User login

### Profile & Resume
- GET `/api/v10/applicant/resume/details` - Get resume
- POST `/api/v10/applicant/profile/update` - Update profile
- POST `/api/v10/resume/update/personal-info` - Update personal info
- POST `/api/v10/resume/experience/store` - Add experience
- And more...

### Jobs
- GET `/api/v10/jobs/recent` - Latest jobs
- GET `/api/v10/jobs/popular` - Popular jobs
- GET `/api/v10/jobs-filter` - Filter jobs
- POST `/api/v10/job/store` - Create job

### Applications
- POST `/api/v10/applicant/job-apply` - Apply for job
- GET `/api/v10/applicant/job/applied` - Applied jobs
- POST `/api/v10/applicant/job/bookmark/store` - Bookmark job

### Master Data
- GET `/api/v10/job-category` - Job categories
- GET `/api/v10/cities` - Cities
- GET `/api/v10/skills` - Skills
- GET `/api/v10/designations` - Designations

## 🆘 Troubleshooting

**Database connection error:**
- Check DATABASE_URL is correct
- Ensure PostgreSQL is running
- Verify database exists

**Import errors:**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

**Port already in use:**
- Change port: `uvicorn main:app --port 8001`

## 📄 License

MIT License
