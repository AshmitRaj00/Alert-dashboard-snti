# Continue from main.py - Alerts Management and Dashboard Endpoints

# Alerts endpoints
@app.get("/alerts/stats")
async def get_alert_stats(current_user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Get total alerts
    cursor.execute("SELECT COUNT(*) FROM alerts")
    total_alerts = cursor.fetchone()[0]
    
    # Get critical alerts
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE severity = 'High'")
    critical_alerts = cursor.fetchone()[0]
    
    # Get open alerts
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE status = 'Open'")
    open_alerts = cursor.fetchone()[0]
    
    # Get closed alerts
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE status = 'Closed'")
    closed_alerts = cursor.fetchone()[0]
    
    # Get alerts by type
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE alert_type LIKE '%SSL%'")
    ssl_alerts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE alert_type LIKE '%Data%' OR alert_type LIKE '%Leak%'")
    data_leaks = cursor.fetchone()[0]
    
    other_alerts = total_alerts - ssl_alerts - data_leaks
    
    conn.close()
    
    return {
        "total_alerts": total_alerts,
        "critical_alerts": critical_alerts,
        "open_alerts": open_alerts,
        "closed_alerts": closed_alerts,
        "ssl_alerts": ssl_alerts,
        "data_leaks": data_leaks,
        "other_alerts": other_alerts
    }

@app.get("/alerts/recent")
async def get_recent_alerts(limit: int = 10, current_user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, alert_type, severity, description, source_system, source_ip, 
               status, created_at, resolved_at
        FROM alerts
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    alerts = []
    for row in cursor.fetchall():
        alerts.append({
            "id": row[0],
            "alert_type": row[1],
            "severity": row[2],
            "description": row[3],
            "source_system": row[4],
            "source_ip": row[5],
            "status": row[6],
            "created_at": row[7],
            "resolved_at": row[8]
        })
    
    conn.close()
    return alerts

@app.get("/alerts/top-sources")
async def get_top_alert_sources(limit: int = 10, current_user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COALESCE(source_system, source_ip, 'Unknown') as source,
            COUNT(*) as alert_count,
            SUM(CASE WHEN severity = 'High' THEN 1 ELSE 0 END) as critical_count
        FROM alerts
        GROUP BY source
        ORDER BY alert_count DESC
        LIMIT ?
    ''', (limit,))
    
    sources = []
    for row in cursor.fetchall():
        sources.append({
            "source": row[0],
            "alert_count": row[1],
            "critical_count": row[2]
        })
    
    conn.close()
    return sources

@app.get("/alerts/trends")
async def get_alert_trends(days: int = 7, current_user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Get alerts for the last N days
    cursor.execute('''
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as count
        FROM alerts
        WHERE created_at >= datetime('now', '-{} days')
        GROUP BY DATE(created_at)
        ORDER BY date
    '''.format(days))
    
    trends = []
    for row in cursor.fetchall():
        trends.append({
            "date": row[0],
            "count": row[1]
        })
    
    conn.close()
    return trends

@app.get("/alerts")
async def get_alerts(
    skip: int = 0,
    limit: int = 50,
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user_id: int = Depends(get_current_user)
):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Build query with filters
    query = '''
        SELECT id, alert_type, severity, description, source_system, source_ip, 
               status, created_at, resolved_at
        FROM alerts
        WHERE 1=1
    '''
    params = []
    
    if alert_type:
        query += " AND alert_type = ?"
        params.append(alert_type)
    
    if severity:
        query += " AND severity = ?"
        params.append(severity)
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    if search:
        query += " AND (description LIKE ? OR alert_type LIKE ? OR source_system LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    cursor.execute(query, params)
    
    alerts = []
    for row in cursor.fetchall():
        alerts.append({
            "id": row[0],
            "alert_type": row[1],
            "severity": row[2],
            "description": row[3],
            "source_system": row[4],
            "source_ip": row[5],
            "status": row[6],
            "created_at": row[7],
            "resolved_at": row[8]
        })
    
    conn.close()
    return alerts

@app.post("/alerts")
async def create_alert(alert: AlertCreate, current_user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO alerts (user_id, alert_type, severity, description, source_system, source_ip)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (current_user_id, alert.alert_type, alert.severity, alert.description, 
          alert.source_system, alert.source_ip))
    
    alert_id = cursor.lastrowid
    conn.commit()
    
    # Get the created alert
    cursor.execute('''
        SELECT id, alert_type, severity, description, source_system, source_ip, 
               status, created_at, resolved_at
        FROM alerts WHERE id = ?
    ''', (alert_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return {
        "id": row[0],
        "alert_type": row[1],
        "severity": row[2],
        "description": row[3],
        "source_system": row[4],
        "source_ip": row[5],
        "status": row[6],
        "created_at": row[7],
        "resolved_at": row[8]
    }

@app.put("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int, current_user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE alerts SET status = 'Closed', resolved_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (alert_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Alert not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Alert resolved successfully"}

@app.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: int, current_user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Alert not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Alert deleted successfully"}

# Dashboard summary endpoint
@app.get("/dashboard/summary")
async def get_dashboard_summary(current_user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Get comprehensive dashboard data
    stats = await get_alert_stats(current_user_id)
    recent_alerts = await get_recent_alerts(5, current_user_id)
    top_sources = await get_top_alert_sources(5, current_user_id)
    trends = await get_alert_trends(7, current_user_id)
    
    # Calculate average turnaround time
    cursor.execute('''
        SELECT AVG(
            CASE 
                WHEN resolved_at IS NOT NULL 
                THEN (julianday(resolved_at) - julianday(created_at)) * 24 * 60
                ELSE NULL 
            END
        ) as avg_turnaround_minutes
        FROM alerts
        WHERE status = 'Closed'
    ''')
    
    avg_turnaround = cursor.fetchone()[0]
    turnaround_hours = int(avg_turnaround // 60) if avg_turnaround else 0
    turnaround_minutes = int(avg_turnaround % 60) if avg_turnaround else 0
    
    conn.close()
    
    return {
        "stats": stats,
        "recent_alerts": recent_alerts,
        "top_sources": top_sources,
        "trends": trends,
        "turnaround_time": {
            "hours": turnaround_hours,
            "minutes": turnaround_minutes,
            "total_minutes": int(avg_turnaround) if avg_turnaround else 0
        }
    }

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)