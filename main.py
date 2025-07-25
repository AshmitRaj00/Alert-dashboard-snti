from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import sqlite3
import hashlib
import jwt
import uvicorn
import base64

# JWT Configuration
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# FastAPI app
app = FastAPI(title="Alerts Dashboard API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount the frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve index.html at root
@app.get("/", response_class=FileResponse)
async def serve_frontend():
    return "frontend/index.html"


# Security
security = HTTPBearer()

# Database helper
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class AlertCreate(BaseModel):
    title: str
    message: str
    alert_type: str
    is_active: bool = True

class AlertUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    alert_type: Optional[str] = None
    is_active: Optional[bool] = None

class Alert(BaseModel):
    id: int
    title: str
    message: str
    alert_type: str
    is_active: bool
    created_at: datetime
    triggered_at: Optional[datetime] = None
    status: str

class User(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class ProfileUpdate(BaseModel):
    name: str
    avatar: Optional[str] = None

class PasswordChange(BaseModel):
    new_password: str

# Utility functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return dict(user)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes

@app.post("/auth/register", response_model=User)
async def register(user: UserRegister):
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", 
                   (user.username, user.email))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Create new user
    password_hash = hash_password(user.password)
    cursor.execute("""
        INSERT INTO users (username, email, password_hash) 
        VALUES (?, ?, ?)
    """, (user.username, user.email, password_hash))
    
    user_id = cursor.lastrowid
    conn.commit()
    
    # Get created user
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    created_user = cursor.fetchone()
    conn.close()
    
    return User(
        id=created_user["id"],
        username=created_user["username"],
        email=created_user["email"],
        created_at=created_user["created_at"]
    )

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
    db_user = cursor.fetchone()
    conn.close()
    
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=User(
            id=db_user["id"],
            username=db_user["username"],
            email=db_user["email"],
            created_at=db_user["created_at"]
        )
    )

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, created_at, avatar FROM users WHERE id = ?", (current_user["id"],))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "created_at": user[3],
        "avatar": user[4]
    }

@app.put("/auth/profile")
async def update_profile(profile: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET username = ?, avatar = ? WHERE id = ?
    ''', (profile.name, profile.avatar, current_user["id"]))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    conn.commit()
    cursor.execute("SELECT id, username, email, created_at, avatar FROM users WHERE id = ?", (current_user["id"],))
    user = cursor.fetchone()
    conn.close()
    return {
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "created_at": user[3],
        "avatar": user[4]
    }

@app.put("/auth/password")
async def change_password(password_change: PasswordChange, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    password_hash = hash_password(password_change.new_password)
    cursor.execute('''
        UPDATE users SET password_hash = ? WHERE id = ?
    ''', (password_hash, current_user["id"]))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    conn.commit()
    conn.close()
    return {"message": "Password updated successfully"}

@app.post("/auth/upload-avatar")
async def upload_avatar(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    content = await file.read()
    avatar_data = base64.b64encode(content).decode('utf-8')
    avatar_url = f"data:{file.content_type};base64,{avatar_data}"
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET avatar = ? WHERE id = ?
    ''', (avatar_url, current_user["id"]))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    conn.commit()
    conn.close()
    return {"avatar_url": avatar_url}

@app.get("/alerts/", response_model=List[Alert])
async def get_alerts(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM alerts 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """, (current_user["id"],))
    
    alerts = cursor.fetchall()
    conn.close()
    
    return [Alert(
        id=alert["id"],
        title=alert["title"],
        message=alert["message"],
        alert_type=alert["alert_type"],
        is_active=alert["is_active"],
        created_at=alert["created_at"],
        triggered_at=alert["triggered_at"],
        status=alert["status"]
    ) for alert in alerts]

@app.post("/alerts/", response_model=Alert)
async def create_alert(alert: AlertCreate, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO alerts (user_id, title, message, alert_type, is_active) 
        VALUES (?, ?, ?, ?, ?)
    """, (current_user["id"], alert.title, alert.message, alert.alert_type, alert.is_active))
    
    alert_id = cursor.lastrowid
    conn.commit()
    
    cursor.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    created_alert = cursor.fetchone()
    conn.close()
    
    return Alert(
        id=created_alert["id"],
        title=created_alert["title"],
        message=created_alert["message"],
        alert_type=created_alert["alert_type"],
        is_active=created_alert["is_active"],
        created_at=created_alert["created_at"],
        triggered_at=created_alert["triggered_at"],
        status=created_alert["status"]
    )

@app.get("/alerts/{alert_id}", response_model=Alert)
async def get_alert(alert_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM alerts WHERE id = ? AND user_id = ?", 
                   (alert_id, current_user["id"]))
    alert = cursor.fetchone()
    conn.close()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return Alert(
        id=alert["id"],
        title=alert["title"],
        message=alert["message"],
        alert_type=alert["alert_type"],
        is_active=alert["is_active"],
        created_at=alert["created_at"],
        triggered_at=alert["triggered_at"],
        status=alert["status"]
    )

@app.put("/alerts/{alert_id}", response_model=Alert)
async def update_alert(alert_id: int, alert_update: AlertUpdate, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if alert exists and belongs to user
    cursor.execute("SELECT * FROM alerts WHERE id = ? AND user_id = ?", 
                   (alert_id, current_user["id"]))
    existing_alert = cursor.fetchone()
    
    if not existing_alert:
        conn.close()
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Update fields
    update_fields = []
    update_values = []
    
    if alert_update.title is not None:
        update_fields.append("title = ?")
        update_values.append(alert_update.title)
    
    if alert_update.message is not None:
        update_fields.append("message = ?")
        update_values.append(alert_update.message)
    
    if alert_update.alert_type is not None:
        update_fields.append("alert_type = ?")
        update_values.append(alert_update.alert_type)
    
    if alert_update.is_active is not None:
        update_fields.append("is_active = ?")
        update_values.append(alert_update.is_active)
    
    if update_fields:
        update_values.append(alert_id)
        cursor.execute(f"""
            UPDATE alerts 
            SET {', '.join(update_fields)} 
            WHERE id = ?
        """, update_values)
        conn.commit()
    
    # Get updated alert
    cursor.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    updated_alert = cursor.fetchone()
    conn.close()
    
    return Alert(
        id=updated_alert["id"],
        title=updated_alert["title"],
        message=updated_alert["message"],
        alert_type=updated_alert["alert_type"],
        is_active=updated_alert["is_active"],
        created_at=updated_alert["created_at"],
        triggered_at=updated_alert["triggered_at"],
        status=updated_alert["status"]
    )

@app.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM alerts WHERE id = ? AND user_id = ?", 
                   (alert_id, current_user["id"]))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Alert not found")
    
    cursor.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Alert deleted successfully"}

@app.post("/alerts/{alert_id}/test")
async def test_alert(alert_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM alerts WHERE id = ? AND user_id = ?", 
                   (alert_id, current_user["id"]))
    alert = cursor.fetchone()
    
    if not alert:
        conn.close()
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Update triggered_at timestamp
    cursor.execute("UPDATE alerts SET triggered_at = ? WHERE id = ?", 
                   (datetime.utcnow(), alert_id))
    conn.commit()
    conn.close()
    
    return {"message": f"Test alert sent: {alert['title']}"}

@app.get("/alerts/stats")
async def get_alert_stats(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    
    # Total alerts
    cursor.execute("SELECT COUNT(*) as total FROM alerts WHERE user_id = ?", 
                   (current_user["id"],))
    total_alerts = cursor.fetchone()["total"]
    
    # Active alerts
    cursor.execute("SELECT COUNT(*) as active FROM alerts WHERE user_id = ? AND is_active = 1", 
                   (current_user["id"],))
    active_alerts = cursor.fetchone()["active"]
    
    # Triggered today
    today = datetime.now().date()
    cursor.execute("""
        SELECT COUNT(*) as triggered 
        FROM alerts 
        WHERE user_id = ? AND DATE(triggered_at) = ?
    """, (current_user["id"], today))
    triggered_today = cursor.fetchone()["triggered"]
    
    conn.close()
    
    success_rate = (active_alerts / total_alerts * 100) if total_alerts > 0 else 0
    
    return {
        "total_alerts": total_alerts,
        "active_alerts": active_alerts,
        "triggered_today": triggered_today,
        "success_rate": round(success_rate, 1)
    }

@app.get("/alerts/recent")
async def get_recent_alerts(limit: int = 10, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, message, alert_type, is_active, created_at, triggered_at, status
        FROM alerts WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (current_user["id"], limit))
    alerts = []
    for row in cursor.fetchall():
        alerts.append({
            "id": row[0],
            "title": row[1],
            "message": row[2],
            "alert_type": row[3],
            "is_active": row[4],
            "created_at": row[5],
            "triggered_at": row[6],
            "status": row[7]
        })
    conn.close()
    return alerts

@app.get("/alerts/top-sources")
async def get_top_alert_sources(limit: int = 10, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT alert_type, COUNT(*) as alert_count
        FROM alerts WHERE user_id = ?
        GROUP BY alert_type
        ORDER BY alert_count DESC
        LIMIT ?
    ''', (current_user["id"], limit))
    sources = []
    for row in cursor.fetchall():
        sources.append({
            "alert_type": row[0],
            "alert_count": row[1]
        })
    conn.close()
    return sources

@app.get("/alerts/trends")
async def get_alert_trends(days: int = 7, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM alerts
        WHERE user_id = ? AND created_at >= datetime('now', '-' || ? || ' days')
        GROUP BY DATE(created_at)
        ORDER BY date
    ''', (current_user["id"], days))
    trends = []
    for row in cursor.fetchall():
        trends.append({
            "date": row[0],
            "count": row[1]
        })
    conn.close()
    return trends

@app.get("/dashboard/summary")
async def get_dashboard_summary(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE user_id = ?", (current_user["id"],))
    total_alerts = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE user_id = ? AND status = 'Open'", (current_user["id"],))
    open_alerts = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE user_id = ? AND status = 'Closed'", (current_user["id"],))
    closed_alerts = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE user_id = ? AND alert_type LIKE '%SSL%'", (current_user["id"],))
    ssl_alerts = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE user_id = ? AND (alert_type LIKE '%Data%' OR alert_type LIKE '%Leak%')", (current_user["id"],))
    data_leaks = cursor.fetchone()[0]
    other_alerts = total_alerts - ssl_alerts - data_leaks
    conn.close()
    return {
        "total_alerts": total_alerts,
        "open_alerts": open_alerts,
        "closed_alerts": closed_alerts,
        "ssl_alerts": ssl_alerts,
        "data_leaks": data_leaks,
        "other_alerts": other_alerts
    }

# Run the server
if __name__ == "__main__":
    print("Starting Alerts Dashboard API...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)