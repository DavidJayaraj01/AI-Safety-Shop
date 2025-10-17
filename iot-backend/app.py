from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for mobile app

# ESP8266 Configuration
ESP8266_IP = "10.54.156.112"  # Your ESP8266 IP
ESP8266_URL = f"http://{ESP8266_IP}"

# In-memory storage for detections and settings
detections = []
cameras = [
    {
        "id": 1,
        "name": "Main Entrance",
        "location": "Building A - Floor 1",
        "status": "active",
        "violation_count": 0
    },
    {
        "id": 2,
        "name": "Production Floor",
        "location": "Building B - Floor 2",
        "status": "active",
        "violation_count": 0
    }
]

settings = {
    "theme": "auto",
    "notifications_enabled": True,
    "refresh_interval": 15000,
    "thresholds": {
        "temperature": {"min": 15, "max": 35},
        "humidity": {"min": 30, "max": 80},
        "gas": {"max": 300},
        "ultrasonic": {"min": 50}
    }
}

def fetch_esp8266_data():
    """Fetch data from ESP8266"""
    try:
        response = requests.get(ESP8266_URL, timeout=5)
        if response.status_code == 200:
            # Parse HTML response from ESP8266
            html = response.text
            
            # Extract values from HTML (simple parsing)
            temp_str = extract_value(html, "Temperature:", "°C")
            humidity_str = extract_value(html, "Humidity:", "%")
            rfid = extract_text_value(html, "RFID Tag:")
            distance_str = extract_value(html, "Distance:", "cm")
            air_quality_str = extract_value(html, "Air Quality (MQ-135):")
            
            # Convert to proper types with validation
            try:
                temp = float(temp_str) if temp_str else 25.0
            except ValueError:
                print(f"Warning: Invalid temperature value: {temp_str}")
                temp = 25.0
                
            try:
                humidity = float(humidity_str) if humidity_str else 50.0
            except ValueError:
                print(f"Warning: Invalid humidity value: {humidity_str}")
                humidity = 50.0
                
            try:
                distance = float(distance_str) if distance_str else 100.0
            except ValueError:
                print(f"Warning: Invalid distance value: {distance_str}")
                distance = 100.0
                
            try:
                gas = int(air_quality_str) if air_quality_str else 150
            except ValueError:
                print(f"Warning: Invalid gas value: {air_quality_str}")
                gas = 150
            
            # Clean RFID value
            if not rfid or rfid.strip() == "":
                rfid = "No Tag Detected"
            
            data = {
                "temperature": temp,
                "humidity": humidity,
                "rfid": rfid.strip(),
                "distance": distance,
                "gas": gas
            }
            
            print(f"✅ ESP8266 data: T={temp}°C, H={humidity}%, Gas={gas}ppm, Dist={distance}cm, RFID={rfid}")
            return data
            
    except Exception as e:
        print(f"Error fetching ESP8266 data: {e}")
    
    # Return None if connection fails
    return None

def extract_value(html, label, unit=""):
    """Extract numeric value from HTML"""
    try:
        start = html.find(label)
        if start == -1:
            return None
        start = start + len(label)
        end = html.find(unit, start) if unit else html.find("<", start)
        value = html[start:end].strip()
        # Remove any HTML tags and special characters
        value = value.replace("<b>", "").replace("</b>", "").replace("</p>", "")
        # Remove non-numeric characters except decimal point and minus
        clean_value = ""
        for char in value:
            if char.isdigit() or char == '.' or char == '-':
                clean_value += char
        return clean_value if clean_value else None
    except Exception as e:
        print(f"Error extracting value for {label}: {e}")
        return None

def extract_text_value(html, label):
    """Extract text value from HTML"""
    try:
        start = html.find(label)
        if start == -1:
            return None
        start = start + len(label)
        end = html.find("</p>", start)
        value = html[start:end].strip()
        # Remove HTML tags and clean up
        value = value.replace("<b>", "").replace("</b>", "")
        # Remove extra whitespace
        value = ' '.join(value.split())
        return value
    except Exception as e:
        print(f"Error extracting text for {label}: {e}")
        return None

def get_status(value, thresholds, sensor_type):
    """Determine sensor status based on thresholds"""
    if sensor_type == "temperature":
        if value < thresholds["temperature"]["min"]:
            return "warning"
        elif value > thresholds["temperature"]["max"]:
            return "danger"
        return "normal"
    elif sensor_type == "humidity":
        if value < thresholds["humidity"]["min"]:
            return "warning"
        elif value > thresholds["humidity"]["max"]:
            return "danger"
        return "normal"
    elif sensor_type == "gas":
        if value > thresholds["gas"]["max"]:
            return "danger"
        elif value > thresholds["gas"]["max"] * 0.7:
            return "warning"
        return "normal"
    elif sensor_type == "ultrasonic":
        if value < thresholds["ultrasonic"]["min"]:
            return "danger"
        elif value < thresholds["ultrasonic"]["min"] * 1.5:
            return "warning"
        return "normal"
    return "normal"

# ==================== ROUTES ====================

@app.route('/')
def home():
    return jsonify({
        "message": "IoT Safety Backend API",
        "version": "1.0.0",
        "esp8266_ip": ESP8266_IP,
        "endpoints": {
            "sensors": "/sensors/live/arduino",
            "cameras": "/cv/cameras",
            "detections": "/cv/detections",
            "reports": "/reports",
            "settings": "/settings"
        }
    })

@app.route('/sensors/live/arduino', methods=['GET'])
def get_sensor_data():
    """Get live sensor data from ESP8266"""
    esp_data = fetch_esp8266_data()
    
    # If ESP8266 is unavailable, use mock data
    if esp_data is None:
        print("⚠️  ESP8266 not available, using mock data")
        esp_data = {
            "temperature": random.uniform(20, 30),
            "humidity": random.uniform(40, 70),
            "rfid": "DEMO123ABC" if random.random() > 0.5 else "No Tag Detected",
            "distance": random.uniform(60, 200),
            "gas": random.randint(100, 250)
        }
    
    # Build response
    response = {
        "sensors": {
            "temperature": {
                "value": round(esp_data["temperature"], 2),
                "unit": "°C",
                "status": get_status(esp_data["temperature"], settings["thresholds"], "temperature")
            },
            "humidity": {
                "value": round(esp_data["humidity"], 2),
                "unit": "%",
                "status": get_status(esp_data["humidity"], settings["thresholds"], "humidity")
            },
            "gas": {
                "value": int(esp_data["gas"]),
                "unit": "ppm",
                "status": get_status(esp_data["gas"], settings["thresholds"], "gas")
            },
            "ultrasonic": {
                "value": round(esp_data["distance"], 2),
                "unit": "cm",
                "status": get_status(esp_data["distance"], settings["thresholds"], "ultrasonic")
            },
            "rfid": {
                "value": esp_data["rfid"],
                "status": "scanned" if esp_data["rfid"] != "No Tag Detected" else "idle"
            }
        },
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(response)

@app.route('/cv/cameras', methods=['GET'])
def get_cameras():
    """Get all cameras"""
    return jsonify(cameras)

@app.route('/cv/detections', methods=['GET'])
def get_detections():
    """Get all detections"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify(detections[:limit])

@app.route('/cv/detections/<int:detection_id>/acknowledge', methods=['POST'])
def acknowledge_detection(detection_id):
    """Acknowledge a detection"""
    for detection in detections:
        if detection['id'] == detection_id:
            detection['acknowledged'] = True
            return jsonify({"message": "Detection acknowledged"})
    return jsonify({"error": "Detection not found"}), 404

@app.route('/reports', methods=['GET'])
def get_reports():
    """Get reports"""
    period = request.args.get('period', 'week')
    
    # Generate mock report data
    report = {
        "period": period,
        "stats": {
            "total_violations": len(detections),
            "critical_alerts": sum(1 for d in detections if d['severity'] == 'critical'),
            "active_cameras": len([c for c in cameras if c['status'] == 'active']),
            "average_response_time": 180
        },
        "severity_distribution": {
            "low": sum(1 for d in detections if d['severity'] == 'low'),
            "medium": sum(1 for d in detections if d['severity'] == 'medium'),
            "high": sum(1 for d in detections if d['severity'] == 'high'),
            "critical": sum(1 for d in detections if d['severity'] == 'critical')
        },
        "incidents_by_day": []
    }
    
    return jsonify(report)

@app.route('/settings', methods=['GET', 'PUT'])
def handle_settings():
    """Get or update settings"""
    global settings
    
    if request.method == 'GET':
        return jsonify(settings)
    
    elif request.method == 'PUT':
        data = request.get_json()
        settings.update(data)
        return jsonify(settings)

@app.route('/notifications/register', methods=['POST'])
def register_device():
    """Register device for push notifications"""
    data = request.get_json()
    token = data.get('token')
    print(f"Device token registered: {token}")
    return jsonify({"message": "Device registered successfully"})

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    esp_status = "connected" if fetch_esp8266_data() is not None else "disconnected"
    return jsonify({
        "status": "healthy",
        "esp8266_status": esp_status,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 IoT Safety Backend Server Starting...")
    print("=" * 50)
    print(f"📡 ESP8266 IP: {ESP8266_IP}")
    print(f"🌐 Backend will run on: http://0.0.0.0:8000")
    print(f"📱 Mobile app should connect to: http://10.54.156.140:8000")
    print(f"💻 Or use your computer's IP address")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8000, debug=True)
