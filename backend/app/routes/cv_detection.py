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
    Optimized for real-time performance with YOLOv8
    """
    logger.info(f"Starting YOLOv8 camera stream for camera_id={camera_id}")
    
    # Try different camera sources
    cap = None
    camera_sources = [camera_id, f"/dev/video{camera_id}", 0]  # Try device ID, then video device, then default
    
    for source in camera_sources:
        try:
            cap = cv2.VideoCapture(source)
            if cap.isOpened():
                logger.info(f"Successfully opened camera source: {source}")
                break
            else:
                cap.release()
        except Exception as e:
            logger.warning(f"Failed to open camera source {source}: {e}")
    
    if cap is None or not cap.isOpened():
        logger.error(f"Failed to open any camera source for camera_id={camera_id}")
        # Yield an error frame
        error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(error_frame, "Camera Error: No camera available", (50, 240),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(error_frame, f"Tried sources: {camera_sources}", (50, 280),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        ret, buffer = cv2.imencode('.jpg', error_frame)
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        return
    
    # Optimize camera settings for real-time performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer to reduce latency
    
    # Get actual camera properties
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    
    logger.info(f"Camera {camera_id} properties: {actual_width}x{actual_height} @ {actual_fps} FPS")
    
    frame_count = 0
    last_detections = []
    detection_count = 0
    detection_fps = 0
    last_detection_time = time.time()
    
    try:
        while True:
            success, frame = cap.read()
            if not success:
                logger.warning("Failed to read frame from camera")
                time.sleep(0.1)
                continue
            
            frame_count += 1
            current_time = time.time()
            
            # Run YOLO detection every 3rd frame for performance (still ~10 FPS detection)
            if frame_count % 3 == 0:
                detection_start = time.time()
                last_detections = cv_detector.detect_from_frame(frame, camera_id)
                detection_time = time.time() - detection_start
                
                detection_count += 1
                if current_time - last_detection_time >= 1.0:  # Update FPS every second
                    detection_fps = detection_count / (current_time - last_detection_time)
                    detection_count = 0
                    last_detection_time = current_time
            
            # Draw enhanced bounding boxes and labels
            annotated_frame = frame.copy()
            
            for det in last_detections:
                bbox = det.get('bbox', {})
                
                # Handle both dict and list bbox formats
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
                
                # Enhanced color coding based on severity
                severity = det.get('severity', '').lower() if isinstance(det.get('severity'), str) else str(det.get('severity', '')).lower()
                if 'danger' in severity:
                    color = (0, 0, 255)  # Red - Critical
                    line_thickness = 4
                elif 'warning' in severity:
                    color = (0, 165, 255)  # Orange - Warning
                    line_thickness = 3
                elif 'info' in severity:
                    color = (0, 255, 0)  # Green - Info
                    line_thickness = 2
                else:
                    color = (255, 0, 0)  # Blue - Default
                    line_thickness = 2
                
                # Draw bounding box with enhanced styling
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, line_thickness)
                
                # Prepare enhanced label
                class_label = det.get('class_name', det.get('detection_type', 'Unknown'))
                confidence = det.get('confidence', 0)
                violation_type = det.get('violation_type', '')
                
                # Create comprehensive label
                if violation_type:
                    label = f"{violation_type.replace('_', ' ')} ({int(confidence * 100)}%)"
                else:
                    label = f"{class_label} ({int(confidence * 100)}%)"
                
                # Calculate text dimensions for background
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.6
                thickness = 2
                (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)
                
                # Draw label background with transparency effect
                cv2.rectangle(annotated_frame, (x1, y1 - text_h - baseline - 8), 
                            (x1 + text_w + 8, y1), color, -1)
                
                # Draw label text
                cv2.putText(annotated_frame, label, (x1 + 4, y1 - baseline - 4), 
                          font, font_scale, (255, 255, 255), thickness)
            
            # Enhanced overlay information
            overlay_color = (0, 0, 0)
            text_color = (0, 255, 0)
            
            # Detection count and performance info
            detection_text = f"Detections: {len(last_detections)} | Det FPS: {detection_fps:.1f}"
            (det_w, det_h), _ = cv2.getTextSize(detection_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated_frame, (5, 5), (det_w + 15, det_h + 15), overlay_color, -1)
            cv2.putText(annotated_frame, detection_text, (10, det_h + 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
            
            # Model info
            model_name = Path(cv_detector.model_path).name if cv_detector.model_path else "Mock Mode"
            model_text = f"Model: {model_name}"
            (model_w, model_h), _ = cv2.getTextSize(model_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated_frame, (5, det_h + 25), (model_w + 15, det_h + model_h + 35), overlay_color, -1)
            cv2.putText(annotated_frame, model_text, (10, det_h + model_h + 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Camera info
            cam_text = f"Camera: {camera_id} | Frame: {frame_count} | {actual_width}x{actual_height}"
            (cam_w, cam_h), _ = cv2.getTextSize(cam_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            cv2.rectangle(annotated_frame, (5, det_h + model_h + 45), (cam_w + 15, det_h + model_h + cam_h + 55), overlay_color, -1)
            cv2.putText(annotated_frame, cam_text, (10, det_h + model_h + cam_h + 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            
            # Status indicator (top right)
            status_text = "LIVE YOLOv8"
            status_color = (0, 255, 0) if cv_detector.initialized else (0, 0, 255)
            (status_w, status_h), _ = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated_frame, (actual_width - status_w - 15, 5), (actual_width - 5, status_h + 15), (0, 0, 0), -1)
            cv2.putText(annotated_frame, status_text, (actual_width - status_w - 10, status_h + 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
            
            # Encode frame with optimized quality for streaming
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 80, cv2.IMWRITE_JPEG_OPTIMIZE, 1]
            ret, buffer = cv2.imencode('.jpg', annotated_frame, encode_params)
            if not ret:
                logger.warning("Failed to encode frame")
                continue
            
            frame_bytes = buffer.tobytes()
            
            # Yield frame in multipart format for MJPEG streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
    except GeneratorExit:
        logger.info(f"YOLOv8 stream closed by client after {frame_count} frames")
    except Exception as e:
        logger.error(f"Error in YOLOv8 camera stream: {e}")
    finally:
        if cap:
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
    Check if camera streaming is available and get YOLO model info
    """
    try:
        cap = cv2.VideoCapture(0)
        is_available = cap.isOpened()
        cap.release()
        
        # Get YOLO model information
        model_info = {
            "loaded": cv_detector.yolo_model is not None,
            "model_path": cv_detector.model_path if cv_detector.model_path else "None",
            "model_name": Path(cv_detector.model_path).name if cv_detector.model_path else "Mock Mode",
            "initialized": cv_detector.initialized,
            "confidence_threshold": cv_detector.detection_confidence_threshold
        }
        
        if cv_detector.yolo_model and hasattr(cv_detector.yolo_model, 'names'):
            model_info["classes"] = list(cv_detector.yolo_model.names.values()) if cv_detector.yolo_model.names else []
            model_info["num_classes"] = len(cv_detector.yolo_model.names) if cv_detector.yolo_model.names else 0
        
        return {
            "status": "available" if is_available else "unavailable",
            "camera_available": is_available,
            "yolo_model": model_info,
            "message": "Camera ready for YOLOv8 streaming" if is_available else "No camera detected",
            "stream_endpoint": "/cv/stream/live?camera_id=0"
        }
    except Exception as e:
        return {
            "status": "error",
            "camera_available": False,
            "yolo_model": {"loaded": False, "error": str(e)},
            "message": f"Error checking camera status: {str(e)}"
        }

@router.get("/stream/test/{camera_id}")
async def test_camera_connection(camera_id: int):
    """
    Test if a specific camera can be opened
    """
    try:
        cap = cv2.VideoCapture(camera_id)
        if cap.isOpened():
            # Get camera properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Try to read a frame
            ret, frame = cap.read()
            cap.release()
            
            return {
                "camera_id": camera_id,
                "status": "available",
                "can_read_frame": ret,
                "properties": {
                    "width": width,
                    "height": height,
                    "fps": fps
                },
                "message": f"Camera {camera_id} is working properly"
            }
        else:
            cap.release()
            return {
                "camera_id": camera_id,
                "status": "unavailable",
                "message": f"Cannot open camera {camera_id}"
            }
    except Exception as e:
        return {
            "camera_id": camera_id,
            "status": "error",
            "message": f"Error testing camera {camera_id}: {str(e)}"
        }
