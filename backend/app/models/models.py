from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base

# Enums
class SensorType(str, enum.Enum):
    GAS = "gas"
    TEMPERATURE = "temperature"
    VIBRATION = "vibration"
    ULTRASONIC = "ultrasonic"
    RFID = "rfid"
    ENVIRONMENTAL = "environmental"

class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"

class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class OperatingMode(str, enum.Enum):
    HEAVY_INDUSTRY = "heavy-industry"
    SHOP_FLOOR = "shop-floor"

class DetectionType(str, enum.Enum):
    PPE_VIOLATION = "ppe_violation"  # Missing helmet, vest, gloves, etc.
    UNSAFE_BEHAVIOR = "unsafe_behavior"  # Running, climbing unsafely, etc.
    HAZARD_ZONE = "hazard_zone"  # Restricted area access
    FIRE_SMOKE = "fire_smoke"  # Fire or smoke detection
    SLIP_TRIP_FALL = "slip_trip_fall"  # Potential fall hazards
    VEHICLE_COLLISION = "vehicle_collision"  # Forklift/vehicle proximity
    CROWD_DENSITY = "crowd_density"  # Overcrowding detection
    EQUIPMENT_MISUSE = "equipment_misuse"  # Improper equipment use

class ViolationType(str, enum.Enum):
    NO_HELMET = "no_helmet"
    NO_VEST = "no_vest"
    NO_GLOVES = "no_gloves"
    NO_GOGGLES = "no_goggles"
    NO_MASK = "no_mask"
    RESTRICTED_AREA = "restricted_area"
    UNSAFE_POSTURE = "unsafe_posture"
    RUNNING = "running"
    SMOKING = "smoking"
    PHONE_USE = "phone_use"

class CameraStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"

# Models
class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    sensor_type = Column(Enum(SensorType), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)  # normal, warning, danger
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    extra_data = Column(JSON, nullable=True)
    
    # Relationships
    alerts = relationship("Alert", back_populates="sensor_data")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False, index=True)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE, index=True)
    sensor_data_id = Column(Integer, ForeignKey("sensor_data.id"), nullable=True)
    alert_type = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    extra_data = Column(JSON, nullable=True)
    
    # Relationships
    sensor_data = relationship("SensorData", back_populates="alerts")

class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    rfid_tag = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    access_logs = relationship("AccessLog", back_populates="worker")

class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    action = Column(String(20), nullable=False)  # entry, exit
    location = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    extra_data = Column(JSON, nullable=True)
    
    # Relationships
    worker = relationship("Worker", back_populates="access_logs")

class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_type = Column(String(50), nullable=False)
    sensor_type = Column(Enum(SensorType), nullable=True)
    predicted_value = Column(Float, nullable=True)
    confidence = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # low, medium, high
    prediction_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    extra_data = Column(JSON, nullable=True)

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_type = Column(String(100), nullable=False, index=True)
    severity = Column(Enum(AlertSeverity), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(200), nullable=True)
    affected_workers = Column(JSON, nullable=True)  # List of worker IDs
    response_actions = Column(JSON, nullable=True)
    status = Column(String(20), default="open")  # open, investigating, resolved
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    extra_data = Column(JSON, nullable=True)

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)
    rtsp_url = Column(String(500), nullable=True)  # For real camera feeds
    status = Column(Enum(CameraStatus), default=CameraStatus.ONLINE, index=True)
    resolution = Column(String(20), nullable=True)  # e.g., "1920x1080"
    fps = Column(Integer, default=30)
    detection_enabled = Column(Boolean, default=True)
    detection_types = Column(JSON, nullable=True)  # List of DetectionType enabled
    operating_mode = Column(Enum(OperatingMode), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON, nullable=True)
    
    # Relationships
    detections = relationship("CVDetection", back_populates="camera")

class CVDetection(Base):
    __tablename__ = "cv_detections"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    detection_type = Column(Enum(DetectionType), nullable=False, index=True)
    violation_type = Column(Enum(ViolationType), nullable=True, index=True)
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    bbox = Column(JSON, nullable=True)  # Bounding box coordinates {"x": 100, "y": 200, "w": 50, "h": 100}
    snapshot_path = Column(String(500), nullable=True)  # Path to saved image
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    severity = Column(Enum(AlertSeverity), nullable=False)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    extra_data = Column(JSON, nullable=True)
    
    # Relationships
    camera = relationship("Camera", back_populates="detections")
    worker = relationship("Worker")

