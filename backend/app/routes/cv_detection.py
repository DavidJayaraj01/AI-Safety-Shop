"""
Computer Vision Detection API Routes
Endpoints for camera management and real-time safety violation detection with YOLO
"""

from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime, timedelta
import shutil
from pathlib import Path
import logging
import cv2
import asyncio
import numpy as np
from io import BytesIO
import time

from app.db.database import get_db
from app.models.models import Camera, CVDetection, DetectionType, ViolationType, CameraStatus, OperatingMode
from app.models.schemas import (
    CameraCreate, CameraUpdate, CameraResponse, 
    CVDetectionCreate, CVDetectionResponse,
    CVStats, CameraWithDetections
)
from app.ai.cv_detector import cv_detector

router = APIRouter(prefix="/cv", tags=["CV Detection"])
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

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
    stats = cv_detector.get_detection_stats()
    stats["yolo_model_loaded"] = cv_detector.initialized
    stats["model_path"] = cv_detector.model_path if cv_detector.model_path else "No model loaded"
    return stats

@router.post("/detect/upload")
async def detect_from_upload(file: UploadFile = File(...)):
    """
    Upload an image and detect safety violations using YOLO
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{datetime.utcnow().timestamp()}_{file.filename}"
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Saved uploaded image to {file_path}")
        
        # Run YOLO detection
        detections = cv_detector.detect_from_image(str(file_path))
        
        return {
            "status": "success",
            "image_path": str(file_path),
            "detections": detections,
            "detection_count": len(detections),
            "model_used": cv_detector.model_path if cv_detector.model_path else "mock",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in image detection: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

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

# ==================== Live Camera Streaming ====================

def generate_camera_frames(camera_id: int = 0):
    """
    Generator function to capture frames from camera and run YOLO detection
    """
    logger.info(f"Starting camera stream for camera_id={camera_id}")
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        logger.error(f"Failed to open camera {camera_id}")
        # Yield an error frame
        error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(error_frame, "Camera Error: Failed to open camera", (50, 240),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        ret, buffer = cv2.imencode('.jpg', error_frame)
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        return
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer to reduce latency
    
    logger.info(f"Camera {camera_id} opened successfully")
    frame_count = 0
    last_detections = []
    
    try:
        while True:
            success, frame = cap.read()
            if not success:
                logger.warning("Failed to read frame from camera")
                time.sleep(0.1)
                continue
            
            frame_count += 1
            
            # Run YOLO detection every 3rd frame for performance (still 10 FPS detection)
            if frame_count % 3 == 0:
                last_detections = cv_detector.detect_from_frame(frame)
            
            # Draw bounding boxes from last detection
            for det in last_detections:
                bbox = det.get('bbox', {})
                # Handle both dict and list formats
                if isinstance(bbox, dict):
                    x1 = int(bbox.get('x', 0))
                    y1 = int(bbox.get('y', 0))
                    w = int(bbox.get('w', 0))
                    h = int(bbox.get('h', 0))
                    x2 = x1 + w
                    y2 = y1 + h
                elif isinstance(bbox, list) and len(bbox) == 4:
                    x1, y1, x2, y2 = [int(coord) for coord in bbox]
                else:
                    continue
                    
                    # Color based on severity (BGR format for OpenCV)
                    color = (255, 0, 0)  # Blue default
                    severity = det.get('severity', '').lower() if isinstance(det.get('severity'), str) else str(det.get('severity', '')).lower()
                    if severity == 'danger' or 'danger' in severity:
                        color = (0, 0, 255)  # Red
                    elif severity == 'warning' or 'warning' in severity:
                        color = (0, 165, 255)  # Orange
                    elif severity == 'info' or 'info' in severity:
                        color = (0, 255, 0)  # Green
                    
                    # Draw rectangle with thicker line
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                    
                    # Draw label with better visibility
                    class_label = det.get('class_name', det.get('class', det.get('detection_type', 'Unknown')))
                    confidence = det.get('confidence', 0)
                    label = f"{class_label} {int(confidence * 100)}%"
                    
                    # Calculate text size for background
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.6
                    thickness = 2
                    (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)
                    
                    # Draw filled rectangle as background
                    cv2.rectangle(frame, (x1, y1 - text_h - baseline - 5), 
                                (x1 + text_w + 5, y1), color, -1)
                    
                    # Draw text
                    cv2.putText(frame, label, (x1 + 2, y1 - baseline - 2), 
                              font, font_scale, (255, 255, 255), thickness)
            
            # Add detection count overlay with background
            detection_text = f"Detections: {len(last_detections)}"
            (det_w, det_h), _ = cv2.getTextSize(detection_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame, (5, 5), (det_w + 15, det_h + 15), (0, 0, 0), -1)
            cv2.putText(frame, detection_text, (10, det_h + 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add frame counter
            frame_text = f"Frame: {frame_count}"
            (frame_w, frame_h), _ = cv2.getTextSize(frame_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (5, det_h + 25), (frame_w + 15, det_h + frame_h + 35), (0, 0, 0), -1)
            cv2.putText(frame, frame_text, (10, det_h + frame_h + 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Encode frame as JPEG with good quality
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 85]
            ret, buffer = cv2.imencode('.jpg', frame, encode_params)
            if not ret:
                logger.warning("Failed to encode frame")
                continue
            
            frame_bytes = buffer.tobytes()
            
            # Yield frame in multipart format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # No sleep - stream as fast as possible
            
    except GeneratorExit:
        logger.info(f"Stream closed by client after {frame_count} frames")
    except Exception as e:
        logger.error(f"Error in camera stream: {e}")
    finally:
        cap.release()
        logger.info(f"Released camera {camera_id}, processed {frame_count} frames")

@router.get("/stream/live")
async def stream_live_camera(camera_id: int = Query(0, description="Camera device ID (0 for default webcam)")):
    """
    Stream live camera feed with real-time YOLO detection
    Returns MJPEG stream that can be displayed in <img> tag
    """
    return StreamingResponse(
        generate_camera_frames(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.get("/stream/status")
async def get_stream_status():
    """
    Check if camera streaming is available
    """
    try:
        cap = cv2.VideoCapture(0)
        is_available = cap.isOpened()
        cap.release()
        
        return {
            "status": "available" if is_available else "unavailable",
            "camera_available": is_available,
            "yolo_loaded": cv_detector.yolo_model is not None,
            "message": "Camera ready for streaming" if is_available else "No camera detected"
        }
    except Exception as e:
        return {
            "status": "error",
            "camera_available": False,
            "message": str(e)
        }
