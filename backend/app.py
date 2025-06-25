from flask import Flask, request, session, jsonify
from flask_cors import CORS
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
CORS(app, supports_credentials=True)

# In-memory user store (replace with DB in production)
users = {}

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email', '').lower()
    if email in users:
        return jsonify({'error': 'Email already registered'}), 400
    users[email] = {
        'name': data.get('name'),
        'email': email,
        'password': generate_password_hash(data.get('password')),
        'avatar': data.get('avatar', ''),
        'theme': 'light'
    }
    return jsonify({'message': 'Registration successful'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').lower()
    password = data.get('password')
    user = users.get(email)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid email or password'}), 401
    session['user'] = email
    return jsonify({'message': 'Login successful', 'user': {k: v for k, v in user.items() if k != 'password'}})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logged out'})

@app.route('/api/profile', methods=['GET', 'POST'])
def profile():
    email = session.get('user')
    if not email or email not in users:
        return jsonify({'error': 'Not logged in'}), 401
    if request.method == 'GET':
        user = users[email].copy()
        user.pop('password')
        return jsonify(user)
    # POST: update profile
    data = request.json
    users[email]['name'] = data.get('name', users[email]['name'])
    users[email]['avatar'] = data.get('avatar', users[email]['avatar'])
    return jsonify({'message': 'Profile updated'})

@app.route('/api/change-password', methods=['POST'])
def change_password():
    email = session.get('user')
    if not email or email not in users:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.json
    new_password = data.get('new_password')
    users[email]['password'] = generate_password_hash(new_password)
    return jsonify({'message': 'Password changed'})

@app.route('/api/theme', methods=['POST'])
def set_theme():
    email = session.get('user')
    if not email or email not in users:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.json
    users[email]['theme'] = data.get('theme', 'light')
    return jsonify({'message': 'Theme updated'})

@app.route('/api/dashboard-data', methods=['GET'])
def dashboard_data():
    email = session.get('user')
    if not email or email not in users:
        return jsonify({'error': 'Not logged in'}), 401
    # Demo data
    return jsonify({
        'alert_count': 324,
        'critical_alerts': 85,
        'open_alerts': 56,
        'closed_alerts': 183,
        'donut': {'ssl': 30, 'data': 60, 'other': 10},
        'trends': [4, 3, 5, 7, 6, 8, 7],
        'recent_alerts': [
            {'datetime': '04/15/2024 10:35 AM', 'type': 'Malware', 'severity': 'High', 'desc': 'Malware detected'},
            {'datetime': '04/15/2024 09:21 AM', 'type': 'Unauthorized Access', 'severity': 'Medium', 'desc': 'Suspicious login'},
            {'datetime': '04/15/2024 08:25 AM', 'type': 'Expired SSL', 'severity': 'Medium', 'desc': 'Expired SSL certificate'}
        ],
        'top_alerts': [
            {'source': '192.168.1.12', 'count': 120, 'critical': 45},
            {'source': 'App Server 3', 'count': 95, 'critical': 33},
            {'source': 'Firewall A', 'count': 50, 'critical': 10}
        ],
        'turnaround_time': '1 h 45 min'
    })

@app.route('/api/monitoring', methods=['GET'])
def monitoring():
    email = session.get('user')
    if not email or email not in users:
        return jsonify({'error': 'Not logged in'}), 401
    # Demo monitoring data
    return jsonify({
        'systems': [
            {'name': 'Web Server', 'status': 'Online', 'uptime': '99.99%'},
            {'name': 'Database', 'status': 'Online', 'uptime': '99.95%'},
            {'name': 'Firewall', 'status': 'Online', 'uptime': '100%'},
            {'name': 'API Gateway', 'status': 'Degraded', 'uptime': '97.5%'}
        ]
    })

@app.route('/api/api-scan', methods=['POST'])
def api_scan():
    email = session.get('user')
    if not email or email not in users:
        return jsonify({'error': 'Not logged in'}), 401
    # Demo scan result
    return jsonify({
        'scan_id': 'scan123',
        'status': 'completed',
        'issues': [
            {'endpoint': '/login', 'issue': 'SQL Injection', 'severity': 'High'},
            {'endpoint': '/user', 'issue': 'Sensitive Data Exposure', 'severity': 'Medium'}
        ]
    })

@app.route('/api/reports', methods=['GET'])
def reports():
    email = session.get('user')
    if not email or email not in users:
        return jsonify({'error': 'Not logged in'}), 401
    # Demo reports
    return jsonify({
        'reports': [
            {'name': 'April Security Report', 'date': '2024-05-01', 'summary': 'No major incidents.'},
            {'name': 'March Security Report', 'date': '2024-04-01', 'summary': '2 critical alerts resolved.'}
        ]
    })

if __name__ == '__main__':
    app.run(debug=True) 