from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import List
import json

from app.db.database import init_db, close_db
from app.routes import sensors, alerts, workers, ai_detection, reports, settings, cv_detection, arduino_sensors

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections.remove(connection)

manager = ConnectionManager()

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AI Safety Monitoring System...")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down AI Safety Monitoring System...")
    await close_db()
    logger.info("Database connections closed")

# Create FastAPI app
app = FastAPI(
    title="AI-Powered Safety Monitoring API",
    description="Backend API for Smart Shop Floor Safety Monitoring System",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sensors.router, prefix="/sensors", tags=["Sensors"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(workers.router, prefix="/workers", tags=["Workers"])
app.include_router(ai_detection.router, prefix="/ai", tags=["AI Detection"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
app.include_router(settings.router, prefix="/settings", tags=["Settings"])
app.include_router(cv_detection.router, tags=["CV Detection"])
app.include_router(arduino_sensors.router, prefix="/api", tags=["Arduino Sensors"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AI-Powered Safety Monitoring System API",
        "version": "1.0.0",
        "status": "operational"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "websocket_connections": len(manager.active_connections)
    }

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Echo back or process the message
            logger.info(f"Received WebSocket message: {message}")
            
            # You can process different message types here
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": message.get("timestamp")})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Function to broadcast sensor data updates
async def broadcast_sensor_update(sensor_data: dict):
    """Broadcast sensor data update to all connected WebSocket clients"""
    message = {
        "type": "sensor_data",
        "payload": sensor_data
    }
    await manager.broadcast(message)

# Function to broadcast alert updates
async def broadcast_alert(alert_data: dict):
    """Broadcast alert to all connected WebSocket clients"""
    message = {
        "type": "alert",
        "payload": alert_data
    }
    await manager.broadcast(message)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
