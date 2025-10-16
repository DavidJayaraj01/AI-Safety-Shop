from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.models.models import Sensor, SensorReading
from pydantic import BaseModel

router = APIRouter()

# Pydantic schemas
class SensorResponse(BaseModel):
    id: str
    name: str
    type: str
    location: str
    status: str
    warning_threshold: float
    critical_threshold: float
    
    class Config:
        from_attributes = True

class SensorReadingResponse(BaseModel):
    id: str
    sensor_id: str
    value: float
    unit: str
    status: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None

@router.get("", response_model=ApiResponse)
async def get_all_sensors(db: Session = Depends(get_db)):
    """Get all sensors"""
    try:
        sensors = db.query(Sensor).all()
        return ApiResponse(success=True, data=sensors)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@router.get("/{sensor_id}", response_model=ApiResponse)
async def get_sensor(sensor_id: str, db: Session = Depends(get_db)):
    """Get sensor by ID"""
    try:
        sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensor not found")
        return ApiResponse(success=True, data=sensor)
    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@router.get("/{sensor_id}/readings", response_model=ApiResponse)
async def get_sensor_readings(
    sensor_id: str,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get readings for a specific sensor"""
    try:
        readings = (
            db.query(SensorReading)
            .filter(SensorReading.sensor_id == sensor_id)
            .order_by(SensorReading.timestamp.desc())
            .limit(limit)
            .all()
        )
        return ApiResponse(success=True, data=readings)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@router.get("/readings/latest", response_model=ApiResponse)
async def get_latest_readings(db: Session = Depends(get_db)):
    """Get latest reading for each sensor"""
    try:
        # This is a simplified version - in production, use a proper subquery
        sensors = db.query(Sensor).all()
        latest_readings = []
        
        for sensor in sensors:
            reading = (
                db.query(SensorReading)
                .filter(SensorReading.sensor_id == sensor.id)
                .order_by(SensorReading.timestamp.desc())
                .first()
            )
            if reading:
                latest_readings.append(reading)
        
        return ApiResponse(success=True, data=latest_readings)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))
