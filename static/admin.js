const API = '/api/v10';
let currentFilter = 'all';

// Show/Hide Sections
function showSection(section) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(section).classList.add('active');
    
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    event.target.closest('.nav-item').classList.add('active');
    
    const titles = {
        dashboard: 'Dashboard',
        users: 'User Management',
        jobs: 'Job Management',
        companies: 'Company Management',
        applications: 'Application Management',
        notifications: 'Notifications',
        chat: 'Chat Conversations',
        categories: 'Category Management',
        recommended: 'Recommended Jobs'
    };
    document.getElementById('pageTitle').textContent = titles[section] || 'Dashboard';
}

// Load All Data
async function loadAllData() {
    await Promise.all([
        loadUserStats(),
        loadUsers(),
        loadJobs(),
        loadCompanies(),
        loadApplications(),
        loadNotifications(),
        loadChat(),
        loadCategories(),
        loadRecommendedJobs()
    ]);
}

// Load User Statistics
async function loadUserStats() {
    try {
        const response = await fetch(`${API}/admin/users/stats`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('totalUsers').textContent = data.data.totalUsers;
            document.getElementById('totalApplicants').textContent = data.data.applicants;
            document.getElementById('totalCompanies').textContent = data.data.companies;
            document.getElementById('onlineUsers').textContent = data.data.onlineUsers;
            document.getElementById('activeUsers').textContent = data.data.activeUsers;
        }
    } catch (error) {
        console.error('Error loading user stats:', error);
    }
}

// Filter Users
function filterUsers(type) {
    currentFilter = type;
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    loadUsers();
}

// Load Users
async function loadUsers() {
    const container = document.getElementById('usersTable');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading users...</div>';
    
    try {
        let url = `${API}/admin/users`;
        if (currentFilter === 'applicant' || currentFilter === 'company') {
            url += `?user_type=${currentFilter}`;
        } else if (currentFilter === 'online') {
            url += `?is_online=true`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success && data.data.users.length > 0) {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Phone</th>
                            <th>Type</th>
                            <th>Status</th>
                            <th>Online</th>
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
                                <td>${user.phone}</td>
                                <td><span class="badge ${user.userType === 'company' ? 'badge-info' : 'badge-warning'}">${user.userType}</span></td>
                                <td><span class="badge ${user.isActive ? 'badge-success' : 'badge-danger'}">${user.isActive ? 'Active' : 'Inactive'}</span></td>
                                <td><span class="badge ${user.isOnline ? 'badge-online' : 'badge-offline'}">${user.isOnline ? 'Online' : 'Offline'}</span></td>
                                <td>${user.lastLogin ? new Date(user.lastLogin).toLocaleString() : 'Never'}</td>
                                <td>
                                    <button class="btn btn-sm btn-warning" onclick="toggleUserStatus(${user.id})">
                                        <i class="fas fa-toggle-on"></i>
                                    </button>
                                    <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-users"></i><p>No users found</p></div>';
        }
    } catch (error) {
        console.error('Error loading users:', error);
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Error loading users</p></div>';
    }
}

// Load Jobs
async function loadJobs() {
    const container = document.getElementById('jobsTable');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading jobs...</div>';
    
    try {
        const response = await fetch(`${API}/jobs/recent`);
        const data = await response.json();
        
        if (data.success && data.data.jobs && data.data.jobs.length > 0) {
            document.getElementById('totalJobs').textContent = data.data.jobs.length;
            
            container.innerHTML = `
                <table>
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
                                <td><span class="badge ${job.isActive ? 'badge-success' : 'badge-danger'}">${job.isActive ? 'Active' : 'Closed'}</span></td>
                                <td>${new Date(job.createdAt).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn btn-sm btn-warning" onclick="toggleJobStatus(${job.id})">
                                        <i class="fas fa-toggle-on"></i>
                                    </button>
                                    <button class="btn btn-sm btn-danger" onclick="deleteJob(${job.id})">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-briefcase"></i><p>No jobs found</p></div>';
        }
    } catch (error) {
        console.error('Error loading jobs:', error);
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Error loading jobs</p></div>';
    }
}

// Load Companies
async function loadCompanies() {
    const container = document.getElementById('companiesTable');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading companies...</div>';
    
    try {
        const response = await fetch(`${API}/companies`);
        const data = await response.json();
        
        if (data.success && data.data.companies && data.data.companies.length > 0) {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Industry</th>
                            <th>Location</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.data.companies.map(company => `
                            <tr>
                                <td>${company.id}</td>
                                <td><strong>${company.name}</strong></td>
                                <td>${company.industry || 'N/A'}</td>
                                <td>${company.location || 'N/A'}</td>
                                <td><span class="badge ${company.isActive ? 'badge-success' : 'badge-danger'}">${company.isActive ? 'Active' : 'Inactive'}</span></td>
                                <td>
                                    <button class="btn btn-sm btn-danger" onclick="deleteCompany(${company.id})">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-building"></i><p>No companies found</p></div>';
        }
    } catch (error) {
        console.error('Error loading companies:', error);
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Error loading companies</p></div>';
    }
}

// Load Applications
async function loadApplications() {
    const container = document.getElementById('applicationsTable');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading applications...</div>';
    
    try {
        const response = await fetch(`${API}/admin/applications`);
        const data = await response.json();
        
        if (data.success && data.data.applications.length > 0) {
            document.getElementById('totalApplications').textContent = data.data.applications.length;
            
            container.innerHTML = `
                <table>
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
                                <td><span class="badge badge-info">${app.status}</span></td>
                                <td>${new Date(app.createdAt).toLocaleDateString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-file-alt"></i><p>No applications found</p></div>';
        }
    } catch (error) {
        console.error('Error loading applications:', error);
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Error loading applications</p></div>';
    }
}

// Load Notifications
async function loadNotifications() {
    const container = document.getElementById('notificationsTable');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading notifications...</div>';
    
    try {
        const response = await fetch(`${API}/admin/notifications`);
        const data = await response.json();
        
        if (data.success && data.data.notifications.length > 0) {
            document.getElementById('totalNotifications').textContent = data.data.notifications.length;
            
            container.innerHTML = `
                <table>
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
                                <td><span class="badge badge-info">${notif.type}</span></td>
                                <td><span class="badge ${notif.isRead ? 'badge-success' : 'badge-warning'}">${notif.isRead ? 'Read' : 'Unread'}</span></td>
                                <td>${new Date(notif.createdAt).toLocaleString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-bell"></i><p>No notifications sent yet</p></div>';
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Error loading notifications</p></div>';
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
            loadUserStats();
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
            loadUserStats();
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

// Delete Company
async function deleteCompany(id) {
    if (!confirm('Are you sure you want to delete this company?')) return;
    
    try {
        const response = await fetch(`${API}/admin/companies/${id}`, { method: 'DELETE' });
        const data = await response.json();
        
        if (data.success) {
            alert('Company deleted successfully');
            loadCompanies();
        } else {
            alert('Failed to delete company');
        }
    } catch (error) {
        console.error('Error deleting company:', error);
        alert('Error deleting company');
    }
}

// Show Notification Modal
function showNotificationModal() {
    document.getElementById('notificationModal').classList.add('active');
}

// Close Notification Modal
function closeNotificationModal() {
    document.getElementById('notificationModal').classList.remove('active');
    document.getElementById('notificationForm').reset();
}

// Send Notification
async function sendNotification(event) {
    event.preventDefault();
    
    const target = document.getElementById('notifTarget').value;
    const title = document.getElementById('notifTitle').value;
    const message = document.getElementById('notifMessage').value;
    const type = document.getElementById('notifType').value;
    
    try {
        const response = await fetch(`${API}/admin/notifications/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_type: target,
                title: title,
                message: message,
                notification_type: type
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Notification sent to ${data.data.recipientCount} user(s)`);
            closeNotificationModal();
            loadNotifications();
        } else {
            alert('Failed to send notification');
        }
    } catch (error) {
        console.error('Error sending notification:', error);
        alert('Error sending notification');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadAllData();
    setInterval(loadUserStats, 30000); // Refresh stats every 30 seconds
});


// ============ CHAT MANAGEMENT ============
async function loadChat() {
    const container = document.getElementById('chatTable');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading conversations...</div>';
    
    try {
        const response = await fetch(`${API}/chat/conversations`);
        const data = await response.json();
        
        if (data.success && data.data.conversations && data.data.conversations.length > 0) {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>User 1</th>
                            <th>User 2</th>
                            <th>Last Message</th>
                            <th>Unread Count</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.data.conversations.map(conv => `
                            <tr>
                                <td>${conv.id}</td>
                                <td>${conv.user1Name || 'User ' + conv.user1Id}</td>
                                <td>${conv.user2Name || 'User ' + conv.user2Id}</td>
                                <td>${conv.lastMessage ? conv.lastMessage.substring(0, 50) + '...' : 'No messages'}</td>
                                <td><span class="badge badge-info">${conv.unreadCount || 0}</span></td>
                                <td>${new Date(conv.createdAt).toLocaleDateString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-comments"></i><p>No conversations found</p></div>';
        }
    } catch (error) {
        console.error('Error loading chat:', error);
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Error loading conversations</p></div>';
    }
}

// ============ CATEGORY MANAGEMENT ============
async function loadCategories() {
    const container = document.getElementById('categoriesTable');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading categories...</div>';
    
    try {
        const response = await fetch(`${API}/admin/categories/manage`);
        const data = await response.json();
        
        if (data.success && data.data.categories && data.data.categories.length > 0) {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Icon</th>
                            <th>Description</th>
                            <th>Status</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.data.categories.map(cat => `
                            <tr>
                                <td>${cat.id}</td>
                                <td><strong>${cat.name}</strong></td>
                                <td><i class="fas ${cat.icon}"></i> ${cat.icon}</td>
                                <td>${cat.description || 'N/A'}</td>
                                <td><span class="badge ${cat.isActive ? 'badge-success' : 'badge-danger'}">${cat.isActive ? 'Active' : 'Inactive'}</span></td>
                                <td>${new Date(cat.createdAt).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary" onclick="editCategory(${cat.id})">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-danger" onclick="deleteCategory(${cat.id})">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-tags"></i><p>No categories found</p></div>';
        }
    } catch (error) {
        console.error('Error loading categories:', error);
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Error loading categories</p></div>';
    }
}

function showCategoryModal() {
    document.getElementById('categoryModalTitle').textContent = 'Add Category';
    document.getElementById('categoryForm').reset();
    document.getElementById('categoryId').value = '';
    document.getElementById('categoryModal').classList.add('active');
}

function closeCategoryModal() {
    document.getElementById('categoryModal').classList.remove('active');
    document.getElementById('categoryForm').reset();
}

async function editCategory(id) {
    try {
        const response = await fetch(`${API}/admin/categories/manage`);
        const data = await response.json();
        
        if (data.success) {
            const category = data.data.categories.find(c => c.id === id);
            if (category) {
                document.getElementById('categoryModalTitle').textContent = 'Edit Category';
                document.getElementById('categoryId').value = category.id;
                document.getElementById('categoryName').value = category.name;
                document.getElementById('categoryIcon').value = category.icon || '';
                document.getElementById('categoryDescription').value = category.description || '';
                document.getElementById('categoryModal').classList.add('active');
            }
        }
    } catch (error) {
        console.error('Error loading category:', error);
        alert('Error loading category');
    }
}

async function saveCategory(event) {
    event.preventDefault();
    
    const id = document.getElementById('categoryId').value;
    const name = document.getElementById('categoryName').value;
    const icon = document.getElementById('categoryIcon').value;
    const description = document.getElementById('categoryDescription').value;
    
    const categoryData = {
        name: name,
        icon: icon,
        description: description,
        is_active: true
    };
    
    try {
        let response;
        if (id) {
            // Update existing category
            response = await fetch(`${API}/admin/categories/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(categoryData)
            });
        } else {
            // Create new category
            response = await fetch(`${API}/admin/categories/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(categoryData)
            });
        }
        
        const data = await response.json();
        
        if (data.success) {
            alert(id ? 'Category updated successfully' : 'Category created successfully');
            closeCategoryModal();
            loadCategories();
        } else {
            alert('Failed to save category');
        }
    } catch (error) {
        console.error('Error saving category:', error);
        alert('Error saving category');
    }
}

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

// ============ RECOMMENDED JOBS MANAGEMENT ============
async function loadRecommendedJobs() {
    const container = document.getElementById('recommendedTable');
    container.innerHTML = '<div class="loading"><div class="spinner"></div>Loading jobs...</div>';
    
    try {
        const response = await fetch(`${API}/admin/jobs/recommended/manage`);
        const data = await response.json();
        
        if (data.success && data.data.jobs && data.data.jobs.length > 0) {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Location</th>
                            <th>Status</th>
                            <th>Recommended</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.data.jobs.map(job => `
                            <tr>
                                <td>${job.id}</td>
                                <td><strong>${job.title}</strong></td>
                                <td>${job.location || 'N/A'}</td>
                                <td><span class="badge ${job.isActive ? 'badge-success' : 'badge-danger'}">${job.isActive ? 'Active' : 'Closed'}</span></td>
                                <td><span class="badge ${job.isRecommended ? 'badge-success' : 'badge-warning'}">${job.isRecommended ? 'Yes' : 'No'}</span></td>
                                <td>${new Date(job.createdAt).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn btn-sm ${job.isRecommended ? 'btn-warning' : 'btn-success'}" onclick="toggleRecommended(${job.id})">
                                        <i class="fas fa-star"></i> ${job.isRecommended ? 'Remove' : 'Add'}
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-briefcase"></i><p>No jobs found</p></div>';
        }
    } catch (error) {
        console.error('Error loading recommended jobs:', error);
        container.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Error loading jobs</p></div>';
    }
}

async function toggleRecommended(id) {
    try {
        const response = await fetch(`${API}/admin/jobs/${id}/toggle-recommended`, { method: 'PATCH' });
        const data = await response.json();
        
        if (data.success) {
            loadRecommendedJobs();
        } else {
            alert('Failed to toggle recommended status');
        }
    } catch (error) {
        console.error('Error toggling recommended:', error);
        alert('Error toggling recommended status');
    }
}
