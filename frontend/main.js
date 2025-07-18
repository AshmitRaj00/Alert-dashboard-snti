// API Configuration
const API_BASE_URL = 'http://localhost:8000';
let authToken = localStorage.getItem('authToken');

// API Helper Functions
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...(authToken && { 'Authorization': `Bearer ${authToken}` })
        },
        ...options
    };

    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

// Authentication Functions
async function login(username, password) {
    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            return { success: true, user: data.user };
        } else {
            throw new Error(data.detail || 'Login failed');
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function register(username, email, password) {
    try {
        const data = await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
        return { success: true, user: data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function logout() {
    authToken = null;
    localStorage.removeItem('authToken');
    showLogin();
}

// Alert Management Functions
async function createAlert(alertData) {
    try {
        const alert = await apiRequest('/alerts/', {
            method: 'POST',
            body: JSON.stringify(alertData)
        });
        return { success: true, alert };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function getAlerts() {
    try {
        const alerts = await apiRequest('/alerts/');
        return alerts;
    } catch (error) {
        console.error('Failed to fetch alerts:', error);
        return [];
    }
}

async function updateAlert(alertId, alertData) {
    try {
        const alert = await apiRequest(`/alerts/${alertId}`, {
            method: 'PUT',
            body: JSON.stringify(alertData)
        });
        return { success: true, alert };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function deleteAlert(alertId) {
    try {
        await apiRequest(`/alerts/${alertId}`, {
            method: 'DELETE'
        });
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

async function getAlertStats() {
    try {
        const stats = await apiRequest('/alerts/stats');
        return stats;
    } catch (error) {
        console.error('Failed to fetch alert stats:', error);
        return null;
    }
}

// UI State Management
let currentView = 'dashboard';
let currentEditingAlert = null;

// DOM Elements
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const dashboardContainer = document.getElementById('dashboardContainer');
const alertsContainer = document.getElementById('alertsContainer');
const settingsContainer = document.getElementById('settingsContainer');
const alertForm = document.getElementById('alertForm');
const alertModal = document.getElementById('alertModal');
// Add new DOM elements for new pages and buttons
const profilePage = document.getElementById('page-profile');
const monitoringPage = document.getElementById('page-monitoring');
const apiScanPage = document.getElementById('page-api-scan');
const reportsPage = document.getElementById('page-reports');
const sidebarLogout = document.querySelector('.sidebar-logout');
const sidebarSettings = document.querySelector('.sidebar-settings');
const themeToggle = document.querySelector('.theme-toggle');
const navProfile = document.getElementById('nav-profile');
const navDashboard = document.getElementById('nav-dashboard');
const navSettings = document.getElementById('nav-settings');
const navMonitoring = document.getElementById('nav-monitoring');
const navApiScan = document.getElementById('nav-api-scan');
const navReports = document.getElementById('nav-reports');
const saveProfileBtn = document.getElementById('save-profile-btn');
const changeAvatarBtn = document.getElementById('change-avatar-btn');
const profileAvatarUpload = document.getElementById('profile-avatar-upload');

// Navigation Functions
function showLogin() {
    hideAllContainers();
    document.getElementById('loginContainer').style.display = 'block';
    document.getElementById('navbar').style.display = 'none';
}

function showRegister() {
    hideAllContainers();
    document.getElementById('registerContainer').style.display = 'block';
    document.getElementById('navbar').style.display = 'none';
}

function showDashboard() {
    hideAllContainers();
    dashboardContainer.style.display = 'block';
    document.getElementById('navbar').style.display = 'flex';
    currentView = 'dashboard';
    loadDashboard();
}

function showAlerts() {
    hideAllContainers();
    alertsContainer.style.display = 'block';
    document.getElementById('navbar').style.display = 'flex';
    currentView = 'alerts';
    loadAlerts();
}

function showSettings() {
    hideAllContainers();
    settingsContainer.style.display = 'block';
    document.getElementById('navbar').style.display = 'flex';
    currentView = 'settings';
}

function showProfile() {
    hideAllContainers();
    if (profilePage) profilePage.style.display = 'block';
    document.getElementById('navbar').style.display = 'flex';
    currentView = 'profile';
    // Optionally load user profile data here
}

function showMonitoring() {
    hideAllContainers();
    if (monitoringPage) monitoringPage.style.display = 'block';
    document.getElementById('navbar').style.display = 'flex';
    currentView = 'monitoring';
}

function showApiScan() {
    hideAllContainers();
    if (apiScanPage) apiScanPage.style.display = 'block';
    document.getElementById('navbar').style.display = 'flex';
    currentView = 'api-scan';
}

function showReports() {
    hideAllContainers();
    if (reportsPage) reportsPage.style.display = 'block';
    document.getElementById('navbar').style.display = 'flex';
    currentView = 'reports';
}

function hideAllContainers() {
    const containers = [
        'loginContainer', 'registerContainer', 'dashboardContainer', 
        'alertsContainer', 'settingsContainer',
        'page-profile', 'page-monitoring', 'page-api-scan', 'page-reports'
    ];
    containers.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.style.display = 'none';
    });
}

// Dashboard Functions
async function loadDashboard() {
    try {
        const stats = await getAlertStats();
        if (stats) {
            updateDashboardStats(stats);
            // Example: render graph with dummy data
            renderAlertTrendsChart({
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                values: [12, 19, 7, 14, 10, 15, 9]
            });
        }
        
        const alerts = await getAlerts();
        updateRecentAlerts(alerts.slice(0, 5));
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

function updateDashboardStats(stats) {
    const statsContainer = document.getElementById('statsContainer');
    if (statsContainer) {
        statsContainer.innerHTML = `
            <div class="stat-card">
                <h3>Total Alerts</h3>
                <p class="stat-number">${stats.total_alerts}</p>
            </div>
            <div class="stat-card">
                <h3>Active Alerts</h3>
                <p class="stat-number">${stats.active_alerts}</p>
            </div>
            <div class="stat-card">
                <h3>Triggered Today</h3>
                <p class="stat-number">${stats.triggered_today}</p>
            </div>
            <div class="stat-card">
                <h3>Success Rate</h3>
                <p class="stat-number">${stats.success_rate}%</p>
            </div>
        `;
    }
}

function updateRecentAlerts(alerts) {
    const recentAlertsContainer = document.getElementById('recentAlerts');
    if (recentAlertsContainer) {
        recentAlertsContainer.innerHTML = alerts.map(alert => `
            <div class="alert-item">
                <h4>${alert.title}</h4>
                <p>${alert.message}</p>
                <span class="alert-status ${alert.status}">${alert.status}</span>
                <span class="alert-date">${new Date(alert.created_at).toLocaleDateString()}</span>
            </div>
        `).join('');
    }
}

// Alert Management Functions
async function loadAlerts() {
    try {
        const alerts = await getAlerts();
        displayAlerts(alerts);
    } catch (error) {
        console.error('Failed to load alerts:', error);
    }
}

function displayAlerts(alerts) {
    const alertsList = document.getElementById('alertsList');
    if (!alertsList) return;

    alertsList.innerHTML = alerts.map(alert => `
        <div class="alert-card" data-alert-id="${alert.id}">
            <div class="alert-header">
                <h3>${alert.title}</h3>
                <span class="alert-status ${alert.status}">${alert.status}</span>
            </div>
            <div class="alert-content">
                <p>${alert.message}</p>
                <div class="alert-details">
                    <span>Type: ${alert.alert_type}</span>
                    <span>Created: ${new Date(alert.created_at).toLocaleDateString()}</span>
                    ${alert.triggered_at ? `<span>Triggered: ${new Date(alert.triggered_at).toLocaleDateString()}</span>` : ''}
                </div>
            </div>
            <div class="alert-actions">
                <button onclick="editAlert(${alert.id})" class="btn btn-secondary">Edit</button>
                <button onclick="deleteAlertConfirm(${alert.id})" class="btn btn-danger">Delete</button>
                <button onclick="testAlert(${alert.id})" class="btn btn-info">Test</button>
            </div>
        </div>
    `).join('');
}

// Modal Functions
function showAlertModal(alert = null) {
    currentEditingAlert = alert;
    const modal = document.getElementById('alertModal');
    const title = document.getElementById('modalTitle');
    const form = document.getElementById('alertForm');
    
    if (alert) {
        title.textContent = 'Edit Alert';
        document.getElementById('alertTitle').value = alert.title;
        document.getElementById('alertMessage').value = alert.message;
        document.getElementById('alertType').value = alert.alert_type;
        document.getElementById('isActive').checked = alert.is_active;
    } else {
        title.textContent = 'Create New Alert';
        form.reset();
    }
    
    modal.style.display = 'block';
}

function closeAlertModal() {
    document.getElementById('alertModal').style.display = 'none';
    currentEditingAlert = null;
}

async function saveAlert() {
    const form = document.getElementById('alertForm');
    const formData = new FormData(form);
    
    const alertData = {
        title: formData.get('title'),
        message: formData.get('message'),
        alert_type: formData.get('alert_type'),
        is_active: formData.get('is_active') === 'on'
    };

    try {
        let result;
        if (currentEditingAlert) {
            result = await updateAlert(currentEditingAlert.id, alertData);
        } else {
            result = await createAlert(alertData);
        }

        if (result.success) {
            closeAlertModal();
            loadAlerts();
            showNotification('Alert saved successfully!', 'success');
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        showNotification('Failed to save alert', 'error');
    }
}

async function editAlert(alertId) {
    try {
        const alert = await apiRequest(`/alerts/${alertId}`);
        showAlertModal(alert);
    } catch (error) {
        showNotification('Failed to load alert details', 'error');
    }
}

async function deleteAlertConfirm(alertId) {
    if (confirm('Are you sure you want to delete this alert?')) {
        const result = await deleteAlert(alertId);
        if (result.success) {
            loadAlerts();
            showNotification('Alert deleted successfully!', 'success');
        } else {
            showNotification(result.error, 'error');
        }
    }
}

async function testAlert(alertId) {
    try {
        await apiRequest(`/alerts/${alertId}/test`, { method: 'POST' });
        showNotification('Test alert sent successfully!', 'success');
    } catch (error) {
        showNotification('Failed to send test alert', 'error');
    }
}

// Utility Functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    if (authToken) {
        showDashboard();
    } else {
        showLogin();
    }

    // Login form
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            const result = await login(username, password);
            if (result.success) {
                showDashboard();
            } else {
                showNotification(result.error, 'error');
            }
        });
    }

    // Register form
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('regUsername').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;
            
            const result = await register(username, email, password);
            if (result.success) {
                showNotification('Registration successful! Please login.', 'success');
                showLogin();
            } else {
                showNotification(result.error, 'error');
            }
        });
    }

    // Alert form
    if (alertForm) {
        alertForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveAlert();
        });
    }

    // Navigation buttons
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const view = this.dataset.view;
            switch(view) {
                case 'dashboard':
                    showDashboard();
                    break;
                case 'alerts':
                    showAlerts();
                    break;
                case 'settings':
                    showSettings();
                    break;
            }
        });
    });

    // Modal close buttons
    const closeButtons = document.querySelectorAll('.close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.modal').style.display = 'none';
        });
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });

    // Sidebar navigation
    if (navDashboard) navDashboard.onclick = showDashboard;
    if (navProfile) navProfile.onclick = showProfile;
    if (navSettings) navSettings.onclick = showSettings;
    if (navMonitoring) navMonitoring.onclick = showMonitoring;
    if (navApiScan) navApiScan.onclick = showApiScan;
    if (navReports) navReports.onclick = showReports;
    // Sidebar logout/settings
    if (sidebarLogout) sidebarLogout.onclick = logout;
    if (sidebarSettings) sidebarSettings.onclick = showSettings;
    // Theme toggle
    if (themeToggle) {
        themeToggle.onclick = function() {
            document.body.classList.toggle('dark');
        };
    }
    // Profile actions
    if (saveProfileBtn) {
        saveProfileBtn.onclick = function() {
            // Save profile logic (stub)
            showNotification('Profile saved!', 'success');
        };
    }
    if (changeAvatarBtn && profileAvatarUpload) {
        changeAvatarBtn.onclick = function() {
            profileAvatarUpload.click();
        };
        profileAvatarUpload.onchange = function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(evt) {
                    document.getElementById('profile-avatar').src = evt.target.result;
                };
                reader.readAsDataURL(file);
            }
        };
    }
});

// Export functions for global access
window.showLogin = showLogin;
window.showRegister = showRegister;
window.showDashboard = showDashboard;
window.showAlerts = showAlerts;
window.showSettings = showSettings;
window.logout = logout;
window.showAlertModal = showAlertModal;
window.closeAlertModal = closeAlertModal;
window.editAlert = editAlert;
window.deleteAlertConfirm = deleteAlertConfirm;
window.testAlert = testAlert;

// Chart.js for dashboard graph
function renderAlertTrendsChart(data) {
    if (window.alertTrendsChart) {
        window.alertTrendsChart.destroy();
    }
    const ctx = document.getElementById('alertTrends');
    if (!ctx || typeof Chart === 'undefined') return;
    window.alertTrendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Alerts',
                data: data.values,
                borderColor: '#5b5bf6',
                backgroundColor: 'rgba(91,91,246,0.1)',
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } }
        }
    });
}