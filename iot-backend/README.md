# 🚀 IoT Safety Backend Server

## Overview

Flask-based REST API backend server that connects to ESP8266 IoT devices and serves real-time sensor data to mobile applications. The server automatically fetches data from connected ESP8266 devices and provides a comprehensive API for monitoring, alerts, and settings management.

## 🌟 Features

- ✅ **Real-time Sensor Data** - Fetches live data from ESP8266 (DHT11, MFRC522, HC-SR04, MQ-135)
- ✅ **RESTful API** - Clean, well-documented endpoints
- ✅ **CORS Enabled** - Cross-origin requests supported for mobile apps
- ✅ **Auto Fallback** - Uses mock data when ESP8266 is unavailable
- ✅ **Status Monitoring** - Automatic status determination based on thresholds
- ✅ **Settings Management** - Persistent configuration storage
- ✅ **Health Checks** - Endpoint to monitor system health
- ✅ **Error Handling** - Robust error handling and logging

## 📋 Requirements

- Python 3.7+
- ESP8266 with sensors (optional - mock data available)
- Network connectivity

## 🔧 Installation

### 1. Install Dependencies

```bash
cd iot-backend
pip install -r requirements.txt
```

### 2. Configure ESP8266 IP

Edit `app.py` line 10:
```python
ESP8266_IP = "10.54.156.112"  # Your ESP8266 IP address
```

### 3. Start the Server

```bash
python3 app.py
```

The server will start on `http://0.0.0.0:8000`

## 📡 ESP8266 Configuration

### Expected Sensors
- **DHT11** - Temperature & Humidity
- **MFRC522** - RFID Card Reader
- **HC-SR04** - Ultrasonic Distance Sensor
- **MQ-135** - Air Quality/Gas Sensor

### ESP8266 Web Interface
The ESP8266 should serve an HTML page with sensor data at `http://<ESP8266_IP>/`:

```html
<p><b>Temperature:</b> 30.00 °C</p>
<p><b>Humidity:</b> 16.00 %</p>
<p><b>RFID Tag:</b> 63121495</p>
<p><b>Distance:</b> 11.03 cm</p>
<p><b>Air Quality (MQ-135):</b> 150</p>
```

## 🛣️ API Endpoints

### Home
```
GET /
```
Returns API information and available endpoints.

**Response:**
```json
{
  "message": "IoT Safety Backend API",
  "version": "1.0.0",
  "esp8266_ip": "10.54.156.112",
  "endpoints": {
    "sensors": "/sensors/live/arduino",
    "cameras": "/cv/cameras",
    "detections": "/cv/detections",
    "reports": "/reports",
    "settings": "/settings"
  }
}
```

### Get Sensor Data
```
GET /sensors/live/arduino
```
Fetches real-time sensor data from ESP8266.

**Response:**
```json
{
  "sensors": {
    "temperature": {
      "value": 30.0,
      "unit": "°C",
      "status": "normal"
    },
    "humidity": {
      "value": 16.0,
      "unit": "%",
      "status": "warning"
    },
    "gas": {
      "value": 150,
      "unit": "ppm",
      "status": "normal"
    },
    "ultrasonic": {
      "value": 11.03,
      "unit": "cm",
      "status": "danger"
    },
    "rfid": {
      "value": "63121495",
      "status": "scanned"
    }
  },
  "timestamp": "2025-10-17T08:43:24.052994"
}
```

### Get Cameras
```
GET /cv/cameras
```
Returns list of all cameras.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Main Entrance",
    "location": "Building A - Floor 1",
    "status": "active",
    "violation_count": 0
  }
]
```

### Get Detections
```
GET /cv/detections?limit=50
```
Returns list of safety violation detections.

**Parameters:**
- `limit` (optional): Maximum number of detections to return

### Acknowledge Detection
```
POST /cv/detections/<detection_id>/acknowledge
```
Marks a detection as acknowledged.

### Get Reports
```
GET /reports?period=week
```
Returns statistical reports.

**Parameters:**
- `period`: `day`, `week`, or `month`

**Response:**
```json
{
  "period": "week",
  "stats": {
    "total_violations": 0,
    "critical_alerts": 0,
    "active_cameras": 2,
    "average_response_time": 180
  },
  "severity_distribution": {
    "low": 0,
    "medium": 0,
    "high": 0,
    "critical": 0
  },
  "incidents_by_day": []
}
```

### Get Settings
```
GET /settings
```
Returns current settings.

### Update Settings
```
PUT /settings
Content-Type: application/json

{
  "theme": "dark",
  "notifications_enabled": true,
  "thresholds": {
    "temperature": {"min": 15, "max": 35},
    "humidity": {"min": 30, "max": 80},
    "gas": {"max": 300},
    "ultrasonic": {"min": 50}
  }
}
```

### Health Check
```
GET /health
```
Returns server health status and ESP8266 connection status.

**Response:**
```json
{
  "status": "healthy",
  "esp8266_status": "connected",
  "timestamp": "2025-10-17T08:43:24.052994"
}
```

### Register Device Token
```
POST /notifications/register
Content-Type: application/json

{
  "token": "device_push_token"
}
```

## 🎯 Status Determination

The backend automatically determines sensor status based on configurable thresholds:

### Temperature
- **Normal**: 15°C - 35°C
- **Warning**: < 15°C or > 35°C
- **Danger**: Extreme values

### Humidity
- **Normal**: 30% - 80%
- **Warning**: < 30% or > 80%
- **Danger**: Extreme values

### Gas (MQ-135)
- **Normal**: < 210 ppm
- **Warning**: 210-300 ppm
- **Danger**: > 300 ppm

### Distance (HC-SR04)
- **Normal**: > 75 cm
- **Warning**: 50-75 cm
- **Danger**: < 50 cm

### RFID
- **Scanned**: Card detected
- **Idle**: No card detected

## 🔄 Auto-Fallback System

When ESP8266 is unavailable:
1. Server attempts to connect (5-second timeout)
2. On failure, generates mock data
3. Logs warning: `⚠️ ESP8266 not available, using mock data`
4. Returns realistic mock values
5. Automatically resumes real data when ESP8266 reconnects

## 🧪 Testing

### Test Backend Health
```bash
curl http://localhost:8000/health
```

### Test Sensor Endpoint
```bash
curl http://localhost:8000/sensors/live/arduino
```

### Test ESP8266 Directly
```bash
curl http://10.54.156.112
```

### Check Logs
Watch the terminal for:
```
✅ ESP8266 data: T=30.0°C, H=16.0%, Gas=150ppm, Dist=11.03cm, RFID=63121495
```

## 🐛 Troubleshooting

### ESP8266 Connection Timeout

**Error:** `Error fetching ESP8266 data: HTTPConnectionPool... Connection to 10.54.156.112 timed out`

**Solutions:**
1. Check ESP8266 is powered on
2. Verify WiFi connection
3. Ping ESP8266: `ping 10.54.156.112`
4. Test in browser: `http://10.54.156.112`
5. Check firewall settings

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
sudo lsof -t -i:8000

# Kill the process
sudo kill -9 <PID>

# Or kill all Python processes
pkill -9 python3
```

### Parsing Errors

**Error:** `could not convert string to float: ' 30.00 Â'`

**Solution:** Already handled! The parser automatically removes non-numeric characters.

### CORS Issues

If mobile app can't connect:
1. Verify CORS is enabled (it is by default)
2. Check mobile app is using correct IP
3. Ensure devices are on same network

## 📊 Architecture

```
┌─────────────────┐
│    ESP8266      │ ← IoT Device
│  10.54.156.112  │
│                 │
│  • DHT11        │ Temperature & Humidity
│  • MFRC522      │ RFID Reader
│  • HC-SR04      │ Distance Sensor
│  • MQ-135       │ Gas Sensor
└────────┬────────┘
         │ HTTP GET
         │ HTML Response
         ▼
┌─────────────────┐
│  Flask Backend  │ ← This Server
│     :8000       │
│                 │
│  • Parse HTML   │ Extract sensor values
│  • Validate     │ Check thresholds
│  • Transform    │ JSON responses
│  • Store        │ In-memory data
└────────┬────────┘
         │ REST API
         │ JSON
         ▼
┌─────────────────┐
│   Mobile App    │ ← Client
│   React Native  │
└─────────────────┘
```

## 🔒 Security Considerations

### Current Setup (Development)
- ⚠️ No authentication
- ⚠️ No HTTPS
- ⚠️ Debug mode enabled
- ⚠️ CORS fully open

### Production Recommendations
1. **Add Authentication** - JWT tokens, API keys
2. **Enable HTTPS** - SSL/TLS certificates
3. **Disable Debug** - `debug=False`
4. **Restrict CORS** - Specific origins only
5. **Rate Limiting** - Prevent abuse
6. **Input Validation** - Sanitize all inputs
7. **Use Production Server** - Gunicorn, uWSGI
8. **Database** - Replace in-memory storage
9. **Logging** - File-based logging
10. **Monitoring** - Add health checks and alerts

## 🚀 Production Deployment

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

```bash
docker build -t iot-backend .
docker run -p 8000:8000 iot-backend
```

### Environment Variables

Create `.env` file:
```
ESP8266_IP=10.54.156.112
PORT=8000
DEBUG=False
SECRET_KEY=your-secret-key
```

Load in `app.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()
ESP8266_IP = os.getenv('ESP8266_IP', '10.54.156.112')
```

## 📝 Logging

### Current Logging
- ✅ ESP8266 connection attempts
- ✅ Successful data fetches
- ✅ Parsing errors
- ✅ Fallback to mock data
- ✅ Device token registrations

### Add Custom Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info('Server started')
```

## 🔄 Auto-Restart

### Using systemd (Linux)

Create `/etc/systemd/system/iot-backend.service`:
```ini
[Unit]
Description=IoT Safety Backend
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/iot-backend
ExecStart=/usr/bin/python3 /path/to/iot-backend/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable iot-backend
sudo systemctl start iot-backend
```

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [ESP8266 Arduino Core](https://github.com/esp8266/Arduino)
- [REST API Best Practices](https://restfulapi.net/)

## 📄 License

MIT License - Feel free to use and modify

## 👨‍💻 Developer

Built for IoT Safety Monitoring System
Version: 1.0.0
Last Updated: October 2025

---

**Need Help?** Check the logs, they're very descriptive! 🔍
