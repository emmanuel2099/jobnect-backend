const API = '/api/v10';
let currentUserFilter = 'all';

// Show Section
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    
    // Show selected section
    const section = document.getElementById(sectionName);
    if (section) {
        section.classList.add('active');
    }
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.closest('.nav-link').classList.add('active');
    
    // Load data for section
    switch(sectionName) {
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
    }
}

// Load Dashboard Stats
async function loadDashboardStats() {
    try {
        // Load user stats
        const userStatsRes = await fetch(`${API}/admin/users/stats`);
        const userStats = await userStatsRes.json();
        
        if (userStats.success) {
            document.getElementById('totalUsers').textContent = userStats.data.totalUsers;
            document.getElementById('totalApplicants').textContent = userStats.data.applicants;
            document.getElementById('totalCompanies').textContent = userStats.data.companies;
            document.getElementById('onlineUsers').textContent = userStats.data.onlineUsers;
        }
        
        // Load jobs count
        const jobsRes = await fetch(`${API}/jobs/recent`);
        const jobsData = await jobsRes.json();
        if (jobsData.success && jobsData.data.jobs) {
            document.getElementById('totalJobs').textContent = jobsData.data.jobs.length;
        }
        
        // Load applications count
        const appsRes = await fetch(`${API}/admin/applications`);
        const appsData = await appsRes.json();
        if (appsData.success && appsData.data.applications) {
            document.getElementById('totalApplications').textContent = appsData.data.applications.length;
        }
        
        // Load conversations count
        const chatRes = await fetch(`${API}/admin/chat/conversations`);
        const chatData = await chatRes.json();
        if (chatData.success && chatData.data.conversations) {
            document.getElementById('totalConversations').textContent = chatData.data.conversations.length;
        }
        
        // Load payments count
        const paymentsRes = await fetch(`${API}/admin/payments`);
        const paymentsData = await paymentsRes.json();
        if (paymentsData.success && paymentsData.data.payments) {
            document.getElementById('totalPayments').textContent = paymentsData.data.payments.length;
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

// Filter Users
function filterUsers(type) {
    currentUserFilter = type;
    
    // Update button states
    const buttons = document.querySelectorAll('.btn-group .btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    loadUsers();
}

// Load Users
async function loadUsers() {
    const container = document.getElementById('usersTable');
    container.innerHTML = '<div class="loading"><div class="spinner-border text-primary"></div><p class="mt-3">Loading users...</p></div>';
    
    try {
        let url = `${API}/admin/users`;
        if (currentUserFilter !== 'all') {
            url += `?user_type=${currentUserFilter}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success && data.data.users.length > 0) {
            container.innerHTML = `
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Phone</th>
                                <th>Type</th>
                                <th>Status</th>
                                <th>Last Login</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.data.users.map(user => `
                                <tr>
                                    <td>${user.id}</td>
                                    <td><strong>${user.name}</strong></td>
                                    <td>${user.email}</td>
                                    <td>${user.phone || 'N/A'}</td>
                                    <td><span class="badge bg-${user.userType === 'company' ? 'info' : 'warning'}">${user.userType}</span></td>
                                    <td><span class="badge bg-${user.isActive ? 'success' : 'danger'}">${user.isActive ? 'Active' : 'Inactive'}</span></td>
                                    <td>${user.lastLogin ? new Date(user.lastLogin).toLocaleString() : 'Never'}</td>
                                    <td>
                                        <button class="btn btn-sm btn-warning" onclick="toggleUserStatus(${user.id})" title="Toggle Status">
                                            <i class="bi bi-toggle-on"></i>
                                        </button>
                                        <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})" title="Delete">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="bi bi-people"></i><p>No users found</p></div>';
        }
    } catch (error) {
        console.error('Error loading users:', error);
        container.innerHTML = '<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>Error loading users</p></div>';
    }
}

// Load Jobs
async function loadJobs() {
    const container = document.getElementById('jobsTable');
    container.innerHTML = '<div class="loading"><div class="spinner-border text-primary"></div><p class="mt-3">Loading jobs...</p></div>';
    
    try {
        const response = await fetch(`${API}/jobs/recent`);
        const data = await response.json();
        
        if (data.success && data.data.jobs && data.data.jobs.length > 0) {
            container.innerHTML = `
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Title</th>
                                <th>Company</th>
                                <th>Location</th>
                                <th>Type</th>
                                <th>Status</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.data.jobs.map(job => `
                                <tr>
                                    <td>${job.id}</td>
                                    <td><strong>${job.title}</strong></td>
                                    <td>${job.company?.name || 'N/A'}</td>
                                    <td>${job.location || 'N/A'}</td>
                                    <td>${job.jobType?.name || 'N/A'}</td>
                                    <td><span class="badge bg-${job.isActive ? 'success' : 'danger'}">${job.isActive ? 'Active' : 'Closed'}</span></td>
                                    <td>${new Date(job.createdAt).toLocaleDateString()}</td>
                                    <td>
                                        <button class="btn btn-sm btn-warning" onclick="toggleJobStatus(${job.id})">
                                            <i class="bi bi-toggle-on"></i>
                                        </button>
                                        <button class="btn btn-sm btn-danger" onclick="deleteJob(${job.id})">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="bi bi-briefcase"></i><p>No jobs found</p></div>';
        }
    } catch (error) {
        console.error('Error loading jobs:', error);
        container.innerHTML = '<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>Error loading jobs</p></div>';
    }
}

// Load Applications
async function loadApplications() {
    const container = document.getElementById('applicationsTable');
    container.innerHTML = '<div class="loading"><div class="spinner-border text-primary"></div><p class="mt-3">Loading applications...</p></div>';
    
    try {
        const response = await fetch(`${API}/admin/applications`);
        const data = await response.json();
        
        if (data.success && data.data.applications.length > 0) {
            container.innerHTML = `
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Applicant</th>
                                <th>Email</th>
                                <th>Job</th>
                                <th>Status</th>
                                <th>Applied Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.data.applications.map(app => `
                                <tr>
                                    <td>${app.id}</td>
                                    <td><strong>${app.userName}</strong></td>
                                    <td>${app.userEmail}</td>
                                    <td>${app.jobTitle}</td>
                                    <td><span class="badge bg-info">${app.status}</span></td>
                                    <td>${new Date(app.createdAt).toLocaleDateString()}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="bi bi-file-earmark-text"></i><p>No applications found</p></div>';
        }
    } catch (error) {
        console.error('Error loading applications:', error);
        container.innerHTML = '<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>Error loading applications</p></div>';
    }
}

// Load Payments
async function loadPayments() {
    const container = document.getElementById('paymentsTable');
    container.innerHTML = '<div class="loading"><div class="spinner-border text-primary"></div><p class="mt-3">Loading payments...</p></div>';
    
    try {
        const response = await fetch(`${API}/admin/payments`);
        const data = await response.json();
        
        if (data.success && data.data.payments.length > 0) {
            container.innerHTML = `
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>User</th>
                                <th>Amount</th>
                                <th>Currency</th>
                                <th>Method</th>
                                <th>Reference</th>
                                <th>Status</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.data.payments.map(payment => `
                                <tr>
                                    <td>${payment.id}</td>
                                    <td>${payment.userName}</td>
                                    <td><strong>${payment.amount}</strong></td>
                                    <td>${payment.currency}</td>
                                    <td>${payment.paymentMethod}</td>
                                    <td>${payment.transactionReference}</td>
                                    <td><span class="badge bg-${payment.status === 'completed' ? 'success' : 'warning'}">${payment.status}</span></td>
                                    <td>${payment.paymentDate ? new Date(payment.paymentDate).toLocaleDateString() : 'N/A'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="bi bi-credit-card"></i><p>No payments found</p></div>';
        }
    } catch (error) {
        console.error('Error loading payments:', error);
        container.innerHTML = '<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>Error loading payments</p></div>';
    }
}

// Load Chat
async function loadChat() {
    const container = document.getElementById('chatTable');
    container.innerHTML = '<div class="loading"><div class="spinner-border text-primary"></div><p class="mt-3">Loading conversations...</p></div>';
    
    try {
        const response = await fetch(`${API}/admin/chat/conversations`);
        const data = await response.json();
        
        if (data.success && data.data.conversations.length > 0) {
            container.innerHTML = `
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>User 1</th>
                                <th>User 2</th>
                                <th>Messages</th>
                                <th>Last Message</th>
                                <th>Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.data.conversations.map(conv => `
                                <tr>
                                    <td>${conv.id}</td>
                                    <td>${conv.user1.name} <span class="badge bg-secondary">${conv.user1.userType}</span></td>
                                    <td>${conv.user2.name} <span class="badge bg-secondary">${conv.user2.userType}</span></td>
                                    <td><span class="badge bg-info">${conv.messageCount}</span></td>
                                    <td>${conv.lastMessage ? conv.lastMessage.substring(0, 50) + '...' : 'No messages'}</td>
                                    <td>${new Date(conv.createdAt).toLocaleDateString()}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="bi bi-chat-dots"></i><p>No conversations found</p></div>';
        }
    } catch (error) {
        console.error('Error loading chat:', error);
        container.innerHTML = '<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>Error loading conversations</p></div>';
    }
}

// Load Categories
async function loadCategories() {
    const container = document.getElementById('categoriesTable');
    container.innerHTML = '<div class="loading"><div class="spinner-border text-primary"></div><p class="mt-3">Loading categories...</p></div>';
    
    try {
        const response = await fetch(`${API}/admin/categories/manage`);
        const data = await response.json();
        
        if (data.success && data.data.categories.length > 0) {
            container.innerHTML = `
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Icon</th>
                                <th>Description</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.data.categories.map(cat => `
                                <tr>
                                    <td>${cat.id}</td>
                                    <td><strong>${cat.name}</strong></td>
                                    <td><i class="bi ${cat.icon}"></i> ${cat.icon}</td>
                                    <td>${cat.description || 'N/A'}</td>
                                    <td><span class="badge bg-${cat.isActive ? 'success' : 'danger'}">${cat.isActive ? 'Active' : 'Inactive'}</span></td>
                                    <td>
                                        <button class="btn btn-sm btn-danger" onclick="deleteCategory(${cat.id})">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="bi bi-tags"></i><p>No categories found</p></div>';
        }
    } catch (error) {
        console.error('Error loading categories:', error);
        container.innerHTML = '<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>Error loading categories</p></div>';
    }
}

// Load Saved Jobs
async function loadSavedJobs() {
    const container = document.getElementById('savedTable');
    container.innerHTML = '<div class="loading"><div class="spinner-border text-primary"></div><p class="mt-3">Loading saved jobs...</p></div>';
    
    try {
        const response = await fetch(`${API}/admin/saved-jobs`);
        const data = await response.json();
        
        if (data.success && data.data.savedJobs.length > 0) {
            container.innerHTML = `
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>User</th>
                                <th>Email</th>
                                <th>Job Title</th>
                                <th>Company</th>
                                <th>Saved Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.data.savedJobs.map(saved => `
                                <tr>
                                    <td>${saved.id}</td>
                                    <td><strong>${saved.userName}</strong></td>
                                    <td>${saved.userEmail}</td>
                                    <td>${saved.jobTitle}</td>
                                    <td>${saved.companyName}</td>
                                    <td>${new Date(saved.savedAt).toLocaleDateString()}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="bi bi-bookmark"></i><p>No saved jobs found</p></div>';
        }
    } catch (error) {
        console.error('Error loading saved jobs:', error);
        container.innerHTML = '<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>Error loading saved jobs</p></div>';
    }
}

// Load Profiles
async function loadProfiles() {
    const container = document.getElementById('profilesTable');
    container.innerHTML = '<div class="loading"><div class="spinner-border text-primary"></div><p class="mt-3">Loading profiles...</p></div>';
    
    try {
        const response = await fetch(`${API}/admin/users/profiles/all`);
        const data = await response.json();
        
        if (data.success && data.data.profiles.length > 0) {
            container.innerHTML = `
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Photo</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Type</th>
                                <th>Designation</th>
                                <th>City</th>
                                <th>Age</th>
                                <th>Skills</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.data.profiles.map(profile => `
                                <tr>
                                    <td>${profile.id}</td>
                                    <td>
                                        ${profile.profilePhoto ? 
                                            `<img src="${profile.profilePhoto}" alt="${profile.name}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">` : 
                                            '<i class="bi bi-person-circle" style="font-size: 40px;"></i>'
                                        }
                                    </td>
                                    <td><strong>${profile.name}</strong></td>
                                    <td>${profile.email}</td>
                                    <td><span class="badge bg-${profile.userType === 'company' ? 'info' : 'warning'}">${profile.userType}</span></td>
                                    <td>${profile.designation || 'N/A'}</td>
                                    <td>${profile.city || 'N/A'}</td>
                                    <td>${profile.age || 'N/A'}</td>
                                    <td><span class="badge bg-secondary">${profile.skillsCount} skills</span></td>
                                    <td><span class="badge bg-${profile.isActive ? 'success' : 'danger'}">${profile.isActive ? 'Active' : 'Inactive'}</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="bi bi-person-badge"></i><p>No profiles found</p></div>';
        }
    } catch (error) {
        console.error('Error loading profiles:', error);
        container.innerHTML = '<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>Error loading profiles</p></div>';
    }
}

// Load Notifications
async function loadNotifications() {
    const container = document.getElementById('notificationsTable');
    container.innerHTML = '<div class="loading"><div class="spinner-border text-primary"></div><p class="mt-3">Loading notifications...</p></div>';
    
    try {
        const response = await fetch(`${API}/admin/notifications`);
        const data = await response.json();
        
        if (data.success && data.data.notifications.length > 0) {
            container.innerHTML = `
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>User</th>
                                <th>Title</th>
                                <th>Message</th>
                                <th>Type</th>
                                <th>Status</th>
                                <th>Sent</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.data.notifications.map(notif => `
                                <tr>
                                    <td>${notif.id}</td>
                                    <td>${notif.userName}</td>
                                    <td><strong>${notif.title}</strong></td>
                                    <td>${notif.message.substring(0, 50)}...</td>
                                    <td><span class="badge bg-info">${notif.type}</span></td>
                                    <td><span class="badge bg-${notif.isRead ? 'success' : 'warning'}">${notif.isRead ? 'Read' : 'Unread'}</span></td>
                                    <td>${new Date(notif.createdAt).toLocaleString()}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="bi bi-bell"></i><p>No notifications sent yet</p></div>';
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
        container.innerHTML = '<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>Error loading notifications</p></div>';
    }
}

// Delete User
async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user?')) return;
    
    try {
        const response = await fetch(`${API}/admin/users/${id}`, { method: 'DELETE' });
        const data = await response.json();
        
        if (data.success) {
            alert('User deleted successfully');
            loadUsers();
            loadDashboardStats();
        } else {
            alert('Failed to delete user');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('Error deleting user');
    }
}

// Toggle User Status
async function toggleUserStatus(id) {
    try {
        const response = await fetch(`${API}/admin/users/${id}/toggle-status`, { method: 'PATCH' });
        const data = await response.json();
        
        if (data.success) {
            loadUsers();
            loadDashboardStats();
        } else {
            alert('Failed to toggle user status');
        }
    } catch (error) {
        console.error('Error toggling user status:', error);
        alert('Error toggling user status');
    }
}

// Delete Job
async function deleteJob(id) {
    if (!confirm('Are you sure you want to delete this job?')) return;
    
    try {
        const response = await fetch(`${API}/admin/jobs/${id}`, { method: 'DELETE' });
        const data = await response.json();
        
        if (data.success) {
            alert('Job deleted successfully');
            loadJobs();
            loadDashboardStats();
        } else {
            alert('Failed to delete job');
        }
    } catch (error) {
        console.error('Error deleting job:', error);
        alert('Error deleting job');
    }
}

// Toggle Job Status
async function toggleJobStatus(id) {
    try {
        const response = await fetch(`${API}/admin/jobs/${id}/toggle-status`, { method: 'PATCH' });
        const data = await response.json();
        
        if (data.success) {
            loadJobs();
        } else {
            alert('Failed to toggle job status');
        }
    } catch (error) {
        console.error('Error toggling job status:', error);
        alert('Error toggling job status');
    }
}

// Save Category
async function saveCategory() {
    const name = document.getElementById('categoryName').value;
    const icon = document.getElementById('categoryIcon').value;
    const description = document.getElementById('categoryDescription').value;
    
    if (!name) {
        alert('Please enter category name');
        return;
    }
    
    try {
        const response = await fetch(`${API}/admin/categories/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                icon: icon,
                description: description,
                is_active: true
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Category created successfully');
            bootstrap.Modal.getInstance(document.getElementById('categoryModal')).hide();
            document.getElementById('categoryForm').reset();
            loadCategories();
        } else {
            alert('Failed to create category');
        }
    } catch (error) {
        console.error('Error creating category:', error);
        alert('Error creating category');
    }
}

// Delete Category
async function deleteCategory(id) {
    if (!confirm('Are you sure you want to delete this category?')) return;
    
    try {
        const response = await fetch(`${API}/admin/categories/${id}`, { method: 'DELETE' });
        const data = await response.json();
        
        if (data.success) {
            alert('Category deleted successfully');
            loadCategories();
        } else {
            alert('Failed to delete category');
        }
    } catch (error) {
        console.error('Error deleting category:', error);
        alert('Error deleting category');
    }
}

// Send Notification
async function sendNotification() {
    const target = document.getElementById('notifTarget').value;
    const title = document.getElementById('notifTitle').value;
    const message = document.getElementById('notifMessage').value;
    
    if (!title || !message) {
        alert('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch(`${API}/admin/notifications/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_type: target,
                title: title,
                message: message,
                notification_type: 'general'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Notification sent to ${data.data.recipientCount} user(s)`);
            bootstrap.Modal.getInstance(document.getElementById('notificationModal')).hide();
            document.getElementById('notificationForm').reset();
            loadNotifications();
        } else {
            alert('Failed to send notification');
        }
    } catch (error) {
        console.error('Error sending notification:', error);
        alert('Error sending notification');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
});

// Email Verification Functions
async function loadEmailVerificationStatus() {
    try {
        const response = await fetch(`${API}/admin/email-verification-status`);
        const data = await response.json();
        
        if (data.success) {
            updateEmailVerificationStats(data.data.summary);
            displayVerifiedUsers(data.data.verified_users);
            displayUnverifiedUsers(data.data.unverified_users);
            displayRecentAttempts(data.data.recent_attempts);
        } else {
            showError('Failed to load email verification status: ' + data.message);
        }
    } catch (error) {
        showError('Error loading email verification status: ' + error.message);
    }
}

function updateEmailVerificationStats(summary) {
    document.getElementById('totalUsersCount').textContent = summary.total_users;
    document.getElementById('verifiedUsersCount').textContent = summary.verified_users;
    document.getElementById('unverifiedUsersCount').textContent = summary.unverified_users;
    document.getElementById('verificationRate').textContent = summary.verification_rate + '%';
}

function displayVerifiedUsers(users) {
    const container = document.getElementById('verifiedUsersTable');
    
    if (users.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-check-circle-fill text-success" style="font-size: 3rem;"></i>
                <h5 class="mt-3">No verified users yet</h5>
                <p class="text-muted">Users will appear here after email verification</p>
            </div>
        `;
        return;
    }
    
    const table = `
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Type</th>
                    <th>Company</th>
                    <th>Verified Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${users.map(user => `
                    <tr>
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="avatar me-2">
                                    <i class="bi bi-person-circle text-success" style="font-size: 1.5rem;"></i>
                                </div>
                                <div>
                                    <strong>${user.name}</strong>
                                    <br><small class="text-muted">ID: ${user.id}</small>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span class="badge bg-success-subtle text-success">
                                <i class="bi bi-check-circle-fill me-1"></i>${user.email}
                            </span>
                        </td>
                        <td>
                            <span class="badge ${user.user_type === 'company' ? 'bg-primary' : 'bg-info'}">
                                ${user.user_type === 'company' ? 'Company' : 'Job Seeker'}
                            </span>
                        </td>
                        <td>${user.company || 'N/A'}</td>
                        <td>${user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-success" disabled>
                                <i class="bi bi-check-circle-fill"></i> Verified
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = table;
}

function displayUnverifiedUsers(users) {
    const container = document.getElementById('unverifiedUsersTable');
    
    if (users.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-check-circle-fill text-success" style="font-size: 3rem;"></i>
                <h5 class="mt-3">All users verified!</h5>
                <p class="text-muted">Great job! All users have verified their emails</p>
            </div>
        `;
        return;
    }
    
    const table = `
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Type</th>
                    <th>Company</th>
                    <th>Registered</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${users.map(user => `
                    <tr>
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="avatar me-2">
                                    <i class="bi bi-person-circle text-warning" style="font-size: 1.5rem;"></i>
                                </div>
                                <div>
                                    <strong>${user.name}</strong>
                                    <br><small class="text-muted">ID: ${user.id}</small>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span class="badge bg-warning-subtle text-warning">
                                <i class="bi bi-exclamation-circle-fill me-1"></i>${user.email}
                            </span>
                        </td>
                        <td>
                            <span class="badge ${user.user_type === 'company' ? 'bg-primary' : 'bg-info'}">
                                ${user.user_type === 'company' ? 'Company' : 'Job Seeker'}
                            </span>
                        </td>
                        <td>${user.company || 'N/A'}</td>
                        <td>${user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="resendVerificationEmail(${user.id}, '${user.email}')">
                                <i class="bi bi-envelope-fill"></i> Resend Email
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = table;
}

function displayRecentAttempts(attempts) {
    const container = document.getElementById('recentAttemptsTable');
    
    if (attempts.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-clock-history text-info" style="font-size: 3rem;"></i>
                <h5 class="mt-3">No recent attempts</h5>
                <p class="text-muted">Email verification attempts will appear here</p>
            </div>
        `;
        return;
    }
    
    const table = `
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>Email</th>
                    <th>Purpose</th>
                    <th>Sent At</th>
                    <th>Expires At</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${attempts.map(attempt => `
                    <tr>
                        <td>${attempt.email}</td>
                        <td>
                            <span class="badge ${attempt.purpose === 'email_verification' ? 'bg-info' : 'bg-warning'}">
                                ${attempt.purpose.replace('_', ' ').toUpperCase()}
                            </span>
                        </td>
                        <td>${attempt.created_at ? new Date(attempt.created_at).toLocaleString() : 'N/A'}</td>
                        <td>${attempt.expires_at ? new Date(attempt.expires_at).toLocaleString() : 'N/A'}</td>
                        <td>
                            <span class="badge ${attempt.status === 'active' ? 'bg-success' : 'bg-secondary'}">
                                ${attempt.status.toUpperCase()}
                            </span>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = table;
}

async function resendVerificationEmail(userId, email) {
    if (!confirm(`Resend verification email to ${email}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API}/admin/resend-verification/${userId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(`Verification email sent to ${email}`);
            // Refresh the email verification status
            loadEmailVerificationStatus();
        } else {
            showError('Failed to send verification email: ' + data.message);
        }
    } catch (error) {
        showError('Error sending verification email: ' + error.message);
    }
}

function refreshEmailVerification() {
    loadEmailVerificationStatus();
    showSuccess('Email verification status refreshed');
}

// Enhanced Payment Analytics Functions
async function refreshPayments() {
    await loadPayments();
}

async function loadPayments() {
    const container = document.getElementById('paymentsTable');
    container.innerHTML = '<div class="loading"><div class="spinner-border text-primary"></div><p class="mt-3">Loading payments...</p></div>';
    
    try {
        const response = await fetch(`${API}/admin/payments`);
        const data = await response.json();
        
        if (data.success) {
            // Update summary cards
            updatePaymentSummary(data.data.summary);
            
            // Update payment methods chart
            updatePaymentMethodsChart(data.data.paymentMethods);
            
            // Update revenue trend chart
            updateRevenueTrendChart(data.data.dailyRevenue);
            
            // Update payments table
            if (data.data.payments.length > 0) {
                container.innerHTML = `
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>User</th>
                                    <th>Email</th>
                                    <th>Amount</th>
                                    <th>Method</th>
                                    <th>Reference</th>
                                    <th>Status</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.data.payments.map(payment => `
                                    <tr>
                                        <td>${payment.id}</td>
                                        <td><strong>${payment.userName}</strong></td>
                                        <td>${payment.userEmail}</td>
                                        <td><strong>₦${payment.amount.toLocaleString()}</strong></td>
                                        <td>
                                            <span class="badge bg-info">
                                                <i class="bi bi-credit-card me-1"></i>
                                                ${payment.paymentMethod || 'N/A'}
                                            </span>
                                        </td>
                                        <td><code>${payment.transactionReference || 'N/A'}</code></td>
                                        <td>
                                            <span class="badge bg-${getPaymentStatusColor(payment.status)}">
                                                <i class="bi bi-${getPaymentStatusIcon(payment.status)} me-1"></i>
                                                ${payment.status}
                                            </span>
                                        </td>
                                        <td>${payment.paymentDate ? new Date(payment.paymentDate).toLocaleDateString() : 'N/A'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            } else {
                container.innerHTML = '<div class="empty-state"><i class="bi bi-credit-card"></i><p>No payments found</p></div>';
            }
        } else {
            container.innerHTML = '<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>Error loading payments</p></div>';
        }
    } catch (error) {
        console.error('Error loading payments:', error);
        container.innerHTML = '<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>Error loading payments</p></div>';
    }
}

function updatePaymentSummary(summary) {
    // Update revenue cards
    document.getElementById('totalRevenue').textContent = `₦${summary.totalRevenue.toLocaleString()}`;
    document.getElementById('monthlyRevenue').textContent = `₦${summary.monthlyRevenue.toLocaleString()}`;
    document.getElementById('weeklyRevenue').textContent = `₦${summary.weeklyRevenue.toLocaleString()}`;
    document.getElementById('averagePayment').textContent = `₦${summary.averagePayment.toLocaleString()}`;
    
    // Update payment status cards
    document.getElementById('completedPayments').textContent = summary.completedPayments;
    document.getElementById('pendingPayments').textContent = summary.pendingPayments;
    document.getElementById('failedPayments').textContent = summary.failedPayments;
}

function updatePaymentMethodsChart(paymentMethods) {
    const container = document.getElementById('paymentMethodsChart');
    
    if (Object.keys(paymentMethods).length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="bi bi-pie-chart"></i><p>No payment methods data</p></div>';
        return;
    }
    
    let html = '<div class="payment-methods-list">';
    
    Object.entries(paymentMethods).forEach(([method, data]) => {
        const percentage = ((data.count / Object.values(paymentMethods).reduce((sum, m) => sum + m.count, 0)) * 100).toFixed(1);
        
        html += `
            <div class="payment-method-item mb-3 p-3" style="background: #f8f9fa; border-radius: 8px;">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                        <strong>${method}</strong>
                        <span class="badge bg-primary ms-2">${data.count} payments</span>
                    </div>
                    <div class="text-end">
                        <div><strong>₦${data.amount.toLocaleString()}</strong></div>
                        <small class="text-muted">${percentage}%</small>
                    </div>
                </div>
                <div class="progress" style="height: 6px;">
                    <div class="progress-bar bg-primary" style="width: ${percentage}%"></div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function updateRevenueTrendChart(dailyRevenue) {
    const container = document.getElementById('revenueTrendChart');
    
    if (Object.keys(dailyRevenue).length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="bi bi-graph-up"></i><p>No revenue trend data</p></div>';
        return;
    }
    
    // Sort dates and create chart
    const sortedDates = Object.keys(dailyRevenue).sort();
    const maxRevenue = Math.max(...Object.values(dailyRevenue));
    
    let html = '<div class="revenue-trend">';
    
    sortedDates.forEach(date => {
        const revenue = dailyRevenue[date];
        const height = maxRevenue > 0 ? (revenue / maxRevenue) * 100 : 0;
        const dateObj = new Date(date);
        const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
        
        html += `
            <div class="trend-item text-center mb-3">
                <div class="trend-bar-container" style="height: 80px; display: flex; align-items: end; justify-content: center;">
                    <div class="trend-bar bg-primary" style="width: 30px; height: ${height}%; border-radius: 4px 4px 0 0; min-height: 2px;"></div>
                </div>
                <div class="mt-2">
                    <small class="text-muted">${dayName}</small><br>
                    <strong style="font-size: 12px;">₦${revenue.toLocaleString()}</strong>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    container.innerHTML = `
        <style>
            .revenue-trend {
                display: flex;
                justify-content: space-around;
                align-items: end;
                padding: 20px 10px;
            }
            .trend-item {
                flex: 1;
                max-width: 80px;
            }
        </style>
        ${html}
    `;
}

function getPaymentStatusColor(status) {
    switch (status?.toLowerCase()) {
        case 'completed':
        case 'success':
            return 'success';
        case 'pending':
            return 'warning';
        case 'failed':
        case 'cancelled':
            return 'danger';
        default:
            return 'secondary';
    }
}

function getPaymentStatusIcon(status) {
    switch (status?.toLowerCase()) {
        case 'completed':
        case 'success':
            return 'check-circle-fill';
        case 'pending':
            return 'clock-fill';
        case 'failed':
        case 'cancelled':
            return 'x-circle-fill';
        default:
            return 'question-circle-fill';
    }
}


// ── Post Job ──────────────────────────────────────────────────────────────

async function openPostJobModal() {
    document.getElementById('postJobModal').style.display = 'block';
    document.getElementById('postJobError').style.display = 'none';
    document.getElementById('postJobSuccess').style.display = 'none';

    // Load categories into dropdown
    try {
        const res = await fetch(`${API}/categories`);
        const data = await res.json();
        const sel = document.getElementById('pj_category');
        sel.innerHTML = '<option value="">Select category</option>';
        const cats = data.data?.categories || data.data || [];
        cats.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = c.name;
            sel.appendChild(opt);
        });
    } catch (e) { /* categories optional */ }
}

function closePostJobModal() {
    document.getElementById('postJobModal').style.display = 'none';
}

async function submitPostJob() {
    const title = document.getElementById('pj_title').value.trim();
    const company = document.getElementById('pj_company').value.trim();
    const description = document.getElementById('pj_description').value.trim();
    const location = document.getElementById('pj_location').value.trim();

    const errEl = document.getElementById('postJobError');
    const sucEl = document.getElementById('postJobSuccess');
    errEl.style.display = 'none';
    sucEl.style.display = 'none';

    if (!title || !company || !description || !location) {
        errEl.textContent = 'Title, Company, Description and Location are required.';
        errEl.style.display = 'block';
        return;
    }

    const btn = document.getElementById('postJobBtn');
    btn.textContent = 'Posting...';
    btn.disabled = true;

    const token = localStorage.getItem('eaglesAdminToken');

    const payload = {
        title,
        company_name: company,
        description,
        requirements: document.getElementById('pj_requirements').value.trim() || null,
        responsibilities: document.getElementById('pj_responsibilities').value.trim() || null,
        location,
        job_type: document.getElementById('pj_job_type').value || null,
        salary_min: parseFloat(document.getElementById('pj_salary_min').value) || null,
        salary_max: parseFloat(document.getElementById('pj_salary_max').value) || null,
        currency: document.getElementById('pj_currency').value || 'NGN',
        vacancies: parseInt(document.getElementById('pj_vacancies').value) || 1,
        deadline: document.getElementById('pj_deadline').value || null,
        experience_required: document.getElementById('pj_experience').value.trim() || null,
        category_id: document.getElementById('pj_category').value || null,
        is_admin_post: true,
    };

    try {
        const res = await fetch(`${API}/admin/post-job`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (res.ok && data.success) {
            sucEl.textContent = `Job "${title}" posted successfully!`;
            sucEl.style.display = 'block';
            // Clear form
            ['pj_title','pj_company','pj_description','pj_requirements','pj_responsibilities',
             'pj_location','pj_salary_min','pj_salary_max','pj_experience','pj_deadline'].forEach(id => {
                document.getElementById(id).value = '';
            });
            document.getElementById('pj_vacancies').value = '1';
            // Reload jobs list after 1.5s
            setTimeout(() => { closePostJobModal(); loadJobs(); }, 1500);
        } else {
            errEl.textContent = data.detail || data.message || 'Failed to post job.';
            errEl.style.display = 'block';
        }
    } catch (e) {
        errEl.textContent = 'Connection error. Please try again.';
        errEl.style.display = 'block';
    } finally {
        btn.textContent = 'Post Job';
        btn.disabled = false;
    }
}
