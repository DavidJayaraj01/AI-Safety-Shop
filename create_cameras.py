#!/usr/bin/env python3
"""
Create sample cameras for YOLOv8 detection in AI Safety Shop
"""

import sqlite3
import json
from datetime import datetime

def create_cameras():
    # Connect to database
    db_path = '/home/balu/AI-Safety-Shop/backend/safety_monitor.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Camera data
    cameras = [
        {
            'camera_id': 'CAM_001',
            'name': 'Main Entrance - PPE Detection',
            'location': 'Factory Main Entrance',
            'rtsp_url': None,
            'status': 'ONLINE',
            'resolution': '1920x1080',
            'fps': 30.0,
            'detection_enabled': True,
            'detection_types': json.dumps(['ppe_violation', 'unsafe_behavior']),
            'operating_mode': 'HEAVY_INDUSTRY',
            'created_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'extra_data': json.dumps({
                'source': '0',  # Webcam
                'yolo_model': 'ppe-detection.pt',
                'confidence_threshold': 0.5
            })
        },
        {
            'camera_id': 'CAM_002',
            'name': 'Workshop Area - Safety Monitor',
            'location': 'Main Workshop Floor',
            'rtsp_url': None,
            'status': 'ONLINE',
            'resolution': '1920x1080',
            'fps': 30.0,
            'detection_enabled': True,
            'detection_types': json.dumps(['ppe_violation', 'hazard_zone']),
            'operating_mode': 'MANUFACTURING',
            'created_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'extra_data': json.dumps({
                'source': '1',  # Second camera if available
                'yolo_model': 'yolov8n.pt',
                'confidence_threshold': 0.6
            })
        },
        {
            'camera_id': 'CAM_003',
            'name': 'Loading Dock - Security',
            'location': 'Loading/Unloading Area',
            'rtsp_url': None,
            'status': 'ONLINE',
            'resolution': '1280x720',
            'fps': 25.0,
            'detection_enabled': True,
            'detection_types': json.dumps(['unsafe_behavior', 'hazard_zone']),
            'operating_mode': 'LOGISTICS',
            'created_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'extra_data': json.dumps({
                'source': 'demo',  # Demo video for testing
                'yolo_model': 'ppe-detection.pt',
                'confidence_threshold': 0.55
            })
        }
    ]
    
    # Insert cameras
    for camera in cameras:
        try:
            cursor.execute('''
                INSERT INTO cameras (
                    camera_id, name, location, rtsp_url, status, resolution, fps,
                    detection_enabled, detection_types, operating_mode, created_at,
                    last_seen, extra_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                camera['camera_id'], camera['name'], camera['location'],
                camera['rtsp_url'], camera['status'], camera['resolution'],
                camera['fps'], camera['detection_enabled'], camera['detection_types'],
                camera['operating_mode'], camera['created_at'], camera['last_seen'],
                camera['extra_data']
            ))
            print(f"✓ Created camera: {camera['camera_id']} - {camera['name']}")
        except sqlite3.IntegrityError as e:
            print(f"✗ Camera {camera['camera_id']} already exists: {e}")
        except Exception as e:
            print(f"✗ Error creating camera {camera['camera_id']}: {e}")
    
    # Commit changes
    conn.commit()
    
    # Verify cameras were created
    cursor.execute('SELECT camera_id, name, status FROM cameras')
    cameras_in_db = cursor.fetchall()
    
    print(f"\n📹 Total cameras in database: {len(cameras_in_db)}")
    for cam in cameras_in_db:
        print(f"   {cam[0]}: {cam[1]} ({cam[2]})")
    
    conn.close()
    print("\n🎯 Camera setup completed! Live YOLOv8 feeds are now ready.")

if __name__ == '__main__':
    create_cameras()