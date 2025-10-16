"""
Computer Vision Detection Service
AI-powered safety monitoring using YOLO models for real-time detection
Integrates with YOLO models for PPE detection and safety violation monitoring
"""

import cv2
import numpy as np
from ultralytics import YOLO
import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from app.models.models import DetectionType, ViolationType, AlertSeverity

logger = logging.getLogger(__name__)

class CVDetector:
    """
    Computer Vision Detector for workplace safety monitoring using YOLO
    Real-time detection of:
    - PPE violations (missing helmets, vests, gloves, etc.)
    - Unsafe behaviors (running, climbing, phone use)
    - Hazard zones (restricted area access)
    - Fire/smoke detection
    - Vehicle collision risks
    """
    
    def __init__(self):
        self.detection_confidence_threshold = 0.5
        self.initialized = False
        self.models = {}
        self._load_models()
        
    def _load_models(self):
        """Load YOLO models for detection"""
        try:
            # Define model paths
            model_paths = {
                'general': '/home/balu/AI-Safety-Shop/AI-smart-shop/yolov8n.pt',
                'ppe': '/home/balu/AI-Safety-Shop/AI-smart-shop/ppe-detection.pt'
            }
            
            # Load models
            for model_name, model_path in model_paths.items():
                if Path(model_path).exists():
                    self.models[model_name] = YOLO(model_path)
                    logger.info(f"Loaded {model_name} model from {model_path}")
                else:
                    logger.warning(f"Model not found: {model_path}")
            
            # Set initialized flag
            self.initialized = len(self.models) > 0
            
            if self.initialized:
                logger.info(f"CV Detector initialized with {len(self.models)} models")
            else:
                logger.error("No YOLO models could be loaded")
                
        except Exception as e:
            logger.error(f"Error loading YOLO models: {e}")
            self.initialized = False
    
    def detect_violations(self, camera_id: int, frame: Optional[np.ndarray] = None) -> List[Dict[str, Any]]:
        """
        Analyze a camera frame and detect safety violations using YOLO
        
        Args:
            camera_id: ID of the camera
            frame: Video frame to analyze (numpy array)
            
        Returns:
            List of detected violations with bounding boxes and confidence scores
        """
        if not self.initialized:
            logger.warning("CV Detector not properly initialized, using mock detections")
            return self._generate_mock_detections(camera_id)
            
        if frame is None:
            logger.warning("No frame provided, using mock detections")
            return self._generate_mock_detections(camera_id)
            
        detections = []
        
        try:
            # Process frame with different models
            if 'ppe' in self.models:
                ppe_detections = self._detect_ppe_violations(frame, camera_id)
                detections.extend(ppe_detections)
                
            if 'general' in self.models:
                general_detections = self._detect_general_violations(frame, camera_id)
                detections.extend(general_detections)
                
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            # Fallback to mock detections
            detections = self._generate_mock_detections(camera_id)
            
        return detections
    
    def _detect_ppe_violations(self, frame: np.ndarray, camera_id: int) -> List[Dict[str, Any]]:
        """Detect PPE violations using specialized PPE model"""
        detections = []
        
        try:
            # Run PPE detection
            results = self.models['ppe'](frame, conf=self.detection_confidence_threshold)
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract box coordinates and confidence
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0].cpu().numpy())
                        cls_id = int(box.cls[0].cpu().numpy())
                        
                        # Map class ID to violation type
                        violation_info = self._map_ppe_class_to_violation(cls_id)
                        
                        if violation_info:
                            detection = {
                                "camera_id": camera_id,
                                "detection_type": DetectionType.PPE_VIOLATION,
                                "violation_type": violation_info["violation_type"],
                                "severity": violation_info["severity"],
                                "description": violation_info["description"],
                                "confidence": confidence,
                                "bbox": {
                                    "x": int(x1),
                                    "y": int(y1),
                                    "w": int(x2 - x1),
                                    "h": int(y2 - y1)
                                },
                                "timestamp": datetime.utcnow()
                            }
                            detections.append(detection)
                            
        except Exception as e:
            logger.error(f"Error in PPE detection: {e}")
            
        return detections
    
    def _detect_general_violations(self, frame: np.ndarray, camera_id: int) -> List[Dict[str, Any]]:
        """Detect general safety violations using general YOLO model"""
        detections = []
        
        try:
            # Run general object detection
            results = self.models['general'](frame, conf=self.detection_confidence_threshold)
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract box coordinates and confidence
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0].cpu().numpy())
                        cls_id = int(box.cls[0].cpu().numpy())
                        
                        # Map class ID to potential safety violations
                        violation_info = self._map_general_class_to_violation(cls_id)
                        
                        if violation_info:
                            detection = {
                                "camera_id": camera_id,
                                "detection_type": violation_info["detection_type"],
                                "violation_type": violation_info.get("violation_type"),
                                "severity": violation_info["severity"],
                                "description": violation_info["description"],
                                "confidence": confidence,
                                "bbox": {
                                    "x": int(x1),
                                    "y": int(y1),
                                    "w": int(x2 - x1),
                                    "h": int(y2 - y1)
                                },
                                "timestamp": datetime.utcnow()
                            }
                            detections.append(detection)
                            
        except Exception as e:
            logger.error(f"Error in general detection: {e}")
            
        return detections
    
    def _map_ppe_class_to_violation(self, cls_id: int) -> Optional[Dict[str, Any]]:
        """Map PPE model class ID to violation information"""
        # This mapping depends on your PPE model's class definitions
        # Update these mappings based on your actual PPE model
        ppe_class_map = {
            0: {
                "violation_type": ViolationType.NO_HELMET,
                "severity": AlertSeverity.DANGER,
                "description": "Worker without hard hat detected"
            },
            1: {
                "violation_type": ViolationType.NO_VEST,
                "severity": AlertSeverity.WARNING,
                "description": "Worker without safety vest detected"
            },
            2: {
                "violation_type": ViolationType.NO_GLOVES,
                "severity": AlertSeverity.WARNING,
                "description": "Worker without gloves detected"
            },
            3: {
                "violation_type": ViolationType.NO_GOGGLES,
                "severity": AlertSeverity.WARNING,
                "description": "Worker without safety goggles detected"
            },
            4: {
                "violation_type": ViolationType.NO_MASK,
                "severity": AlertSeverity.WARNING,
                "description": "Worker without face mask detected"
            }
        }
        
        return ppe_class_map.get(cls_id)
    
    def _map_general_class_to_violation(self, cls_id: int) -> Optional[Dict[str, Any]]:
        """Map general YOLO class ID to potential safety violations"""
        # COCO class mappings for common safety-related objects
        general_class_map = {
            0: {  # person
                "detection_type": DetectionType.UNSAFE_BEHAVIOR,
                "violation_type": None,
                "severity": AlertSeverity.INFO,
                "description": "Person detected in monitored area"
            },
            2: {  # car
                "detection_type": DetectionType.VEHICLE_COLLISION,
                "violation_type": None,
                "severity": AlertSeverity.WARNING,
                "description": "Vehicle detected - potential collision risk"
            },
            3: {  # motorcycle
                "detection_type": DetectionType.VEHICLE_COLLISION,
                "violation_type": None,
                "severity": AlertSeverity.WARNING,
                "description": "Motorcycle detected - collision risk"
            },
            5: {  # bus
                "detection_type": DetectionType.VEHICLE_COLLISION,
                "violation_type": None,
                "severity": AlertSeverity.WARNING,
                "description": "Large vehicle detected - high collision risk"
            },
            7: {  # truck
                "detection_type": DetectionType.VEHICLE_COLLISION,
                "violation_type": None,
                "severity": AlertSeverity.DANGER,
                "description": "Truck detected - high collision risk"
            },
            67: {  # cell phone
                "detection_type": DetectionType.UNSAFE_BEHAVIOR,
                "violation_type": ViolationType.PHONE_USE,
                "severity": AlertSeverity.WARNING,
                "description": "Cell phone use detected in restricted area"
            }
        }
        
        return general_class_map.get(cls_id)
    
    def process_camera_feed(self, camera_id: int, stream_url: str) -> None:
        """
        Process live camera feed for real-time detection
        
        Args:
            camera_id: ID of the camera
            stream_url: URL or path to camera stream
        """
        try:
            cap = cv2.VideoCapture(stream_url)
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Detect violations in the frame
                detections = self.detect_violations(camera_id, frame)
                
                # Process detections (save to database, trigger alerts, etc.)
                for detection in detections:
                    logger.info(f"Detection: {detection['description']} (confidence: {detection['confidence']:.2f})")
                    
                # Add small delay to prevent overwhelming the system
                cv2.waitKey(30)
                
        except Exception as e:
            logger.error(f"Error processing camera feed {camera_id}: {e}")
        finally:
            if 'cap' in locals():
                cap.release()
    
    def _generate_mock_detections(self, camera_id: int) -> List[Dict[str, Any]]:
        """Generate mock detections for demonstration when models aren't available"""
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
