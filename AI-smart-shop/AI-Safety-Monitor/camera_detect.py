from ultralytics import YOLO
import cv2
import requests
import argparse
import os
import sys
import numpy as np
import time
from datetime import datetime

API_URL = "http://192.168.1.8:8000/alert"  # Replace with your FastAPI server IP

# PPE class mappings for COCO model (we'll simulate PPE detection)
PPE_CLASSES = {
    'helmet': 1000,
    'vest': 1001,
    'goggles': 1002,
    'gloves': 1003,
    'person': 0
}

REQUIRED_PPE = ['helmet', 'vest', 'goggles', 'gloves']

def parse_args():
    p = argparse.ArgumentParser(description="Run PPE Safety Detection Camera")
    p.add_argument("--weights", "-w", default="yolov8n.pt", help="Path to model weights (.pt)")
    p.add_argument("--device", "-d", default=0, help="Camera device index or path. Default: 0")
    p.add_argument("--endpoint", "-e", default=API_URL, help="Alert endpoint URL")
    p.add_argument("--confidence", "-c", default=0.5, type=float, help="Detection confidence threshold")
    p.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    p.add_argument("--fps", "-f", default=15, type=int, help="Camera FPS limit for performance (default: 15)")
    p.add_argument("--resolution", "-r", default="640x480", help="Camera resolution (default: 640x480)")
    p.add_argument("--process-interval", "-p", default=0.5, type=float, help="Processing interval in seconds (default: 0.5)")
    return p.parse_args()

def simulate_ppe_detection(person_box, frame_shape):
    """Simulate PPE detection for demo purposes"""
    x1, y1, x2, y2 = person_box
    person_width = x2 - x1
    person_height = y2 - y1
    
    # Simulate PPE items with some randomness for realism
    ppe_items = []
    
    # Helmet (top of person)
    if np.random.random() > 0.3:  # 70% chance of having helmet
        helmet_conf = np.random.uniform(0.6, 0.95)
        helmet_box = [x1 + person_width*0.2, y1, x2 - person_width*0.2, y1 + person_height*0.3]
        ppe_items.append(('helmet', helmet_box, helmet_conf))
    
    # Vest (torso area)
    if np.random.random() > 0.25:  # 75% chance of having vest
        vest_conf = np.random.uniform(0.65, 0.92)
        vest_box = [x1 + person_width*0.1, y1 + person_height*0.3, x2 - person_width*0.1, y1 + person_height*0.8]
        ppe_items.append(('vest', vest_box, vest_conf))
    
    # Goggles (face area)
    if np.random.random() > 0.4:  # 60% chance of having goggles
        goggles_conf = np.random.uniform(0.55, 0.88)
        goggles_box = [x1 + person_width*0.3, y1 + person_height*0.1, x2 - person_width*0.3, y1 + person_height*0.25]
        ppe_items.append(('goggles', goggles_box, goggles_conf))
    
    # Gloves (hand areas)
    if np.random.random() > 0.5:  # 50% chance of having gloves
        gloves_conf = np.random.uniform(0.5, 0.85)
        # Left glove
        glove_box = [x1, y1 + person_height*0.4, x1 + person_width*0.2, y1 + person_height*0.7]
        ppe_items.append(('gloves', glove_box, gloves_conf))
    
    return ppe_items

def check_ppe_compliance(person_box, detected_ppe):
    """Check if person has all required PPE"""
    detected_items = set([item[0] for item in detected_ppe])
    missing_ppe = []
    
    for required_item in REQUIRED_PPE:
        if required_item not in detected_items:
            missing_ppe.append(required_item)
    
    return missing_ppe

def send_alert(person_id, missing_ppe, endpoint, verbose=False):
    """Send alert to endpoint about missing PPE"""
    payload = {
        "timestamp": datetime.now().isoformat(),
        "person_id": person_id,
        "alert_type": "PPE_VIOLATION",
        "missing_ppe": missing_ppe,
        "severity": "HIGH" if len(missing_ppe) >= 3 else "MEDIUM",
        "location": "Camera_1"
    }
    
    try:
        response = requests.post(endpoint, json=payload, timeout=2)
        if response.status_code == 200:
            if verbose:
                print(f"🔔 Alert sent successfully for Person {person_id}")
            return True
        else:
            if verbose:
                print(f"⚠️ Alert failed (Status: {response.status_code}) for Person {person_id}")
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"⚠️ Network error sending alert for Person {person_id}: {e}")
    except Exception as e:
        if verbose:
            print(f"⚠️ Error sending alert for Person {person_id}: {e}")
    
    return False

def draw_ppe_detection(frame, person_box, detected_ppe, missing_ppe, person_id):
    """Draw PPE detection results on frame"""
    x1, y1, x2, y2 = map(int, person_box)
    
    # Draw person box
    person_color = (0, 255, 0) if not missing_ppe else (0, 0, 255)
    cv2.rectangle(frame, (x1, y1), (x2, y2), person_color, 2)
    
    # Draw person label
    status = "✅ PPE COMPLIANT" if not missing_ppe else f"❌ MISSING: {', '.join(missing_ppe).upper()}"
    cv2.putText(frame, f"Person {person_id}", (x1, y1-30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, person_color, 2)
    cv2.putText(frame, status, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, person_color, 2)
    
    # Draw detected PPE items
    for ppe_type, ppe_box, conf in detected_ppe:
        px1, py1, px2, py2 = map(int, ppe_box)
        ppe_color = (0, 255, 0)  # Green for detected PPE
        cv2.rectangle(frame, (px1, py1), (px2, py2), ppe_color, 1)
        cv2.putText(frame, f"{ppe_type} {conf:.2f}", (px1, py1-5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, ppe_color, 1)

def main():
    args = parse_args()
    weights_path = args.weights

    if not os.path.isfile(weights_path):
        print(f"ERROR: Weights file not found: '{weights_path}'")
        print(f"💡 Using default YOLO model for PPE simulation demo")
        weights_path = "yolov8n.pt"

    try:
        model = YOLO(weights_path)
        print("📦 Model loaded successfully.")
        print(f"🎯 Endpoint: {args.endpoint}")
        print(f"🔍 Confidence threshold: {args.confidence}")
        print("📋 Required PPE: helmet, vest, goggles, gloves")
        print("🚀 Starting PPE safety monitoring...")
    except Exception as e:
        print("Failed loading model:", e)
        sys.exit(3)

    cap = cv2.VideoCapture(int(args.device) if str(args.device).isdigit() else args.device)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        sys.exit(4)

    # Optimize camera settings for better performance
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to prevent lag
    
    # Parse resolution
    try:
        width, height = map(int, args.resolution.split('x'))
    except:
        width, height = 640, 480  # Default fallback
    
    cap.set(cv2.CAP_PROP_FPS, args.fps)        # Set FPS limit
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)   # Set resolution for faster processing
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    print(f"📹 Camera settings: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))} @ {int(cap.get(cv2.CAP_PROP_FPS))}fps")

    frame_count = 0
    last_process_time = time.time()
    process_interval = args.process_interval  # Use configurable interval
    last_detections = []    # Store last detections for smooth display
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera.")
            break

        frame_count += 1
        current_time = time.time()
        
        # Only process detection every interval to improve performance
        if current_time - last_process_time >= process_interval:
            try:
                results = model(frame, conf=args.confidence, verbose=False)[0]
                detections = results.boxes.data.cpu().numpy() if results.boxes is not None else []
                
                # Filter for person detections
                persons = []
                for det in detections:
                    x1, y1, x2, y2, conf, cls = det
                    if int(cls) == 0:  # Person class in COCO
                        persons.append([x1, y1, x2, y2, conf])
                
                last_detections = persons  # Store for display
                last_process_time = current_time
                
                if len(persons) > 0:
                    print(f"\n[Frame {frame_count}] 👥 {len(persons)} personnel detected")
                    
                    for i, person in enumerate(persons):
                        person_id = i + 1
                        
                        # Simulate PPE detection for this person
                        detected_ppe = simulate_ppe_detection(person[:4], frame.shape)
                        
                        # Check PPE compliance
                        missing_ppe = check_ppe_compliance(person[:4], detected_ppe)
                        
                        # Console output
                        if missing_ppe:
                            print(f"🚨 Person {person_id}: MISSING {', '.join(missing_ppe).upper()}")
                            # Send alert (non-blocking)
                            try:
                                send_alert(person_id, missing_ppe, args.endpoint, args.verbose)
                            except:
                                pass  # Don't let alert failures stop the system
                        else:
                            print(f"✅ Person {person_id}: PPE compliant")
                        
                        if args.verbose:
                            detected_items = [item[0] for item in detected_ppe]
                            print(f"   Detected: {', '.join(detected_items) if detected_items else 'None'}")
            
            except Exception as e:
                print(f"⚠️ Processing error: {e}")
                continue
        
        # Draw using last detections for smooth display
        if len(last_detections) == 0:
            cv2.putText(frame, "🔍 No personnel detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        else:
            for i, person in enumerate(last_detections):
                person_id = i + 1
                detected_ppe = simulate_ppe_detection(person[:4], frame.shape)
                missing_ppe = check_ppe_compliance(person[:4], detected_ppe)
                draw_ppe_detection(frame, person[:4], detected_ppe, missing_ppe, person_id)

        # Show frame info
        fps = 1.0 / (current_time - last_process_time + 0.001)
        cv2.putText(frame, f"Frame: {frame_count} | Personnel: {len(last_detections)} | FPS: {fps:.1f}", 
                   (10, frame.shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Show camera feed
        cv2.imshow("PPE Safety Monitor", frame)
        
        # Non-blocking key check
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            print("\n🛑 Stopping PPE safety monitoring...")
            break
        elif key == ord("r"):  # Press 'r' to reset/refresh
            print("🔄 Refreshing detection...")
            last_detections = []

    cap.release()
    cv2.destroyAllWindows()
    print("📊 PPE monitoring session completed")

if __name__ == "__main__":
    main()
