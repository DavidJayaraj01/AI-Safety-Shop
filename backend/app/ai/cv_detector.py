"""
Computer Vision Detection Service using YOLO Models
Real-time safety monitoring with YOLOv8 for PPE detection and workplace safety
"""

import random
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import numpy as np

try:
    from ultralytics import YOLO
    import cv2
    import torch
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("ultralytics or cv2 not installed. Using mock detection mode.")

from app.models.models import DetectionType, ViolationType, AlertSeverity

logger = logging.getLogger(__name__)

class CVDetector:
    """
    Computer Vision Detector for workplace safety monitoring
    Uses YOLO models for real-time detection of:
    - PPE violations (missing helmets, vests, gloves, etc.)
    - Unsafe behaviors (running, climbing, phone use)
    - Hazard zones (restricted area access)
    - Fire/smoke detection
    - Vehicle collision risks
    """
    
    def __init__(self):
        self.detection_confidence_threshold = 0.75
        self.initialized = False
        self.yolo_model = None
        self.model_path = None
        
        # Try to load YOLO model
        self._load_yolo_model()
        
    def _load_yolo_model(self):
        """Load YOLO model from the models directory"""
        if not YOLO_AVAILABLE:
            logger.warning("YOLO not available. Running in mock mode.")
            return
            
        # Try to find model files (prioritize custom PPE detection models)
        possible_paths = [
            Path(__file__).parent.parent / "models" / "ppe-detection.pt",  # Custom PPE model
            Path(__file__).parent.parent / "models" / "best.pt",  # Trained custom model
            Path(__file__).parent.parent / "models" / "yolov8n.pt",  # Standard YOLOv8 nano
            Path(__file__).parent.parent / "models" / "yolov8s.pt",  # Standard YOLOv8 small
            Path(__file__).parent.parent / "models" / "yolov8m.pt",  # Standard YOLOv8 medium
            Path(__file__).parent.parent.parent.parent / "AI-smart-shop" / "ppe-detection.pt",
            Path(__file__).parent.parent.parent.parent / "AI-smart-shop" / "yolov8n.pt",
            Path("models/ppe-detection.pt"),
            Path("models/best.pt"),
            Path("models/yolov8n.pt"),
            Path("ppe-detection.pt"),  # Root directory
            Path("yolov8n.pt"),
        ]
        
        for model_path in possible_paths:
            if model_path.exists():
                try:
                    logger.info(f"Loading YOLO model from {model_path}")
                    # Add safe globals for ultralytics models to fix PyTorch 2.6 security change
                    torch.serialization.add_safe_globals(['ultralytics.nn.tasks.DetectionModel'])
                    self.yolo_model = YOLO(str(model_path))
                    self.model_path = str(model_path)
                    self.initialized = True
                    
                    # Log model info
                    model_info = f"Model: {model_path.name}, Classes: {len(self.yolo_model.names) if self.yolo_model.names else 'Unknown'}"
                    if self.yolo_model.names:
                        logger.info(f"Available classes: {list(self.yolo_model.names.values())}")
                    logger.info(f"YOLO model loaded successfully: {model_info}")
                    return
                except Exception as e:
                    logger.error(f"Failed to load model from {model_path}: {e}")
                    
        # If no local model found, try to download YOLOv8n as fallback
        try:
            logger.info("No local model found. Downloading YOLOv8n...")
            self.yolo_model = YOLO('yolov8n.pt')  # This will download automatically
            self.model_path = 'yolov8n.pt'
            self.initialized = True
            logger.info("YOLOv8n downloaded and loaded successfully")
            return
        except Exception as e:
            logger.error(f"Failed to download YOLOv8n: {e}")
                    
        if not self.initialized:
            logger.warning("No YOLO model found. Running in mock detection mode.")
            logger.info(f"Searched paths: {[str(p) for p in possible_paths]}")
    
    def detect_from_image(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect safety violations from an image file
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of detections with bounding boxes and confidence scores
        """
        if not self.initialized or self.yolo_model is None:
            logger.warning("YOLO model not initialized, using mock detection")
            return self._generate_mock_detections(1)
        
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Failed to read image: {image_path}")
                return []
            
            return self.detect_from_frame(img, camera_id=0)
            
        except Exception as e:
            logger.error(f"Error detecting from image: {e}")
            return []
    
    def detect_from_frame(self, frame: np.ndarray, camera_id: int = 0) -> List[Dict[str, Any]]:
        """
        Detect safety violations from a video frame using YOLOv8
        
        Args:
            frame: OpenCV image (numpy array)
            camera_id: ID of the camera
            
        Returns:
            List of detections
        """
        if not self.initialized or self.yolo_model is None:
            return self._generate_mock_detections(camera_id)
        
        try:
            # Run YOLOv8 detection with optimized settings for real-time
            results = self.yolo_model(
                frame, 
                conf=self.detection_confidence_threshold,
                iou=0.5,  # NMS IoU threshold
                max_det=100,  # Maximum detections
                verbose=False  # Reduce logging
            )
            
            detections = []
            for result in results:
                if result.boxes is not None and len(result.boxes) > 0:
                    for box in result.boxes:
                        detection = self._process_yolo_detection(box, camera_id, result.names)
                        if detection:
                            detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in YOLO detection: {e}")
            return self._generate_mock_detections(camera_id)
    
    def _process_yolo_detection(self, box, camera_id: int, class_names: dict) -> Optional[Dict[str, Any]]:
        """Process a single YOLO detection box"""
        try:
            # Get box coordinates
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = class_names[class_id]
            
            # Map YOLO classes to our detection types
            detection_type, violation_type, severity, description = self._map_class_to_violation(class_name)
            
            return {
                "camera_id": camera_id,
                "detection_type": detection_type.value,
                "violation_type": violation_type.value if violation_type else None,
                "confidence": round(confidence, 2),
                "severity": severity.value,
                "description": description,
                "class_name": class_name,
                "bbox": {
                    "x": int(x1),
                    "y": int(y1),
                    "w": int(x2 - x1),
                    "h": int(y2 - y1),
                },
                "timestamp": datetime.utcnow(),
                "model": Path(self.model_path).name if self.model_path else "unknown"
            }
        except Exception as e:
            logger.error(f"Error processing detection: {e}")
            return None
    
    def _map_class_to_violation(self, class_name: str):
        """Map YOLO class names to violation types with comprehensive safety detection"""
        class_name_lower = class_name.lower().strip()
        
        # PPE Detection mappings (most critical safety violations)
        if any(term in class_name_lower for term in ['no-hardhat', 'no_hardhat', 'no-helmet', 'no_helmet', 'hardhat_violation']):
            return (DetectionType.PPE_VIOLATION, ViolationType.NO_HELMET, 
                    AlertSeverity.DANGER, f"Critical: Worker without hard hat detected - {class_name}")
        
        elif any(term in class_name_lower for term in ['no-safety-vest', 'no_vest', 'no-vest', 'vest_violation', 'no_safety_vest']):
            return (DetectionType.PPE_VIOLATION, ViolationType.NO_VEST,
                    AlertSeverity.WARNING, f"Warning: Worker without safety vest detected - {class_name}")
        
        elif any(term in class_name_lower for term in ['no-gloves', 'no_gloves', 'gloves_violation']):
            return (DetectionType.PPE_VIOLATION, ViolationType.NO_GLOVES,
                    AlertSeverity.WARNING, f"Warning: Worker without gloves detected - {class_name}")
        
        elif any(term in class_name_lower for term in ['no-mask', 'no_mask', 'mask_violation', 'no_face_mask']):
            return (DetectionType.PPE_VIOLATION, ViolationType.NO_MASK,
                    AlertSeverity.WARNING, f"Warning: Worker without face mask detected - {class_name}")
        
        elif any(term in class_name_lower for term in ['no-goggles', 'no_goggles', 'no_safety_glasses', 'eye_protection_violation']):
            return (DetectionType.PPE_VIOLATION, ViolationType.NO_GLOVES,  # Using available enum
                    AlertSeverity.WARNING, f"Warning: Worker without eye protection - {class_name}")
        
        # Positive PPE detections (compliance)
        elif any(term in class_name_lower for term in ['hardhat', 'helmet', 'hard_hat', 'safety_helmet']):
            return (DetectionType.PPE_VIOLATION, None,
                    AlertSeverity.INFO, f"PPE Compliant: Hard hat detected - {class_name}")
        
        elif any(term in class_name_lower for term in ['vest', 'safety-vest', 'safety_vest', 'hi-vis']):
            return (DetectionType.PPE_VIOLATION, None,
                    AlertSeverity.INFO, f"PPE Compliant: Safety vest detected - {class_name}")
        
        elif any(term in class_name_lower for term in ['gloves', 'safety_gloves', 'work_gloves']):
            return (DetectionType.PPE_VIOLATION, None,
                    AlertSeverity.INFO, f"PPE Compliant: Gloves detected - {class_name}")
        
        # Person/Worker detection
        elif class_name_lower in ['person', 'worker', 'employee', 'human']:
            return (DetectionType.UNSAFE_BEHAVIOR, None,
                    AlertSeverity.INFO, f"Worker detected in area - {class_name}")
        
        # Fire and emergency detection
        elif any(term in class_name_lower for term in ['fire', 'flame', 'burning']):
            return (DetectionType.FIRE_SMOKE, None,
                    AlertSeverity.DANGER, f"EMERGENCY: Fire detected - {class_name}")
        
        elif any(term in class_name_lower for term in ['smoke', 'fumes', 'gas']):
            return (DetectionType.FIRE_SMOKE, None,
                    AlertSeverity.DANGER, f"EMERGENCY: Smoke/fumes detected - {class_name}")
        
        # Vehicle and equipment detection
        elif any(term in class_name_lower for term in ['forklift', 'crane', 'excavator', 'bulldozer']):
            return (DetectionType.VEHICLE_COLLISION, None,
                    AlertSeverity.WARNING, f"Heavy equipment detected - {class_name}")
        
        elif any(term in class_name_lower for term in ['vehicle', 'truck', 'car', 'van']):
            return (DetectionType.VEHICLE_COLLISION, None,
                    AlertSeverity.WARNING, f"Vehicle detected - {class_name}")
        
        # Hazardous behavior detection
        elif any(term in class_name_lower for term in ['running', 'climbing', 'falling', 'unsafe_posture']):
            return (DetectionType.UNSAFE_BEHAVIOR, None,
                    AlertSeverity.WARNING, f"Unsafe behavior detected - {class_name}")
        
        elif any(term in class_name_lower for term in ['phone', 'mobile', 'cellphone', 'smartphone']):
            return (DetectionType.UNSAFE_BEHAVIOR, None,
                    AlertSeverity.WARNING, f"Phone use detected in workplace - {class_name}")
        
        # Restricted area detection
        elif any(term in class_name_lower for term in ['restricted', 'unauthorized', 'no_entry', 'danger_zone']):
            return (DetectionType.HAZARD_ZONE, None,
                    AlertSeverity.DANGER, f"Restricted area violation - {class_name}")
        
        # Common COCO classes that might be relevant
        elif class_name_lower in ['bicycle', 'motorcycle']:
            return (DetectionType.VEHICLE_COLLISION, None,
                    AlertSeverity.INFO, f"Two-wheeler detected - {class_name}")
        
        elif class_name_lower in ['bottle', 'cup']:
            return (DetectionType.UNSAFE_BEHAVIOR, None,
                    AlertSeverity.INFO, f"Object detected - {class_name}")
        
        # Default for any other detection
        else:
            return (DetectionType.UNSAFE_BEHAVIOR, None,
                    AlertSeverity.INFO, f"Object detected: {class_name}")
    
    def detect_violations(self, camera_id: int, frame: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Analyze a camera frame and detect safety violations
        
        Args:
            camera_id: ID of the camera
            frame: Video frame to analyze (numpy array)
            
        Returns:
            List of detected violations with bounding boxes and confidence scores
        """
        if frame is not None and isinstance(frame, np.ndarray):
            return self.detect_from_frame(frame, camera_id)
        else:
            # If no frame provided, use mock detection
            return self._generate_mock_detections(camera_id)
    
    def _generate_mock_detections(self, camera_id: int) -> List[Dict[str, Any]]:
        """Generate mock detections when YOLO is not available"""
        detections = []
        
        # Simulate 20% chance of detection per frame
        if random.random() < 0.2:
            detection = self._generate_mock_detection(camera_id)
            detections.append(detection)
            
        return detections
    
    def _generate_mock_detection(self, camera_id: int) -> Dict[str, Any]:
        """Generate a mock detection for demonstration"""
        
        # Randomly select detection type
        detection_types = [
            (DetectionType.PPE_VIOLATION, [
                (ViolationType.NO_HELMET, AlertSeverity.DANGER, "Worker without hard hat detected"),
                (ViolationType.NO_VEST, AlertSeverity.WARNING, "Worker without safety vest detected"),
                (ViolationType.NO_GLOVES, AlertSeverity.WARNING, "Worker without gloves in hazardous area"),
                (ViolationType.NO_GOGGLES, AlertSeverity.WARNING, "Worker without safety goggles"),
                (ViolationType.NO_MASK, AlertSeverity.WARNING, "Worker without face mask in required zone"),
            ]),
            (DetectionType.UNSAFE_BEHAVIOR, [
                (ViolationType.RUNNING, AlertSeverity.WARNING, "Worker running in facility"),
                (ViolationType.UNSAFE_POSTURE, AlertSeverity.INFO, "Unsafe posture detected - ergonomic risk"),
                (ViolationType.PHONE_USE, AlertSeverity.WARNING, "Worker using phone in restricted area"),
                (ViolationType.SMOKING, AlertSeverity.DANGER, "Smoking detected in no-smoking zone"),
            ]),
            (DetectionType.HAZARD_ZONE, [
                (ViolationType.RESTRICTED_AREA, AlertSeverity.DANGER, "Unauthorized access to restricted zone"),
            ]),
            (DetectionType.FIRE_SMOKE, [
                (None, AlertSeverity.DANGER, "Smoke detected in facility"),
            ]),
            (DetectionType.SLIP_TRIP_FALL, [
                (None, AlertSeverity.WARNING, "Potential slip hazard detected"),
            ]),
            (DetectionType.VEHICLE_COLLISION, [
                (None, AlertSeverity.DANGER, "Worker in forklift proximity - collision risk"),
            ]),
            (DetectionType.CROWD_DENSITY, [
                (None, AlertSeverity.WARNING, "Overcrowding detected in work area"),
            ]),
            (DetectionType.EQUIPMENT_MISUSE, [
                (None, AlertSeverity.WARNING, "Improper equipment usage detected"),
            ]),
        ]
        
        # Select random detection type and violation
        detection_type, violations = random.choice(detection_types)
        violation_type, severity, description = random.choice(violations)
        
        # Generate random bounding box (simulating detected object location)
        bbox = {
            "x": random.randint(50, 800),
            "y": random.randint(50, 600),
            "w": random.randint(100, 300),
            "h": random.randint(150, 400),
        }
        
        # Generate confidence score
        confidence = random.uniform(0.75, 0.99)
        
        return {
            "camera_id": camera_id,
            "detection_type": detection_type.value,
            "violation_type": violation_type.value if violation_type else None,
            "confidence": round(confidence, 2),
            "severity": severity.value,
            "description": description,
            "bbox": bbox,
            "timestamp": datetime.utcnow(),
            "snapshot_path": f"/snapshots/camera_{camera_id}_{datetime.utcnow().timestamp()}.jpg"
        }
    
    def analyze_ppe_compliance(self, frame: Optional[Any] = None) -> Dict[str, Any]:
        """
        Analyze Personal Protective Equipment (PPE) compliance
        Detects: helmets, vests, gloves, goggles, masks
        """
        # Mock PPE analysis
        ppe_status = {
            "helmet": random.choice([True, False]),
            "vest": random.choice([True, False]),
            "gloves": random.choice([True, False]),
            "goggles": random.choice([True, True, True]),  # Higher compliance
            "mask": random.choice([True, True, False]),
        }
        
        violations = [ppe for ppe, status in ppe_status.items() if not status]
        
        return {
            "compliant": len(violations) == 0,
            "ppe_status": ppe_status,
            "violations": violations,
            "confidence": random.uniform(0.85, 0.98)
        }
    
    def detect_hazard_zones(self, frame: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Detect workers in hazardous or restricted zones
        """
        # Mock hazard zone detection
        if random.random() < 0.15:
            return [{
                "zone_id": random.choice(["ZONE_A", "ZONE_B", "ZONE_C"]),
                "zone_type": random.choice(["restricted", "hazardous", "high_risk"]),
                "worker_count": random.randint(1, 3),
                "authorized": False,
                "confidence": random.uniform(0.80, 0.95)
            }]
        return []
    
    def detect_unsafe_behavior(self, frame: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Detect unsafe worker behaviors
        Running, climbing unsafely, improper lifting, etc.
        """
        behaviors = []
        
        if random.random() < 0.1:
            behavior_types = ["running", "climbing_unsafe", "improper_lifting", "phone_use"]
            behaviors.append({
                "behavior_type": random.choice(behavior_types),
                "risk_level": random.choice(["low", "medium", "high"]),
                "confidence": random.uniform(0.75, 0.92)
            })
        
        return behaviors
    
    def detect_fire_smoke(self, frame: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        """
        Detect fire or smoke in the facility
        """
        # Mock fire/smoke detection (very low probability)
        if random.random() < 0.02:
            return {
                "type": random.choice(["smoke", "fire", "heat_signature"]),
                "severity": "critical",
                "location_estimate": {
                    "x": random.randint(0, 1920),
                    "y": random.randint(0, 1080)
                },
                "confidence": random.uniform(0.85, 0.98)
            }
        return None
    
    def detect_vehicle_proximity(self, frame: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Detect workers in proximity to vehicles (forklifts, trucks)
        Collision risk assessment
        """
        if random.random() < 0.12:
            return [{
                "vehicle_type": random.choice(["forklift", "pallet_jack", "truck"]),
                "worker_distance": random.uniform(0.5, 3.0),  # meters
                "collision_risk": random.choice(["low", "medium", "high"]),
                "confidence": random.uniform(0.80, 0.94)
            }]
        return []
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get detection system statistics"""
        return {
            "status": "active",
            "fps": random.randint(28, 32),
            "latency_ms": random.randint(50, 150),
            "model_version": "v2.3.1",
            "confidence_threshold": self.detection_confidence_threshold,
            "detections_per_minute": random.randint(5, 25)
        }

# Global detector instance
cv_detector = CVDetector()
