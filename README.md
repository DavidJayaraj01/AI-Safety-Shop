# AI-Powered Safety Monitoring System for Smarter Shop Floors

A comprehensive full-stack IoT safety monitoring system using ESP32, YOLOv8n for PPE detection, multi-sensor integration, and AI-powered analytics.

## 🚀 Features

### Core Capabilities
- **Real-Time PPE Detection**: YOLOv8n computer vision for helmet, vest, gloves, goggles, and safety shoes detection
- **Multi-Sensor IoT Integration**: Gas (MQ series), Temperature/Humidity (DHT22), Vibration, Ultrasonic proximity, RFID
- **AI Anomaly Detection**: Machine learning models for predictive maintenance and unsafe behavior detection
- **Multi-Channel Alerts**: SMS (Twilio), Email, Telegram, Slack, in-app notifications
- **Auto-Shutdown System**: Critical alert response with relay control
- **Real-Time Dashboard**: Live sensor data, worker tracking, incident reports

### Operating Modes
1. **Heavy Industry Mode**: Gas leak detection, vibration monitoring, auto-shutdown
2. **Shop Floor Mode**: PPE compliance, proximity alerts, fall detection, posture analysis

## 📋 Project Structure

```
AI-Safety-Monitor/
├── frontend/                 # React + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Dashboard, Reports, Settings
│   │   ├── context/         # State management (Zustand)
│   │   ├── services/        # API integration
│   │   └── types/           # TypeScript definitions
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── api/             # REST API endpoints
│   │   ├── detection/       # YOLOv8 PPE detector
│   │   ├── mqtt/            # MQTT client for ESP32
│   │   ├── ml/              # Anomaly detection models
│   │   ├── alerts/          # Multi-channel notifier
│   │   ├── models/          # Database models
│   │   └── core/            # Configuration
│   ├── main.py
│   └── requirements.txt
│
├── esp32/                    # Arduino firmware for ESP32
│   └── safety_monitor.ino
│
├── docker-compose.yml        # Full stack deployment
└── README.md

```

## 🛠️ Technology Stack

### Frontend
- **Framework**: Vite + React 18 + TypeScript
- **Styling**: Tailwind CSS v3.4
- **State Management**: Zustand
- **Routing**: React Router v6
- **Charts**: Recharts
- **Notifications**: react-hot-toast
- **HTTP Client**: Axios
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL + SQLAlchemy
- **Cache**: Redis
- **MQTT**: Paho MQTT (Mosquitto broker)
- **AI/ML**: 
  - YOLOv8 (Ultralytics)
  - Scikit-learn (Isolation Forest)
  - Prophet (Time series forecasting)
  - OpenCV (Computer vision)
- **Alerts**:
  - Twilio (SMS)
  - SMTP (Email)
  - Telegram Bot API
  - Slack Webhooks

### Hardware
- **Microcontroller**: ESP32
- **Sensors**:
  - MQ-2/MQ-135 (Gas detection)
  - DHT22 (Temperature & Humidity)
  - SW-420 (Vibration)
  - HC-SR04 (Ultrasonic proximity)
  - RC522 (RFID)
  - Active buzzer & LED indicators
  - Relay module (Auto-shutdown)

## 🚦 Quick Start

### Prerequisites
```bash
- Node.js 18+
- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Mosquitto MQTT Broker
- ESP32 + Arduino IDE
- Camera (USB/IP) for PPE detection
```

### 1. Clone Repository
```bash
git clone <repository-url>
cd AI-Safety-Monitor
```

### 2. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your configuration
npm run dev
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python main.py
```

### 4. Database Setup
```bash
# Create PostgreSQL database
createdb safety_monitor

# Run migrations (implement with Alembic)
alembic upgrade head
```

### 5. ESP32 Setup
```bash
1. Open esp32/safety_monitor.ino in Arduino IDE
2. Install libraries: WiFi, PubSubClient, ArduinoJson, DHT
3. Update WiFi credentials and MQTT broker IP
4. Connect sensors according to pin definitions
5. Upload to ESP32
```

### 6. Docker Deployment (Recommended)
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📡 MQTT Topics

```
sensors/gas          - Gas sensor readings
sensors/temperature  - Temperature readings
sensors/vibration    - Vibration data
sensors/ultrasonic   - Proximity distance
sensors/environment  - Humidity, pressure
rfid/entry           - Worker entry events
rfid/exit            - Worker exit events
control/shutdown     - Emergency shutdown command
alerts/ppe           - PPE violation alerts
```

## 🎯 API Endpoints

### Sensors
- `GET /api/sensors` - Get all sensors
- `GET /api/sensors/{id}/readings` - Get sensor readings
- `GET /api/sensors/readings/latest` - Latest readings

### Alerts
- `GET /api/alerts` - Get alerts (with filters)
- `PUT /api/alerts/{id}/resolve` - Resolve alert

### Workers
- `GET /api/workers` - Get all workers
- `GET /api/workers/active` - Get active workers

### PPE Detection
- `GET /api/ppe/detections/latest` - Latest PPE detections
- `GET /api/ppe/compliance` - Compliance rate

### Analytics
- `GET /api/analytics/dashboard` - Dashboard statistics

### Camera
- `GET /api/camera/stream` - Live video stream with PPE detection
- `POST /api/camera/detection` - Toggle detection on/off

## 🔧 Configuration

### Environment Variables

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/safety_monitor
REDIS_URL=redis://localhost:6379/0

# MQTT
MQTT_BROKER=localhost
MQTT_PORT=1883

# Twilio SMS
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
ALERT_PHONE_NUMBERS=+1234567890,+0987654321

# Email
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_password
ALERT_EMAILS=admin@example.com

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Thresholds
GAS_WARNING_THRESHOLD=300
GAS_CRITICAL_THRESHOLD=500
TEMP_WARNING_THRESHOLD=40
TEMP_CRITICAL_THRESHOLD=60
```

## 🤖 YOLOv8 PPE Model Training

```bash
# Install Ultralytics
pip install ultralytics

# Train custom PPE model
yolo task=detect mode=train model=yolov8n.pt data=ppe_dataset.yaml epochs=100 imgsz=640

# Export model
yolo export model=best.pt format=onnx

# Copy to backend
cp runs/detect/train/weights/best.pt backend/models/yolov8n-ppe.pt
```

## 📊 Dashboard Features

- **Real-Time Sensor Cards**: Live gas, temperature, vibration readings
- **PPE Compliance Tracking**: Visual indicators for workers
- **Alert Feed**: Color-coded priority alerts
- **Worker Status**: Location tracking and PPE status
- **Live Camera Feed**: Real-time PPE detection overlay
- **Analytics Charts**: Trend analysis and predictions
- **Incident Reports**: Searchable history with PDF export

## 🔐 Security

- Role-based access control (Admin, Supervisor, Viewer)
- JWT authentication for API endpoints
- HTTPS/TLS encryption
- Secure WebSocket connections
- API rate limiting
- Input validation and sanitization

## 📈 Performance

- WebSocket for real-time updates (<100ms latency)
- Redis caching for fast queries
- Optimized YOLOv8n for edge devices (30+ FPS)
- PostgreSQL indexing for large datasets
- Async FastAPI endpoints

## 🐛 Troubleshooting

### Camera not detected
```bash
# List available cameras
ls /dev/video*

# Update CAMERA_INDEX in .env
CAMERA_INDEX=0
```

### MQTT connection failed
```bash
# Check Mosquitto status
systemctl status mosquitto

# Test connection
mosquitto_sub -h localhost -t '#' -v
```

### Database connection error
```bash
# Check PostgreSQL
psql -U postgres -d safety_monitor -c "SELECT 1"
```

## 📝 License

MIT License - see LICENSE file

## 👥 Contributors

Your Name - Initial Development

## 🙏 Acknowledgments

- Ultralytics for YOLOv8
- FastAPI team
- React and Vite communities
- ESP32 community

## 📞 Support

For issues and questions:
- GitHub Issues: <repository-url>/issues
- Email: support@example.com
- Documentation: <docs-url>

---

**⚠️ Safety Notice**: This system is designed to assist in safety monitoring but should not replace proper safety training, procedures, and human oversight. Always follow your organization's safety protocols.
