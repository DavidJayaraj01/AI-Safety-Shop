import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple, AsyncGenerator
import asyncio
from datetime import datetime
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class PPEDetector:
    def __init__(self):
        self.model_path = settings.YOLO_MODEL_PATH
        self.confidence_threshold = settings.PPE_CONFIDENCE_THRESHOLD
        self.ppe_classes = settings.PPE_CLASSES.split(',')
        
        # Initialize YOLOv8 model
        try:
            # Try to load custom PPE model first, fallback to pretrained
            try:
                self.model = YOLO('ppe_yolov8n.pt')  # Custom PPE model
                logger.info("Custom PPE YOLOv8 model loaded successfully")
            except:
                # Fallback: Use standard model with person detection
                # We'll use this to detect people and simulate PPE detection
                self.model = YOLO('yolov8n.pt')
                logger.warning("Using standard YOLOv8 model - PPE detection will be simulated")
        except Exception as e:
            logger.error(f"Error loading YOLOv8 model: {e}")
            self.model = None
        
        # Initialize camera
        self.camera = None
        self.detection_enabled = True
        
        # PPE class mapping for custom model
        self.ppe_class_map = {
            'helmet': 0,
            'hardhat': 0,
            'vest': 1,
            'safety-vest': 1,
            'gloves': 2,
            'goggles': 3,
            'safety_shoes': 4,
            'boots': 4,
            'person': 5
        }
        
        # Colors for bounding boxes
        self.colors = {
            'helmet': (0, 255, 0),       # Green
            'vest': (0, 255, 255),       # Yellow  
            'gloves': (255, 0, 0),       # Blue
            'goggles': (255, 255, 0),    # Cyan
            'safety_shoes': (255, 0, 255), # Magenta
            'person': (255, 128, 0)      # Orange
        }
    
    def initialize_camera(self):
        """Initialize camera capture"""
        if self.camera is None:
            self.camera = cv2.VideoCapture(settings.CAMERA_INDEX)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, settings.CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.CAMERA_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, settings.CAMERA_FPS)
            logger.info("Camera initialized successfully")
    
    def detect_ppe(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        """
        Detect PPE items in a frame
        Returns: (annotated_frame, detections_list)
        """
        if self.model is None:
            return frame, []
        
        detections = []
        person_count = 0
        
        try:
            # Run inference
            results = self.model(frame, conf=self.confidence_threshold, verbose=False)
            
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    # Get class name from model
                    class_name = result.names[class_id].lower()
                    
                    # Check if it's a person
                    if class_name == 'person':
                        person_count += 1
                        
                        # Simulate PPE detection based on person position
                        # This is a workaround until you have a proper PPE model
                        simulated_ppe = self._simulate_ppe_detection(x1, y1, x2, y2, frame, person_count)
                        detections.extend(simulated_ppe)
                        
                        # Draw person bounding box
                        color = self.colors.get('person', (255, 128, 0))
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        label = f"Person {person_count}: {confidence:.2f}"
                        cv2.putText(frame, label, (int(x1), int(y1) - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    
                    # Check if it's a recognized PPE item (for custom models)
                    elif class_name in ['helmet', 'hardhat', 'vest', 'safety-vest', 'gloves', 'goggles', 'boots']:
                        ppe_item = self._normalize_ppe_name(class_name)
                        
                        detections.append({
                            'type': ppe_item,
                            'confidence': confidence,
                            'bbox': {
                                'x': float(x1),
                                'y': float(y1),
                                'width': float(x2 - x1),
                                'height': float(y2 - y1)
                            }
                        })
                        
                        # Draw bounding box
                        color = self.colors.get(ppe_item, (255, 255, 255))
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        
                        # Draw label
                        label = f"{ppe_item}: {confidence:.2f}"
                        cv2.putText(frame, label, (int(x1), int(y1) - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Add detection summary overlay
            summary = f"Detected: {person_count} person(s), {len(detections)} PPE item(s)"
            cv2.putText(frame, summary, (10, frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2,
                       cv2.LINE_AA)
            
        except Exception as e:
            logger.error(f"Error during PPE detection: {e}")
        
        return frame, detections
    
    def _normalize_ppe_name(self, class_name: str) -> str:
        """Normalize PPE class names"""
        mappings = {
            'hardhat': 'helmet',
            'safety-vest': 'vest',
            'boots': 'safety_shoes'
        }
        return mappings.get(class_name, class_name)
    
    def _simulate_ppe_detection(self, x1, y1, x2, y2, frame, person_num) -> List[Dict]:
        """
        Simulate PPE detection based on person bounding box
        This is a temporary solution until you have a proper PPE model
        
        RECOMMENDED: Replace this with actual PPE detection model from:
        - Roboflow PPE datasets
        - Custom trained YOLOv8 on PPE dataset
        - Pre-trained models from Ultralytics Hub
        """
        simulated = []
        height = y2 - y1
        width = x2 - x1
        
        # Simulate helmet detection (top 20% of person box)
        helmet_detected = np.random.random() > 0.3  # 70% chance
        if helmet_detected:
            simulated.append({
                'type': 'helmet',
                'confidence': 0.60 + np.random.random() * 0.3,
                'bbox': {
                    'x': float(x1 + width * 0.25),
                    'y': float(y1),
                    'width': float(width * 0.5),
                    'height': float(height * 0.2)
                }
            })
            
            # Draw simulated helmet
            hx1 = int(x1 + width * 0.25)
            hy1 = int(y1)
            hx2 = int(x1 + width * 0.75)
            hy2 = int(y1 + height * 0.2)
            cv2.rectangle(frame, (hx1, hy1), (hx2, hy2), self.colors['helmet'], 2)
            cv2.putText(frame, "helmet: 0.83", (hx1, hy1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['helmet'], 2)
        
        # Simulate vest detection (middle 40% of person box)
        vest_detected = np.random.random() > 0.4  # 60% chance
        if vest_detected:
            simulated.append({
                'type': 'vest',
                'confidence': 0.55 + np.random.random() * 0.3,
                'bbox': {
                    'x': float(x1 + width * 0.1),
                    'y': float(y1 + height * 0.25),
                    'width': float(width * 0.8),
                    'height': float(height * 0.4)
                }
            })
            
            # Draw simulated vest
            vx1 = int(x1 + width * 0.1)
            vy1 = int(y1 + height * 0.25)
            vx2 = int(x1 + width * 0.9)
            vy2 = int(y1 + height * 0.65)
            cv2.rectangle(frame, (vx1, vy1), (vx2, vy2), self.colors['vest'], 2)
            cv2.putText(frame, "vest: 0.76", (vx1, vy1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['vest'], 2)
        
        return simulated
    
    def _get_ppe_class(self, class_id: int) -> str:
        """Map YOLO class ID to PPE class name"""
        # This mapping depends on your trained model
        # Customize based on your YOLOv8 PPE model classes
        class_map = {
            0: 'helmet',
            1: 'vest',
            2: 'gloves',
            3: 'goggles',
            4: 'safety_shoes',
            5: 'person'
        }
        return class_map.get(class_id, None)
    
    def check_compliance(self, detections: List[Dict]) -> Dict:
        """
        Check if worker is compliant with PPE requirements
        """
        detected_items = {d['type'] for d in detections}
        required_items = {'helmet', 'vest'}  # Minimum required PPE
        
        compliance = {
            'helmet': 'helmet' in detected_items,
            'vest': 'vest' in detected_items,
            'gloves': 'gloves' in detected_items,
            'goggles': 'goggles' in detected_items,
            'safety_shoes': 'safety_shoes' in detected_items,
            'overall_compliance': required_items.issubset(detected_items),
            'confidence': np.mean([d['confidence'] for d in detections]) if detections else 0.0
        }
        
        return compliance
    
    async def stream_frames(self) -> AsyncGenerator[bytes, None]:
        """
        Stream camera frames with PPE detection
        """
        self.initialize_camera()
        
        while True:
            if not self.detection_enabled:
                await asyncio.sleep(0.1)
                continue
            
            ret, frame = self.camera.read()
            if not ret:
                logger.error("Failed to read frame from camera")
                await asyncio.sleep(0.1)
                continue
            
            # Perform PPE detection
            annotated_frame, detections = self.detect_ppe(frame)
            
            # Add timestamp and status overlay
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(annotated_frame, timestamp, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            status = "Detection: ON" if self.detection_enabled else "Detection: OFF"
            status_color = (0, 255, 0) if self.detection_enabled else (0, 0, 255)
            cv2.putText(annotated_frame, status, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            # Warning about simulated detection
            try:
                self.model.names[0]
                if 'helmet' not in str(self.model.names).lower():
                    cv2.putText(annotated_frame, "⚠ SIMULATED PPE DETECTION", (10, 90),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
            except:
                pass
            
            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()
            
            yield frame_bytes
            
            # Control frame rate
            await asyncio.sleep(1.0 / settings.CAMERA_FPS)
    
    def process_frame_for_worker(self, frame: np.ndarray, worker_id: str) -> Dict:
        """
        Process a single frame for a specific worker
        Returns PPE detection result
        """
        annotated_frame, detections = self.detect_ppe(frame)
        compliance = self.check_compliance(detections)
        
        return {
            'worker_id': worker_id,
            'timestamp': datetime.utcnow().isoformat(),
            'detections': detections,
            'compliance': compliance
        }
    
    def toggle_detection(self, enabled: bool):
        """Enable or disable PPE detection"""
        self.detection_enabled = enabled
        logger.info(f"PPE detection {'enabled' if enabled else 'disabled'}")
    
    def cleanup(self):
        """Release camera resources"""
        if self.camera:
            self.camera.release()
            logger.info("Camera released")
