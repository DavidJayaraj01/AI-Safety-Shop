from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Any

from app.core.database import get_db
from app.models.models import Incident

router = APIRouter()

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

@router.get("", response_model=ApiResponse)
async def get_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all incidents"""
    try:
        query = db.query(Incident)
        
        if status:
            query = query.filter(Incident.status == status)
        if severity:
            query = query.filter(Incident.severity == severity)
        
        incidents = query.order_by(Incident.timestamp.desc()).limit(limit).all()
        return ApiResponse(success=True, data=incidents)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))
