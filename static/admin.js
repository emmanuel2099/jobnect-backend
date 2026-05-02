// Eagle's Pride Admin Dashboard - admin.js
const API = '/api/v10';
const ADMIN_TOKEN_KEY = 'eaglesAdminToken';

let currentUserFilter = 'all';

function getToken() {
  return localStorage.getItem(ADMIN_TOKEN_KEY);
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + getToken()
  };
}

// ─── Navigation ────────────────────────────────────────────────────────────────

function showSection(name) {
  // Hide all sections
  document.querySelectorAll('.section').forEach(function(sec) {
    sec.style.display = 'none';
  });

  // Show the target section
  var target = document.getElementById(name);
  if (target) {
    target.style.display = 'block';
  }

  // Safe nav highlighting — never uses event.target
  document.querySelectorAll('.nav-link').forEach(function(link) {
    link.classList.remove('active');
    if (link.getAttribute('data-section') === name) {
      link.classList.add('active');
    }
  });

  // Load section data
  switch (name) {
    case 'dashboard':
      loadDashboardStats();
      break;
    case 'users':
      loadUsers();
      break;
    case 'email-verification':
      loadEmailVerificationStatus();
      break;
    case 'jobs':
      loadJobs();
      break;
    case 'post-job':
      loadPostJobCategories();
      break;
    case 'applications':
      loadApplications();
      break;
    case 'payments':
      loadPayments();
      refreshPayments();
      break;
    case 'chat':
      loadChat();
      break;
    case 'categories':
      loadCategories();
      break;
    case 'saved':
      loadSavedJobs();
      break;
    case 'profiles':
      loadProfiles();
      break;
    case 'notifications':
      loadNotifications();
      break;
    case 'danger-zone':
      // nothing to load
      break;
    default:
      break;
  }
}

// ─── Dashboard Stats ────────────────────────────────────────────────────────────

async function loadDashboardStats() {
  try {
    // User stats
    const usersRes = await fetch(API + '/admin/users/stats', { headers: authHeaders() });
    if (usersRes.ok) {
      const usersData = await usersRes.json();
      const stats = usersData.data || usersData;
      setEl('totalUsers', stats.total_users || stats.totalUsers || 0);
      setEl('totalApplicants', stats.total_applicants || stats.totalApplicants || 0);
      setEl('totalCompanies', stats.total_companies || stats.totalCompanies || 0);
      setEl('onlineUsers', stats.online_users || stats.onlineUsers || 0);
    }
  } catch (e) { console.error('User stats error:', e); }

  try {
    // Jobs
    const jobsRes = await fetch(API + '/jobs/recent', { headers: authHeaders() });
    if (jobsRes.ok) {
      const jobsData = await jobsRes.json();
      const jobs = jobsData.data || jobsData.jobs || jobsData || [];
      setEl('totalJobs', Array.isArray(jobs) ? jobs.length : (jobs.total || 0));
    }
  } catch (e) { console.error('Jobs stats error:', e); }

  try {
    // Applications
    const appsRes = await fetch(API + '/admin/applications', { headers: authHeaders() });
    if (appsRes.ok) {
      const appsData = await appsRes.json();
      const apps = appsData.data || appsData.applications || appsData || [];
      setEl('totalApplications', Array.isArray(apps) ? apps.length : (apps.total || 0));
    }
  } catch (e) { console.error('Applications stats error:', e); }

  try {
    // Chat conversations
    const chatRes = await fetch(API + '/admin/chat/conversations', { headers: authHeaders() });
    if (chatRes.ok) {
      const chatData = await chatRes.json();
      const convs = chatData.data || chatData.conversations || chatData || [];
      setEl('totalConversations', Array.isArray(convs) ? convs.length : (convs.total || 0));
    }
  } catch (e) { console.error('Chat stats error:', e); }

  try {
    // Payments
    const paymentsRes = await fetch(API + '/admin/payments', { headers: authHeaders() });
    if (paymentsRes.ok) {
      const paymentsData = await paymentsRes.json();
      const payments = paymentsData.data || paymentsData.payments || paymentsData || [];
      setEl('totalPayments', Array.isArray(payments) ? payments.length : (payments.total || 0));
    }
  } catch (e) { console.error('Payments stats error:', e); }
}

function setEl(id, value) {
  var el = document.getElementById(id);
  if (el) el.textContent = value;
}

// ─── Users ──────────────────────────────────────────────────────────────────────

function filterUsers(type) {
  currentUserFilter = type;
  loadUsers();
}

async function loadUsers() {
  var container = document.getElementById('usersTable');
  if (!container) return;
  container.innerHTML = '<div class="loading"><div class="spinner-border text-primary"></div><p class="mt-3">Loading...</p></div>';

  try {
    var url = API + '/admin/users';
    if (currentUserFilter && currentUserFilter !== 'all') {
      url += '?user_type=' + encodeURIComponent(currentUserFilter);
    }
    const res = await fetch(url, { headers: authHeaders() });
    if (!res.ok) throw new Error('Failed to load users');
    const data = await res.json();
    const users = (data.data && data.data.users) ? data.data.users : (data.data || data.users || data || []);

    if (!Array.isArray(users) || users.length === 0) {
      container.innerHTML = '<div class="empty-state"><i class="bi bi-people"></i><p>No users found</p></div>';
      return;
    }

    var rows = users.map(function(u) {
      var typeBadge = (u.userType || u.user_type) === 'company'
        ? '<span class="badge bg-info">Company</span>'
        : '<span class="badge bg-primary">Applicant</span>';
      var statusBadge = (u.isActive !== undefined ? u.isActive : u.is_active)
        ? '<span class="badge bg-success">Active</span>'
        : '<span class="badge bg-secondary">Inactive</span>';
      var lastLogin = (u.lastLogin || u.last_login) ? new Date(u.lastLogin || u.last_login).toLocaleDateString('en-GB') : 'Never';
      return '<tr>' +
        '<td>' + (u.id || '') + '</td>' +
        '<td>' + escHtml((u.full_name || u.name || '') + '') + '</td>' +
        '<td>' + escHtml((u.email || '') + '') + '</td>' +
        '<td>' + escHtml((u.phone || '') + '') + '</td>' +
        '<td>' + typeBadge + '</td>' +
        '<td>' + statusBadge + '</td>' +
        '<td>' + lastLogin + '</td>' +
        '<td>' +
          '<button class="btn btn-sm btn-outline-warning me-1" onclick="toggleUserStatus(' + u.id + ')"><i class="bi bi-toggle-on"></i></button>' +
          '<button class="btn btn-sm btn-outline-danger" onclick="deleteUser(' + u.id + ')"><i class="bi bi-trash"></i></button>' +
        '</td>' +
        '</tr>';
    }).join('');

    container.innerHTML = '<div class="table-responsive"><table class="table table-hover">' +
      '<thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Type</th><th>Status</th><th>Last Login</th><th>Actions</th></tr></thead>' +
      '<tbody>' + rows + '</tbody></table></div>';
  } catch (e) {
    container.innerHTML = '<div class="alert alert-danger">Error loading users: ' + escHtml(e.message) + '</div>';
  }
}

async function deleteUser(id) {
  if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) return;
  try {
    const res = await fetch(API + '/admin/users/' + id, {
      method: 'DELETE',
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Delete failed');
    loadUsers();
  } catch (e) {
    alert('Error deleting user: ' + e.message);
  }
}

async function toggleUserStatus(id) {
  try {
    const res = await fetch(API + '/admin/users/' + id + '/toggle-status', {
      method: 'PATCH',
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Toggle failed');
    loadUsers();
  } catch (e) {
    alert('Error toggling user status: ' + e.message);
  }
}

// ─── Jobs ───────────────────────────────────────────────────────────────────────

async function loadJobs() {
  var container = document.getElementById('jobsTable');
  if (!container) return;
  container.innerHTML = '<div class="loading"><div class="spinner-border text-primary"></div><p class="mt-3">Loading...</p></div>';

  try {
    const res = await fetch(API + '/admin/all-jobs', {
      headers: { 'Authorization': 'Bearer ' + getToken() }
    });
    if (!res.ok) throw new Error('Failed to load jobs');
    const data = await res.json();
    const jobs = data.data || data.jobs || data || [];

    if (!Array.isArray(jobs) || jobs.length === 0) {
      container.innerHTML = '<div class="empty-state"><i class="bi bi-briefcase"></i><p>No jobs found</p></div>';
      return;
    }

    var rows = jobs.map(function(job) {
      var statusBadge = job.is_active
        ? '<span class="badge bg-success">Active</span>'
        : '<span class="badge bg-secondary">Inactive</span>';
      var createdAt = job.created_at ? new Date(job.created_at).toLocaleDateString('en-GB') : 'N/A';
      return '<tr>' +
        '<td>' + (job.id || '') + '</td>' +
        '<td>' + escHtml((job.title || '') + '') + '</td>' +
        '<td>' + escHtml((job.company_name || job.company || '') + '') + '</td>' +
        '<td>' + escHtml((job.location || '') + '') + '</td>' +
        '<td>' + statusBadge + '</td>' +
        '<td>' + createdAt + '</td>' +
        '<td>' +
          '<button class="btn btn-sm btn-outline-warning me-1" onclick="toggleJobStatus(' + job.id + ')"><i class="bi bi-toggle-on"></i></button>' +
          '<button class="btn btn-sm btn-outline-danger" onclick="deleteJob(' + job.id + ')"><i class="bi bi-trash"></i></button>' +
        '</td>' +
        '</tr>';
    }).join('');

    container.innerHTML = '<div class="table-responsive"><table class="table table-hover">' +
      '<thead><tr><th>ID</th><th>Title</th><th>Company</th><th>Location</th><th>Status</th><th>Created</th><th>Actions</th></tr></thead>' +
      '<tbody>' + rows + '</tbody></table></div>';
  } catch (e) {
    container.innerHTML = '<div class="alert alert-danger">Error loading jobs: ' + escHtml(e.message) + '</div>';
  }
}

async function deleteJob(id) {
  if (!confirm('Are you sure you want to delete this job? This action cannot be undone.')) return;
  try {
    const res = await fetch(API + '/admin/jobs/' + id, {
      method: 'DELETE',
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Delete failed');
    loadJobs();
  } catch (e) {
    alert('Error deleting job: ' + e.message);
  }
}

async function toggleJobStatus(id) {
  try {
    const res = await fetch(API + '/admin/jobs/' + id + '/toggle-status', {
      method: 'PATCH',
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Toggle failed');
    loadJobs();
  } catch (e) {
    alert('Error toggling job status: ' + e.message);
  }
}

// ─── Post Job ───────────────────────────────────────────────────────────────────

async function loadPostJobCategories() {
  try {
    const res = await fetch(API + '/categories', { headers: authHeaders() });
    if (!res.ok) throw new Error('Failed to load categories');
    const data = await res.json();
    const categories = (data.data && data.data.categories) ? data.data.categories : (data.categories || data || []);

    var select = document.getElementById('pj_category');
    if (!select) return;
    select.innerHTML = '<option value="">Select Category</option>';
    categories.forEach(function(cat) {
      var opt = document.createElement('option');
      opt.value = cat.id;
      opt.textContent = (cat.icon ? cat.icon + ' ' : '') + cat.name;
      select.appendChild(opt);
    });
  } catch (e) {
    console.error('Error loading post-job categories:', e);
  }
}

async function submitPostJob() {
  var successEl = document.getElementById('postJobSuccess');
  var errorEl = document.getElementById('postJobError');
  if (successEl) successEl.style.display = 'none';
  if (errorEl) errorEl.style.display = 'none';

  function getVal(id) {
    var el = document.getElementById(id);
    return el ? el.value.trim() : '';
  }

  var payload = {
    title: getVal('pj_title'),
    company_name: getVal('pj_company'),
    description: getVal('pj_description'),
    requirements: getVal('pj_requirements'),
    responsibilities: getVal('pj_responsibilities'),
    location: getVal('pj_location'),
    job_type: getVal('pj_job_type'),
    salary_min: parseFloat(getVal('pj_salary_min')) || null,
    salary_max: parseFloat(getVal('pj_salary_max')) || null,
    currency: getVal('pj_currency') || 'NGN',
    vacancies: parseInt(getVal('pj_vacancies')) || 1,
    deadline: getVal('pj_deadline'),
    experience_level: getVal('pj_experience'),
    category_id: getVal('pj_category') || null
  };

  try {
    const res = await fetch(API + '/admin/post-job', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || data.message || 'Failed to post job');

    // Clear form
    ['pj_title','pj_company','pj_description','pj_requirements','pj_responsibilities',
     'pj_location','pj_job_type','pj_salary_min','pj_salary_max','pj_currency',
     'pj_vacancies','pj_deadline','pj_experience','pj_category'].forEach(function(id) {
      var el = document.getElementById(id);
      if (el) el.value = '';
    });

    if (successEl) {
      successEl.textContent = 'Job posted successfully!';
      successEl.style.display = 'block';
      setTimeout(function() { successEl.style.display = 'none'; }, 4000);
    }
  } catch (e) {
    if (errorEl) {
      errorEl.textContent = 'Error: ' + e.message;
      errorEl.style.display = 'block';
    }
  }
}
