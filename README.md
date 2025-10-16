# 🏭 AI-Powered Safety Monitoring for Smarter Shop Floors

A comprehensive full-stack IoT safety monitoring system that uses AI to detect hazards, predict incidents, and ensure workplace safety in industrial environments.

## � Latest Updates (October 16, 2025)

### ✅ Camera Feeds & Recent Violations - WORKING
- **Database Seeding System**: 6 cameras and 30+ sample detections automatically added
- **Real-Time Data Display**: Camera grid and violations list show actual database data
- **Live YOLOv8 Detection**: Working webcam integration with real-time object detection
- **Complete Statistics**: All metrics powered by real database queries

### ✅ Real-Time Reports & Analytics - WORKING
- **Dynamic Data**: No more mock data - everything pulls from the database in real-time
- **Multiple Time Periods**: Filter by Today, Week, Month, Quarter, or Year
- **Interactive Charts**: Incident trends and severity distribution with actual data
- **Auto-Refresh**: Data updates every 30 seconds automatically
- **Comprehensive Analytics**: Response times, critical violations, detection type breakdown

**📄 See detailed documentation:**
- [CAMERA_FEEDS_SETUP.md](./CAMERA_FEEDS_SETUP.md) - Complete camera feeds guide
- [REPORTS_REALTIME_SETUP.md](./REPORTS_REALTIME_SETUP.md) - Complete reports guide

## �🌟 Features

### 🎯 Dual Operating Modes
- **Heavy Industry Mode**: Gas leaks, vibration monitoring, temperature alerts, auto-shutdown
- **Shop Floor Mode**: PPE detection, proximity alerts, fall detection, access control

### 📊 Real-Time Monitoring
- Live sensor data from Gas, Temperature, Vibration, Ultrasonic, RFID, and Environmental sensors
- WebSocket-based real-time updates
- Status indicators (Normal/Warning/Danger)
- Trend analysis and visualization

### 🤖 AI-Powered Detection
- Anomaly detection using machine learning
- Predictive analytics for incident prevention
- PPE (Personal Protective Equipment) detection
- Safety violation identification

### 🚨 Alert System
- Multi-level alerts (Info, Warning, Critical)
- Sound, email, and SMS notifications
- Alert acknowledgment and resolution tracking
- Historical alert analysis

### 📈 Analytics & Reporting
- Incident history and trends
- Sensor performance metrics
- Worker access logs (RFID)
- Customizable reports

### ⚙️ System Features
- Dark/Light theme
- Responsive design (Mobile, Tablet, Desktop)
- Configurable thresholds
- Auto-shutdown on critical alerts

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS v3.4
- **State Management**: React Context API
- **Charts**: Recharts
- **Icons**: Lucide React
- **Notifications**: React Hot Toast
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy (Async)
- **WebSockets**: Native FastAPI WebSocket support
- **AI/ML**: Scikit-learn, TensorFlow
- **Image Processing**: OpenCV, Pillow

### IoT Integration
- **Hardware**: ESP32 microcontroller
- **Sensors**: Gas (MQ-2/MQ-135), Temperature (DHT22), Vibration (SW-420), Ultrasonic (HC-SR04), RFID (RC522)
- **Protocol**: MQTT / HTTP JSON

## 📁 Project Structure

```
AI-Smart-Shop/
├── frontend/                 # React TypeScript Frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── context/         # React Context providers
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── types/           # TypeScript type definitions
│   │   └── App.tsx          # Main app component
│   ├── public/
│   ├── package.json
│   └── tailwind.config.js
│
└── backend/                  # FastAPI Python Backend
    ├── app/
    │   ├── ai/              # AI/ML modules
    │   ├── db/              # Database configuration
    │   ├── models/          # SQLAlchemy models & Pydantic schemas
    │   ├── routes/          # API endpoints
    │   ├── services/        # Business logic
    │   └── main.py          # FastAPI application
    ├── tests/
    ├── requirements.txt
    └── .env.example
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- PostgreSQL 14+
- Git

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with your PostgreSQL credentials
nano .env

# Create PostgreSQL database
createdb ai_safety_monitoring

# Run database migrations (if using Alembic)
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Database Setup (PostgreSQL)

```sql
-- Create database
CREATE DATABASE ai_safety_monitoring;

-- Create user (optional)
CREATE USER safety_admin WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_safety_monitoring TO safety_admin;
```

## 📡 IoT Sensor Integration

### ESP32 Setup

1. Install Arduino IDE or PlatformIO
2. Install required libraries:
   - WiFi
   - HTTPClient / PubSubClient (MQTT)
   - DHT sensor library
   - MFRC522 (RFID)

3. Sample ESP32 code structure:

```cpp
// Send sensor data to backend
void sendSensorData() {
  HTTPClient http;
  http.begin("http://your-server:8000/sensors");
  http.addHeader("Content-Type", "application/json");
  
  String payload = "{\"sensor_type\":\"temperature\",\"value\":" + 
                   String(temperature) + ",\"unit\":\"°C\",\"status\":\"normal\"}";
  
  int httpCode = http.POST(payload);
  http.end();
}
```

## 🎨 UI Screenshots & Features

### Dashboard
- Real-time sensor cards with status indicators
- Live charts for each sensor
- Alert panel with active notifications
- Operating mode switcher
- Statistics overview

### Reports
- Historical data analysis
- Incident breakdown by type
- Sensor performance metrics
- AI predictions display

### Settings
- Configurable sensor thresholds
- Alert preferences (Email, SMS, Sound)
- System configuration
- Dark/Light mode toggle

## 🔧 Configuration

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

### Backend (.env)
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_safety_monitoring
API_PORT=8000
CORS_ORIGINS=http://localhost:5173
# Add other configurations from .env.example
```

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm test
```

### Backend Tests
```bash
cd backend
pytest
```

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

- `GET /sensors` - Get all sensor data
- `GET /sensors/{type}/history` - Get sensor history
- `GET /alerts/active` - Get active alerts
- `POST /sensors` - Submit sensor data (from ESP32)
- `WS /ws` - WebSocket for real-time updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Your Name** - *Initial work*

## 🙏 Acknowledgments

- FastAPI documentation
- React and Vite teams
- Tailwind CSS
- Open source community

## 📞 Support

For support, email support@example.com or open an issue in the repository.

---

Built with ❤️ for safer workplaces
