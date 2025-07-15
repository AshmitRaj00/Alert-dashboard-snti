# main.py
from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
import hashlib
import secrets
import asyncio
import sqlite3
import json
import base64
from contextlib import asynccontextmanager

# Database setup
DATABASE_URL = "alerts_dashboard.db"

def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            avatar TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            source_system TEXT,
            source_ip TEXT,
            status TEXT DEFAULT 'Open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # OTP table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            otp_code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT FALSE
        )
    ''')
    
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    # Insert sample data
    await insert_sample_data()
    yield
    # Shutdown
    pass

app = FastAPI(title="Alerts Dashboard API", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT configuration
JWT_SECRET_KEY = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

security = HTTPBearer()

# Pydantic models
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    avatar: Optional[str] = None

class AlertCreate(BaseModel):
    alert_type: str
    severity: str
    description: str
    source_system: Optional[str] = None
    source_ip: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    description: str
    source_system: Optional[str]
    source_ip: Optional[str]
    status: str
    created_at: str
    resolved_at: Optional[str]

class AlertStats(BaseModel):
    total_alerts: int
    critical_alerts: int
    open_alerts: int
    closed_alerts: int
    ssl_alerts: int
    data_leaks: int
    other_alerts: int

class ProfileUpdate(BaseModel):
    name: str
    avatar: Optional[str] = None

class PasswordChange(BaseModel):
    new_password: str

# Utility functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)

async def insert_sample_data():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check if sample data already exists
    cursor.execute("SELECT COUNT(*) FROM alerts")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Insert sample alerts
    sample_alerts = [
        ('Malware', 'High', 'Malware detected on endpoint', 'Endpoint Security', '192.168.1.15', 'Open'),
        ('Unauthorized Access', 'Medium', 'Suspicious login from unknown location', 'Auth System', '10.0.0.5', 'Open'),
        ('SSL Certificate', 'Medium', 'SSL certificate expiring soon', 'Web Server', '192.168.1.10', 'Closed'),
        ('Data Leak', 'High', 'Potential data exfiltration detected', 'DLP System', '192.168.1.20', 'Open'),
        ('Phishing', 'High', 'Phishing email detected', 'Email Security', '172.16.0.1', 'Closed'),
        ('Vulnerability', 'Medium', 'Critical vulnerability found', 'Vulnerability Scanner', '192.168.1.12', 'Open'),
        ('Anomaly', 'Low', 'Unusual network traffic pattern', 'Network Monitor', '10.0.0.8', 'Closed'),
        ('Intrusion', 'High', 'Potential intrusion attempt', 'IDS/IPS', '172.16.0.5', 'Open'),
    ]
    
    for alert in sample_alerts:
        cursor.execute('''
            INSERT INTO alerts (user_id, alert_type, severity, description, source_system, source_ip, status)
            VALUES (NULL, ?, ?, ?, ?, ?, ?)
        ''', alert)
    
    conn.commit()
    conn.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}