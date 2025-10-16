"""
Seed data for initializing the database with sample cameras and detections
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from app.models.models import Camera, CVDetection, CameraStatus, OperatingMode, DetectionType, ViolationType
import random
import logging

logger = logging.getLogger(__name__)

async def seed_cameras(db: AsyncSession):
    """Seed sample cameras if none exist"""
    result = await db.execute(select(Camera))
    existing_cameras = result.scalars().all()
    
    if len(existing_cameras) > 0:
        logger.info(f"Database already has {len(existing_cameras)} cameras. Skipping camera seeding.")
        return existing_cameras
    
    logger.info("Seeding cameras...")
    
    cameras_data = [
        {
            "name": "Main Entrance Camera",
            "location": "Building A - Main Gate",
            "camera_id": 0,
            "status": CameraStatus.ONLINE,
            "resolution": "1920x1080",
            "fps": 30,
            "detection_enabled": True,
            "operating_mode": OperatingMode.SHOP_FLOOR,
            "last_seen": datetime.utcnow()
        },
        {
            "name": "Assembly Line Camera 1",
            "location": "Production Floor - Station A1",
            "camera_id": 1,
            "status": CameraStatus.ONLINE,
            "resolution": "1920x1080",
            "fps": 30,
            "detection_enabled": True,
            "operating_mode": OperatingMode.SHOP_FLOOR,
            "last_seen": datetime.utcnow()
        },
        {
            "name": "Warehouse Camera",
            "location": "Warehouse - Zone B",
            "camera_id": 2,
            "status": CameraStatus.ONLINE,
            "resolution": "1280x720",
            "fps": 25,
            "detection_enabled": True,
            "operating_mode": OperatingMode.SHOP_FLOOR,
            "last_seen": datetime.utcnow()
        },
        {
            "name": "Heavy Machinery Area",
            "location": "Heavy Industry Zone - Sector C",
            "camera_id": 3,
            "status": CameraStatus.ONLINE,
            "resolution": "1920x1080",
            "fps": 30,
            "detection_enabled": True,
            "operating_mode": OperatingMode.HEAVY_INDUSTRY,
            "last_seen": datetime.utcnow()
        },
        {
            "name": "Loading Dock Camera",
            "location": "Loading Dock - Bay 3",
            "camera_id": 4,
            "status": CameraStatus.ONLINE,
            "resolution": "1920x1080",
            "fps": 30,
            "detection_enabled": True,
            "operating_mode": OperatingMode.SHOP_FLOOR,
            "last_seen": datetime.utcnow()
        },
        {
            "name": "Quality Control Station",
            "location": "QC Department - Lab 2",
            "camera_id": 5,
            "status": CameraStatus.ONLINE,
            "resolution": "1920x1080",
            "fps": 30,
            "detection_enabled": True,
            "operating_mode": OperatingMode.SHOP_FLOOR,
            "last_seen": datetime.utcnow()
        }
    ]
    
    created_cameras = []
    for camera_data in cameras_data:
        camera = Camera(**camera_data)
        db.add(camera)
        created_cameras.append(camera)
    
    await db.commit()
    
    # Refresh to get IDs
    for camera in created_cameras:
        await db.refresh(camera)
    
    logger.info(f"Successfully seeded {len(created_cameras)} cameras")
    return created_cameras

async def seed_detections(db: AsyncSession, cameras: list):
    """Seed sample detections for testing"""
    result = await db.execute(select(CVDetection))
    existing_detections = result.scalars().all()
    
    if len(existing_detections) > 10:
        logger.info(f"Database already has {len(existing_detections)} detections. Skipping detection seeding.")
        return
    
    logger.info("Seeding sample detections...")
    
    # Detection templates
    detection_templates = [
        {
            "detection_type": DetectionType.PPE_VIOLATION,
            "violation_type": ViolationType.NO_HELMET,
            "severity": "danger",
            "description": "Worker not wearing safety helmet in restricted area",
            "confidence": 0.92
        },
        {
            "detection_type": DetectionType.PPE_VIOLATION,
            "violation_type": ViolationType.NO_VEST,
            "severity": "warning",
            "description": "Worker without high-visibility safety vest",
            "confidence": 0.88
        },
        {
            "detection_type": DetectionType.PPE_VIOLATION,
            "violation_type": ViolationType.NO_GLOVES,
            "severity": "warning",
            "description": "Worker handling materials without protective gloves",
            "confidence": 0.85
        },
        {
            "detection_type": DetectionType.FIRE_SMOKE,
            "violation_type": None,
            "severity": "danger",
            "description": "Smoke detected in production area",
            "confidence": 0.95
        },
        {
            "detection_type": DetectionType.HAZARD_ZONE,
            "violation_type": ViolationType.RESTRICTED_AREA,
            "severity": "danger",
            "description": "Unauthorized person in restricted hazard zone",
            "confidence": 0.90
        },
        {
            "detection_type": DetectionType.UNSAFE_BEHAVIOR,
            "violation_type": ViolationType.UNSAFE_POSTURE,
            "severity": "warning",
            "description": "Worker in unsafe working posture",
            "confidence": 0.78
        },
        {
            "detection_type": DetectionType.VEHICLE_COLLISION,
            "violation_type": None,
            "severity": "info",
            "description": "Forklift detected in operational area",
            "confidence": 0.96
        },
        {
            "detection_type": DetectionType.PPE_VIOLATION,
            "violation_type": ViolationType.NO_MASK,
            "severity": "warning",
            "description": "Worker not wearing required face mask",
            "confidence": 0.87
        },
        {
            "detection_type": DetectionType.UNSAFE_BEHAVIOR,
            "violation_type": ViolationType.RUNNING,
            "severity": "warning",
            "description": "Person running in production area",
            "confidence": 0.82
        },
        {
            "detection_type": DetectionType.FIRE_SMOKE,
            "violation_type": None,
            "severity": "danger",
            "description": "Fire detected - immediate action required",
            "confidence": 0.98
        },
        {
            "detection_type": DetectionType.PPE_VIOLATION,
            "violation_type": ViolationType.NO_GOGGLES,
            "severity": "warning",
            "description": "Worker not wearing safety goggles",
            "confidence": 0.84
        },
        {
            "detection_type": DetectionType.UNSAFE_BEHAVIOR,
            "violation_type": ViolationType.SMOKING,
            "severity": "danger",
            "description": "Smoking detected in prohibited area",
            "confidence": 0.91
        },
        {
            "detection_type": DetectionType.UNSAFE_BEHAVIOR,
            "violation_type": ViolationType.PHONE_USE,
            "severity": "warning",
            "description": "Worker using phone while operating machinery",
            "confidence": 0.79
        },
        {
            "detection_type": DetectionType.EQUIPMENT_MISUSE,
            "violation_type": None,
            "severity": "warning",
            "description": "Improper equipment usage detected",
            "confidence": 0.83
        }
    ]
    
    # Generate detections for the last 24 hours
    now = datetime.utcnow()
    detections = []
    
    for i in range(30):  # Create 30 detections
        # Random time in the last 24 hours
        hours_ago = random.uniform(0, 24)
        timestamp = now - timedelta(hours=hours_ago)
        
        # Random camera
        camera = random.choice(cameras)
        
        # Random detection template
        template = random.choice(detection_templates)
        
        # Random bbox within frame
        x = random.randint(100, 1500)
        y = random.randint(100, 800)
        w = random.randint(100, 300)
        h = random.randint(150, 400)
        
        # Some detections are acknowledged
        acknowledged = random.random() < 0.3  # 30% are acknowledged
        acknowledged_at = timestamp + timedelta(minutes=random.randint(5, 60)) if acknowledged else None
        
        detection = CVDetection(
            camera_id=camera.id,
            detection_type=template["detection_type"],
            violation_type=template["violation_type"],
            severity=template["severity"],
            confidence=template["confidence"] + random.uniform(-0.1, 0.05),
            bbox={"x": x, "y": y, "w": w, "h": h},
            description=template["description"],
            timestamp=timestamp,
            acknowledged=acknowledged,
            acknowledged_at=acknowledged_at
        )
        db.add(detection)
        detections.append(detection)
    
    await db.commit()
    logger.info(f"Successfully seeded {len(detections)} sample detections")

async def seed_all_data(db: AsyncSession):
    """Seed all sample data"""
    try:
        cameras = await seed_cameras(db)
        await seed_detections(db, cameras)
        logger.info("Database seeding completed successfully")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        await db.rollback()
        raise
