"""
Computer Vision Detection API Routes
Endpoints for camera management and real-time safety violation detection
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime, timedelta
import cv2
import asyncio
import json

from app.db.database import get_db
from app.models.models import Camera, CVDetection, DetectionType, ViolationType, CameraStatus, OperatingMode, AlertSeverity
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

# ==================== Live Camera Feed Processing ====================

@router.post("/cameras/{camera_id}/start-monitoring")
async def start_camera_monitoring(
    camera_id: int,
    stream_url: str = Query(..., description="Camera stream URL or device path"),
    operating_mode: OperatingMode = Query(OperatingMode.HEAVY_INDUSTRY, description="Operating mode for detection"),
    db: AsyncSession = Depends(get_db)
):
    """
    Start live monitoring for a specific camera with YOLO model integration
    
    Args:
        camera_id: ID of the camera to monitor
        stream_url: URL or path to camera stream (e.g., rtsp://camera_ip:port/stream, /dev/video0, http://ip/mjpeg)
        operating_mode: Operating mode (INDUSTRY for industrial safety monitoring)
    """
    # Verify camera exists
    result = await db.execute(select(Camera).filter(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Update camera status and stream URL
    camera.status = CameraStatus.ACTIVE
    camera.operating_mode = operating_mode
    camera.stream_url = stream_url
    camera.last_activity = datetime.utcnow()
    
    await db.commit()
    
    try:
        # Start processing camera feed in background
        # Note: In production, this should be handled by a background task/worker
        import threading
        
        def process_feed():
            cv_detector.process_camera_feed(camera_id, stream_url)
        
        thread = threading.Thread(target=process_feed, daemon=True)
        thread.start()
        
        return {
            "message": f"Started monitoring camera {camera_id}",
            "camera_id": camera_id,
            "stream_url": stream_url,
            "operating_mode": operating_mode.value,
            "detection_enabled": True,
            "yolo_models_loaded": len(cv_detector.models) > 0,
            "models_available": list(cv_detector.models.keys())
        }
        
    except Exception as e:
        # Update camera status to error
        camera.status = CameraStatus.ERROR
        await db.commit()
        
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to start camera monitoring: {str(e)}"
        )

@router.post("/cameras/{camera_id}/stop-monitoring")
async def stop_camera_monitoring(
    camera_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Stop live monitoring for a specific camera"""
    result = await db.execute(select(Camera).filter(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Update camera status
    camera.status = CameraStatus.INACTIVE
    camera.last_activity = datetime.utcnow()
    
    await db.commit()
    
    return {
        "message": f"Stopped monitoring camera {camera_id}",
        "camera_id": camera_id,
        "status": "inactive"
    }

@router.post("/cameras/{camera_id}/detect-frame")
async def detect_violations_in_frame(
    camera_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Perform real-time detection on a single frame from camera
    Useful for testing YOLO model integration
    """
    result = await db.execute(select(Camera).filter(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # For demo, we'll use None frame which will trigger mock detection or actual if models are loaded
    detections = cv_detector.detect_violations(camera_id, None)
    
    # Save detections to database
    for detection in detections:
        cv_detection = CVDetection(
            camera_id=camera_id,
            detection_type=DetectionType[detection["detection_type"]] if isinstance(detection["detection_type"], str) else detection["detection_type"],
            violation_type=ViolationType[detection["violation_type"]] if detection.get("violation_type") and isinstance(detection["violation_type"], str) else detection.get("violation_type"),
            confidence=detection["confidence"],
            bbox_x=detection["bbox"]["x"],
            bbox_y=detection["bbox"]["y"],
            bbox_width=detection["bbox"]["w"],
            bbox_height=detection["bbox"]["h"],
            description=detection["description"],
            severity=AlertSeverity[detection["severity"]] if isinstance(detection["severity"], str) else detection["severity"],
            timestamp=detection["timestamp"]
        )
        db.add(cv_detection)
    
    await db.commit()
    
    return {
        "camera_id": camera_id,
        "detections_count": len(detections),
        "detections": detections,
        "yolo_models_active": cv_detector.initialized,
        "models_loaded": list(cv_detector.models.keys()) if cv_detector.initialized else [],
        "timestamp": datetime.utcnow()
    }

@router.get("/models/status")
async def get_model_status():
    """Get status of loaded YOLO models"""
    return {
        "initialized": cv_detector.initialized,
        "models_loaded": list(cv_detector.models.keys()) if cv_detector.initialized else [],
        "model_paths": {
            "general": "/home/balu/AI-Safety-Shop/AI-smart-shop/yolov8n.pt",
            "ppe": "/home/balu/AI-Safety-Shop/AI-smart-shop/ppe-detection.pt"
        },
        "confidence_threshold": cv_detector.detection_confidence_threshold,
        "detection_classes": {
            "ppe_violations": ["NO_HELMET", "NO_VEST", "NO_GLOVES", "NO_GOGGLES", "NO_MASK"],
            "general_detections": ["PERSON", "VEHICLE", "PHONE_USE"]
        }
    }

# ==================== Live Video Streaming with YOLO Detection ====================

def generate_frames(camera_source: str, camera_id: int):
    """
    Generate video frames with YOLO detection overlays
    
    Args:
        camera_source: Camera source (0 for webcam, URL for IP camera, file path for video)
        camera_id: Database camera ID
    """
    try:
        # Initialize video capture
        cap = cv2.VideoCapture(camera_source)
        
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        while True:
            success, frame = cap.read()
            if not success:
                break
                
            # Resize frame for better performance
            frame = cv2.resize(frame, (640, 480))
            
            # Perform YOLO detection
            detections = cv_detector.detect_violations(camera_id, frame)
            
            # Draw detection boxes and labels on frame
            annotated_frame = draw_detections(frame, detections, camera_id)
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Small delay to control frame rate
            cv2.waitKey(1)
            
    except Exception as e:
        print(f"Error in video streaming: {e}")
    finally:
        if 'cap' in locals():
            cap.release()

def draw_detections(frame, detections, camera_id=None):
    """
    Draw detection bounding boxes and labels on frame
    
    Args:
        frame: OpenCV frame
        detections: List of detection results from YOLO
        camera_id: Camera ID for display
    
    Returns:
        Annotated frame with bounding boxes
    """
    annotated_frame = frame.copy()
    
    for detection in detections:
        bbox = detection['bbox']
        confidence = detection['confidence']
        description = detection['description']
        severity = detection['severity']
        
        # Define colors based on severity
        color_map = {
            AlertSeverity.DANGER: (0, 0, 255),      # Red
            AlertSeverity.WARNING: (0, 165, 255),   # Orange
            AlertSeverity.INFO: (0, 255, 255),      # Yellow
        }
        
        color = color_map.get(severity, (0, 255, 0))  # Default green
        
        # Draw bounding box
        x, y, w, h = bbox['x'], bbox['y'], bbox['w'], bbox['h']
        cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
        
        # Draw label background
        label = f"{description} ({confidence:.2f})"
        (label_width, label_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(annotated_frame, (x, y - label_height - 10), (x + label_width, y), color, -1)
        
        # Draw label text
        cv2.putText(annotated_frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Add timestamp and camera info
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if camera_id:
        cv2.putText(annotated_frame, f"Camera {camera_id} - {timestamp}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    else:
        cv2.putText(annotated_frame, f"{timestamp}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    return annotated_frame

@router.get("/cameras/{camera_id}/stream")
async def stream_camera_feed(
    camera_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Stream live camera feed with YOLO detection overlays
    
    Args:
        camera_id: Database camera ID
    
    Returns:
        MJPEG stream with detection overlays
    """
    # Verify camera exists in database
    result = await db.execute(select(Camera).filter(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Update camera status
    camera.status = CameraStatus.ACTIVE
    camera.last_activity = datetime.utcnow()
    await db.commit()
    
    # Use camera's rtsp_url as source (stored as string in database)
    source = camera.rtsp_url
    
    # Convert source to appropriate format
    try:
        # Try to convert to int for webcam index
        camera_source = int(source)
    except ValueError:
        # Use as string for file path or URL
        camera_source = source
    
    return StreamingResponse(
        generate_frames(camera_source, camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.get("/cameras/{camera_id}/test-detection")
async def test_camera_detection(
    camera_id: int,
    source: str = Query(default="0", description="Camera source for testing"),
    db: AsyncSession = Depends(get_db)
):
    """
    Test YOLO detection on a single frame from camera
    
    Args:
        camera_id: Database camera ID
        source: Camera source
    
    Returns:
        Detection results and base64 encoded image with annotations
    """
    import base64
    
    # Verify camera exists
    result = await db.execute(select(Camera).filter(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    try:
        # Convert source to appropriate format
        try:
            camera_source = int(source)
        except ValueError:
            camera_source = source
        
        # Capture single frame
        cap = cv2.VideoCapture(camera_source)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise HTTPException(status_code=500, detail="Failed to capture frame from camera")
        
        # Resize frame
        frame = cv2.resize(frame, (640, 480))
        
        # Perform detection
        detections = cv_detector.detect_violations(camera_id, frame)
        
        # Draw detections on frame
        annotated_frame = draw_detections(frame, detections, camera_id)
        
        # Encode frame to base64
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "camera_id": camera_id,
            "detections_count": len(detections),
            "detections": detections,
            "annotated_frame": f"data:image/jpeg;base64,{frame_base64}",
            "yolo_models_active": cv_detector.initialized,
            "models_loaded": list(cv_detector.models.keys()) if cv_detector.initialized else [],
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing detection: {str(e)}")
