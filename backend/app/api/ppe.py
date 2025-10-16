from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Any

from app.core.database import get_db
from app.models.models import PPEDetection

router = APIRouter()

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

@router.get("/detections/latest", response_model=ApiResponse)
async def get_latest_detections(limit: int = 50, db: Session = Depends(get_db)):
    """Get latest PPE detections"""
    try:
        detections = (
            db.query(PPEDetection)
            .order_by(PPEDetection.timestamp.desc())
            .limit(limit)
            .all()
        )
        return ApiResponse(success=True, data=detections)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@router.get("/compliance", response_model=ApiResponse)
async def get_compliance_rate(db: Session = Depends(get_db)):
    """Get overall PPE compliance rate"""
    try:
        from sqlalchemy import func
        total = db.query(func.count(PPEDetection.id)).scalar()
        compliant = db.query(func.count(PPEDetection.id)).filter(
            PPEDetection.overall_compliance == True
        ).scalar()
        
        rate = (compliant / total * 100) if total > 0 else 100.0
        
        return ApiResponse(success=True, data={"rate": round(rate, 2)})
    except Exception as e:
        return ApiResponse(success=False, error=str(e))
