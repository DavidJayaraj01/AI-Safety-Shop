#!/bin/bash

# AI Safety Monitoring System - Setup Script
# This script sets up the entire development environment

echo "🚀 Setting up AI Safety Monitoring System..."
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p backend/models
mkdir -p mosquitto/config mosquitto/data mosquitto/log
mkdir -p frontend/src/{components,pages,context,services,types}

# Backend setup
echo ""
echo "🐍 Setting up Backend..."
cd backend

# Create Python virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Backend dependencies installed"

# Copy environment file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Please update backend/.env with your configuration"
fi

cd ..

# Frontend setup
echo ""
echo "⚛️  Setting up Frontend..."
cd frontend

# Install Node dependencies
if [ ! -d "node_modules" ]; then
    npm install
    echo "✅ Frontend dependencies installed"
fi

# Copy environment file
if [ ! -f ".env" ]; then
    cp ../.env.example .env
    echo "⚠️  Please update frontend/.env with your configuration"
fi

cd ..

# Create mosquitto config if not exists
if [ ! -f "mosquitto/config/mosquitto.conf" ]; then
    cat > mosquitto/config/mosquitto.conf << EOF
listener 1883
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
EOF
    echo "✅ Mosquitto configuration created"
fi

echo ""
echo "=========================================="
echo "✨ Setup Complete!"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Configure environment variables:"
echo "   - Edit backend/.env"
echo "   - Edit frontend/.env"
echo ""
echo "2. Start services with Docker:"
echo "   docker-compose up -d"
echo ""
echo "3. Initialize database:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python init_db.py"
echo ""
echo "4. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "5. Configure ESP32:"
echo "   - Open esp32/safety_monitor.ino in Arduino IDE"
echo "   - Update WiFi credentials and MQTT broker IP"
echo "   - Upload to ESP32"
echo ""
echo "6. Optional - Train YOLOv8 PPE Model:"
echo "   - Prepare PPE dataset"
echo "   - Run: yolo task=detect mode=train model=yolov8n.pt data=ppe_dataset.yaml epochs=100"
echo "   - Copy trained model to backend/models/yolov8n-ppe.pt"
echo ""
echo "=========================================="
echo "📚 Documentation: See README.md for more details"
echo "🐛 Issues: Report at GitHub repository"
echo ""
echo "Happy monitoring! 🛡️"
