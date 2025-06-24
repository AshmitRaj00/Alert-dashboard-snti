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

function setRandomUser() {
    let user = JSON.parse(localStorage.getItem('dashboardUser'));
    if (!user) {
        user = randomUsers[Math.floor(Math.random() * randomUsers.length)];
        localStorage.setItem('dashboardUser', JSON.stringify(user));
    }
    document.getElementById('user-name').textContent = user.name;
    document.getElementById('user-email').textContent = user.email;
    document.getElementById('user-avatar').src = user.avatar;
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
function showOTPInput(email) {
    document.getElementById('login-email-group').style.display = 'none';
    document.getElementById('otp-group').style.display = '';
    document.getElementById('login-btn').textContent = 'Login';
    document.getElementById('otp-message').textContent = `Your OTP is: ${currentOTP}`;
    document.getElementById('login-otp').value = '';
    currentLoginEmail = email;
}
function generateOTP() {
    return Math.floor(100000 + Math.random() * 900000).toString();
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
}); 