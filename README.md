# 🏭 AI-Smarter-Shop: Industrial IoT Safety Monitoring System

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-19.1.1-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**A comprehensive full-stack IoT safety monitoring system integrating Arduino sensors, AI-powered computer vision, real-time alerts (Email & SMS), and analytics dashboards for industrial safety management.**

[Features](#-features) • [Quick Start](#-quick-start) • [Installation](#-installation) • [Documentation](#-documentation) • [Demo](#-demo)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Hardware Setup](#-hardware-setup)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

AI-Smarter-Shop is an enterprise-grade safety monitoring solution designed for industrial environments, manufacturing floors, and heavy machinery operations. It combines IoT sensors, artificial intelligence, and real-time data analytics to prevent workplace accidents and ensure regulatory compliance.

### Key Highlights

- **Real-Time Monitoring**: Live sensor data from Arduino ESP8266 with 15-second refresh rates
- **AI-Powered Detection**: YOLOv8-based computer vision for PPE detection and hazard identification
- **Predictive Analytics**: Machine learning algorithms predict incidents before they occur
- **Multi-Channel Alerts**: Email (Gmail SMTP) and SMS (Twilio) notifications with smart cooldown
- **Comprehensive Dashboard**: Interactive visualizations with dark/light themes
- **Scalable Architecture**: FastAPI backend with React frontend, ready for production deployment

---

## ✨ Features

### 🔌 Real-Time IoT Monitoring

| Feature | Description |
|---------|-------------|
| **Arduino Integration** | ESP8266 with DHT11 (Temp/Humidity), MQ-135 (Gas), HC-SR04 (Distance), MFRC522 (RFID) |
| **Live Dashboard** | Updates every 15 seconds with color-coded status indicators |
| **Historical Charts** | Real-time line charts tracking last 20 data points per sensor |
| **Status Tracking** | Normal/Warning/Danger states based on configurable thresholds |
| **RFID Access Control** | Real-time badge scanning and worker tracking |

### 🚨 Smart Alert System

- **Email Alerts**: Gmail SMTP with HTML-formatted notifications
- **SMS Alerts**: Twilio integration for critical warnings
- **5-Minute Cooldown**: Intelligent throttling prevents alert spam
- **Threshold-Based Triggers**:
  - Gas: Warning at 300 ppm, Danger at 500 ppm
  - Temperature: Warning at 35°C, Danger at 45°C
  - Distance: Warning at 100 cm, Danger at 800 cm
  - Vibration: Warning at 5g, Danger at 10g

### 📹 Computer Vision Monitoring

- **6 Camera Feeds**: Main Entrance, Assembly Line, Warehouse, Heavy Machinery, Loading Dock, QC Station
- **YOLOv8 Detection**: Real-time PPE detection (helmets, vests), hazard zone violations, unsafe behavior
- **Violation Tracking**: Live list with acknowledgment feature and severity classification
- **Detection Types**: No Helmet, No Vest, Unsafe Behavior, Hazard Zone Violation, Equipment Misuse
- **Confidence Scores**: AI confidence levels (Low/Medium/High/Critical) with adjustable thresholds

### 📊 Reports & Analytics

- **Dynamic Statistics**: Total violations, critical alerts, average response time
- **Interactive Charts**: 
  - Incident trends (line chart with daily/weekly/monthly views)
  - Severity distribution (pie chart breakdown)
- **Time Period Filters**: Today, Week, Month, Quarter, Year
- **Auto-Refresh**: Updates every 30 seconds with real database queries
- **Export Capabilities**: CSV/PDF report generation (planned)

### ⚙️ System Features

- **Dual Operating Modes**: Shop Floor / Heavy Industry with customized configurations
- **Dark/Light Theme**: User preference persistence across sessions
- **Responsive Design**: Mobile, tablet, desktop optimized layouts
- **Database Seeding**: Automatic demo data generation for testing
- **Custom Branding**: AI-Smarter-Shop logo integration throughout UI
- **Settings Management**: Configurable thresholds, alert preferences, system parameters

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                               │
│  React 19.1.1 + TypeScript + Vite + Tailwind CSS (Port 5173)       │
│                                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │Dashboard │  │ CV Mon.  │  │ Reports  │  │ Settings │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└───────────────────────────┬───────────────────────────────────────┘
                            │ HTTP/WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Backend Layer                                │
│         FastAPI 0.104.1 + SQLAlchemy + Uvicorn (Port 8000)         │
│                                                                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │ Sensors │  │   CV    │  │ Reports │  │ Alerts  │  │ Arduino │ │
│  │  API    │  │  API    │  │   API   │  │   API   │  │   API   │ │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘ │
│                                                                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐               │
│  │ YOLOv8  │  │ Alert   │  │Database │  │  Auth   │               │
│  │ Engine  │  │ Service │  │ Manager │  │ Service │               │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘               │
└───────────┬─────────────┬────────────┬─────────────┬───────────────┘
            │             │            │             │
            ▼             ▼            ▼             ▼
┌─────────────┐  ┌────────────┐  ┌─────────┐  ┌─────────────┐
│   SQLite    │  │  Arduino   │  │  Gmail  │  │   Twilio    │
│  Database   │  │  ESP8266   │  │  SMTP   │  │     SMS     │
│             │  │10.54.156   │  │         │  │             │
│- Cameras    │  │   .112     │  │ Email   │  │SMS Alerts   │
│- Detections │  │            │  │ Alerts  │  │             │
│- Alerts     │  │- DHT11     │  └─────────┘  └─────────────┘
│- Settings   │  │- MQ-135    │
│- Workers    │  │- HC-SR04   │
└─────────────┘  │- MFRC522   │
                 └────────────┘
```

### Data Flow

1. **Sensor Data Flow**: Arduino → Backend Proxy → Database → Frontend (15s refresh)
2. **CV Detection Flow**: Cameras → YOLOv8 → Database → Frontend → Acknowledgment
3. **Alert Flow**: Backend monitors thresholds → Email/SMS services → User notification
4. **Report Flow**: Database aggregation → Analytics processing → Charts/Statistics

---

## 🛠️ Tech Stack

### Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.104.1 | High-performance async web framework |
| **Server** | Uvicorn | 0.24.0 | ASGI server with hot reload |
| **Database** | SQLite / PostgreSQL | 3.x / 14+ | Data persistence |
| **ORM** | SQLAlchemy (Async) | 2.0.23 | Database abstraction layer |
| **Async DB Driver** | aiosqlite | 0.19.0 | Async SQLite operations |
| **HTTP Client** | httpx | 0.25.2 | Arduino communication |
| **Email** | smtplib | Built-in | Gmail SMTP alerts |
| **SMS** | Twilio | 8.10.0 | SMS notifications |
| **AI Framework** | TensorFlow | 2.15.0 | Deep learning models |
| **Object Detection** | Ultralytics YOLOv8 | 8.0.220 | Real-time CV detection |
| **Image Processing** | OpenCV | 4.8.1.78 | Video frame processing |
| **Data Science** | NumPy, Pandas | 1.26.2, 2.1.3 | Data analysis |
| **ML Library** | Scikit-learn | 1.3.2 | Anomaly detection |
| **Validation** | Pydantic | 2.5.0 | Request/response validation |
| **WebSockets** | websocket | 12.0 | Real-time updates |

### Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | React | 19.1.1 | UI component library |
| **Language** | TypeScript | 5.9.3 | Type-safe JavaScript |
| **Build Tool** | Vite | 7.1.7 | Fast development server |
| **Styling** | Tailwind CSS | 3.4 | Utility-first CSS |
| **HTTP Client** | Axios | 1.12.2 | API communication |
| **Charts** | Recharts | 3.2.1 | Data visualization |
| **Icons** | Lucide React | 0.545.0 | Modern icon library |
| **Notifications** | React Hot Toast | 2.6.0 | Toast messages |
| **Routing** | React Router DOM | 7.9.4 | Client-side routing |
| **Headless UI** | @headlessui/react | 2.2.9 | Accessible components |

### Hardware Components

| Component | Model | Specs | Purpose |
|-----------|-------|-------|---------|
| **Microcontroller** | ESP8266 | WiFi, 80MHz, 4MB | IoT controller |
| **Temperature** | DHT11 | 0-50°C, ±2°C | Climate monitoring |
| **Gas Sensor** | MQ-135 | NH3, NOx, CO2 | Air quality detection |
| **Distance** | HC-SR04 | 2-400cm, Ultrasonic | Proximity detection |
| **RFID Reader** | MFRC522 | 13.56MHz | Access control |
| **Network** | WiFi (Klassy) | 10.54.156.112 | Local network |

---

## 📦 Installation

### Prerequisites

Before starting, ensure you have:

- ✅ **Node.js** 18+ and npm 9+
- ✅ **Python** 3.10+
- ✅ **Git** for version control
- ✅ **Arduino IDE** (optional, for ESP8266 programming)
- ✅ **Gmail Account** with App Password (for email alerts)
- ✅ **Twilio Account** (optional, for SMS alerts)

### Backend Installation

```bash
# 1. Clone the repository
git clone https://github.com/Klassy01/AI-Safety-Shop.git
cd AI-Safety-Shop/backend

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create environment file
cp .env.example .env

# 6. Configure environment variables
nano .env  # Or use your preferred editor

# 7. Initialize database (automatic on first run)
# Database will be created at: backend/data/ai_safety_monitoring.db

# 8. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
INFO:     Database initialized successfully
INFO:     Database seeded successfully
```

### Frontend Installation

```bash
# 1. Navigate to frontend directory
cd ../frontend

# 2. Install dependencies
npm install

# 3. Create environment file
cp .env.example .env

# 4. Configure environment variables
nano .env

# 5. Start development server
npm run dev
```

**Expected Output:**
```
VITE v7.1.7  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.1.100:5173/
➜  press h + enter to show help
```

### Quick Start (All-in-One)

```bash
# Terminal 1: Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm install && npm run dev
```

---

## ⚙️ Configuration

### Backend Configuration (.env)

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Database (SQLite for dev, PostgreSQL for production)
DATABASE_URL=sqlite:///./data/ai_safety_monitoring.db
# DATABASE_URL=postgresql://user:pass@localhost:5432/ai_safety

# Email Configuration (Gmail SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your_app_password_here
ALERT_EMAIL_FROM=your-email@gmail.com
ALERT_EMAIL_TO=recipient@gmail.com

# SMS Configuration (Twilio)
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
ALERT_PHONE_NUMBER=+0987654321

# Arduino Configuration
ARDUINO_ENDPOINT=http://10.54.156.112/
ARDUINO_TIMEOUT=5

# Sensor Thresholds
GAS_WARNING_THRESHOLD=300
GAS_DANGER_THRESHOLD=500
TEMPERATURE_WARNING_THRESHOLD=35
TEMPERATURE_DANGER_THRESHOLD=45
PROXIMITY_WARNING_THRESHOLD=100
PROXIMITY_DANGER_THRESHOLD=800
VIBRATION_WARNING_THRESHOLD=5
VIBRATION_DANGER_THRESHOLD=10

# AI Configuration
AI_MODEL_PATH=./models
AI_CONFIDENCE_THRESHOLD=0.75
ANOMALY_DETECTION_SENSITIVITY=medium

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend Configuration (.env)

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000

# WebSocket URL (optional)
VITE_WS_URL=ws://localhost:8000/ws

# Refresh intervals (milliseconds)
VITE_REFRESH_INTERVAL=15000
```

### Email Setup (Gmail)

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Factor Authentication**
3. Navigate to **App Passwords** → Select **Mail** → Generate
4. Copy the 16-character password to `SMTP_PASSWORD` in `.env`

### SMS Setup (Twilio)

1. Sign up at [twilio.com](https://www.twilio.com/)
2. Get **Account SID** and **Auth Token** from dashboard
3. Purchase a **phone number** ($1/month)
4. Add credentials to `.env` file
5. Verify recipient phone number in Twilio console

---

## 🔌 Hardware Setup

### Arduino ESP8266 Wiring

```
ESP8266 Pin Connections:
├── DHT11 (Temperature & Humidity)
│   ├── VCC → 3.3V
│   ├── GND → GND
│   └── DATA → D4 (GPIO2)
│
├── MQ-135 (Gas Sensor)
│   ├── VCC → 5V (if available, else 3.3V)
│   ├── GND → GND
│   └── AOUT → A0 (Analog)
│
├── HC-SR04 (Ultrasonic Distance)
│   ├── VCC → 5V
│   ├── GND → GND
│   ├── TRIG → D3 (GPIO0)
│   └── ECHO → D8 (GPIO15)
│
└── MFRC522 (RFID Reader) - SPI
    ├── VCC → 3.3V
    ├── GND → GND
    ├── RST → D1 (GPIO5)
    ├── SDA → D2 (GPIO4)
    ├── MOSI → D7 (GPIO13)
    ├── MISO → D6 (GPIO12)
    └── SCK → D5 (GPIO14)
```

### Arduino Code

The Arduino code is provided in the repository. Key features:

- Serves sensor data via HTTP on port 80
- HTML-formatted response for easy parsing
- Auto-refresh every 15 seconds
- Static IP: 10.54.156.112

### Network Configuration

```cpp
const char* ssid = "Klassy";  // Your WiFi SSID
const char* password = "your_password";
IPAddress staticIP(10, 54, 156, 112);
IPAddress gateway(10, 54, 156, 1);
IPAddress subnet(255, 255, 255, 0);
```

### Testing Arduino Connection

```bash
# Test Arduino HTTP endpoint
curl http://10.54.156.112/

# Expected response: HTML page with sensor readings
```

---

## 🎮 Usage

### Accessing the Dashboard

1. **Start Backend**: `http://localhost:8000`
2. **Start Frontend**: `http://localhost:5173`
3. **Open Browser**: Navigate to frontend URL

### Dashboard Features

#### 1. **Dashboard Page** (`/`)

- **Live Sensor Cards**: Temperature, Humidity, Gas, Distance, RFID
- **Status Indicators**: Green (Normal), Yellow (Warning), Red (Danger)
- **Real-Time Charts**: Line graphs showing last 20 data points
- **Alert Panel**: Active warnings and critical alerts
- **Statistics**: Data points collected, active alerts, system uptime

#### 2. **CV Monitoring Page** (`/cv-monitoring`)

- **Camera Grid**: 6 camera feeds with status indicators
- **Recent Violations**: Scrollable list of safety violations
- **Acknowledgment**: Mark violations as reviewed
- **Filters**: By camera, type, severity
- **Statistics**: Total detections, by type, severity distribution

#### 3. **Reports Page** (`/reports`)

- **Summary Cards**: Total violations, critical alerts, avg response time
- **Incident Trends**: Line chart with time-series data
- **Severity Distribution**: Pie chart breakdown
- **Time Filters**: Today, Week, Month, Quarter, Year
- **Incident Table**: Detailed list with timestamps and actions

#### 4. **Settings Page** (`/settings`)

- **Operating Mode**: Switch between Shop Floor / Heavy Industry
- **Theme Toggle**: Dark/Light mode
- **Alert Config**: Enable/disable email, SMS, sound alerts
- **Threshold Settings**: Adjust warning/danger levels for all sensors
- **System Config**: Refresh intervals, auto-shutdown, API endpoints

### Testing Alerts

#### Email Alert Test

```bash
curl -X POST http://localhost:8000/test/alert/email
```

**Response:**
```json
{
  "success": true,
  "message": "Test email sent successfully!",
  "email_to": "davidjayaraj01@gmail.com"
}
```

#### SMS Alert Test

```bash
curl -X POST http://localhost:8000/test/alert/sms
```

**Response:**
```json
{
  "success": true,
  "message": "Test SMS sent successfully!",
  "phone_to": "+919840488355"
}
```

#### Manual Alert Trigger

```bash
curl -X POST "http://localhost:8000/alert/manual?sensor_type=gas&value=600"
```

---

## 📡 API Documentation

### Base URL

```
http://localhost:8000
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Sensor Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sensors` | Get all sensor data |
| GET | `/sensors/live/arduino` | Get live Arduino data with alerts |
| GET | `/sensors/{type}/history` | Get sensor history (24h default) |
| POST | `/sensors` | Create sensor data entry |

#### CV Monitoring Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cv/cameras` | Get all cameras |
| GET | `/cv/detections` | Get detections (filterable) |
| POST | `/cv/detections` | Create new detection |
| PATCH | `/cv/detections/{id}/acknowledge` | Acknowledge violation |
| GET | `/cv/stats` | Get CV statistics |

#### Reports Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports` | Get report summary |
| GET | `/reports/analytics` | Get analytics data |
| GET | `/reports/list` | Get incident list |

#### Alert Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/alerts/active` | Get active alerts |
| GET | `/alert/config` | Get alert configuration |
| POST | `/alert/manual` | Trigger manual alert |
| POST | `/test/alert/email` | Test email configuration |
| POST | `/test/alert/sms` | Test SMS configuration |
| PUT | `/alerts/{id}/acknowledge` | Acknowledge alert |

### Example API Call

```bash
# Get live Arduino sensor data
curl -X GET "http://localhost:8000/sensors/live/arduino"
```

**Response:**
```json
{
  "status": "connected",
  "source": "arduino_esp8266",
  "endpoint": "http://10.54.156.112/",
  "sensors": {
    "temperature": {
      "value": 28.5,
      "unit": "°C",
      "status": "normal",
      "threshold": {"warning": 35, "danger": 45}
    },
    "humidity": {
      "value": 65,
      "unit": "%",
      "status": "normal"
    },
    "gas": {
      "value": 219,
      "unit": "ppm",
      "status": "normal",
      "threshold": {"warning": 300, "danger": 500}
    },
    "ultrasonic": {
      "value": 150,
      "unit": "cm",
      "status": "normal",
      "threshold": {"warning": 100, "danger": 800}
    },
    "rfid": {
      "value": "A1:B2:C3:D4",
      "status": "active"
    }
  },
  "timestamp": "2025-10-17T10:30:45.123Z",
  "alerts_triggered": null
}
```

---

## 🚀 Deployment

### Docker Deployment

#### Backend Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/ai_safety
    depends_on:
      - db
    volumes:
      - ./backend/data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:14
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: ai_safety
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### Deploy Commands

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Cloud Deployment

#### Vercel (Frontend)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel --prod
```

#### Heroku (Backend)

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create ai-safety-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main
```

#### AWS EC2 (Full Stack)

```bash
# Connect to EC2 instance
ssh -i key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip nodejs npm nginx

# Clone repository
git clone https://github.com/Klassy01/AI-Safety-Shop.git

# Setup backend
cd AI-Safety-Shop/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Setup frontend
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/html/

# Configure Nginx
sudo nano /etc/nginx/sites-available/default
sudo systemctl restart nginx
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Arduino Connection Failed

```bash
# Error: "Arduino connection timeout - device offline"

# Solutions:
1. Check Arduino is powered on
2. Verify WiFi connection: ping 10.54.156.112
3. Test Arduino HTTP: curl http://10.54.156.112/
4. Check ARDUINO_ENDPOINT in .env
5. Verify Arduino code is uploaded correctly
```

#### 2. Email Alerts Not Sending

```bash
# Error: "Failed to send email"

# Solutions:
1. Verify Gmail App Password (not regular password)
2. Check 2FA is enabled on Google Account
3. Test SMTP: curl -X POST http://localhost:8000/test/alert/email
4. Check SMTP_USER and SMTP_PASSWORD in .env
5. Verify recipient email in ALERT_EMAIL_TO
```

#### 3. SMS Alerts Not Sending

```bash
# Error: "Failed to send SMS"

# Solutions:
1. Verify Twilio Account SID and Auth Token
2. Check phone number is verified in Twilio console
3. Test SMS: curl -X POST http://localhost:8000/test/alert/sms
4. Ensure phone number format: +919840488355 (country code included)
5. Check Twilio account balance
```

#### 4. Database Issues

```bash
# Error: "Database connection failed"

# Solutions:
1. Delete database: rm backend/data/ai_safety_monitoring.db
2. Restart backend (auto-creates database)
3. Check DATABASE_URL in .env
4. For PostgreSQL: verify credentials and server status
```

#### 5. CORS Errors

```javascript
// Error: "CORS policy: No 'Access-Control-Allow-Origin'"

// Solutions:
1. Check CORS_ORIGINS in backend/.env includes frontend URL
2. Restart backend after .env changes
3. Use backend proxy for Arduino calls (already implemented)
4. Clear browser cache: Ctrl+Shift+Delete
```

#### 6. Frontend Build Errors

```bash
# Error: npm build fails

# Solutions:
1. Clear cache: rm -rf node_modules package-lock.json
2. Reinstall: npm install
3. Clear Vite cache: rm -rf .vite
4. Check Node.js version: node --version (must be 18+)
5. Update dependencies: npm update
```

#### 7. YOLOv8 Model Not Found

```bash
# Error: "Model file not found"

# Solutions:
1. Download models:
   - best.pt (custom trained)
   - yolov8n.pt (official)
2. Place in: backend/app/models/
3. Update AI_MODEL_PATH in .env
4. Verify file permissions: chmod 644 backend/app/models/*.pt
```

### Debug Mode

Enable detailed logging:

```bash
# Backend
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --log-level debug

# Frontend
VITE_DEBUG=true npm run dev
```

### Health Check

```bash
# Check backend status
curl http://localhost:8000/

# Check Arduino status
curl http://localhost:8000/api/arduino/status

# Check database
sqlite3 backend/data/ai_safety_monitoring.db "SELECT COUNT(*) FROM cameras;"
```

---

## 📚 Documentation

### Detailed Documentation

- **[Backend README](./backend/README.md)** - Complete backend guide (API, database, Arduino, alerts)
- **[Frontend README](./frontend/README.md)** - Complete frontend guide (components, state, styling)

### Project Structure

```
AI-Safety-Shop/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── ai/                # AI/ML modules
│   │   │   └── cv_detector.py # YOLOv8 computer vision
│   │   ├── db/                # Database layer
│   │   │   ├── database.py    # SQLAlchemy config
│   │   │   └── seed_data.py   # Demo data seeding
│   │   ├── models/            # Data models
│   │   │   ├── models.py      # SQLAlchemy models
│   │   │   ├── schemas.py     # Pydantic schemas
│   │   │   ├── best.pt        # Custom YOLOv8 model
│   │   │   └── yolov8n.pt     # Official YOLOv8 nano
│   │   ├── routes/            # API endpoints
│   │   │   ├── sensors.py     # Sensor data API
│   │   │   ├── cv_detection.py# CV monitoring API
│   │   │   ├── reports.py     # Reports & analytics
│   │   │   ├── alerts.py      # Alert management
│   │   │   ├── arduino_sensors.py # Arduino proxy
│   │   │   └── settings.py    # System settings
│   │   ├── services/          # Business logic
│   │   │   └── alert_service.py # Email/SMS alerts
│   │   └── main.py            # FastAPI app entry
│   ├── data/                  # SQLite database
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment config
│   └── README.md              # Backend docs
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── Navbar.tsx     # Top navigation
│   │   │   ├── Sidebar.tsx    # Side menu
│   │   │   ├── SensorCard.tsx # Sensor display
│   │   │   ├── CameraFeed.tsx # Camera view
│   │   │   ├── ViolationCard.tsx # Violation display
│   │   │   ├── Chart.tsx      # Recharts wrapper
│   │   │   └── AlertPanel.tsx # Alert notifications
│   │   ├── context/           # React Context
│   │   │   ├── ModeContext.tsx # Operating mode state
│   │   │   └── AlertContext.tsx # Alert state
│   │   ├── pages/             # Main pages
│   │   │   ├── Dashboard.tsx  # Live sensor dashboard
│   │   │   ├── CVMonitoring.tsx # CV monitoring
│   │   │   ├── Reports.tsx    # Reports & analytics
│   │   │   └── Settings.tsx   # System settings
│   │   ├── services/          # API client
│   │   │   └── api.ts         # Axios API service
│   │   ├── types/             # TypeScript types
│   │   │   └── index.ts       # Shared interfaces
│   │   └── main.tsx           # React entry point
│   ├── public/                # Static assets
│   │   └── logo.png           # App logo
│   ├── package.json           # Node dependencies
│   ├── tailwind.config.js     # Tailwind config
│   ├── vite.config.ts         # Vite config
│   └── README.md              # Frontend docs
│
└── README.md                   # This file
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/AmazingFeature`
3. **Commit** your changes: `git commit -m 'Add some AmazingFeature'`
4. **Push** to the branch: `git push origin feature/AmazingFeature`
5. **Open** a Pull Request

### Coding Standards

#### Backend (Python)

- Follow **PEP 8** style guide
- Use **type hints** for function signatures
- Add **docstrings** for classes and functions
- Write **unit tests** for new features
- Maximum line length: **120 characters**

```python
def calculate_risk_score(sensor_data: Dict[str, float]) -> float:
    """
    Calculate overall risk score from sensor data.
    
    Args:
        sensor_data: Dictionary containing sensor readings
        
    Returns:
        Risk score between 0-100
    """
    # Implementation here
    pass
```

#### Frontend (TypeScript/React)

- Follow **React best practices**
- Use **TypeScript** for all new code
- Use **functional components** with hooks
- Follow **Tailwind CSS** utility-first approach
- Add **JSDoc comments** for complex functions

```typescript
/**
 * Fetches live sensor data from Arduino
 * @returns Promise with sensor data
 */
const fetchSensorData = async (): Promise<SensorData> => {
  const response = await sensorsApi.getLiveArduinoData();
  return response.data;
};
```

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Linting
npm run lint
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add voice alert system
fix: resolve Arduino connection timeout
docs: update installation instructions
style: format code with black
refactor: improve anomaly detection algorithm
test: add tests for alert service
chore: update dependencies
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 AI-Smarter-Shop

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 👥 Authors

- **David Jayaraj** - *System Architecture & Integration* - [GitHub](https://github.com/Klassy01)
- **Development Team** - *Frontend, Backend, Hardware Integration*

---

## 🙏 Acknowledgments

Special thanks to:

- **FastAPI** - High-performance Python web framework
- **React Team** - Modern UI library
- **Vite** - Next-generation frontend tooling
- **Tailwind CSS** - Utility-first CSS framework
- **Ultralytics** - YOLOv8 object detection
- **Twilio** - SMS communication platform
- **Google** - Gmail SMTP service
- **Arduino Community** - ESP8266 support and libraries
- **Open Source Community** - Countless libraries and tools

---

## 📞 Support & Contact

### Get Help

- 📧 **Email**: davidjayaraj01@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/Klassy01/AI-Safety-Shop/issues)
- 📖 **Documentation**: [Backend](./backend/README.md) | [Frontend](./frontend/README.md)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Klassy01/AI-Safety-Shop/discussions)

### Reporting Bugs

When reporting bugs, please include:

1. **Environment**: OS, Python version, Node version
2. **Steps to reproduce**: Clear step-by-step instructions
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Logs**: Relevant error messages or stack traces
6. **Screenshots**: If applicable

### Feature Requests

We love new ideas! When suggesting features:

1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives**: Other approaches considered
4. **Additional context**: Screenshots, mockups, etc.

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐!

[![Star History Chart](https://api.star-history.com/svg?repos=Klassy01/AI-Safety-Shop&type=Date)](https://star-history.com/#Klassy01/AI-Safety-Shop&Date)

---

## 📈 Project Stats

![GitHub repo size](https://img.shields.io/github/repo-size/Klassy01/AI-Safety-Shop)
![GitHub contributors](https://img.shields.io/github/contributors/Klassy01/AI-Safety-Shop)
![GitHub stars](https://img.shields.io/github/stars/Klassy01/AI-Safety-Shop?style=social)
![GitHub forks](https://img.shields.io/github/forks/Klassy01/AI-Safety-Shop?style=social)
![GitHub issues](https://img.shields.io/github/issues/Klassy01/AI-Safety-Shop)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Klassy01/AI-Safety-Shop)
![GitHub last commit](https://img.shields.io/github/last-commit/Klassy01/AI-Safety-Shop)

---

## 🚀 Roadmap

### Version 2.0 (Planned)

- [ ] **Mobile App**: Native iOS/Android app with push notifications
- [ ] **Voice Alerts**: Text-to-speech announcements without extra hardware
- [ ] **Advanced Analytics**: ML-powered incident prediction
- [ ] **Multi-Site Support**: Manage multiple locations from one dashboard
- [ ] **Incident Reports**: Automated PDF report generation
- [ ] **Integration APIs**: Connect with existing ERP/MES systems
- [ ] **Edge Computing**: Run AI models on ESP32-CAM
- [ ] **Blockchain**: Immutable audit trail for compliance
- [ ] **AR Overlays**: Augmented reality safety visualization
- [ ] **Drone Integration**: Aerial monitoring for large facilities

### Version 1.5 (In Progress)

- [x] Real-time Arduino sensor integration
- [x] YOLOv8 computer vision detection
- [x] Email and SMS alert system
- [x] Comprehensive analytics dashboard
- [ ] Export reports (CSV/PDF)
- [ ] User authentication and roles
- [ ] Notification preferences per user
- [ ] Historical trend analysis

---

<div align="center">

**Built with ❤️ for safer workplaces**

*Last Updated: October 17, 2025*

[⬆ Back to Top](#-ai-smarter-shop-industrial-iot-safety-monitoring-system)

</div>
