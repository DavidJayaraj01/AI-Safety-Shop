#!/usr/bin/env python3
"""
Quick PPE Model Downloader
Downloads a pre-trained PPE detection model for the AI Safety Monitor system
"""

import os
import sys
import urllib.request
from pathlib import Path

def download_ppe_model():
    """Download a sample PPE detection model"""
    
    print("=" * 60)
    print("AI Safety Monitor - PPE Model Downloader")
    print("=" * 60)
    print()
    
    # Model options
    models = {
        "1": {
            "name": "Sample PPE Model (Simulated)",
            "url": None,
            "description": "Keep using simulated detection (current setup)",
        },
        "2": {
            "name": "Download from Roboflow",
            "url": "roboflow",
            "description": "Requires Roboflow API key (free)",
        },
    }
    
    print("Available options:")
    for key, model in models.items():
        print(f"{key}. {model['name']}")
        print(f"   {model['description']}")
        print()
    
    choice = input("Enter your choice (1-2): ").strip()
    
    if choice == "1":
        print("\n✓ Continuing with simulated PPE detection")
        print("  The system will detect persons and simulate helmet/vest detection")
        print("  For production use, choose option 2 or follow SETUP_PPE_MODEL.md")
        return
    
    elif choice == "2":
        print("\n📥 Setting up Roboflow model download...")
        print("\nSteps:")
        print("1. Sign up at https://roboflow.com (free)")
        print("2. Get your API key from Account Settings")
        print("3. Install Roboflow: pip install roboflow")
        print("\nThen run:")
        print("""
from roboflow import Roboflow
rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace("roboflow-universe").project("ppe-zfiec")
version = project.version(1)
dataset = version.download("yolov8")
# Copy the model: cp PPE-1/weights/best.pt backend/ppe_yolov8n.pt
""")
        return
    
    else:
        print("Invalid choice!")
        return

if __name__ == "__main__":
    try:
        download_ppe_model()
    except KeyboardInterrupt:
        print("\n\nDownload cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
