from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timedelta
import random

from app.db.database import get_db
from app.models.schemas import AlertResponse, AlertCreate, AlertSeverity

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_all_alerts(db: AsyncSession = Depends(get_db)):
    """Get all alerts"""
    # Mock alerts
    alerts = []
    for i in range(5):
        alerts.append({
            "id": i + 1,
            "title": f"Alert {i + 1}",
            "message": f"Sample alert message {i + 1}",
            "severity": random.choice(["info", "warning", "danger"]),
            "status": "active",
            "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
            "sensor": random.choice(["gas", "temperature", "vibration"])
        })
    return alerts

@router.get("/active", response_model=List[dict])
async def get_active_alerts(db: AsyncSession = Depends(get_db)):
    """Get active alerts only"""
    alerts = []
    severities = ["warning", "danger", "info"]
    for i in range(3):
        alerts.append({
            "id": i + 1,
            "title": f"{severities[i].upper()} Alert",
            "message": f"Active {severities[i]} condition detected",
            "severity": severities[i],
            "status": "active",
            "timestamp": (datetime.utcnow() - timedelta(minutes=i * 15)).isoformat(),
            "sensor": random.choice(["gas", "temperature", "vibration"])
        })
    return alerts

@router.get("/history")
async def get_alert_history(
    days: int = Query(default=7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """Get alert history"""
    alerts = []
    for i in range(20):
        alerts.append({
            "id": i + 1,
            "title": f"Historical Alert {i + 1}",
            "message": f"Past alert message",
            "severity": random.choice(["info", "warning", "danger"]),
            "status": random.choice(["resolved", "acknowledged"]),
            "timestamp": (datetime.utcnow() - timedelta(days=i // 3, hours=i)).isoformat()
        })
    return alerts

@router.put("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Acknowledge an alert"""
    return {
        "message": f"Alert {alert_id} acknowledged successfully",
        "acknowledged_at": datetime.utcnow().isoformat()
    }

@router.post("/", response_model=dict)
async def create_alert(alert: AlertCreate, db: AsyncSession = Depends(get_db)):
    """Create a new alert"""
    return {
        "message": "Alert created successfully",
        "id": random.randint(1000, 9999),
        "timestamp": datetime.utcnow().isoformat()
    }
