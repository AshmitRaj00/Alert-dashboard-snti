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

    // Login logic
    showLogin(!isLoggedIn());
    document.querySelector('.login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById('login-email').value.trim();
        const pass = document.getElementById('login-password').value.trim();
        if (email && pass) {
            localStorage.setItem('loggedIn', 'true');
            showLogin(false);
        }
    });
    // Logout logic
    document.querySelector('.sidebar-logout').addEventListener('click', function() {
        logout();
    });
}); 