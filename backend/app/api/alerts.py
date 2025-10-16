from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional, Any
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import Alert
from app.alerts.notifier import AlertNotifier

router = APIRouter()

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

notifier = AlertNotifier()

@router.get("", response_model=ApiResponse)
async def get_alerts(
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all alerts with optional filters"""
    try:
        query = db.query(Alert)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        if resolved is not None:
            query = query.filter(Alert.resolved == resolved)
        
        alerts = query.order_by(Alert.timestamp.desc()).limit(limit).all()
        return ApiResponse(success=True, data=alerts)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@router.get("/{alert_id}", response_model=ApiResponse)
async def get_alert(alert_id: str, db: Session = Depends(get_db)):
    """Get alert by ID"""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return ApiResponse(success=False, error="Alert not found")
        return ApiResponse(success=True, data=alert)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@router.put("/{alert_id}/resolve", response_model=ApiResponse)
async def resolve_alert(
    alert_id: str,
    resolved_by: str,
    db: Session = Depends(get_db)
):
    """Mark alert as resolved"""
    try:
        from datetime import datetime
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return ApiResponse(success=False, error="Alert not found")
        
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = resolved_by
        db.commit()
        
        return ApiResponse(success=True, data=alert, message="Alert resolved")
    except Exception as e:
        db.rollback()
        return ApiResponse(success=False, error=str(e))
