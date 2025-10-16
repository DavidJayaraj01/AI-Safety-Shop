from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Any
from sqlalchemy import func

from app.core.database import get_db
from app.models.models import Alert, Worker, Sensor, Incident, PPEDetection

router = APIRouter()

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

@router.get("/dashboard", response_model=ApiResponse)
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get dashboard analytics"""
    try:
        # Get counts
        total_alerts = db.query(func.count(Alert.id)).scalar()
        critical_alerts = db.query(func.count(Alert.id)).filter(
            Alert.severity == "critical"
        ).scalar()
        resolved_alerts = db.query(func.count(Alert.id)).filter(
            Alert.resolved == True
        ).scalar()
        active_workers = db.query(func.count(Worker.id)).filter(
            Worker.status == "active"
        ).scalar()
        active_sensors = db.query(func.count(Sensor.id)).filter(
            Sensor.status == "active"
        ).scalar()
        incidents_today = db.query(func.count(Incident.id)).scalar()
        
        # PPE compliance
        total_ppe = db.query(func.count(PPEDetection.id)).scalar()
        compliant_ppe = db.query(func.count(PPEDetection.id)).filter(
            PPEDetection.overall_compliance == True
        ).scalar()
        ppe_rate = (compliant_ppe / total_ppe * 100) if total_ppe > 0 else 100.0
        
        analytics = {
            "totalAlerts": total_alerts or 0,
            "criticalAlerts": critical_alerts or 0,
            "resolvedAlerts": resolved_alerts or 0,
            "averageResponseTime": 5.2,  # Mock data - calculate from actual data
            "ppeComplianceRate": round(ppe_rate, 1),
            "activeWorkers": active_workers or 0,
            "activeSensors": active_sensors or 0,
            "incidentsToday": incidents_today or 0,
            "timeRange": "today"
        }
        
        return ApiResponse(success=True, data=analytics)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))
