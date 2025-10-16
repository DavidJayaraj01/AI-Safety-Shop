#!/usr/bin/env python3
"""
FastAPI Alert Server for PPE Safety Monitoring
Receives and logs PPE violation alerts from the camera detection system
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
import os

app = FastAPI(title="PPE Safety Alert Server", version="1.0.0")

class PPEAlert(BaseModel):
    timestamp: str
    person_id: int
    alert_type: str
    missing_ppe: list
    severity: str
    location: str

# Store alerts in memory and optionally log to file
alerts_log = []
LOG_FILE = "ppe_alerts.json"

@app.post("/alert")
async def receive_alert(alert: PPEAlert):
    """Receive PPE violation alert"""
    try:
        # Add to memory
        alerts_log.append(alert.dict())
        
        # Log to console
        print(f"\n🚨 PPE VIOLATION ALERT:")
        print(f"   Time: {alert.timestamp}")
        print(f"   Person ID: {alert.person_id}")
        print(f"   Location: {alert.location}")
        print(f"   Missing PPE: {', '.join(alert.missing_ppe).upper()}")
        print(f"   Severity: {alert.severity}")
        print("-" * 50)
        
        # Save to file
        with open(LOG_FILE, 'w') as f:
            json.dump(alerts_log, f, indent=2)
        
        return {
            "status": "success",
            "message": "Alert received and logged",
            "alert_id": len(alerts_log)
        }
    
    except Exception as e:
        print(f"Error processing alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts")
async def get_alerts():
    """Get all stored alerts"""
    return {
        "total_alerts": len(alerts_log),
        "alerts": alerts_log
    }

@app.get("/alerts/recent")
async def get_recent_alerts(limit: int = 10):
    """Get recent alerts"""
    return {
        "recent_alerts": alerts_log[-limit:] if alerts_log else []
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_alerts": len(alerts_log)
    }

@app.delete("/alerts")
async def clear_alerts():
    """Clear all alerts"""
    global alerts_log
    count = len(alerts_log)
    alerts_log.clear()
    
    # Clear log file
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    
    return {
        "status": "success",
        "message": f"Cleared {count} alerts"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting PPE Alert Server...")
    print("📊 Dashboard: http://localhost:8000/docs")
    print("📝 Alerts endpoint: http://localhost:8000/alert")
    uvicorn.run(app, host="0.0.0.0", port=8000)