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
        case 'jobs':
            loadJobs();
            break;
        case 'applications':
            loadApplications();
            break;
        case 'payments':
            loadPayments();
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
