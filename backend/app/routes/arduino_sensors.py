from fastapi import APIRouter, HTTPException
import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter()

# Arduino endpoint configuration
ARDUINO_ENDPOINT = "http://10.115.11.112/"
ARDUINO_TIMEOUT = 5.0  # 5 seconds timeout

@router.get("/arduino/sensors")
async def get_arduino_sensors():
    """
    Fetch live sensor data from Arduino endpoint
    """
    try:
        async with httpx.AsyncClient(timeout=ARDUINO_TIMEOUT) as client:
            response = await client.get(ARDUINO_ENDPOINT)
            response.raise_for_status()
            
            # Parse Arduino response
            # Expected format: { "temperature": 25.5, "humidity": 60, "smoke": 150, "distance": 30, "rfid": "ABC123" }
            data = response.json()
            
            logger.info(f"Successfully fetched Arduino sensor data: {data}")
            
            return {
                "status": "connected",
                "endpoint": ARDUINO_ENDPOINT,
                "data": data,
                "timestamp": response.headers.get("Date", "")
            }
            
    except httpx.TimeoutException:
        logger.error("Arduino connection timeout")
        raise HTTPException(
            status_code=504,
            detail="Arduino connection timeout - device may be offline"
        )
    except httpx.HTTPError as e:
        logger.error(f"Arduino HTTP error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to Arduino: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching Arduino data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/arduino/status")
async def get_arduino_status():
    """
    Check Arduino connection status
    """
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(ARDUINO_ENDPOINT)
            response.raise_for_status()
            
            return {
                "status": "connected",
                "endpoint": ARDUINO_ENDPOINT,
                "response_time_ms": response.elapsed.total_seconds() * 1000
            }
            
    except Exception as e:
        return {
            "status": "disconnected",
            "endpoint": ARDUINO_ENDPOINT,
            "error": str(e)
        }

@router.post("/arduino/config")
async def update_arduino_config(config: Dict[str, Any]):
    """
    Update Arduino endpoint configuration
    """
    global ARDUINO_ENDPOINT
    
    if "endpoint" in config:
        ARDUINO_ENDPOINT = config["endpoint"]
        logger.info(f"Arduino endpoint updated to: {ARDUINO_ENDPOINT}")
    
    return {
        "message": "Configuration updated successfully",
        "endpoint": ARDUINO_ENDPOINT
    }
