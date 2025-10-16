# 🔧 Backend - AI-Smarter-Shop Safety Monitoring System

FastAPI-based backend server for real-time IoT sensor monitoring, AI-powered safety detection, and alert management.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
- [Database](#database)
- [Arduino Integration](#arduino-integration)
- [Alert System](#alert-system)
- [Testing](#testing)
- [Deployment](#deployment)

---

## 🎯 Overview

The backend server provides:
- **Real-time sensor data processing** from Arduino ESP8266
- **AI-powered computer vision** for safety violation detection (YOLOv8)
- **Alert management** with email (Gmail SMTP) and SMS (Twilio) notifications
- **Database management** with SQLite/PostgreSQL support
- **WebSocket support** for real-time updates
- **RESTful API** with automatic OpenAPI documentation

---

## ✨ Features

### 🔌 IoT Sensor Integration
- **Arduino ESP8266 Connection**: HTTP-based sensor data fetching
- **Real-time Data Parsing**: HTML to JSON conversion
- **Sensor Types**:
  - Gas/Smoke (MQ-135)
  - Temperature & Humidity (DHT11)
  - Distance (HC-SR04 Ultrasonic)
  - RFID Tag Reading (MFRC522)

### 🤖 AI/ML Capabilities
- **YOLOv8 Object Detection**: Real-time safety equipment detection
- **PPE Detection**: Hard hat, safety vest, gloves detection
- **Anomaly Detection**: Unusual behavior pattern recognition
- **Computer Vision Pipeline**: Frame processing and analysis

### 🚨 Alert System
- **Multi-level Thresholds**: Warning and Danger levels
- **Alert Cooldown**: 5-minute spam prevention
- **Email Notifications**: HTML-formatted alerts via Gmail
- **SMS Notifications**: Twilio integration for critical alerts
- **Real-time Alerts**: WebSocket broadcasting

### 📊 Data Management
- **SQLite Database**: Development & testing
- **PostgreSQL Support**: Production deployment
- **Async ORM**: SQLAlchemy 2.0 with async support
- **Database Seeding**: Auto-populate sample data
- **Historical Data**: Sensor readings, alerts, incidents

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | 0.104.1 |
| **Server** | Uvicorn | 0.24.0 |
| **Database** | SQLite/PostgreSQL | - |
| **ORM** | SQLAlchemy | 2.0.23 |
| **Async DB** | aiosqlite/asyncpg | 0.19.0 |
| **Validation** | Pydantic | 2.5.0 |
| **AI/ML** | TensorFlow | 2.15.0 |
| **CV** | OpenCV | 4.8.1 |
| **YOLO** | Ultralytics | 8.0.220 |
| **Email** | SMTP (Gmail) | - |
| **SMS** | Twilio | 8.10.0 |
| **HTTP Client** | httpx | 0.25.2 |

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   │
│   ├── ai/                     # AI/ML modules
│   │   ├── __init__.py
│   │   └── cv_detector.py      # YOLOv8 computer vision detector
│   │
│   ├── db/                     # Database configuration
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy async setup
│   │   └── seed_data.py        # Database seeding functions
│   │
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── models.py           # SQLAlchemy ORM models
│   │   ├── schemas.py          # Pydantic schemas
│   │   ├── best.pt             # YOLOv8 custom model
│   │   └── yolov8n.pt          # YOLOv8 base model
│   │
│   ├── routes/                 # API endpoints
│   │   ├── __init__.py
│   │   ├── sensors.py          # Sensor data endpoints
│   │   ├── arduino_sensors.py  # Arduino integration
│   │   ├── alerts.py           # Alert management
│   │   ├── reports.py          # Analytics & reports
│   │   ├── cv_detection.py     # Computer vision endpoints
│   │   ├── ai_detection.py     # AI detection endpoints
│   │   ├── workers.py          # Worker/RFID management
│   │   └── settings.py         # System settings
│   │
│   └── services/               # Business logic
│       ├── __init__.py
│       └── alert_service.py    # Alert notification service
│
├── data/                       # Database & uploads
│   └── ai_safety_monitoring.db # SQLite database
│
├── uploads/                    # File uploads (images, etc.)
│
├── .env                        # Environment variables (DO NOT COMMIT)
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
├── init_database.py            # Database initialization script
└── seed_database.py            # Standalone seeding script
```

---

## 🚀 Installation

### Prerequisites

- **Python**: 3.10 or higher
- **pip**: Latest version
- **Virtual Environment**: Recommended

### Step 1: Clone Repository

```bash
cd backend
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Environment Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit with your configuration
nano .env
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True

# Database (SQLite for development)
DATABASE_URL=sqlite+aiosqlite:///./data/ai_safety_monitoring.db

# Database (PostgreSQL for production)
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ai_safety_monitoring

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (Gmail SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use App Password, not regular password
ALERT_EMAIL_FROM=your-email@gmail.com
ALERT_EMAIL_TO=recipient@gmail.com

# SMS Configuration (Twilio)
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890
ALERT_PHONE_NUMBER=recipient-phone

# AI Model Configuration
AI_MODEL_PATH=./app/models
AI_CONFIDENCE_THRESHOLD=0.75
ANOMALY_DETECTION_SENSITIVITY=medium

# Sensor Thresholds
GAS_WARNING_THRESHOLD=300        # ppm
GAS_DANGER_THRESHOLD=500         # ppm
TEMP_WARNING_THRESHOLD=35        # °C
TEMP_DANGER_THRESHOLD=45         # °C
VIBRATION_WARNING_THRESHOLD=5    # g
VIBRATION_DANGER_THRESHOLD=10    # g
PROXIMITY_WARNING_THRESHOLD=100  # cm
PROXIMITY_DANGER_THRESHOLD=800   # cm

# CORS Origins
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Arduino Configuration
ARDUINO_ENDPOINT=http://10.54.156.112/
ARDUINO_TIMEOUT=5

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### Gmail App Password Setup

1. Go to Google Account Settings
2. Enable 2-Factor Authentication
3. Go to Security → App Passwords
4. Create app password for "Mail"
5. Copy 16-character password to `.env`

### Twilio Setup

1. Sign up at https://www.twilio.com
2. Get Account SID and Auth Token from Console
3. Get Twilio phone number
4. Verify destination phone number (required for trial)

---

## 🏃 Running the Server

### Development Mode

```bash
# Activate virtual environment first
source venv/bin/activate

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Run with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Python Script

```bash
python -m app.main
```

### Access Points

- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📖 API Documentation

### Core Endpoints

#### Sensor Endpoints

```bash
# Get all sensors (mock data)
GET /sensors/

# Get live Arduino sensor data
GET /sensors/live/arduino

# Get specific sensor
GET /sensors/{sensor_type}

# Get sensor history
GET /sensors/history?hours=24

# Get RFID logs
GET /sensors/rfid/logs?days=7

# Get sensor statistics
GET /sensors/statistics
```

#### Arduino Endpoints

```bash
# Get Arduino status
GET /api/arduino/status

# Get parsed Arduino sensor data
GET /api/arduino/sensors
```

#### Alert Endpoints

```bash
# Get all alerts
GET /alerts/

# Get active alerts
GET /alerts/active

# Acknowledge alert
PUT /alerts/{alert_id}/acknowledge

# Get alert history
GET /alerts/history?days=7

# Test email alert
POST /sensors/test/alert/email

# Test SMS alert
POST /sensors/test/alert/sms

# Get alert configuration
GET /sensors/alert/config
```

#### Computer Vision Endpoints

```bash
# Get all cameras
GET /cv/cameras

# Get camera by ID
GET /cv/cameras/{camera_id}

# Create camera
POST /cv/cameras

# Update camera
PATCH /cv/cameras/{camera_id}

# Delete camera
DELETE /cv/cameras/{camera_id}

# Get detections
GET /cv/detections?hours=24

# Acknowledge detection
PATCH /cv/detections/{detection_id}/acknowledge

# Simulate detection
POST /cv/detections/simulate/{camera_id}

# Get CV statistics
GET /cv/stats

# Upload image for detection
POST /cv/detect/upload
```

#### Reports Endpoints

```bash
# Get report summary
GET /reports/?period=week

# Get analytics data
GET /reports/analytics?period=week

# Get incident list
GET /reports/list?period=week

# Get detailed incidents
GET /reports/incidents?period=week
```

#### WebSocket

```bash
# Real-time updates
WS /ws
```

---

## 🗄️ Database

### SQLite (Development)

**Automatic Setup**: Database is created automatically on first run.

```bash
# Initialize database manually
python init_database.py

# Seed sample data
python seed_database.py
```

### PostgreSQL (Production)

```bash
# Create database
createdb ai_safety_monitoring

# Update .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ai_safety_monitoring

# Run migrations (if using Alembic)
alembic upgrade head
```

### Database Schema

#### Tables:
- **cameras**: Camera configurations and status
- **cv_detections**: Computer vision detection records
- **alerts**: System alerts and notifications
- **sensor_data**: Historical sensor readings
- **incidents**: Safety incident records
- **workers**: Worker information and RFID tags

### Seeded Data

On startup, the system seeds:
- **6 Cameras**: Main Entrance, Assembly Line, Warehouse, Heavy Machinery, Loading Dock, QC Station
- **30+ Detections**: Various violation types and severities
- **Timestamps**: Recent data (last 24 hours)

---

## 🔌 Arduino Integration

### Arduino ESP8266 Setup

**Hardware**:
- ESP8266 NodeMCU
- DHT11 (Temperature & Humidity)
- MQ-135 (Gas Sensor)
- HC-SR04 (Ultrasonic)
- MFRC522 (RFID Reader)

**Network**:
- WiFi SSID: "Klassy"
- IP Address: 10.54.156.112
- Port: 80 (HTTP)

### Arduino Code Structure

```cpp
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DHT.h>
#include <MFRC522.h>

const char* ssid = "Klassy";
const char* password = "your-password";

ESP8266WebServer server(80);
DHT dht(D4, DHT11);
MFRC522 mfrc522(D2, D1);

void handleRoot() {
  String html = "<html><body>";
  html += "<p><b>Temperature:</b> " + String(dht.readTemperature()) + " °C</p>";
  html += "<p><b>Humidity:</b> " + String(dht.readHumidity()) + " %</p>";
  html += "<p><b>Gas Level:</b> " + String(analogRead(A0)) + "</p>";
  html += "<p><b>Distance:</b> " + String(getDistance()) + " cm</p>";
  html += "<p><b>RFID Tag:</b> " + lastTagID + "</p>";
  html += "</body></html>";
  server.send(200, "text/html", html);
}

void setup() {
  WiFi.begin(ssid, password);
  server.on("/", handleRoot);
  server.begin();
}
```

### Backend Connection

The backend fetches Arduino data via HTTP:

```python
# GET http://10.54.156.112/
# Parses HTML response
# Converts to JSON
# Checks thresholds
# Sends alerts if needed
```

---

## 🚨 Alert System

### How It Works

1. **Sensor Reading**: Backend fetches data from Arduino
2. **Threshold Check**: Compares values against configured thresholds
3. **Alert Trigger**: If breach detected, triggers alert
4. **Notification**: Sends email and SMS
5. **Cooldown**: 5-minute cooldown prevents spam

### Alert Levels

| Level | Condition | Action |
|-------|-----------|--------|
| **Normal** | Below warning threshold | No alert |
| **Warning** | Above warning, below danger | Email + SMS |
| **Danger** | Above danger threshold | Email + SMS + Notification |

### Threshold Configuration

Edit `.env` to adjust thresholds:

```bash
# Gas Sensor (MQ-135)
GAS_WARNING_THRESHOLD=300   # Show warning at 300 ppm
GAS_DANGER_THRESHOLD=500    # Critical alert at 500 ppm

# Temperature (DHT11)
TEMP_WARNING_THRESHOLD=35   # Warning at 35°C
TEMP_DANGER_THRESHOLD=45    # Danger at 45°C

# Distance (Ultrasonic)
PROXIMITY_WARNING_THRESHOLD=100   # Warning at 100 cm
PROXIMITY_DANGER_THRESHOLD=800    # Danger at 800 cm
```

### Email Alert Format

- **Subject**: ⚠️ DANGER/WARNING ALERT: SENSOR_TYPE Threshold Breached
- **Format**: HTML with styled tables
- **Content**: Sensor value, threshold, timestamp, link to dashboard

### SMS Alert Format

```
🚨 DANGER ALERT
Sensor: GAS
Value: 520 ppm
Threshold: 500 ppm
Check dashboard immediately!
```

---

## 🧪 Testing

### Manual Testing

```bash
# Test Arduino connection
curl http://10.54.156.112/

# Test backend Arduino proxy
curl http://localhost:8000/api/arduino/status
curl http://localhost:8000/sensors/live/arduino

# Test email alert
curl -X POST http://localhost:8000/sensors/test/alert/email

# Test SMS alert
curl -X POST http://localhost:8000/sensors/test/alert/sms

# Manual alert trigger
curl -X POST http://localhost:8000/sensors/alert/manual \
  -H "Content-Type: application/json" \
  -d '{"sensor_type": "gas", "value": 550, "unit": "ppm"}'
```

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_sensors.py
```

---

## 🚀 Deployment

### Using Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build image
docker build -t ai-safety-backend .

# Run container
docker run -p 8000:8000 --env-file .env ai-safety-backend
```

### Using Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/ai_safety
    depends_on:
      - db
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=ai_safety_monitoring
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Production Checklist

- [ ] Set `ENV=production` in `.env`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure strong `SECRET_KEY`
- [ ] Set up proper CORS origins
- [ ] Enable HTTPS/SSL
- [ ] Set up reverse proxy (Nginx)
- [ ] Configure monitoring (Prometheus, Grafana)
- [ ] Set up logging (ELK stack)
- [ ] Configure backup strategy
- [ ] Set up rate limiting
- [ ] Enable authentication/authorization

---

## 📝 Logs

```bash
# View logs
tail -f logs/app.log

# Filter by level
grep "ERROR" logs/app.log
grep "WARNING" logs/app.log
```

---

## 🔧 Troubleshooting

### Arduino Connection Issues

```bash
# Check Arduino is accessible
ping 10.54.156.112
curl http://10.54.156.112/

# Check backend logs
tail -f logs/app.log | grep Arduino

# Increase timeout in .env
ARDUINO_TIMEOUT=10
```

### Email Not Sending

1. Verify Gmail App Password (not regular password)
2. Check SMTP settings in `.env`
3. Test with manual endpoint: `POST /sensors/test/alert/email`
4. Check spam folder

### SMS Not Sending

1. Verify Twilio credentials
2. Check account balance
3. Verify phone number format (+country code)
4. For trial accounts, verify destination number

### Database Issues

```bash
# Delete and recreate database
rm data/ai_safety_monitoring.db
python init_database.py

# Check database
sqlite3 data/ai_safety_monitoring.db
> .tables
> SELECT * FROM cameras;
```

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [Twilio Python SDK](https://www.twilio.com/docs/libraries/python)

---

## 🤝 Contributing

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Write docstrings for modules and functions
4. Add unit tests for new features
5. Update this README for significant changes

---

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for safer workplaces**
