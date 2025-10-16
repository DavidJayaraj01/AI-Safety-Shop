#!/usr/bin/env python3
"""
Fast PPE Detection Camera - Optimized for Performance
Lightweight version for maximum camera performance
"""

from ultralytics import YOLO
import cv2
import requests
import argparse
import os
import sys
import numpy as np
import time
from datetime import datetime
import threading
from queue import Queue

class FastPPEDetector:
    def __init__(self, args):
        self.args = args
        self.model = None
        self.cap = None
        self.alert_queue = Queue()
        self.running = False
        self.last_detections = []
        
        # Performance settings
        self.process_interval = args.process_interval
        self.last_process_time = 0
        
    def load_model(self):
        """Load YOLO model"""
        weights_path = self.args.weights
        if not os.path.isfile(weights_path):
            print(f"ERROR: Weights file not found: '{weights_path}'")
            weights_path = "yolov8n.pt"
            
        try:
            self.model = YOLO(weights_path)
            print("📦 Model loaded successfully.")
            return True
        except Exception as e:
            print(f"Failed loading model: {e}")
            return False
    
    def setup_camera(self):
        """Setup camera with optimized settings"""
        device = int(self.args.device) if str(self.args.device).isdigit() else self.args.device
        self.cap = cv2.VideoCapture(device)
        
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            return False
        
        # Optimize camera settings
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Parse resolution
        try:
            width, height = map(int, self.args.resolution.split('x'))
        except:
            width, height = 640, 480
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, self.args.fps)
        
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        
        print(f"📹 Camera: {actual_width}x{actual_height} @ {actual_fps}fps")
        return True
    
    def alert_worker(self):
        """Background thread for sending alerts"""
        while self.running:
            try:
                if not self.alert_queue.empty():
                    alert_data = self.alert_queue.get(timeout=1)
                    try:
                        response = requests.post(
                            self.args.endpoint, 
                            json=alert_data, 
                            timeout=1
                        )
                        if self.args.verbose and response.status_code == 200:
                            print(f"🔔 Alert sent for Person {alert_data['person_id']}")
                    except:
                        pass  # Silently ignore alert failures
            except:
                continue
    
    def simulate_ppe_detection(self, person_box):
        """Fast PPE simulation"""
        x1, y1, x2, y2 = person_box
        person_width = x2 - x1
        person_height = y2 - y1
        
        ppe_items = []
        
        # Simplified simulation for performance
        if np.random.random() > 0.3:
            ppe_items.append('helmet')
        if np.random.random() > 0.25:
            ppe_items.append('vest')
        if np.random.random() > 0.4:
            ppe_items.append('goggles')
        if np.random.random() > 0.5:
            ppe_items.append('gloves')
            
        return ppe_items
    
    def check_compliance(self, detected_ppe):
        """Check PPE compliance"""
        required = {'helmet', 'vest', 'goggles', 'gloves'}
        detected_set = set(detected_ppe)
        missing = list(required - detected_set)
        return missing
    
    def send_alert_async(self, person_id, missing_ppe):
        """Queue alert for background sending"""
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "person_id": person_id,
            "alert_type": "PPE_VIOLATION",
            "missing_ppe": missing_ppe,
            "severity": "HIGH" if len(missing_ppe) >= 3 else "MEDIUM",
            "location": "Camera_1"
        }
        
        try:
            self.alert_queue.put_nowait(alert_data)
        except:
            pass  # Queue full, skip this alert
    
    def draw_fast_overlay(self, frame, persons):
        """Fast drawing with minimal processing"""
        for i, person in enumerate(persons):
            x1, y1, x2, y2 = map(int, person[:4])
            person_id = i + 1
            
            # Quick PPE check
            detected_ppe = self.simulate_ppe_detection(person[:4])
            missing_ppe = self.check_compliance(detected_ppe)
            
            # Simple color coding
            color = (0, 0, 255) if missing_ppe else (0, 255, 0)
            status = f"Person {person_id}: {'VIOLATION' if missing_ppe else 'OK'}"
            
            # Minimal drawing
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, status, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Send alert if needed
            if missing_ppe:
                self.send_alert_async(person_id, missing_ppe)
                if not self.args.verbose:  # Only print if not verbose to reduce console spam
                    print(f"🚨 Person {person_id}: MISSING {', '.join(missing_ppe).upper()}")
    
    def run(self):
        """Main detection loop"""
        if not self.load_model() or not self.setup_camera():
            return False
        
        self.running = True
        
        # Start alert worker thread
        alert_thread = threading.Thread(target=self.alert_worker, daemon=True)
        alert_thread.start()
        
        print("🚀 Fast PPE monitoring started (Press 'q' to quit, 'r' to reset)")
        
        frame_count = 0
        
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("Camera read failed")
                    break
                
                frame_count += 1
                current_time = time.time()
                
                # Process detection at intervals
                if current_time - self.last_process_time >= self.process_interval:
                    try:
                        # Fast detection
                        results = self.model(frame, conf=self.args.confidence, verbose=False)[0]
                        detections = results.boxes.data.cpu().numpy() if results.boxes is not None else []
                        
                        # Filter persons quickly
                        persons = [det for det in detections if int(det[5]) == 0]
                        self.last_detections = persons
                        self.last_process_time = current_time
                        
                        if persons and self.args.verbose:
                            print(f"[Frame {frame_count}] 👥 {len(persons)} personnel")
                            
                    except Exception as e:
                        if self.args.verbose:
                            print(f"⚠️ Detection error: {e}")
                
                # Fast drawing
                if self.last_detections:
                    self.draw_fast_overlay(frame, self.last_detections)
                else:
                    cv2.putText(frame, "No personnel detected", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Minimal frame info
                cv2.putText(frame, f"Personnel: {len(self.last_detections)}", 
                           (10, frame.shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Show frame
                cv2.imshow("Fast PPE Monitor", frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.last_detections = []
                    print("🔄 Reset detections")
                    
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        
        finally:
            self.running = False
            self.cap.release()
            cv2.destroyAllWindows()
            print("📊 Fast PPE monitoring stopped")
        
        return True

def parse_args():
    p = argparse.ArgumentParser(description="Fast PPE Detection Camera")
    p.add_argument("--weights", "-w", default="yolov8n.pt", help="Model weights path")
    p.add_argument("--device", "-d", default=0, help="Camera device")
    p.add_argument("--endpoint", "-e", default="http://localhost:8000/alert", help="Alert endpoint")
    p.add_argument("--confidence", "-c", default=0.5, type=float, help="Confidence threshold")
    p.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    p.add_argument("--fps", "-f", default=15, type=int, help="Camera FPS limit")
    p.add_argument("--resolution", "-r", default="320x240", help="Camera resolution (smaller=faster)")
    p.add_argument("--process-interval", "-p", default=1.0, type=float, help="Processing interval (larger=faster)")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    detector = FastPPEDetector(args)
    detector.run()