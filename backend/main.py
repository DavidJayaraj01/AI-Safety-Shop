from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import asyncio
from typing import List
import logging

from app.core.config import settings
from app.api import sensors, alerts, workers, ppe, incidents, analytics, settings as settings_api
from app.mqtt.client import MQTTClient
from app.detection.ppe_detector import PPEDetector
from app.ml.anomaly_detector import AnomalyDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")

manager = ConnectionManager()

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AI Safety Monitoring System...")
    
    # Initialize MQTT client
    mqtt_client = MQTTClient()
    mqtt_client.start()
    app.state.mqtt_client = mqtt_client
    
    # Initialize PPE detector
    ppe_detector = PPEDetector()
    app.state.ppe_detector = ppe_detector
    
    # Initialize anomaly detector
    anomaly_detector = AnomalyDetector()
    app.state.anomaly_detector = anomaly_detector
    
    logger.info("System initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    mqtt_client.stop()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sensors.router, prefix="/api/sensors", tags=["sensors"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(workers.router, prefix="/api/workers", tags=["workers"])
app.include_router(ppe.router, prefix="/api/ppe", tags=["ppe"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(settings_api.router, prefix="/api", tags=["settings"])

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Camera stream endpoint
@app.get("/api/camera/stream")
async def camera_stream():
    async def generate():
        detector = app.state.ppe_detector
        async for frame in detector.stream_frames():
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "mqtt_connected": app.state.mqtt_client.is_connected(),
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Safety Monitoring System API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

# Store manager globally for MQTT callbacks
app.state.ws_manager = manager

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
