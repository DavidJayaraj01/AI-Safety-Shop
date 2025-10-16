"""
Computer Vision Detection API Routes
Endpoints for camera management and real-time safety violation detection
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.models import Camera, CVDetection, DetectionType, ViolationType, CameraStatus, OperatingMode
from app.models.schemas import (
    CameraCreate, CameraUpdate, CameraResponse, 
    CVDetectionCreate, CVDetectionResponse,
    CVStats, CameraWithDetections
)
from app.ai.cv_detector import cv_detector

router = APIRouter(prefix="/cv", tags=["CV Detection"])

# ==================== Camera Management ====================

@router.get("/cameras", response_model=List[CameraResponse])
async def get_cameras(
    skip: int = 0,
    limit: int = 100,
    status: Optional[CameraStatus] = None,
    operating_mode: Optional[OperatingMode] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all cameras with optional filtering"""
    query = select(Camera)
    
    if status:
        query = query.filter(Camera.status == status)
    if operating_mode:
        query = query.filter(Camera.operating_mode == operating_mode)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    cameras = result.scalars().all()
    
    return cameras

@router.get("/cameras/{camera_id}", response_model=CameraWithDetections)
async def get_camera(camera_id: int, db: AsyncSession = Depends(get_db)):
    """Get camera details with recent detections"""
    result = await db.execute(select(Camera).filter(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Get recent detections (last 10)
    detections_result = await db.execute(
        select(CVDetection)
        .filter(CVDetection.camera_id == camera_id)
        .order_by(CVDetection.timestamp.desc())
        .limit(10)
    )
    detections = detections_result.scalars().all()
    
    return {
        **camera.__dict__,
        "recent_detections": detections
    }

@router.post("/cameras", response_model=CameraResponse)
async def create_camera(camera: CameraCreate, db: AsyncSession = Depends(get_db)):
    """Create a new camera"""
    db_camera = Camera(**camera.dict())
    db.add(db_camera)
    await db.commit()
    await db.refresh(db_camera)
    return db_camera

@router.patch("/cameras/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: int, 
    camera_update: CameraUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update camera settings"""
    result = await db.execute(select(Camera).filter(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Update fields
    update_data = camera_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(camera, field, value)
    
    camera.last_seen = datetime.utcnow()
    await db.commit()
    await db.refresh(camera)
    return camera

@router.delete("/cameras/{camera_id}")
async def delete_camera(camera_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a camera"""
    result = await db.execute(select(Camera).filter(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    await db.delete(camera)
    await db.commit()
    return {"message": "Camera deleted successfully"}

# ==================== Detection Management ====================

@router.get("/detections", response_model=List[CVDetectionResponse])
async def get_detections(
    skip: int = 0,
    limit: int = 100,
    camera_id: Optional[int] = None,
    detection_type: Optional[DetectionType] = None,
    violation_type: Optional[ViolationType] = None,
    acknowledged: Optional[bool] = None,
    hours: int = Query(24, description="Hours to look back"),
    db: AsyncSession = Depends(get_db)
):
    """Get detections with optional filtering"""
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(CVDetection).filter(CVDetection.timestamp >= time_threshold)
    
    if camera_id:
        query = query.filter(CVDetection.camera_id == camera_id)
    if detection_type:
        query = query.filter(CVDetection.detection_type == detection_type)
    if violation_type:
        query = query.filter(CVDetection.violation_type == violation_type)
    if acknowledged is not None:
        query = query.filter(CVDetection.acknowledged == acknowledged)
    
    query = query.order_by(CVDetection.timestamp.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    detections = result.scalars().all()
    
    return detections

@router.post("/detections", response_model=CVDetectionResponse)
async def create_detection(detection: CVDetectionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new detection (typically called by CV processing pipeline)"""
    db_detection = CVDetection(**detection.dict())
    db.add(db_detection)
    await db.commit()
    await db.refresh(db_detection)
    return db_detection

@router.patch("/detections/{detection_id}/acknowledge")
async def acknowledge_detection(detection_id: int, db: AsyncSession = Depends(get_db)):
    """Acknowledge a detection"""
    result = await db.execute(select(CVDetection).filter(CVDetection.id == detection_id))
    detection = result.scalar_one_or_none()
    
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    
    detection.acknowledged = True
    detection.acknowledged_at = datetime.utcnow()
    await db.commit()
    await db.refresh(detection)
    return detection

@router.post("/detections/simulate/{camera_id}")
async def simulate_detection(camera_id: int, db: AsyncSession = Depends(get_db)):
    """
    Simulate CV detection for a camera (for testing/demo)
    In production, this would be triggered by actual video frame analysis
    """
    # Verify camera exists
    result = await db.execute(select(Camera).filter(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Run detection simulation
    detections = cv_detector.detect_violations(camera_id)
    
    if not detections:
        return {"message": "No violations detected", "detections": []}
    
    # Save detections to database
    saved_detections = []
    for det in detections:
        db_detection = CVDetection(**det)
        db.add(db_detection)
        saved_detections.append(db_detection)
    
    await db.commit()
    
    # Refresh to get IDs
    for det in saved_detections:
        await db.refresh(det)
    
    return {
        "message": f"Detected {len(saved_detections)} violation(s)",
        "detections": saved_detections
    }

# ==================== Statistics & Analytics ====================

@router.get("/stats", response_model=CVStats)
async def get_cv_stats(db: AsyncSession = Depends(get_db)):
    """Get CV monitoring statistics"""
    
    # Total cameras
    total_cameras_result = await db.execute(select(func.count(Camera.id)))
    total_cameras = total_cameras_result.scalar()
    
    # Active cameras
    active_cameras_result = await db.execute(
        select(func.count(Camera.id)).filter(Camera.status == CameraStatus.ONLINE)
    )
    active_cameras = active_cameras_result.scalar()
    
    # Detections today
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    detections_today_result = await db.execute(
        select(func.count(CVDetection.id)).filter(CVDetection.timestamp >= today)
    )
    detections_today = detections_today_result.scalar()
    
    # Critical violations (not acknowledged)
    critical_result = await db.execute(
        select(func.count(CVDetection.id)).filter(
            and_(
                CVDetection.timestamp >= today,
                CVDetection.severity == "danger",
                CVDetection.acknowledged == False
            )
        )
    )
    critical_violations = critical_result.scalar()
    
    # PPE violations
    ppe_result = await db.execute(
        select(func.count(CVDetection.id)).filter(
            and_(
                CVDetection.timestamp >= today,
                CVDetection.detection_type == DetectionType.PPE_VIOLATION
            )
        )
    )
    ppe_violations = ppe_result.scalar()
    
    # Hazard zone violations
    hazard_result = await db.execute(
        select(func.count(CVDetection.id)).filter(
            and_(
                CVDetection.timestamp >= today,
                CVDetection.detection_type == DetectionType.HAZARD_ZONE
            )
        )
    )
    hazard_violations = hazard_result.scalar()
    
    # Average confidence
    avg_confidence_result = await db.execute(
        select(func.avg(CVDetection.confidence)).filter(CVDetection.timestamp >= today)
    )
    avg_confidence = avg_confidence_result.scalar() or 0.0
    
    return {
        "total_cameras": total_cameras,
        "active_cameras": active_cameras,
        "total_detections_today": detections_today,
        "critical_violations": critical_violations,
        "ppe_violations": ppe_violations,
        "hazard_zone_violations": hazard_violations,
        "average_confidence": round(avg_confidence, 2)
    }

@router.get("/detector/status")
async def get_detector_status():
    """Get CV detector system status"""
    return cv_detector.get_detection_stats()

@router.post("/analyze/ppe")
async def analyze_ppe():
    """Analyze PPE compliance (demo endpoint)"""
    return cv_detector.analyze_ppe_compliance()

@router.post("/analyze/hazard-zones")
async def analyze_hazard_zones():
    """Analyze hazard zone intrusions (demo endpoint)"""
    return cv_detector.detect_hazard_zones()

@router.post("/analyze/unsafe-behavior")
async def analyze_unsafe_behavior():
    """Detect unsafe worker behaviors (demo endpoint)"""
    return cv_detector.detect_unsafe_behavior()
