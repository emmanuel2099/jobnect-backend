# 🚀 Render.com Setup Guide (5 Minutes)

## Why Render.com?
- ✅ 100% Free tier (1GB database)
- ✅ No installation needed
- ✅ Built-in database viewer
- ✅ Production-ready
- ✅ Automatic backups

---

## Step 1: Create Render.com Account (1 minute)

1. Go to https://render.com
2. Click "Get Started"
3. Sign up with:
   - GitHub (recommended)
   - Or email

---

## Step 2: Create PostgreSQL Database (2 minutes)

1. After login, click **"New +"** (top right)
2. Select **"PostgreSQL"**
3. Configure:
   - **Name**: `jobnect-db`
   - **Database**: `jobnect_db` (auto-filled)
   - **User**: (auto-generated)
   - **Region**: Choose closest to you
     - US: Oregon (US West)
     - Europe: Frankfurt
     - Asia: Singapore
   - **PostgreSQL Version**: 15 (default)
   - **Plan**: **Free** (select this!)
4. Click **"Create Database"**

⏳ Wait 2-3 minutes for database to be created...

---

## Step 3: Get Connection Details (1 minute)

After creation, you'll see the dashboard with:

### Internal Database URL (Use this!)
```
postgresql://jobnect_db_user:xxxxx@dpg-xxxxx-a.oregon-postgres.render.com/jobnect_db
```

**Copy this entire URL!**

### Connection Details (Alternative)
- **Hostname**: dpg-xxxxx-a.oregon-postgres.render.com
- **Port**: 5432
- **Database**: jobnect_db
- **Username**: jobnect_db_user
- **Password**: (long random string)

---

## Step 4: Update Your .env File (30 seconds)

1. Open `jobnect-backend-python/.env`
2. Paste the Internal Database URL:

```env
DATABASE_URL=postgresql://jobnect_db_user:xxxxx@dpg-xxxxx-a.oregon-postgres.render.com/jobnect_db
SECRET_KEY=your-secret-key-at-least-32-characters-long
```

**Important:** Use the **Internal Database URL**, not External!

---

## Step 5: Run Your Backend (30 seconds)

```bash
cd jobnect-backend-python
python main.py
```

You should see:
```
🔄 Creating database tables...
✅ Database tables created
🔄 Initializing default data...
✅ Default data initialized
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **Done!** Your backend is connected to Render.com database!

---

## Step 6: View Your Database (1 minute)

### Option A: Render.com Dashboard
1. Go back to Render.com
2. Click on your database "jobnect-db"
3. Click **"Connect"** tab
4. Click **"External Connection"**
5. Use these details with any database tool

### Option B: Built-in Query Tool
1. In Render dashboard, click your database
2. Click **"Shell"** tab
3. Run SQL queries:
```sql
-- List all tables
\dt

-- View job categories
SELECT * FROM job_categories;

-- View users
SELECT * FROM users;
```

### Option C: Connect with pgAdmin
1. Open pgAdmin
2. Right-click "Servers" → "Register" → "Server"
3. **General Tab:**
   - Name: Render JobNect DB
4. **Connection Tab:**
   - Copy details from Render "External Connection"
   - Host: dpg-xxxxx-a.oregon-postgres.render.com
   - Port: 5432
   - Database: jobnect_db
   - Username: jobnect_db_user
   - Password: (from Render)
5. Click "Save"

---

## 🎉 You're Done!

Your setup:
- ✅ Free PostgreSQL database on Render.com
- ✅ Backend connected to database
- ✅ Sample data loaded
- ✅ Ready to test with Flutter app

---

## 📊 Check Your Data

After running the backend, verify data was created:

### In Render Shell:
```sql
-- Count tables (should be 20+)
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check sample data
SELECT COUNT(*) FROM job_categories;  -- Should be 10
SELECT COUNT(*) FROM cities;          -- Should be 8
SELECT COUNT(*) FROM companies;       -- Should be 5
SELECT COUNT(*) FROM jobs;            -- Should be 10
```

---

## 🔄 Deploy Backend to Render (Optional)

Want to deploy your backend too?

1. Push code to GitHub
2. In Render, click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Configure:
   - **Name**: `jobnect-api`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - **DATABASE_URL**: (copy from your database)
   - **SECRET_KEY**: (random 32+ chars)
6. Click **"Create Web Service"**

Your API will be live at: `https://jobnect-api.onrender.com`

---

## 💰 Free Tier Limits

**What you get FREE:**
- 1 GB storage (enough for ~10,000 users)
- 90 days free, then $7/month (but free tier still available)
- Automatic backups
- SSL/HTTPS included
- 99.9% uptime

**When to upgrade:**
- Database > 1GB
- Need faster performance
- Need more connections

For your app, free tier is perfect!

---

## 🆘 Troubleshooting

**Can't connect to database:**
- Check you copied the **Internal** URL, not External
- Verify URL is complete (starts with `postgresql://`)
- Check internet connection

**Tables not created:**
- Run `python main.py` again
- Check console for errors
- Verify DATABASE_URL is correct

**"Too many connections" error:**
- Free tier has connection limit
- Close unused connections
- Restart backend

---

## 📱 Update Flutter App

After deploying backend to Render:

Update `urls.dart`:
```dart
static const String _baseUrl = 'https://jobnect-api.onrender.com/api/v10';
```

---

## ✅ Checklist

- [ ] Created Render.com account
- [ ] Created PostgreSQL database
- [ ] Copied Internal Database URL
- [ ] Updated .env file
- [ ] Ran backend successfully
- [ ] Verified tables were created
- [ ] Tested API at http://localhost:8000/docs

---

## 🎯 Next Steps

1. Test your API endpoints in Swagger UI
2. Run Flutter app and test signup/login
3. Deploy backend to Render (optional)
4. Update Flutter app with production URL

You're all set! 🚀
