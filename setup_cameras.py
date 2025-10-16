#!/usr/bin/env python3
"""
Setup script to initialize cameras for YOLOv8 live detection
Creates sample cameras and configures them for live monitoring
"""

import asyncio
import sys
import os
import requests
from datetime import datetime

# Add backend to path
sys.path.insert(0, '/home/balu/AI-Safety-Shop/backend')

from app.db.database import AsyncSessionLocal
from app.models.models import Camera, CameraStatus, OperatingMode

async def create_sample_cameras():
    """Create sample cameras for YOLOv8 detection"""
    
    cameras_data = [
        {
            "camera_id": "CAM_001",
            "name": "Main Entrance - PPE Detection",
            "location": "Factory Main Entrance",
            "rtsp_url": None,  # Will use webcam (source=0)
            "status": CameraStatus.ACTIVE,
            "resolution": "640x480",
            "fps": 30,
            "detection_enabled": True,
            "detection_types": ["ppe_violation", "unsafe_behavior"],
            "operating_mode": OperatingMode.HEAVY_INDUSTRY,
            "created_at": datetime.utcnow(),
            "last_seen": datetime.utcnow(),
            "extra_data": {
                "yolo_model": "ppe-detection.pt",
                "confidence_threshold": 0.5,
                "source": "0"  # Webcam
            }
        },
        {
            "camera_id": "CAM_002", 
            "name": "Production Floor - Safety Monitor",
            "location": "Production Floor Zone A",
            "rtsp_url": None,
            "status": CameraStatus.ACTIVE,
            "resolution": "640x480", 
            "fps": 30,
            "detection_enabled": True,
            "detection_types": ["ppe_violation", "hazard_zone", "unsafe_behavior"],
            "operating_mode": OperatingMode.HEAVY_INDUSTRY,
            "created_at": datetime.utcnow(),
            "last_seen": datetime.utcnow(),
            "extra_data": {
                "yolo_model": "yolov8n.pt",
                "confidence_threshold": 0.6,
                "source": "1"  # Second camera if available
            }
        },
        {
            "camera_id": "CAM_003",
            "name": "Loading Dock - Vehicle Safety",
            "location": "Loading Dock Area",
            "rtsp_url": None,
            "status": CameraStatus.ACTIVE,
            "resolution": "640x480",
            "fps": 25,
            "detection_enabled": True,
            "detection_types": ["vehicle_collision", "ppe_violation"],
            "operating_mode": OperatingMode.HEAVY_INDUSTRY,
            "created_at": datetime.utcnow(),
            "last_seen": datetime.utcnow(),
            "extra_data": {
                "yolo_model": "yolov8n.pt",
                "confidence_threshold": 0.5,
                "source": "0"  # Share webcam for demo
            }
        }
    ]
    
    async with AsyncSessionLocal() as db:
        try:
            for camera_data in cameras_data:
                # Check if camera already exists
                from sqlalchemy import select
                result = await db.execute(
                    select(Camera).filter(Camera.camera_id == camera_data["camera_id"])
                )
                existing_camera = result.scalar_one_or_none()
                
                if existing_camera:
                    print(f"Camera {camera_data['camera_id']} already exists, updating...")
                    # Update existing camera
                    for key, value in camera_data.items():
                        if key != "camera_id":  # Don't update the ID
                            setattr(existing_camera, key, value)
                else:
                    print(f"Creating new camera: {camera_data['camera_id']}")
                    # Create new camera
                    camera = Camera(**camera_data)
                    db.add(camera)
            
            await db.commit()
            print("✅ Sample cameras created/updated successfully!")
            
            # List all cameras
            result = await db.execute(select(Camera))
            cameras = result.scalars().all()
            
            print(f"\n📹 Available Cameras ({len(cameras)}):")
            for camera in cameras:
                print(f"  - {camera.camera_id}: {camera.name}")
                print(f"    Location: {camera.location}")
                print(f"    Status: {camera.status}")
                print(f"    Detection: {camera.detection_enabled}")
                print(f"    Source: {camera.extra_data.get('source', 'N/A')}")
                print()
                
        except Exception as e:
            print(f"❌ Error creating cameras: {e}")
            await db.rollback()
            raise

async def test_api_connection():
    """Test if the FastAPI server is running"""
    try:
        response = requests.get("http://localhost:8000/cv/cameras", timeout=5)
        if response.status_code == 200:
            cameras = response.json()
            print(f"✅ API connection successful! Found {len(cameras)} cameras")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure the FastAPI server is running on http://localhost:8000")
        return False

async def main():
    print("🎥 Setting up YOLOv8 Camera Detection System")
    print("=" * 50)
    
    # Test API connection first
    if not await test_api_connection():
        print("\n⚠️  Please start the FastAPI server first:")
        print("cd /home/balu/AI-Safety-Shop/backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    # Create sample cameras
    await create_sample_cameras()
    
    print("\n🚀 Setup completed! You can now:")
    print("1. View cameras at: http://localhost:5175/cv-monitoring") 
    print("2. Stream camera feed: http://localhost:8000/cv/cameras/1/stream")
    print("3. Test detection: http://localhost:8000/cv/cameras/1/test-detection")
    print("\n💡 Make sure your webcam is connected for live detection!")

if __name__ == "__main__":
    asyncio.run(main())