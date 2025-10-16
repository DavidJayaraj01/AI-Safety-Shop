from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class SensorType(str, Enum):
    gas = "gas"
    temperature = "temperature"
    vibration = "vibration"
    ultrasonic = "ultrasonic"
    rfid = "rfid"
    environmental = "environmental"

class AlertSeverity(str, Enum):
    info = "info"
    warning = "warning"
    danger = "danger"

class AlertStatus(str, Enum):
    active = "active"
    acknowledged = "acknowledged"
    resolved = "resolved"

class DetectionType(str, Enum):
    ppe_violation = "ppe_violation"
    unsafe_behavior = "unsafe_behavior"
    hazard_zone = "hazard_zone"
    fire_smoke = "fire_smoke"
    slip_trip_fall = "slip_trip_fall"
    vehicle_collision = "vehicle_collision"
    crowd_density = "crowd_density"
    equipment_misuse = "equipment_misuse"

class ViolationType(str, Enum):
    no_helmet = "no_helmet"
    no_vest = "no_vest"
    no_gloves = "no_gloves"
    no_goggles = "no_goggles"
    no_mask = "no_mask"
    restricted_area = "restricted_area"
    unsafe_posture = "unsafe_posture"
    running = "running"
    smoking = "smoking"
    phone_use = "phone_use"

class CameraStatus(str, Enum):
    online = "online"
    offline = "offline"
    error = "error"
    maintenance = "maintenance"

class OperatingMode(str, Enum):
    heavy_industry = "heavy-industry"
    shop_floor = "shop-floor"

# Sensor Schemas
class SensorDataBase(BaseModel):
    sensor_type: SensorType
    value: float
    unit: str
    status: str
    extra_data: Optional[Dict[str, Any]] = None

class SensorDataCreate(SensorDataBase):
    pass

class SensorDataResponse(SensorDataBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Alert Schemas
class AlertBase(BaseModel):
    title: str
    message: str
    severity: AlertSeverity
    alert_type: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

class AlertCreate(AlertBase):
    sensor_data_id: Optional[int] = None

class AlertResponse(AlertBase):
    id: int
    status: AlertStatus
    sensor_data_id: Optional[int] = None
    timestamp: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Worker Schemas
class WorkerBase(BaseModel):
    worker_id: str
    name: str
    rfid_tag: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None

class WorkerCreate(WorkerBase):
    pass

class WorkerResponse(WorkerBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Access Log Schemas
class AccessLogBase(BaseModel):
    action: str  # entry or exit
    location: str
    extra_data: Optional[Dict[str, Any]] = None

class AccessLogCreate(AccessLogBase):
    worker_id: int

class AccessLogResponse(AccessLogBase):
    id: int
    worker_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Prediction Schemas
class PredictionBase(BaseModel):
    prediction_type: str
    sensor_type: Optional[SensorType] = None
    predicted_value: Optional[float] = None
    confidence: float
    risk_level: str
    prediction_data: Optional[Dict[str, Any]] = None
    extra_data: Optional[Dict[str, Any]] = None

class PredictionCreate(PredictionBase):
    pass

class PredictionResponse(PredictionBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# System Config Schemas
class SystemConfigBase(BaseModel):
    key: str
    value: Dict[str, Any]
    description: Optional[str] = None

class SystemConfigCreate(SystemConfigBase):
    pass

class SystemConfigResponse(SystemConfigBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_workers: int
    active_workers: int
    active_alerts: int
    critical_alerts: int
    system_uptime: float
    data_points_today: int

class SensorStats(BaseModel):
    sensor_type: str
    current_value: float
    status: str
    trend: str
    last_update: datetime

# Report Schemas
class ReportSummary(BaseModel):
    total_incidents: int
    total_warnings: int
    resolved_alerts: int
    average_response_time: float
    uptime: float
    total_data_points: int

# Camera Schemas
class CameraBase(BaseModel):
    camera_id: str
    name: str
    location: str
    rtsp_url: Optional[str] = None
    resolution: Optional[str] = "1920x1080"
    fps: Optional[int] = 30
    detection_enabled: bool = True
    detection_types: Optional[List[str]] = None
    operating_mode: OperatingMode

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    rtsp_url: Optional[str] = None
    status: Optional[CameraStatus] = None
    detection_enabled: Optional[bool] = None
    detection_types: Optional[List[str]] = None

class CameraResponse(CameraBase):
    id: int
    status: CameraStatus
    created_at: datetime
    last_seen: datetime
    extra_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# CV Detection Schemas
class BoundingBox(BaseModel):
    x: int
    y: int
    w: int
    h: int

class CVDetectionBase(BaseModel):
    detection_type: DetectionType
    violation_type: Optional[ViolationType] = None
    confidence: float
    bbox: Optional[BoundingBox] = None
    description: Optional[str] = None
    severity: AlertSeverity

class CVDetectionCreate(CVDetectionBase):
    camera_id: int
    worker_id: Optional[int] = None
    snapshot_path: Optional[str] = None

class CVDetectionResponse(CVDetectionBase):
    id: int
    camera_id: int
    worker_id: Optional[int] = None
    snapshot_path: Optional[str] = None
    timestamp: datetime
    acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    extra_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# CV Monitoring Stats
class CVStats(BaseModel):
    total_cameras: int
    active_cameras: int
    total_detections_today: int
    critical_violations: int
    ppe_violations: int
    hazard_zone_violations: int
    average_confidence: float

class CameraWithDetections(CameraResponse):
    recent_detections: List[CVDetectionResponse] = []

