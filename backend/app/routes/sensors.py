from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta
import httpx
import os

from app.db.database import get_db
from app.models.models import SensorData, SensorType
from app.models.schemas import SensorDataCreate, SensorDataResponse
from app.services.alert_service import alert_service
import random
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Arduino configuration
ARDUINO_ENDPOINT = os.getenv("ARDUINO_ENDPOINT", "http://10.54.156.112/")
ARDUINO_TIMEOUT = float(os.getenv("ARDUINO_TIMEOUT", "5"))

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
    """Get current readings from all sensors with automatic alert monitoring"""
    try:
        # For now, return mock data
        # In production, fetch from database or IoT gateway
        mock_data = generate_mock_sensor_data()
        
        result = {}
        alerts_triggered = []
        
        for sensor_type, data in mock_data.items():
            value = data["value"]
            
            # Check threshold and send alerts if needed
            if sensor_type in ["gas", "temperature", "vibration", "ultrasonic"]:
                breach_check = alert_service.check_threshold(sensor_type, value)
                
                if breach_check['breached']:
                    # Update status based on breach level
                    data["status"] = breach_check['level']
                    
                    # Send alerts (email and SMS)
                    alert_result = alert_service.send_alert(sensor_type, data)
                    if alert_result['alert_sent']:
                        alerts_triggered.append({
                            "sensor_type": sensor_type,
                            "level": alert_result['level'],
                            "email_sent": alert_result['email_sent'],
                            "sms_sent": alert_result['sms_sent']
                        })
                        logger.info(f"Alert triggered for {sensor_type}: {alert_result}")
            
            result[sensor_type] = {
                **data,
                "timestamp": datetime.utcnow().isoformat(),
                "trend": random.choice(["up", "down", "stable"])
            }
        
        response = {"sensors": result}
        if alerts_triggered:
            response["alerts_triggered"] = alerts_triggered
        
        return response
    except Exception as e:
        logger.error(f"Error in get_all_sensors: {e}")
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

@router.post("/test/alert/email")
async def test_email_alert():
    """Test email alert configuration"""
    try:
        result = alert_service.test_email()
        if result:
            return {
                "success": True,
                "message": "Test email sent successfully! Check your inbox.",
                "email_to": alert_service.alert_email_to
            }
        else:
            return {
                "success": False,
                "message": "Failed to send test email. Check server logs for details.",
                "email_to": alert_service.alert_email_to
            }
    except Exception as e:
        logger.error(f"Email test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/alert/sms")
async def test_sms_alert():
    """Test SMS alert configuration"""
    try:
        result = alert_service.test_sms()
        if result:
            return {
                "success": True,
                "message": "Test SMS sent successfully! Check your phone.",
                "phone_to": alert_service.alert_phone_number
            }
        else:
            return {
                "success": False,
                "message": "Failed to send test SMS. Check server logs for details.",
                "phone_to": alert_service.alert_phone_number
            }
    except Exception as e:
        logger.error(f"SMS test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alert/manual")
async def trigger_manual_alert(
    sensor_type: str = Query(..., description="Sensor type: gas, temperature, vibration, ultrasonic"),
    value: float = Query(..., description="Sensor value that breached threshold")
):
    """Manually trigger an alert for testing purposes"""
    try:
        if sensor_type not in ["gas", "temperature", "vibration", "ultrasonic"]:
            raise HTTPException(status_code=400, detail="Invalid sensor type")
        
        # Get unit for sensor type
        units = {
            "gas": "ppm",
            "temperature": "°C",
            "vibration": "g",
            "ultrasonic": "cm"
        }
        
        sensor_data = {
            "value": value,
            "unit": units.get(sensor_type, "")
        }
        
        # Trigger alert
        result = alert_service.send_alert(sensor_type, sensor_data)
        
        return {
            "success": result['alert_sent'],
            "sensor_type": sensor_type,
            "value": value,
            "level": result['level'],
            "email_sent": result.get('email_sent', False),
            "sms_sent": result.get('sms_sent', False),
            "message": result['message']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manual alert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alert/config")
async def get_alert_config():
    """Get current alert service configuration"""
    try:
        return {
            "email": {
                "configured": bool(alert_service.smtp_user and alert_service.smtp_password),
                "smtp_host": alert_service.smtp_host,
                "smtp_port": alert_service.smtp_port,
                "from": alert_service.alert_email_from,
                "to": alert_service.alert_email_to
            },
            "sms": {
                "configured": bool(alert_service.twilio_client),
                "provider": alert_service.sms_provider,
                "from": alert_service.twilio_phone_number,
                "to": alert_service.alert_phone_number
            },
            "thresholds": alert_service.thresholds
        }
    except Exception as e:
        logger.error(f"Get config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/live/arduino")
async def get_live_arduino_data():
    """
    Get live sensor data directly from Arduino ESP8266
    Includes automatic threshold checking and alert triggering
    """
    try:
        # Fetch data from Arduino
        async with httpx.AsyncClient(timeout=ARDUINO_TIMEOUT) as client:
            response = await client.get(ARDUINO_ENDPOINT)
            response.raise_for_status()
            
            # Parse HTML response (same logic as arduino_sensors.py)
            import re
            html = response.text
            
            # Extract sensor values
            temp_match = re.search(r'<b>Temperature:</b>\s*([\d.]+)\s*°C', html)
            temperature = float(temp_match.group(1)) if temp_match else 0.0
            
            hum_match = re.search(r'<b>Humidity:</b>\s*([\d.]+)\s*%', html)
            humidity = float(hum_match.group(1)) if hum_match else 0.0
            
            rfid_match = re.search(r'<b>RFID Tag:</b>\s*([^<]+)', html)
            rfid_tag = rfid_match.group(1).strip() if rfid_match else "No Tag Detected"
            
            dist_match = re.search(r'<b>Distance:</b>\s*([\d.]+)\s*cm', html)
            distance = float(dist_match.group(1)) if dist_match else 0.0
            
            air_match = re.search(r'<b>Air Quality \(MQ-135\):</b>\s*([\d]+)', html)
            gas_level = int(air_match.group(1)) if air_match else 0
            
            # Build sensor data with alerts
            sensors = {}
            alerts_triggered = []
            
            # Gas sensor (MQ-135)
            gas_data = {"value": gas_level, "unit": "ppm", "status": "normal"}
            gas_breach = alert_service.check_threshold("gas", gas_level)
            if gas_breach['breached']:
                gas_data["status"] = gas_breach['level']
                alert_result = alert_service.send_alert("gas", gas_data)
                if alert_result['alert_sent']:
                    alerts_triggered.append({
                        "sensor": "gas",
                        "level": alert_result['level'],
                        "value": gas_level,
                        "email": alert_result['email_sent'],
                        "sms": alert_result['sms_sent']
                    })
            sensors["gas"] = gas_data
            
            # Temperature sensor (DHT11)
            temp_data = {"value": temperature, "unit": "°C", "status": "normal"}
            temp_breach = alert_service.check_threshold("temperature", temperature)
            if temp_breach['breached']:
                temp_data["status"] = temp_breach['level']
                alert_result = alert_service.send_alert("temperature", temp_data)
                if alert_result['alert_sent']:
                    alerts_triggered.append({
                        "sensor": "temperature",
                        "level": alert_result['level'],
                        "value": temperature,
                        "email": alert_result['email_sent'],
                        "sms": alert_result['sms_sent']
                    })
            sensors["temperature"] = temp_data
            
            # Humidity sensor (DHT11)
            sensors["humidity"] = {"value": humidity, "unit": "%", "status": "normal"}
            
            # Distance sensor (Ultrasonic)
            dist_data = {"value": distance, "unit": "cm", "status": "normal"}
            # Note: ultrasonic maps to proximity threshold
            prox_breach = alert_service.check_threshold("ultrasonic", distance)
            if prox_breach['breached']:
                dist_data["status"] = prox_breach['level']
                alert_result = alert_service.send_alert("ultrasonic", dist_data)
                if alert_result['alert_sent']:
                    alerts_triggered.append({
                        "sensor": "ultrasonic",
                        "level": alert_result['level'],
                        "value": distance,
                        "email": alert_result['email_sent'],
                        "sms": alert_result['sms_sent']
                    })
            sensors["ultrasonic"] = dist_data
            
            # RFID
            sensors["rfid"] = {"value": rfid_tag, "unit": "tag", "status": "active" if rfid_tag != "No Tag Detected" else "idle"}
            
            response_data = {
                "status": "connected",
                "source": "arduino_esp8266",
                "endpoint": ARDUINO_ENDPOINT,
                "sensors": sensors,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if alerts_triggered:
                response_data["alerts_triggered"] = alerts_triggered
                logger.warning(f"Arduino alerts triggered: {len(alerts_triggered)}")
            
            return response_data
            
    except httpx.TimeoutException:
        logger.error(f"Arduino timeout at {ARDUINO_ENDPOINT}")
        raise HTTPException(
            status_code=504,
            detail=f"Arduino connection timeout - device offline at {ARDUINO_ENDPOINT}"
        )
    except Exception as e:
        logger.error(f"Arduino fetch error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Arduino data: {str(e)}"
        )
