from fastapi import APIRouter, HTTPException
import httpx
import logging
from typing import Dict, Any
import os
import re
from datetime import datetime
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

router = APIRouter()

# Arduino timeout configuration
ARDUINO_TIMEOUT = 5.0  # 5 seconds timeout

def get_arduino_ip():
    """Get Arduino IP from environment variable"""
    load_dotenv(override=True)  # Reload .env file
    return os.getenv("ARDUINO_ENDPOINT", "http://10.54.156.112/").replace("http://", "").replace("/", "")

def get_arduino_endpoint():
    """Get Arduino endpoint URL"""
    return f"http://{get_arduino_ip()}/"

def parse_arduino_html(html: str) -> Dict[str, Any]:
    """Parse Arduino HTML response to extract sensor data"""
    try:
        # Extract temperature
        temp_match = re.search(r'<b>Temperature:</b>\s*([\d.]+)\s*°C', html)
        temperature = float(temp_match.group(1)) if temp_match else 0.0
        
        # Extract humidity
        hum_match = re.search(r'<b>Humidity:</b>\s*([\d.]+)\s*%', html)
        humidity = float(hum_match.group(1)) if hum_match else 0.0
        
        # Extract RFID Tag
        rfid_match = re.search(r'<b>RFID Tag:</b>\s*([^<]+)', html)
        rfid_tag = rfid_match.group(1).strip() if rfid_match else "No Tag Detected"
        
        # Extract Distance
        dist_match = re.search(r'<b>Distance:</b>\s*([\d.]+)\s*cm', html)
        distance = float(dist_match.group(1)) if dist_match else 0.0
        
        # Extract Air Quality (MQ-135)
        air_match = re.search(r'<b>Air Quality \(MQ-135\):</b>\s*([\d]+)', html)
        air_quality = int(air_match.group(1)) if air_match else 0
        
        return {
            "temperature": temperature,
            "humidity": humidity,
            "rfid_tag": rfid_tag,
            "distance": distance,
            "air_quality": air_quality,
            "gas_level": air_quality,  # MQ-135 is gas sensor
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error parsing Arduino HTML: {e}")
        return {
            "temperature": 0.0,
            "humidity": 0.0,
            "rfid_tag": "Parse Error",
            "distance": 0.0,
            "air_quality": 0,
            "gas_level": 0,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.get("/arduino/sensors")
async def get_arduino_sensors():
    """
    Fetch live sensor data from Arduino/ESP8266 endpoint
    Parses HTML response from ESP8266 web server
    """
    arduino_ip = get_arduino_ip()
    arduino_endpoint = get_arduino_endpoint()
    
    try:
        async with httpx.AsyncClient(timeout=ARDUINO_TIMEOUT) as client:
            response = await client.get(arduino_endpoint)
            response.raise_for_status()
            
            # Parse Arduino HTML response
            html_content = response.text
            sensor_data = parse_arduino_html(html_content)
            
            logger.info(f"Successfully fetched Arduino sensor data from {arduino_endpoint}")
            logger.info(f"Parsed data: Temp={sensor_data['temperature']}°C, Gas={sensor_data['gas_level']}, Distance={sensor_data['distance']}cm")
            
            return {
                "status": "connected",
                "endpoint": arduino_endpoint,
                "ip": arduino_ip,
                "data": sensor_data,
                "raw_available": True
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
            # Try to connect to Arduino root endpoint
            response = await client.get(arduino_endpoint)
            response.raise_for_status()
            
            # Calculate response time
            response_time = response.elapsed.total_seconds() * 1000 if hasattr(response, 'elapsed') else 0
            
            return {
                "status": "connected",
                "endpoint": arduino_endpoint,
                "ip": arduino_ip,
                "response_time_ms": response_time,
                "content_type": response.headers.get("content-type", "unknown"),
                "message": "Arduino ESP8266 is online and responding"
            }
            
    except Exception as e:
        return {
            "status": "disconnected",
            "endpoint": arduino_endpoint,
            "ip": arduino_ip,
            "error": str(e),
            "message": "Cannot connect to Arduino ESP8266"
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
