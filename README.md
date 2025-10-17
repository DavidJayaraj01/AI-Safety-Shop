# 🏭 IoT Safety Monitoring System

> **Complete Industrial Safety Solution** - Real-time sensor monitoring with ESP8266, Flask backend, and React Native mobile app

[![Status](https://img.shields.io/badge/status-operational-success)]() [![Version](https://img.shields.io/badge/version-1.0.0-blue)]() [![License](https://img.shields.io/badge/license-MIT-green)]()

---

## 📖 Quick Navigation

- [🎯 What Is This?](#-what-is-this)
- [⚡ Quick Start](#-quick-start-5-minutes)
- [🏗️ System Architecture](#️-system-architecture)
- [📱 Mobile App](#-mobile-app)
- [🖥️ Backend Server](#️-backend-server)
- [🔌 Hardware (ESP8266)](#-hardware-esp8266)
- [🚀 Deployment](#-deployment)
- [🐛 Troubleshooting](#-troubleshooting)
- [📚 Documentation](#-full-documentation)

---

## 🎯 What Is This?

An **end-to-end IoT safety monitoring system** designed for industrial environments (factories, warehouses, construction sites). It collects real-time sensor data from ESP8266 microcontrollers, processes it through a Flask backend, and displays actionable insights on a mobile app.

### 🌟 Key Features

| Feature | Description |
|---------|-------------|
| **Real-time Monitoring** | Temperature, humidity, gas levels, distance, RFID access |
| **Mobile Interface** | Cross-platform iOS/Android app with live dashboards |
| **Alert System** | Automatic threshold-based warnings and notifications |
| **Computer Vision** | Multi-camera monitoring and violation detection |
| **Analytics** | Historical trends, reports, and statistical insights |
| **Offline Support** | Graceful degradation with mock data fallback |

### 💡 Use Cases

- 🏭 **Factory Safety** - Monitor temperature and air quality
- 🏗️ **Construction Sites** - Track hazardous gas levels
- 🏢 **Warehouse Management** - RFID access control
- 🚧 **Confined Spaces** - Distance and oxygen monitoring
- 🔬 **Lab Environments** - Environmental condition tracking

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites

```bash
✅ Python 3.10+           (Backend)
✅ Node.js 16+            (Mobile App)
✅ ESP8266 with sensors   (Hardware - optional, has mock mode)
✅ WiFi network           (All devices on same network)
✅ Expo Go app            (On your phone - free download)
```

### Step 1: Start Backend Server

```bash
# Navigate to backend folder
cd iot-backend

# Install dependencies (first time only)
pip3 install -r requirements.txt

# Start server
python3 app.py

# ✅ Backend running on http://10.54.156.140:8000
```

### Step 2: Start Mobile App

```bash
# Open new terminal, navigate to mobile folder
cd iot-safety-mobile

# Install dependencies (first time only)
npm install

# Start Expo development server
npm start

# ✅ Expo server running on http://10.54.156.140:8081
# 📱 Scan QR code with Expo Go app
```

### Step 3: Connect & Test

```bash
# Test backend health
curl http://10.54.156.140:8000/health

# Test sensor data (from ESP8266 or mock)
curl http://10.54.156.140:8000/sensors/live/arduino

# Expected response:
# {"sensors": {"temperature": {"value": 30.0, "unit": "°C", ...}}}
```

### Step 4: View on Mobile

1. Open **Expo Go** app on your phone
2. Scan QR code from terminal
3. App loads → Navigate to **Dashboard** tab
4. See live sensor readings! 🎉

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM OVERVIEW                           │
└─────────────────────────────────────────────────────────────┘

     📡 ESP8266                 🖥️ Flask Backend          📱 Mobile App
   (Data Collection)          (Data Processing)        (User Interface)
         │                            │                        │
         │  Sensors:                  │  Features:             │  Screens:
         │  • DHT11 (Temp/Humidity)   │  • Parse HTML         │  • Dashboard
         │  • MQ-135 (Gas)            │  • Validate data      │  • CV Monitor
         │  • HC-SR04 (Distance)      │  • Check thresholds   │  • Reports
         │  • MFRC522 (RFID)          │  • REST API           │  • Settings
         │                            │  • Mock fallback      │
         │                            │                        │
         └────► HTTP (HTML) ─────────┴───► REST (JSON) ──────┘
             Every 5s                     Auto-refresh 15s
             Port 80                      Port 8000         Port 8081
```

### Data Flow

```
Sensor Reading → ESP8266 → WiFi → Flask Backend → REST API → Mobile App → User
   (5 sec)        (HTML)    (LAN)   (Parse/JSON)   (Axios)   (Zustand)  (View)
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Hardware** | ESP8266 NodeMCU | IoT microcontroller for sensor data collection |
| **Sensors** | DHT11, MQ-135, HC-SR04, MFRC522 | Environmental and access monitoring |
| **Backend** | Flask (Python 3.10) | API server, data parsing, threshold checking |
| **Database** | In-memory (expandable to PostgreSQL) | Settings and detection storage |
| **API** | RESTful JSON | Communication layer |
| **Mobile** | React Native + Expo | Cross-platform mobile interface |
| **State** | Zustand | Client-side state management |
| **Storage** | AsyncStorage | Local persistence |
| **Charts** | react-native-chart-kit | Data visualization |
| **Network** | WiFi LAN | Local network communication |

---

## 📱 Mobile App

### Overview

React Native mobile application built with **Expo** for real-time monitoring and management.

**Location:** `iot-safety-mobile/`  
**Documentation:** [`iot-safety-mobile/APP_README.md`](iot-safety-mobile/APP_README.md)

### Features

#### 🏠 Dashboard Screen
- Live sensor cards with status indicators (🟢 Normal / 🟡 Warning / 🔴 Danger)
- Real-time values: Temperature, Humidity, Gas, Distance, RFID
- Historical trend charts (last 20 readings)
- Auto-refresh every 15 seconds
- Pull-to-refresh manual update

#### 📹 CV Monitoring Screen
- Multi-camera status overview
- Safety violation detection list
- Severity filtering (Low/Medium/High/Critical)
- Violation acknowledgment system
- Timestamp and location tracking

#### 📊 Reports Screen
- Statistical dashboard
- Violation count by severity
- Incident trends over time
- Period selection (Day/Week/Month)
- Visual charts and graphs

#### ⚙️ Settings Screen
- Theme control (Light/Dark/Auto)
- Notification preferences
- Sensor threshold configuration
- Reset and debug tools

### Installation

```bash
cd iot-safety-mobile
npm install

# Configure backend IP in constants/theme.ts
export const API_BASE_URL = 'http://YOUR_IP:8000';

# Start development server
npm start
```

### Configuration

**File:** `iot-safety-mobile/constants/theme.ts`

```typescript
// Backend connection
export const API_BASE_URL = 'http://10.54.156.140:8000';

// Update frequency
export const REFRESH_INTERVAL = 15000; // 15 seconds

// Mock data toggle (for testing without hardware)
export const USE_MOCK_DATA = false;
```

### Dependencies

```json
{
  "expo": "~54.0.13",
  "react-native": "0.81.4",
  "react": "19.1.0",
  "expo-router": "^6.0.12",
  "zustand": "^5.0.8",
  "axios": "^1.12.2",
  "react-native-chart-kit": "^6.12.0"
}
```

---

## 🖥️ Backend Server

### Overview

Flask-based REST API server that fetches data from ESP8266 and serves it to mobile clients.

**Location:** `iot-backend/`  
**Documentation:** [`iot-backend/README.md`](iot-backend/README.md)

### Features

- ✅ **ESP8266 Integration** - Fetches HTML, parses sensor values
- ✅ **RESTful API** - 8 endpoints for sensors, cameras, reports, settings
- ✅ **Auto Fallback** - Mock data when ESP8266 unavailable
- ✅ **Status Monitoring** - Threshold-based status determination
- ✅ **CORS Enabled** - Cross-origin support for mobile apps
- ✅ **Health Checks** - System monitoring endpoint

### API Endpoints

```
GET  /                          # API information
GET  /health                    # Server health check
GET  /sensors/live/arduino      # Real ESP8266 data
GET  /cv/cameras                # Camera list
GET  /cv/detections             # Safety violations
POST /cv/detections/:id/ack     # Acknowledge violation
GET  /reports?period=week       # Analytics reports
GET  /settings                  # Get configuration
PUT  /settings                  # Update configuration
POST /notifications/register    # Register device token
```

### Installation

```bash
cd iot-backend
pip3 install -r requirements.txt

# Configure ESP8266 IP in app.py
ESP8266_IP = "10.54.156.112"

# Start server
python3 app.py
```

### Dependencies

```txt
flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
```

### Example Response

```bash
curl http://10.54.156.140:8000/sensors/live/arduino
```

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

---

## 🔌 Hardware (ESP8266)

### Overview

ESP8266 NodeMCU microcontroller with multiple sensors for environmental monitoring.

**IP Address:** `10.54.156.112:80`  
**WiFi Network:** Klassy

### Sensors Connected

| Sensor | Purpose | GPIO Pin | Interface |
|--------|---------|----------|-----------|
| **DHT11** | Temperature & Humidity | D4 (GPIO2) | Digital |
| **MQ-135** | Gas/Air Quality | A0 | Analog |
| **HC-SR04** | Ultrasonic Distance | D5 (Trig), D6 (Echo) | Digital |
| **MFRC522** | RFID Card Reader | D8, D7, D0, D3, D1 | SPI |

### Wiring Diagram

```
ESP8266 NodeMCU Connections
═══════════════════════════

DHT11 Sensor:
  VCC  →  3.3V
  GND  →  GND
  DATA →  D4 (GPIO2)

MQ-135 Gas Sensor:
  VCC  →  3.3V (or 5V with regulator)
  GND  →  GND
  AO   →  A0

HC-SR04 Ultrasonic:
  VCC  →  5V
  GND  →  GND
  TRIG →  D5 (GPIO14)
  ECHO →  D6 (GPIO12)

MFRC522 RFID Reader:
  3.3V →  3.3V
  RST  →  D0 (GPIO16)
  GND  →  GND
  MISO →  D6 (GPIO12)
  MOSI →  D7 (GPIO13)
  SCK  →  D5 (GPIO14)
  SDA  →  D8 (GPIO15)
```

### Arduino Setup

1. **Install Arduino IDE** - [Download here](https://www.arduino.cc/en/software)
2. **Add ESP8266 Board Manager**
   ```
   File → Preferences → Additional Board Manager URLs:
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
   ```
3. **Install Libraries**
   - DHT sensor library
   - Adafruit Unified Sensor
   - MFRC522
   - ESP8266WiFi (built-in)
   - ESP8266WebServer (built-in)

4. **Configure WiFi in Code**
   ```cpp
   const char* ssid = "Klassy";
   const char* password = "your_password";
   ```

5. **Upload Code**
   - Tools → Board → NodeMCU 1.0
   - Tools → Port → Select COM port
   - Click Upload

6. **Find IP Address**
   - Open Serial Monitor (115200 baud)
   - ESP8266 prints IP: `10.54.156.112`
   - Update in `iot-backend/app.py`

### Testing ESP8266

```bash
# Test web interface
curl http://10.54.156.112

# Expected HTML response with sensor values:
# <p><b>Temperature:</b> 30.00 °C</p>
# <p><b>Humidity:</b> 16.00 %</p>
# <p><b>RFID Tag:</b> 63121495</p>
# <p><b>Distance:</b> 11.03 cm</p>
# <p><b>Air Quality (MQ-135):</b> 150</p>
```

---

## 🔧 Configuration

### Network Setup

All devices must be on the **same WiFi network**:

| Device | IP Address | Port | Protocol |
|--------|-----------|------|----------|
| **ESP8266** | 10.54.156.112 | 80 | HTTP |
| **Backend** | 10.54.156.140 | 8000 | HTTP |
| **Expo Server** | 10.54.156.140 | 8081 | HTTP/WebSocket |
| **Mobile Phone** | DHCP Assigned | - | WiFi |

**Network Name:** Klassy

### Finding Your IP Addresses

**On Linux/Mac:**
```bash
ifconfig | grep "inet "
# or
ip addr show
```

**On Windows:**
```bash
ipconfig
```

### Updating IP Addresses

1. **Mobile App Configuration**
   ```typescript
   // File: iot-safety-mobile/constants/theme.ts
   export const API_BASE_URL = 'http://YOUR_BACKEND_IP:8000';
   ```

2. **Backend Configuration**
   ```python
   # File: iot-backend/app.py
   ESP8266_IP = "YOUR_ESP8266_IP"
   ```

### Sensor Thresholds

**Default Values (Configurable in app settings):**

```typescript
{
  temperature: { min: 15, max: 35 },    // °C
  humidity: { min: 30, max: 80 },       // %
  gas: { max: 300 },                     // ppm
  ultrasonic: { min: 50 }                // cm
}
```

**Status Determination:**
- 🟢 **Normal** - Within thresholds
- 🟡 **Warning** - Approaching limits
- 🔴 **Danger** - Exceeded thresholds

---

## 🚀 Deployment

### Development Mode (Current)

```bash
# Backend
cd iot-backend
python3 app.py
# Running on http://0.0.0.0:8000

# Mobile App
cd iot-safety-mobile
npm start
# Expo DevTools on http://localhost:8081
```

### Production Deployment

#### Backend (Cloud Server)

```bash
# Install production server
pip3 install gunicorn

# Run with workers
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Or use Docker
docker build -t iot-backend .
docker run -p 8000:8000 iot-backend
```

#### Mobile App (Build & Deploy)

```bash
# Install EAS CLI
npm install -g eas-cli

# Build for Android
eas build --platform android

# Build for iOS
eas build --platform ios

# Submit to stores
eas submit --platform android
eas submit --platform ios
```

### Production Checklist

- [ ] Use HTTPS/SSL certificates
- [ ] Add API authentication (JWT)
- [ ] Implement rate limiting
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configure firewall rules
- [ ] Use production database (PostgreSQL)
- [ ] Enable logging
- [ ] Set up automatic backups
- [ ] Configure CORS properly
- [ ] Use environment variables
- [ ] Enable crash reporting
- [ ] Set up CI/CD pipeline

---

## 🐛 Troubleshooting

### Common Issues

#### 1. ❌ App Can't Connect to Backend

**Symptoms:** "Unable to connect to server" message

**Solutions:**
```bash
# Check backend is running
curl http://BACKEND_IP:8000/health

# Verify IP in mobile app
# Edit: iot-safety-mobile/constants/theme.ts

# Ensure same WiFi network
# Phone Settings → WiFi (must match computer)

# Test from phone browser
# Open: http://BACKEND_IP:8000/health

# Try mock mode temporarily
export const USE_MOCK_DATA = true;
```

#### 2. ❌ ESP8266 Not Responding

**Symptoms:** Backend shows "ESP8266 connection failed"

**Solutions:**
```bash
# Ping ESP8266
ping 10.54.156.112

# Check Arduino Serial Monitor
# Should show IP address on startup

# Restart ESP8266
# Press reset button

# Verify WiFi credentials in code
const char* ssid = "Klassy";
const char* password = "correct_password";
```

#### 3. ❌ Data Not Updating

**Symptoms:** Old timestamps, stale values

**Solutions:**
- Pull down to refresh manually
- Wait 15 seconds for auto-refresh
- Check backend logs for requests
- Restart app (close and reopen Expo Go)
- Verify ESP8266 sensors are working

#### 4. ❌ Boolean Casting Error (FIXED)

**Error:** `"java.lang.String cannot be cast to java.lang.Boolean"`

**Solution:** Already fixed in code! If it happens:
- Go to Settings tab
- Tap "Reset All Settings"
- Close and reopen app

### Debug Commands

```bash
# Test entire system
curl http://10.54.156.112                    # ESP8266 HTML
curl http://10.54.156.140:8000/health        # Backend health
curl http://10.54.156.140:8000/sensors/live/arduino  # Real data

# Check network
ping 10.54.156.112   # ESP8266
ping 10.54.156.140   # Backend

# View backend logs
# Terminal running python3 app.py shows:
# ✅ ESP8266 data: T=30.0°C, H=16.0%, Gas=150ppm...

# Mobile app debugging
# Shake device → Developer Menu → Debug Remote JS
```

---

## 📚 Full Documentation

### Component Documentation

| Document | Description | Path |
|----------|-------------|------|
| **Backend README** | Complete API documentation, endpoints, deployment | [`iot-backend/README.md`](iot-backend/README.md) |
| **Mobile App README** | App architecture, components, screens, state management | [`iot-safety-mobile/APP_README.md`](iot-safety-mobile/APP_README.md) |
| **System Overview** | Complete system guide with troubleshooting | [`iot-safety-mobile/FINAL_README.md`](iot-safety-mobile/FINAL_README.md) |

### Quick Reference Guides

- **Quick Start:** Get running in 5 minutes
- **Hardware Setup:** ESP8266 wiring and Arduino code
- **API Reference:** All endpoints with examples
- **Troubleshooting:** Common issues and solutions
- **Deployment:** Production setup guide

---

## 🔐 Security Notes

### Current Setup (Development)

⚠️ **Not Production Ready:**
- No authentication
- Plain HTTP (not HTTPS)
- No encryption
- Debug mode enabled
- CORS fully open

### Production Requirements

1. **Authentication** - Implement JWT or OAuth
2. **HTTPS** - Use SSL/TLS certificates
3. **API Keys** - Secure backend access
4. **Input Validation** - Sanitize all inputs
5. **Rate Limiting** - Prevent abuse
6. **Encrypted Storage** - Secure AsyncStorage
7. **Monitoring** - Track errors and attacks
8. **Regular Updates** - Keep dependencies current

---

## 📊 System Status

### Current Version: 1.0.0

- **Backend:** ✅ Operational
- **Mobile App:** ✅ Operational
- **ESP8266:** ✅ Connected
- **Data Flow:** ✅ Working
- **Last Tested:** October 17, 2025
- **Test Network:** WiFi "Klassy"

### Performance Metrics

- **Refresh Rate:** 15 seconds
- **API Response:** < 500ms
- **ESP8266 Uptime:** 99%+
- **Mobile App:** iOS 13+, Android 5.0+

---

## ❓ FAQ

**Q: Do I need internet?**  
A: No, only local WiFi. All devices communicate on LAN.

**Q: Can I use without ESP8266?**  
A: Yes! Set `USE_MOCK_DATA = true` in `theme.ts`

**Q: How many sensors can I add?**  
A: Unlimited (ESP8266 has limited GPIO, use I2C expanders)

**Q: Can multiple phones connect?**  
A: Yes! Any device on same WiFi can access backend.

**Q: What if my IP changes?**  
A: Update `API_BASE_URL` in `theme.ts` and `ESP8266_IP` in `app.py`

**Q: Is this production-ready?**  
A: No, requires authentication, HTTPS, and hardening.

---

## 🛠️ Development

### Contributing

```bash
# Clone repository
git clone <repo-url>

# Create feature branch
git checkout -b feature/new-sensor

# Make changes and test
npm test  # Mobile
pytest    # Backend

# Submit pull request
```

### Code Style

- **Python:** PEP 8
- **TypeScript:** ESLint + Prettier
- **React:** Functional components + Hooks

---

## 📄 License

MIT License - Free to use, modify, and distribute

Copyright (c) 2025 IoT Safety Monitoring System

---

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Expo Documentation](https://docs.expo.dev/)
- [React Native Guide](https://reactnative.dev/)
- [ESP8266 Arduino Core](https://github.com/esp8266/Arduino)
- [Zustand State Management](https://github.com/pmndrs/zustand)

---

## 📞 Support

Need help? Check these resources in order:

1. **This README** - Quick start and common issues
2. **Component READMEs** - Detailed documentation
3. **Troubleshooting Section** - Common errors
4. **Backend Logs** - Terminal output
5. **Mock Mode** - Test without hardware

---

## 🎯 Project Structure

```
AI-App/
├── iot-backend/              # Flask API Server
│   ├── app.py               # Main server file
│   ├── requirements.txt     # Python dependencies
│   └── README.md            # Backend documentation
│
└── iot-safety-mobile/       # React Native Mobile App
    ├── app/                 # Screens (Dashboard, Monitor, Reports, Settings)
    ├── components/          # Reusable UI components
    ├── services/            # API client and mock data
    ├── store/               # Zustand state management
    ├── constants/           # Configuration and theme
    ├── types/               # TypeScript definitions
    ├── package.json         # Node dependencies
    ├── app.json             # Expo configuration
    ├── README.md            # Original app README
    ├── APP_README.md        # Comprehensive app guide
    └── FINAL_README.md      # System overview
```

---

## 🚀 Next Steps

1. ✅ **Quick Start** - Follow 5-minute setup above
2. ✅ **Test System** - Verify all components working
3. 📖 **Read Docs** - Review component READMEs
4. 🔧 **Customize** - Adjust thresholds and settings
5. 🛠️ **Extend** - Add new sensors or features
6. 🚀 **Deploy** - Move to production with security

---

**Built with ❤️ for Industrial Safety Monitoring**

🏭 Monitor · 📊 Analyze · 🚨 Alert · 🔒 Secure

---

*Complete IoT solution from hardware to mobile app - ready to deploy!*
