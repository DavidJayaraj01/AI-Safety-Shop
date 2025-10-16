from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Any

from app.core.database import get_db
from app.models.models import Worker

router = APIRouter()

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

@router.get("", response_model=ApiResponse)
async def get_all_workers(db: Session = Depends(get_db)):
    """Get all workers"""
    try:
        workers = db.query(Worker).all()
        return ApiResponse(success=True, data=workers)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@router.get("/active", response_model=ApiResponse)
async def get_active_workers(db: Session = Depends(get_db)):
    """Get active workers"""
    try:
        workers = db.query(Worker).filter(Worker.status == "active").all()
        return ApiResponse(success=True, data=workers)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@router.get("/{worker_id}", response_model=ApiResponse)
async def get_worker(worker_id: str, db: Session = Depends(get_db)):
    """Get worker by ID"""
    try:
        worker = db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            return ApiResponse(success=False, error="Worker not found")
        return ApiResponse(success=True, data=worker)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))
