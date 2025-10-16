from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class SensorType(str, enum.Enum):
    GAS = "gas"
    TEMPERATURE = "temperature"
    VIBRATION = "vibration"
    ULTRASONIC = "ultrasonic"
    RFID = "rfid"
    ENVIRONMENTAL = "environmental"

class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Sensor(Base):
    __tablename__ = "sensors"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Enum(SensorType), nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, default="active")
    warning_threshold = Column(Float, nullable=False)
    critical_threshold = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    readings = relationship("SensorReading", back_populates="sensor")

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    id = Column(String, primary_key=True)
    sensor_id = Column(String, ForeignKey("sensors.id"))
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    sensor = relationship("Sensor", back_populates="readings")

class Worker(Base):
    __tablename__ = "workers"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    department = Column(String, nullable=False)
    assigned_area = Column(String, nullable=False)
    photo_url = Column(String)
    status = Column(String, default="active")
    ppe_compliance = Column(Boolean, default=True)
    location_x = Column(Float, default=0.0)
    location_y = Column(Float, default=0.0)
    location_zone = Column(String, default="")
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ppe_detections = relationship("PPEDetection", back_populates="worker")
    rfid_events = relationship("RFIDEvent", back_populates="worker")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    message = Column(String, nullable=False)
    location = Column(String, nullable=False)
    worker_id = Column(String, ForeignKey("workers.id"), nullable=True)
    sensor_id = Column(String, ForeignKey("sensors.id"), nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)
    actions = Column(JSON, default=[])
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class PPEDetection(Base):
    __tablename__ = "ppe_detections"
    
    id = Column(String, primary_key=True)
    worker_id = Column(String, ForeignKey("workers.id"))
    helmet = Column(Boolean, default=False)
    vest = Column(Boolean, default=False)
    gloves = Column(Boolean, default=False)
    goggles = Column(Boolean, default=False)
    safety_shoes = Column(Boolean, default=False)
    confidence = Column(Float, nullable=False)
    overall_compliance = Column(Boolean, default=False)
    image_url = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    worker = relationship("Worker", back_populates="ppe_detections")

class RFIDEvent(Base):
    __tablename__ = "rfid_events"
    
    id = Column(String, primary_key=True)
    worker_id = Column(String, ForeignKey("workers.id"))
    event_type = Column(String, nullable=False)  # entry or exit
    location = Column(String, nullable=False)
    access_granted = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    worker = relationship("Worker", back_populates="rfid_events")

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    description = Column(String, nullable=False)
    location = Column(String, nullable=False)
    workers_involved = Column(JSON, default=[])
    sensors_involved = Column(JSON, default=[])
    actions_taken = Column(JSON, default=[])
    status = Column(String, default="open")
    reported_by = Column(String, nullable=False)
    resolved_by = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    images = Column(JSON, default=[])
    video_url = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class AnomalyPrediction(Base):
    __tablename__ = "anomaly_predictions"
    
    id = Column(String, primary_key=True)
    sensor_id = Column(String, ForeignKey("sensors.id"))
    predicted_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    forecast_minutes = Column(Integer, nullable=False)
    anomaly_type = Column(String, nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    recommendation = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
