# Quick Start Guide

## 🎯 Getting Started in 5 Minutes

### Option 1: Docker (Recommended)

```bash
# 1. Clone and navigate
cd AI-Safety-Monitor

# 2. Run setup script
./setup.sh

# 3. Configure environment
# Edit backend/.env and frontend/.env with your settings

# 4. Start all services
docker-compose up -d

# 5. Initialize database
docker-compose exec backend python init_db.py

# 6. Open browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python main.py
```

#### Services
```bash
# PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=safety_monitor postgres:15

# Redis
docker run -d -p 6379:6379 redis:7-alpine

# Mosquitto MQTT
docker run -d -p 1883:1883 -p 9001:9001 eclipse-mosquitto:2
```

## 🔧 ESP32 Setup

1. Open Arduino IDE
2. Install Libraries:
   - WiFi (built-in)
   - PubSubClient
   - ArduinoJson
   - DHT sensor library
3. Open `esp32/safety_monitor.ino`
4. Configure WiFi and MQTT:
   ```cpp
   const char* ssid = "Your_WiFi_SSID";
   const char* password = "Your_WiFi_Password";
   const char* mqtt_server = "192.168.1.100"; // Your computer IP
   ```
5. Connect sensors:
   - Gas (MQ-2): Pin 34
   - Temperature (DHT22): Pin 27
   - Vibration: Pin 35
   - Ultrasonic: Trig=5, Echo=18
   - Buzzer: Pin 25
   - LED: Pin 2
   - Relay: Pin 26
6. Upload to ESP32

## 📊 Test the System

### 1. Verify Services
```bash
# Check all containers are running
docker-compose ps

# Check logs
docker-compose logs -f
```

### 2. Test MQTT
```bash
# Subscribe to all topics
mosquitto_sub -h localhost -t '#' -v

# Publish test message (in another terminal)
mosquitto_pub -h localhost -t 'sensors/gas' -m '{"sensor_id":"gas_1","value":450,"location":"Test"}'
```

### 3. Test API
```bash
# Health check
curl http://localhost:8000/health

# Get sensors
curl http://localhost:8000/api/sensors

# Get alerts
curl http://localhost:8000/api/alerts
```

### 4. Test WebSocket
Open browser console on dashboard and check for WebSocket connection messages.

### 5. Test PPE Detection
- Ensure a camera is connected
- Navigate to Dashboard → Camera Feed
- Stand in front of camera wearing PPE items

## ⚙️ Configuration

### Essential Settings

#### 1. Alert Notifications

**SMS (Twilio):**
```env
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1234567890
ALERT_PHONE_NUMBERS=+1234567890,+0987654321
```

**Email:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_EMAILS=admin@example.com,supervisor@example.com
```

**Telegram:**
1. Create bot with @BotFather
2. Get bot token
3. Get your chat ID from @userinfobot
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789
```

**Slack:**
1. Create incoming webhook in Slack
2. Copy webhook URL
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00/B00/XXX
```

#### 2. Sensor Thresholds

```env
GAS_WARNING_THRESHOLD=300        # PPM
GAS_CRITICAL_THRESHOLD=500       # PPM
TEMP_WARNING_THRESHOLD=40        # °C
TEMP_CRITICAL_THRESHOLD=60       # °C
VIBRATION_WARNING_THRESHOLD=8    # m/s²
VIBRATION_CRITICAL_THRESHOLD=15  # m/s²
```

#### 3. Camera Settings

```env
CAMERA_INDEX=0                   # 0 for /dev/video0
CAMERA_WIDTH=1920
CAMERA_HEIGHT=1080
CAMERA_FPS=30
PPE_CONFIDENCE_THRESHOLD=0.6     # 60% confidence
```

## 🚨 Troubleshooting

### Frontend won't start
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend errors
```bash
# Check Python version (needs 3.10+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database connection error
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Recreate database
docker-compose down -v
docker-compose up -d postgres
python init_db.py
```

### MQTT not receiving messages
```bash
# Check ESP32 serial monitor for connection status
# Check Mosquitto logs
docker-compose logs mosquitto

# Test local publish
mosquitto_pub -h localhost -t 'test' -m 'hello'
mosquitto_sub -h localhost -t 'test'
```

### Camera not detected
```bash
# List cameras
ls -l /dev/video*

# Test camera
ffplay /dev/video0

# Update CAMERA_INDEX in .env
```

## 📱 Mobile Access

To access from mobile devices on same network:

1. Find your computer's IP:
   ```bash
   ip addr show  # Linux
   ipconfig      # Windows
   ```

2. Update frontend/.env:
   ```env
   VITE_API_URL=http://192.168.1.100:8000/api
   VITE_WS_URL=ws://192.168.1.100:8000/ws
   ```

3. Access from mobile: `http://192.168.1.100:3000`

## 🎓 Demo Mode

To run without hardware:

1. Use mock MQTT publisher:
```bash
# Install mosquitto clients
sudo apt install mosquitto-clients

# Run mock sensor script
python scripts/mock_sensors.py
```

2. Disable camera detection:
```env
CAMERA_INDEX=-1  # Disables camera
```

3. Use sample worker data already seeded in `init_db.py`

## 📚 Next Steps

1. ✅ Customize sensor thresholds for your environment
2. ✅ Configure alert channels (SMS, Email, Telegram, Slack)
3. ✅ Train custom YOLOv8 model with your PPE dataset
4. ✅ Add more sensors to ESP32
5. ✅ Configure worker profiles and access levels
6. ✅ Setup automated backups
7. ✅ Deploy to production server

## 💡 Tips

- Start with demo/mock mode to test the system
- Calibrate sensors in your actual environment
- Test alert system during off-hours
- Keep YOLOv8 model updated with new PPE types
- Regular database backups
- Monitor system logs for anomalies

## 🆘 Getting Help

- 📖 Full documentation: `README.md`
- 🐛 Report issues: GitHub Issues
- 💬 Community: Discord/Slack channel
- 📧 Email: support@example.com

---

**Ready to make your workplace safer!** 🛡️✨
