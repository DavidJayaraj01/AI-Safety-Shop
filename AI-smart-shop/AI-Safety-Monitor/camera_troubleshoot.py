#!/usr/bin/env python3
"""
Camera Troubleshooting Tool
Diagnoses camera issues and provides performance recommendations
"""

import cv2
import time
import sys

def test_camera_access():
    """Test basic camera access"""
    print("🔍 Testing camera access...")
    
    for device_id in range(3):  # Test first 3 camera devices
        try:
            cap = cv2.VideoCapture(device_id)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    height, width = frame.shape[:2]
                    print(f"✅ Camera {device_id}: Working - {width}x{height}")
                    cap.release()
                    return device_id
                else:
                    print(f"❌ Camera {device_id}: Can't read frames")
            else:
                print(f"❌ Camera {device_id}: Can't open")
            cap.release()
        except Exception as e:
            print(f"❌ Camera {device_id}: Error - {e}")
    
    print("🚨 No working cameras found!")
    return None

def test_camera_performance(device_id):
    """Test camera performance"""
    print(f"\n📊 Testing camera {device_id} performance...")
    
    cap = cv2.VideoCapture(device_id)
    if not cap.isOpened():
        print("❌ Cannot open camera for performance test")
        return
    
    # Test different settings
    settings = [
        (160, 120, "Minimal"),
        (320, 240, "Low"),
        (640, 480, "Standard"),
        (1280, 720, "High")
    ]
    
    for width, height, label in settings:
        print(f"\n🔧 Testing {label} resolution ({width}x{height})...")
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Measure frame rate
        start_time = time.time()
        frame_count = 0
        test_duration = 3.0  # seconds
        
        while time.time() - start_time < test_duration:
            ret, frame = cap.read()
            if ret:
                frame_count += 1
            else:
                print("❌ Frame read failed")
                break
        
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if fps > 10:
            status = "✅ Good"
        elif fps > 5:
            status = "⚠️ Slow"
        else:
            status = "❌ Too Slow"
        
        print(f"   Resolution: {actual_width}x{actual_height}")
        print(f"   FPS: {fps:.1f} {status}")
        
        if fps >= 10:
            print(f"   💡 Recommended for PPE detection")
    
    cap.release()

def recommend_settings():
    """Provide performance recommendations"""
    print(f"\n💡 Performance Recommendations:")
    print(f"   📹 For best performance:")
    print(f"      - Use resolution 320x240 or lower")
    print(f"      - Set process-interval to 1.0 or higher")
    print(f"      - Limit FPS to 15 or lower")
    print(f"   ⚡ For ultra-fast detection:")
    print(f"      - Use fast_camera_detect.py")
    print(f"      - Set resolution to 160x120")
    print(f"      - Set process-interval to 2.0")
    print(f"   🔧 If camera gets stuck:")
    print(f"      - Reduce resolution")
    print(f"      - Increase process-interval")
    print(f"      - Check camera connections")

def main():
    print("🚨 PPE Camera Troubleshooting Tool")
    print("=" * 40)
    
    # Test camera access
    working_camera = test_camera_access()
    
    if working_camera is not None:
        # Test performance
        test_camera_performance(working_camera)
        
        # Show sample commands
        print(f"\n🚀 Sample Commands for Camera {working_camera}:")
        print(f"   Fast detection:")
        print(f"   python fast_camera_detect.py --device {working_camera} --resolution 320x240 --process-interval 2.0")
        print(f"   \n   Standard detection:")
        print(f"   python camera_detect.py --device {working_camera} --resolution 640x480 --process-interval 1.0 --fps 10")
    
    # Show recommendations
    recommend_settings()

if __name__ == "__main__":
    main()