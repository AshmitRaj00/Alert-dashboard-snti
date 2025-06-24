// Dashboard interactivity will go here 

// Draw Donut Chart
function drawDonutChart() {
    const canvas = document.getElementById('alertDonut');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const data = [60, 30, 10]; // Data Leaks, SSL Alerts, Others
    const colors = ['#5b5bf6', '#f44336', '#c49a4a'];
    const total = data.reduce((a, b) => a + b, 0);
    let startAngle = -0.5 * Math.PI;
    for (let i = 0; i < data.length; i++) {
        const sliceAngle = (data[i] / total) * 2 * Math.PI;
        ctx.beginPath();
        ctx.moveTo(50, 50);
        ctx.arc(50, 50, 45, startAngle, startAngle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = colors[i];
        ctx.fill();
        startAngle += sliceAngle;
    }
    // Add percentage labels
    ctx.font = 'bold 16px Poppins';
    ctx.fillStyle = '#5b5bf6';
    ctx.fillText('60%', 18, 38);
    ctx.fillStyle = '#f44336';
    ctx.fillText('30%', 68, 28);
    ctx.fillStyle = '#c49a4a';
    ctx.fillText('10%', 70, 80);
}

// Draw Line Chart
function drawLineChart() {
    const canvas = document.getElementById('alertTrends');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const data = [4, 3, 5, 7, 6, 8, 7];
    const labels = ['Apr 1', 'Apr 7', 'Apr 13', 'Apr 19', 'Apr 25', 'Apr 29', 'May 1'];
    const w = canvas.width = canvas.offsetWidth || 350;
    const h = canvas.height = 120;
    ctx.clearRect(0, 0, w, h);
    // Draw line
    ctx.beginPath();
    ctx.moveTo(30, h - 20 - data[0] * 10);
    for (let i = 1; i < data.length; i++) {
        ctx.lineTo(30 + (i * (w - 60) / (data.length - 1)), h - 20 - data[i] * 10);
    }
    const grad = ctx.createLinearGradient(30, 0, w - 30, 0);
    grad.addColorStop(0, '#f44336');
    grad.addColorStop(1, '#5b5bf6');
    ctx.strokeStyle = grad;
    ctx.lineWidth = 3;
    ctx.stroke();
    // Draw points
    for (let i = 0; i < data.length; i++) {
        ctx.beginPath();
        ctx.arc(30 + (i * (w - 60) / (data.length - 1)), h - 20 - data[i] * 10, 5, 0, 2 * Math.PI);
        ctx.fillStyle = grad;
        ctx.fill();
    }
    // Draw labels
    ctx.font = '12px Poppins';
    ctx.fillStyle = '#888';
    for (let i = 0; i < labels.length; i++) {
        ctx.fillText(labels[i], 18 + (i * (w - 60) / (labels.length - 1)), h - 2);
    }
}

// Fill Turnaround Bar
function fillTurnaroundBar() {
    const fill = document.querySelector('.turnaround-fill');
    if (fill) fill.style.width = '70%';
}

// Theme toggle logic
function setTheme(dark) {
    document.body.classList.toggle('dark', dark);
    const icon = document.querySelector('.theme-toggle i');
    if (icon) {
        icon.className = dark ? 'bx bx-sun' : 'bx bx-moon';
    }
}

function showLogin(show) {
    document.querySelector('.login-overlay').style.display = show ? 'flex' : 'none';
    document.querySelector('.dashboard-app').style.display = show ? 'none' : '';
}

function isLoggedIn() {
    return localStorage.getItem('loggedIn') === 'true';
}

function logout() {
    localStorage.removeItem('loggedIn');
    showLogin(true);
}

const randomUsers = [
    { name: 'Alex Carter', email: 'alex.carter@example.com', avatar: 'https://randomuser.me/api/portraits/men/32.jpg' },
    { name: 'Priya Singh', email: 'priya.singh@example.com', avatar: 'https://randomuser.me/api/portraits/women/65.jpg' },
    { name: 'Jordan Lee', email: 'jordan.lee@example.com', avatar: 'https://randomuser.me/api/portraits/men/76.jpg' },
    { name: 'Sara Kim', email: 'sara.kim@example.com', avatar: 'https://randomuser.me/api/portraits/women/12.jpg' },
    { name: 'Chris Brown', email: 'chris.brown@example.com', avatar: 'https://randomuser.me/api/portraits/men/45.jpg' },
    { name: 'Taylor Green', email: 'taylor.green@example.com', avatar: 'https://randomuser.me/api/portraits/men/88.jpg' },
    { name: 'Nina Patel', email: 'nina.patel@example.com', avatar: 'https://randomuser.me/api/portraits/women/23.jpg' }
];

function setRandomUser(user) {
    if (!user) {
        user = JSON.parse(localStorage.getItem('dashboardUser'));
        if (!user) {
            user = randomUsers[Math.floor(Math.random() * randomUsers.length)];
            localStorage.setItem('dashboardUser', JSON.stringify(user));
        }
    }
    document.getElementById('user-name').textContent = user.name;
    document.getElementById('user-email').textContent = user.email;
    document.getElementById('user-avatar').src = user.avatar || 'https://randomuser.me/api/portraits/lego/1.jpg';
}

function clearRandomUser() {
    localStorage.removeItem('dashboardUser');
}

function getRegisteredUsers() {
    return JSON.parse(localStorage.getItem('registeredUsers') || '[]');
}
function saveRegisteredUser(user) {
    const users = getRegisteredUsers();
    users.push(user);
    localStorage.setItem('registeredUsers', JSON.stringify(users));
}
function findUserByEmail(email) {
    return getRegisteredUsers().find(u => u.email === email);
}

let currentOTP = '';
let currentLoginEmail = '';
let resendTimeout = null;
let resendCooldown = 30; // seconds

function showLoginForm() {
    document.getElementById('login-form').style.display = '';
    document.getElementById('register-form').style.display = 'none';
    document.getElementById('otp-group').style.display = 'none';
    document.getElementById('login-email-group').style.display = '';
    document.getElementById('login-btn').textContent = 'Send OTP';
    document.getElementById('otp-message').textContent = '';
    document.getElementById('login-email').value = '';
    document.getElementById('login-otp').value = '';
}
function showRegisterForm() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = '';
    document.getElementById('register-name').value = '';
    document.getElementById('register-email').value = '';
    document.getElementById('register-password').value = '';
}
function showOTPInput(email, showResendMsg = false) {
    document.getElementById('login-email-group').style.display = 'none';
    document.getElementById('otp-group').style.display = '';
    document.getElementById('login-btn').textContent = 'Login';
    document.getElementById('login-otp').value = '';
    currentLoginEmail = email;
    document.getElementById('login-otp').focus();
    setResendOTPEnabled(false);
    let msg = `<div style='color:var(--text-main);margin-bottom:4px;'>OTP was sent to <b>${email}</b></div>`;
    if (showResendMsg) {
        msg += `<div class='success'>A new OTP has been sent.</div>`;
    }
    document.getElementById('otp-message').innerHTML = msg;
    startResendCooldown();
}
function generateOTP() {
    return Math.floor(100000 + Math.random() * 900000).toString();
}

function setResendOTPEnabled(enabled) {
    const resendLink = document.getElementById('resend-otp');
    resendLink.style.pointerEvents = enabled ? 'auto' : 'none';
    resendLink.style.opacity = enabled ? '1' : '0.5';
}

function startResendCooldown() {
    setResendOTPEnabled(false);
    let seconds = resendCooldown;
    const resendLink = document.getElementById('resend-otp');
    resendLink.textContent = `Resend OTP (${seconds})`;
    if (resendTimeout) clearInterval(resendTimeout);
    resendTimeout = setInterval(() => {
        seconds--;
        resendLink.textContent = seconds > 0 ? `Resend OTP (${seconds})` : 'Resend OTP';
        if (seconds <= 0) {
            clearInterval(resendTimeout);
            setResendOTPEnabled(true);
        }
    }, 1000);
}

function showPage(page) {
    document.getElementById('page-dashboard').style.display = page === 'dashboard' ? '' : 'none';
    document.getElementById('page-profile').style.display = page === 'profile' ? '' : 'none';
    document.getElementById('page-settings').style.display = page === 'settings' ? '' : 'none';
    // Sidebar active state
    document.getElementById('nav-dashboard').classList.toggle('active', page === 'dashboard');
    document.getElementById('nav-profile').classList.toggle('active', page === 'profile');
    document.getElementById('nav-settings').classList.toggle('active', page === 'settings');
}

function loadProfile() {
    const user = getCurrentUser();
    if (!user) return;
    document.getElementById('profile-name').value = user.name;
    document.getElementById('profile-email').value = user.email;
    document.getElementById('profile-avatar').src = user.avatar || 'https://randomuser.me/api/portraits/lego/1.jpg';
}
function saveProfile() {
    const name = document.getElementById('profile-name').value.trim();
    let user = getCurrentUser();
    if (!user) return;
    user.name = name;
    // Save avatar if changed
    user.avatar = document.getElementById('profile-avatar').src;
    updateRegisteredUser(user);
    setRandomUser(user); // update header
    alert('Profile updated!');
}
function getCurrentUser() {
    const email = document.getElementById('user-email').textContent.trim().toLowerCase();
    return findUserByEmail(email);
}
function updateRegisteredUser(updatedUser) {
    let users = getRegisteredUsers();
    users = users.map(u => u.email === updatedUser.email ? updatedUser : u);
    localStorage.setItem('registeredUsers', JSON.stringify(users));
    localStorage.setItem('dashboardUser', JSON.stringify(updatedUser));
}
// Avatar upload
function handleAvatarUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(evt) {
        document.getElementById('profile-avatar').src = evt.target.result;
    };
    reader.readAsDataURL(file);
}
// Password change
function changePassword() {
    const newPass = document.getElementById('settings-password').value.trim();
    if (!newPass) return alert('Enter a new password.');
    let user = getCurrentUser();
    if (!user) return;
    user.password = newPass;
    updateRegisteredUser(user);
    document.getElementById('settings-password').value = '';
    alert('Password changed!');
}
// Theme toggle from settings
function toggleThemeFromSettings() {
    const dark = !document.body.classList.contains('dark');
    setTheme(dark);
    localStorage.setItem('theme', dark ? 'dark' : 'light');
}

document.addEventListener('DOMContentLoaded', function() {
    drawDonutChart();
    drawLineChart();
    fillTurnaroundBar();

    // Theme toggle
    const themeBtn = document.querySelector('.theme-toggle');
    let dark = localStorage.getItem('theme') === 'dark';
    setTheme(dark);
    themeBtn.addEventListener('click', function() {
        dark = !document.body.classList.contains('dark');
        setTheme(dark);
        localStorage.setItem('theme', dark ? 'dark' : 'light');
    });

    // Login/Registration/OTP logic
    showLogin(!isLoggedIn());
    if (isLoggedIn()) setRandomUser();

    // Switch forms
    document.getElementById('show-register').onclick = function(e) {
        e.preventDefault();
        showRegisterForm();
    };
    document.getElementById('show-login').onclick = function(e) {
        e.preventDefault();
        showLoginForm();
    };

    // Registration
    document.getElementById('register-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const name = document.getElementById('register-name').value.trim();
        const email = document.getElementById('register-email').value.trim().toLowerCase();
        const password = document.getElementById('register-password').value.trim();
        if (!name || !email || !password) return;
        if (findUserByEmail(email)) {
            alert('Email already registered. Please login.');
            showLoginForm();
            return;
        }
        saveRegisteredUser({ name, email, password });
        alert('Registration successful! Please login.');
        showLoginForm();
    });

    // OTP Login
    document.getElementById('login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById('login-email').value.trim().toLowerCase();
        const otp = document.getElementById('login-otp').value.trim();
        if (document.getElementById('otp-group').style.display === 'none') {
            // Step 1: Send OTP
            const user = findUserByEmail(email);
            if (!user) {
                document.getElementById('otp-message').textContent = 'Email not registered.';
                return;
            }
            currentOTP = generateOTP();
            showOTPInput(email);
        } else {
            // Step 2: Verify OTP
            if (otp === currentOTP) {
                localStorage.setItem('loggedIn', 'true');
                clearRandomUser();
                setRandomUser();
                showLogin(false);
                document.getElementById('otp-message').textContent = '';
                currentOTP = '';
                currentLoginEmail = '';
            } else {
                document.getElementById('otp-message').textContent = 'Invalid OTP. Try again.';
            }
        }
    });

    // Logout logic
    document.querySelector('.sidebar-logout').addEventListener('click', function() {
        logout();
        clearRandomUser();
        showLoginForm();
    });

    // Resend OTP
    document.getElementById('resend-otp').addEventListener('click', function(e) {
        e.preventDefault();
        if (!currentLoginEmail) return;
        currentOTP = generateOTP();
        showOTPInput(currentLoginEmail, true);
    });

    // Navigation
    document.getElementById('nav-dashboard').onclick = function() { showPage('dashboard'); };
    document.getElementById('nav-profile').onclick = function() { loadProfile(); showPage('profile'); };
    document.getElementById('nav-settings').onclick = function() { showPage('settings'); };
    // Profile
    document.getElementById('change-avatar-btn').onclick = function() {
        document.getElementById('profile-avatar-upload').click();
    };
    document.getElementById('profile-avatar-upload').onchange = handleAvatarUpload;
    document.getElementById('save-profile-btn').onclick = saveProfile;
    // Settings
    document.getElementById('change-password-btn').onclick = changePassword;
    document.getElementById('settings-theme-btn').onclick = toggleThemeFromSettings;
    // Show dashboard by default
    showPage('dashboard');
}); 