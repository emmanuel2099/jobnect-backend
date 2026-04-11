from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os

from app.database import engine, Base, init_db
from app.routers import auth, profile, jobs, applications, companies, master_data, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🔄 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    print("🔄 Initializing default data...")
    init_db()
    print("✅ Default data initialized")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")

app = FastAPI(
    title="JobNect API",
    description="Complete REST API for JobNect Mobile Application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v10", tags=["Authentication"])
app.include_router(profile.router, prefix="/api/v10", tags=["Profile & Resume"])
app.include_router(jobs.router, prefix="/api/v10", tags=["Jobs"])
app.include_router(applications.router, prefix="/api/v10", tags=["Applications"])
app.include_router(companies.router, prefix="/api/v10", tags=["Companies"])
app.include_router(master_data.router, prefix="/api/v10", tags=["Master Data"])
app.include_router(admin.router, prefix="/api/v10/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {
        "message": "🎉 JobNect Python API is running!",
        "version": "1.0.0",
        "status": "active",
        "framework": "FastAPI",
        "documentation": "/docs",
        "admin_dashboard": "/admin",
        "endpoints": {
            "auth": "POST /api/v10/registration, POST /api/v10/login",
            "profile": "GET /api/v10/applicant/resume/details",
            "jobs": "GET /api/v10/jobs/recent, GET /api/v10/jobs/popular",
            "applications": "POST /api/v10/applicant/job-apply",
            "companies": "GET /api/v10/companies",
            "master_data": "GET /api/v10/job-category, GET /api/v10/cities"
        }
    }

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    """Admin Dashboard - View and manage all data"""
    html_content = open("templates/admin_full.html", "r", encoding="utf-8").read() if os.path.exists("templates/admin_full.html") else """
    <!DOCTYPE html><html><head><title>JobNect Admin</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;background:#f8fafc}.sidebar{position:fixed;left:0;top:0;width:260px;height:100vh;background:linear-gradient(180deg,#1e293b 0%,#0f172a 100%);padding:24px;overflow-y:auto}.logo{color:white;margin-bottom:40px;padding-bottom:24px;border-bottom:1px solid rgba(255,255,255,0.1)}.logo h1{font-size:20px}.nav-item{display:flex;align-items:center;gap:12px;padding:12px 16px;margin-bottom:8px;border-radius:8px;color:#cbd5e1;cursor:pointer;transition:all 0.2s}.nav-item:hover,.nav-item.active{background:rgba(59,130,246,0.1);color:#3b82f6}.main-content{margin-left:260px;padding:24px}.header{background:white;padding:24px 32px;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);margin-bottom:24px;display:flex;justify-content:space-between;align-items:center}.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin-bottom:24px}.stat-card{background:white;padding:24px;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05)}.stat-value{font-size:32px;font-weight:700;color:#1e293b}.section{background:white;padding:24px;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,0.05);margin-bottom:24px}table{width:100%;border-collapse:collapse}th{background:#f8fafc;padding:12px 16px;text-align:left;font-weight:600;font-size:13px;color:#64748b}td{padding:16px;border-bottom:1px solid #f1f5f9;font-size:14px}tr:hover{background:#f8fafc}.btn{padding:6px 12px;border:none;border-radius:6px;cursor:pointer;font-size:12px;font-weight:500;transition:all 0.2s}.btn-delete{background:#ef4444;color:white}.btn-delete:hover{background:#dc2626}.btn-toggle{background:#10b981;color:white}.btn-toggle:hover{background:#059669}.badge{padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600}.badge.active{background:#d1fae5;color:#065f46}.badge.inactive{background:#fee2e2;color:#991b1b}</style>
    </head><body>
    <div class="sidebar"><div class="logo"><h1>🎯 JobNect Admin</h1></div>
    <div class="nav-item active" onclick="showTab('users')"><i class="fas fa-users"></i><span>Users</span></div>
    <div class="nav-item" onclick="showTab('jobs')"><i class="fas fa-briefcase"></i><span>Jobs</span></div>
    <div class="nav-item" onclick="showTab('companies')"><i class="fas fa-building"></i><span>Companies</span></div>
    <div class="nav-item" onclick="showTab('applications')"><i class="fas fa-file-alt"></i><span>Applications</span></div>
    </div>
    <div class="main-content">
    <div class="header"><h2 id="pageTitle">User Management</h2>
    <button class="btn btn-toggle" onclick="loadAllData()"><i class="fas fa-sync-alt"></i> Refresh</button></div>
    <div class="stats-grid">
    <div class="stat-card"><div class="stat-value" id="totalUsers">0</div><div>Total Users</div></div>
    <div class="stat-card"><div class="stat-value" id="totalJobs">0</div><div>Total Jobs</div></div>
    <div class="stat-card"><div class="stat-value" id="totalCompanies">0</div><div>Total Companies</div></div>
    <div class="stat-card"><div class="stat-value" id="totalApplications">0</div><div>Total Applications</div></div>
    </div>
    <div id="users" class="section"><h3>All Users</h3><div id="usersTable"></div></div>
    <div id="jobs" class="section" style="display:none"><h3>All Jobs</h3><div id="jobsTable"></div></div>
    <div id="companies" class="section" style="display:none"><h3>All Companies</h3><div id="companiesTable"></div></div>
    <div id="applications" class="section" style="display:none"><h3>All Applications</h3><div id="applicationsTable"></div></div>
    </div>
    <script>
    const API='/api/v10';
    function showTab(tab){document.querySelectorAll('.section').forEach(s=>s.style.display='none');document.getElementById(tab).style.display='block';document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));event.target.closest('.nav-item').classList.add('active');}
    async function deleteUser(id){if(confirm('Delete this user?')){const r=await fetch(`${API}/admin/users/${id}`,{method:'DELETE'});if(r.ok)loadUsers();}}
    async function toggleUser(id){const r=await fetch(`${API}/admin/users/${id}/toggle-status`,{method:'PATCH'});if(r.ok)loadUsers();}
    async function deleteJob(id){if(confirm('Delete this job?')){const r=await fetch(`${API}/admin/jobs/${id}`,{method:'DELETE'});if(r.ok)loadJobs();}}
    async function toggleJob(id){const r=await fetch(`${API}/admin/jobs/${id}/toggle-status`,{method:'PATCH'});if(r.ok)loadJobs();}
    async function deleteCompany(id){if(confirm('Delete this company?')){const r=await fetch(`${API}/admin/companies/${id}`,{method:'DELETE'});if(r.ok)loadCompanies();}}
    async function loadUsers(){const r=await fetch(`${API}/users/list`);const d=await r.json();if(d.success){document.getElementById('totalUsers').textContent=d.data.users.length;document.getElementById('usersTable').innerHTML='<table><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Status</th><th>Actions</th></tr></thead><tbody>'+d.data.users.map(u=>`<tr><td>${u.id}</td><td>${u.name}</td><td>${u.email}</td><td>${u.phone}</td><td><span class="badge ${u.isActive?'active':'inactive'}">${u.isActive?'Active':'Inactive'}</span></td><td><button class="btn btn-toggle" onclick="toggleUser(${u.id})">Toggle</button> <button class="btn btn-delete" onclick="deleteUser(${u.id})">Delete</button></td></tr>`).join('')+'</tbody></table>';}}
    async function loadJobs(){const r=await fetch(`${API}/jobs/recent`);const d=await r.json();if(d.success&&d.data.jobs){document.getElementById('totalJobs').textContent=d.data.jobs.length;document.getElementById('jobsTable').innerHTML='<table><thead><tr><th>ID</th><th>Title</th><th>Company</th><th>Status</th><th>Actions</th></tr></thead><tbody>'+d.data.jobs.map(j=>`<tr><td>${j.id}</td><td>${j.title}</td><td>${j.company?.name||'N/A'}</td><td><span class="badge ${j.isActive?'active':'inactive'}">${j.isActive?'Active':'Closed'}</span></td><td><button class="btn btn-toggle" onclick="toggleJob(${j.id})">Toggle</button> <button class="btn btn-delete" onclick="deleteJob(${j.id})">Delete</button></td></tr>`).join('')+'</tbody></table>';}}
    async function loadCompanies(){const r=await fetch(`${API}/companies`);const d=await r.json();if(d.success&&d.data.companies){document.getElementById('totalCompanies').textContent=d.data.companies.length;document.getElementById('companiesTable').innerHTML='<table><thead><tr><th>ID</th><th>Name</th><th>Industry</th><th>Status</th><th>Actions</th></tr></thead><tbody>'+d.data.companies.map(c=>`<tr><td>${c.id}</td><td>${c.name}</td><td>${c.industry||'N/A'}</td><td><span class="badge ${c.isActive?'active':'inactive'}">${c.isActive?'Active':'Inactive'}</span></td><td><button class="btn btn-delete" onclick="deleteCompany(${c.id})">Delete</button></td></tr>`).join('')+'</tbody></table>';}}
    async function loadApplications(){const r=await fetch(`${API}/admin/applications`);const d=await r.json();if(d.success){document.getElementById('totalApplications').textContent=d.data.applications.length;document.getElementById('applicationsTable').innerHTML='<table><thead><tr><th>ID</th><th>User</th><th>Job</th><th>Status</th><th>Date</th></tr></thead><tbody>'+d.data.applications.map(a=>`<tr><td>${a.id}</td><td>${a.userName}</td><td>${a.jobTitle}</td><td>${a.status}</td><td>${new Date(a.createdAt).toLocaleDateString()}</td></tr>`).join('')+'</tbody></table>';}}
    async function loadAllData(){await Promise.all([loadUsers(),loadJobs(),loadCompanies(),loadApplications()]);}
    loadAllData();setInterval(loadAllData,30000);
    </script>
    </body></html>
    """
    return html_content

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
