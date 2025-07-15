# Continue from main.py - Authentication and User Management Endpoints

# Authentication endpoints
@app.post("/auth/register")
async def register(user: UserRegister):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and create user
    password_hash = hash_password(user.password)
    cursor.execute('''
        INSERT INTO users (name, email, password_hash)
        VALUES (?, ?, ?)
    ''', (user.name, user.email, password_hash))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Create access token
    access_token = create_access_token({"user_id": user_id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": user.name,
            "email": user.email,
            "avatar": None
        }
    }

@app.post("/auth/login")
async def login(user: UserLogin):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Find user
    cursor.execute("SELECT id, name, email, password_hash, avatar FROM users WHERE email = ?", (user.email,))
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data or not verify_password(user.password, user_data[3]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token = create_access_token({"user_id": user_data[0]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_data[0],
            "name": user_data[1],
            "email": user_data[2],
            "avatar": user_data[4]
        }
    }

@app.get("/auth/me")
async def get_current_user_profile(current_user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, email, avatar FROM users WHERE id = ?", (current_user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user_data[0],
        "name": user_data[1],
        "email": user_data[2],
        "avatar": user_data[3]
    }

@app.put("/auth/profile")
async def update_profile(profile: ProfileUpdate, current_user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users SET name = ?, avatar = ? WHERE id = ?
    ''', (profile.name, profile.avatar, current_user_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    conn.commit()
    
    # Return updated user data
    cursor.execute("SELECT id, name, email, avatar FROM users WHERE id = ?", (current_user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    return {
        "id": user_data[0],
        "name": user_data[1],
        "email": user_data[2],
        "avatar": user_data[3]
    }

@app.put("/auth/password")
async def change_password(password_change: PasswordChange, current_user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    password_hash = hash_password(password_change.new_password)
    cursor.execute('''
        UPDATE users SET password_hash = ? WHERE id = ?
    ''', (password_hash, current_user_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Password updated successfully"}

@app.post("/auth/upload-avatar")
async def upload_avatar(file: UploadFile = File(...), current_user_id: int = Depends(get_current_user)):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file content
    content = await file.read()
    
    # Convert to base64
    avatar_data = base64.b64encode(content).decode('utf-8')
    avatar_url = f"data:{file.content_type};base64,{avatar_data}"
    
    # Update user avatar
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users SET avatar = ? WHERE id = ?
    ''', (avatar_url, current_user_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    conn.commit()
    conn.close()
    
    return {"avatar_url": avatar_url}

# OTP endpoints (for enhanced security)
@app.post("/auth/send-otp")
async def send_otp(email: EmailStr):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    # Store OTP
    cursor.execute('''
        INSERT INTO otp_codes (email, otp_code, expires_at)
        VALUES (?, ?, ?)
    ''', (email, otp_code, expires_at))
    
    conn.commit()
    conn.close()
    
    # In production, send OTP via email/SMS
    # For demo purposes, we'll return it (remove in production)
    return {"message": "OTP sent successfully", "otp": otp_code}

@app.post("/auth/verify-otp")
async def verify_otp(email: EmailStr, otp: str):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Find valid OTP
    cursor.execute('''
        SELECT id FROM otp_codes 
        WHERE email = ? AND otp_code = ? AND expires_at > ? AND used = FALSE
    ''', (email, otp, datetime.utcnow()))
    
    otp_record = cursor.fetchone()
    if not otp_record:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    # Mark OTP as used
    cursor.execute("UPDATE otp_codes SET used = TRUE WHERE id = ?", (otp_record[0],))
    
    # Get user data
    cursor.execute("SELECT id, name, email, avatar FROM users WHERE email = ?", (email,))
    user_data = cursor.fetchone()
    
    conn.commit()
    conn.close()
    
    # Create access token
    access_token = create_access_token({"user_id": user_data[0]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_data[0],
            "name": user_data[1],
            "email": user_data[2],
            "avatar": user_data[3]
        }
    }