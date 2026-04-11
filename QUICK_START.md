# 🚀 Quick Start - JobNect Backend

Get your backend running in 5 minutes!

## ✅ Checklist

### Step 1: Install Dependencies (2 minutes)
```bash
cd jobnect-backend-python
pip install -r requirements.txt
```

### Step 2: Setup Database (1 minute)

**Option A - Local PostgreSQL:**
```sql
CREATE DATABASE jobnect_db;
```

**Option B - Free Cloud Database:**
- Go to https://render.com
- Create PostgreSQL database (free)
- Copy the "Internal Database URL"

### Step 3: Configure Environment (30 seconds)
```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/jobnect_db
SECRET_KEY=your-secret-key-min-32-chars
```

### Step 4: Run Backend (30 seconds)
```bash
python main.py
```

✅ Backend running at: http://localhost:8000

### Step 5: Test API (1 minute)

Open browser: http://localhost:8000/docs

Try the `/api/v10/registration` endpoint:
```json
{
  "name": "Test User",
  "email": "test@example.com",
  "phone": "1234567890",
  "password": "password123",
  "password_confirmation": "password123",
  "company": "N/A"
}
```

✅ You should get a token back!

---

## 📱 Connect Flutter App

### For Android Emulator:
Already configured in `urls.dart`:
```dart
static const String _baseUrl = 'http://10.0.2.2:8000/api/v10';
```

### For iOS Simulator:
Change to:
```dart
static const String _baseUrl = 'http://localhost:8000/api/v10';
```

### For Physical Device:
1. Find your IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Update `urls.dart`:
```dart
static const String _baseUrl = 'http://YOUR_IP:8000/api/v10';
```

---

## 🎯 What You Get

✅ **66 API Endpoints** - Complete backend for entire app  
✅ **Auto-seeded Database** - Sample data ready to use  
✅ **JWT Authentication** - Secure token-based auth  
✅ **Interactive Docs** - Swagger UI at `/docs`  
✅ **Production Ready** - Deploy to Render.com in minutes  

---

## 📚 Documentation

- **README.md** - Overview and features
- **SETUP_GUIDE.md** - Detailed setup instructions
- **API_ENDPOINTS.md** - Complete API reference with examples

---

## 🆘 Common Issues

**Database connection error?**
- Check PostgreSQL is running
- Verify DATABASE_URL in .env

**Import errors?**
- Run: `pip install -r requirements.txt`

**Port already in use?**
- Run: `uvicorn main:app --port 8001`

---

## 🎉 You're Done!

Your backend is now running with:
- ✅ User authentication
- ✅ Profile & resume management
- ✅ Job listings & applications
- ✅ Company profiles
- ✅ Master data (categories, cities, etc.)

**Next Steps:**
1. Test endpoints in Swagger UI: http://localhost:8000/docs
2. Run your Flutter app
3. Test signup/login flow
4. Deploy to production (see SETUP_GUIDE.md)

---

## 🚀 Deploy to Production (5 minutes)

1. Push code to GitHub
2. Go to https://render.com
3. Create PostgreSQL database
4. Create Web Service:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy!

Your API will be live at: `https://your-app.onrender.com`

---

## 📞 Need Help?

Check the documentation:
- SETUP_GUIDE.md - Detailed setup
- API_ENDPOINTS.md - All endpoints
- README.md - Overview

Happy coding! 🎉
