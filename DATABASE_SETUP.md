# PostgreSQL Database Setup Guide

## Option 1: Free Cloud Database (Easiest - No Installation)

### Using Render.com (Recommended)

**Step 1: Create Database**
1. Go to https://render.com
2. Sign up for free account
3. Click "New +" → "PostgreSQL"
4. Configure:
   - **Name**: jobnect-db
   - **Database**: jobnect_db
   - **User**: (auto-generated)
   - **Region**: Choose closest to you
   - **Plan**: Free
5. Click "Create Database"

**Step 2: Get Connection Details**
After creation, you'll see:
- **Internal Database URL**: `postgresql://user:pass@host/db`
- **External Database URL**: For external tools
- **PSQL Command**: For command line access

**Step 3: View Database**
- Click "Connect" → "External Connection"
- Use the connection details with any tool below

**Step 4: Update .env**
```env
DATABASE_URL=postgresql://user:pass@host:5432/jobnect_db
```

---

## Option 2: Local PostgreSQL Installation

### Windows

**Install PostgreSQL:**
1. Download from: https://www.postgresql.org/download/windows/
2. Run installer (includes pgAdmin)
3. Set password for postgres user
4. Remember port (default: 5432)

**Create Database:**
1. Open pgAdmin (installed with PostgreSQL)
2. Right-click "Databases" → "Create" → "Database"
3. Name: `jobnect_db`
4. Click "Save"

**Update .env:**
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/jobnect_db
```

### Mac

**Install PostgreSQL:**
```bash
# Using Homebrew
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb jobnect_db
```

**Update .env:**
```env
DATABASE_URL=postgresql://your_username@localhost:5432/jobnect_db
```

### Linux

**Install PostgreSQL:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql

# Create database
sudo -u postgres createdb jobnect_db
```

**Update .env:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/jobnect_db
```

---

## Database Viewing Tools

### 1. pgAdmin (Best for PostgreSQL)

**What it is:** Official PostgreSQL GUI tool

**Install:**
- Windows/Mac: Included with PostgreSQL installer
- Or download: https://www.pgadmin.org/download/

**Connect:**
1. Open pgAdmin
2. Right-click "Servers" → "Register" → "Server"
3. **General Tab:**
   - Name: JobNect DB
4. **Connection Tab:**
   - Host: localhost (or your cloud host)
   - Port: 5432
   - Database: jobnect_db
   - Username: postgres (or your username)
   - Password: your_password
5. Click "Save"

**View Data:**
- Expand: Servers → JobNect DB → Databases → jobnect_db → Schemas → public → Tables
- Right-click any table → "View/Edit Data" → "All Rows"

### 2. DBeaver (Universal Database Tool)

**What it is:** Free, cross-platform database tool

**Install:**
1. Download: https://dbeaver.io/download/
2. Install and open
3. Click "New Database Connection" (plug icon)
4. Select "PostgreSQL"
5. Enter connection details:
   - Host: localhost
   - Port: 5432
   - Database: jobnect_db
   - Username: postgres
   - Password: your_password
6. Click "Test Connection"
7. Click "Finish"

**View Data:**
- Expand connection → jobnect_db → Schemas → public → Tables
- Double-click any table to view data

### 3. TablePlus (Modern & Beautiful)

**What it is:** Modern, native database client

**Install:**
1. Download: https://tableplus.com/
2. Install and open
3. Click "Create a new connection"
4. Select "PostgreSQL"
5. Enter details and connect

**View Data:**
- Click any table in sidebar
- View and edit data in spreadsheet-like interface

### 4. VS Code Extension

**Install:**
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search "PostgreSQL" by Chris Kolkman
4. Install

**Connect:**
1. Click PostgreSQL icon in sidebar
2. Click "+" to add connection
3. Enter connection details
4. Browse tables and run queries

### 5. Command Line (psql)

**Connect:**
```bash
# Local database
psql -U postgres -d jobnect_db

# Cloud database (Render.com)
psql postgresql://user:pass@host:5432/jobnect_db
```

**Useful Commands:**
```sql
-- List all tables
\dt

-- Describe table structure
\d users
\d jobs

-- View data
SELECT * FROM users;
SELECT * FROM job_categories;
SELECT * FROM jobs LIMIT 10;

-- Count records
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM jobs;

-- Exit
\q
```

---

## Verify Database After Running Backend

After running `python main.py`, your database should have:

### Tables Created (20+):
```sql
-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

### Sample Data Inserted:
```sql
-- Check job categories (should have 10)
SELECT * FROM job_categories;

-- Check cities (should have 8)
SELECT * FROM cities;

-- Check companies (should have 5)
SELECT * FROM companies;

-- Check jobs (should have 10)
SELECT * FROM jobs;
```

---

## Recommended Setup for Beginners

**For Local Development:**
1. Install PostgreSQL with pgAdmin (easiest)
2. Create database using pgAdmin
3. Use pgAdmin to view data

**For Cloud/Production:**
1. Use Render.com (free, no installation)
2. View data in their dashboard
3. Or connect with pgAdmin using external URL

---

## Connection String Format

```
postgresql://username:password@host:port/database

Examples:
- Local: postgresql://postgres:mypass@localhost:5432/jobnect_db
- Render: postgresql://user:pass@dpg-xxx.oregon-postgres.render.com:5432/jobnect_db
```

---

## Troubleshooting

**Can't connect to database:**
- Check PostgreSQL is running
- Verify username/password
- Check port (default: 5432)
- Check firewall settings

**Database doesn't exist:**
```sql
-- Create it manually
CREATE DATABASE jobnect_db;
```

**Permission denied:**
```sql
-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE jobnect_db TO your_username;
```

---

## Quick Test

After setting up, test your connection:

```bash
# Run backend
python main.py

# In another terminal, check if tables were created
psql -U postgres -d jobnect_db -c "\dt"
```

You should see all 20+ tables listed!

---

## My Recommendation

**For you (Windows user):**

1. **Easiest Option**: Use Render.com
   - No installation needed
   - Free tier available
   - Built-in database browser
   - Works from anywhere

2. **Best Local Option**: Install PostgreSQL + pgAdmin
   - Download: https://www.postgresql.org/download/windows/
   - Includes pgAdmin GUI
   - Full control over database

Choose based on your preference! Both work perfectly with the backend.
