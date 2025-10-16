from fastapi import APIRouter, HTTPException
import httpx
import logging
from typing import Dict, Any
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

router = APIRouter()

# Arduino timeout configuration
ARDUINO_TIMEOUT = 5.0  # 5 seconds timeout

def get_arduino_ip():
    """Get Arduino IP from environment variable (reloads on each call)"""
    load_dotenv(override=True)  # Reload .env file
    return os.getenv("ARDUINO_IP", "192.168.1.100")

def get_arduino_endpoint():
    """Get Arduino endpoint URL"""
    return f"http://{get_arduino_ip()}/api/sensors"

@router.get("/arduino/sensors")
async def get_arduino_sensors():
    """
    Fetch live sensor data from Arduino/ESP8266 endpoint
    """
    arduino_ip = get_arduino_ip()
    arduino_endpoint = get_arduino_endpoint()
    
    try:
        async with httpx.AsyncClient(timeout=ARDUINO_TIMEOUT) as client:
            response = await client.get(arduino_endpoint)
            response.raise_for_status()
            
            # Parse Arduino response
            data = response.json()
            
            logger.info(f"Successfully fetched Arduino sensor data from {arduino_endpoint}")
            
            return {
                "status": "connected",
                "endpoint": arduino_endpoint,
                "data": data,
                "timestamp": response.headers.get("Date", "")
            }
            
    except httpx.TimeoutException:
        logger.error(f"Arduino connection timeout - cannot reach {arduino_endpoint}")
        raise HTTPException(
            status_code=504,
            detail=f"Arduino connection timeout - device may be offline at {arduino_ip}"
        )
    except httpx.HTTPError as e:
        logger.error(f"Arduino HTTP error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to Arduino at {arduino_ip}: {str(e)}"
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
    Check Arduino/ESP8266 connection status
    """
    arduino_ip = get_arduino_ip()
    arduino_endpoint = get_arduino_endpoint()
    
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            # Check health endpoint
            health_endpoint = f"http://{arduino_ip}/api/health"
            response = await client.get(health_endpoint)
            response.raise_for_status()
            
            return {
                "status": "connected",
                "endpoint": arduino_endpoint,
                "ip": arduino_ip,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "health": response.json()
            }
            
    except Exception as e:
        return {
            "status": "disconnected",
            "endpoint": arduino_endpoint,
            "ip": arduino_ip,
            "error": str(e)
        }

@router.post("/arduino/config")
async def update_arduino_config(config: Dict[str, Any]):
    """
    Update Arduino endpoint configuration by updating the .env file
    """
    if "ip" in config:
        new_ip = config["ip"]
        
        # Update .env file
        env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        
        try:
            # Read current .env file
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Update ARDUINO_IP line
            with open(env_path, 'w') as f:
                for line in lines:
                    if line.startswith('ARDUINO_IP='):
                        f.write(f'ARDUINO_IP={new_ip}\n')
                    else:
                        f.write(line)
            
            logger.info(f"Arduino IP updated to: {new_ip}")
            
            return {
                "message": "Configuration updated successfully",
                "ip": new_ip,
                "endpoint": f"http://{new_ip}/api/sensors"
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update configuration: {str(e)}"
            )
    
    return {
        "message": "No changes made",
        "ip": get_arduino_ip(),
        "endpoint": get_arduino_endpoint()
    }
