from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.models import SensorData, SensorType
from app.models.schemas import SensorDataCreate, SensorDataResponse
import random

router = APIRouter()

# Mock data generator for demonstration
def generate_mock_sensor_data():
    """Generate mock sensor data for testing"""
    return {
        "gas": {"value": random.uniform(0, 120), "unit": "ppm", "status": "normal"},
        "temperature": {"value": random.uniform(20, 50), "unit": "°C", "status": "normal"},
        "vibration": {"value": random.uniform(0, 12), "unit": "g", "status": "normal"},
        "ultrasonic": {"value": random.uniform(10, 100), "unit": "cm", "status": "normal"},
        "environmental": {"value": random.uniform(50, 200), "unit": "AQI", "status": "normal"},
        "rfid": {"value": random.randint(5, 15), "unit": "workers", "status": "normal"}
    }

@router.get("/")
async def get_all_sensors(db: AsyncSession = Depends(get_db)):
    """Get current readings from all sensors"""
    try:
        # For now, return mock data
        # In production, fetch from database or IoT gateway
        mock_data = generate_mock_sensor_data()
        
        result = {}
        for sensor_type, data in mock_data.items():
            # Determine status based on thresholds
            value = data["value"]
            if sensor_type == "gas" and value >= 100:
                data["status"] = "danger"
            elif sensor_type == "gas" and value >= 50:
                data["status"] = "warning"
            elif sensor_type == "temperature" and value >= 45:
                data["status"] = "danger"
            elif sensor_type == "temperature" and value >= 35:
                data["status"] = "warning"
            
            result[sensor_type] = {
                **data,
                "timestamp": datetime.utcnow().isoformat(),
                "trend": random.choice(["up", "down", "stable"])
            }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{sensor_type}")
async def get_sensor_data(
    sensor_type: str,
    db: AsyncSession = Depends(get_db)
):
    """Get current reading from a specific sensor"""
    try:
        # Validate sensor type
        if sensor_type not in ["gas", "temperature", "vibration", "ultrasonic", "environmental", "rfid"]:
            raise HTTPException(status_code=400, detail="Invalid sensor type")
        
        mock_data = generate_mock_sensor_data()
        sensor_data = mock_data.get(sensor_type, {})
        
        return {
            "sensor_type": sensor_type,
            **sensor_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_sensor_history(
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """Get sensor history for all sensors"""
    try:
        result = {}
        sensor_types = ["gas", "temperature", "vibration", "ultrasonic", "environmental"]
        
        for sensor_type in sensor_types:
            # Generate mock historical data
            history = []
            for i in range(20):
                timestamp = datetime.utcnow() - timedelta(minutes=i * 3)
                history.append({
                    "timestamp": timestamp.strftime("%H:%M"),
                    "value": random.uniform(20, 100)
                })
            result[sensor_type] = list(reversed(history))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{sensor_type}/history")
async def get_specific_sensor_history(
    sensor_type: str,
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """Get historical data for a specific sensor"""
    try:
        # Generate mock historical data
        history = []
        for i in range(50):
            timestamp = datetime.utcnow() - timedelta(minutes=i * 3)
            value = random.uniform(20, 100)
            
            history.append({
                "timestamp": timestamp.isoformat(),
                "value": value,
                "status": "normal"
            })
        
        return {
            "sensor_type": sensor_type,
            "data": list(reversed(history))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_sensor_data(
    sensor_data: SensorDataCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new sensor data entry (typically from ESP32 or IoT gateway)"""
    try:
        db_sensor_data = SensorData(
            sensor_type=sensor_data.sensor_type,
            value=sensor_data.value,
            unit=sensor_data.unit,
            status=sensor_data.status,
            metadata=sensor_data.metadata
        )
        
        db.add(db_sensor_data)
        await db.commit()
        await db.refresh(db_sensor_data)
        
        return {"message": "Sensor data created successfully", "id": db_sensor_data.id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rfid/logs")
async def get_rfid_logs(
    days: int = Query(default=7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """Get RFID access logs"""
    try:
        # Generate mock RFID logs
        logs = []
        for i in range(10):
            logs.append({
                "id": i + 1,
                "workerId": f"W{1000 + i}",
                "workerName": f"Worker {i + 1}",
                "action": random.choice(["entry", "exit"]),
                "location": random.choice(["Gate A", "Gate B", "Workshop", "Storage"]),
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat()
            })
        
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """Get sensor statistics"""
    try:
        return {
            "totalWorkers": random.randint(10, 20),
            "activeAlerts": random.randint(0, 5),
            "systemUptime": round(random.uniform(95, 99.9), 1),
            "dataPoints": random.randint(10000, 50000)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
