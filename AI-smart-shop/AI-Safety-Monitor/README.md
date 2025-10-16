# AI Safety Monitor - PPE Detection Camera

Real-time PPE (Personal Protective Equipment) detection using YOLO and OpenCV, with alert notifications to a remote API.

## Features

- **Real-time PPE monitoring** with live camera feed
- **Visual safety dashboard** integrated into camera window
- **Smart violation detection** (No Helmet, No Vest, No Mask, No Gloves)
- **Live status overlay** with timestamp and personnel count
- **Color-coded bounding boxes** (Red for violations, Green for compliance)
- **Detailed information panel** showing current safety status
- **Automated alert system** via HTTP API to control room
- **Violation counter** and live monitoring status
- **Command-line interface** for easy configuration

## Requirements

- Python 3.8+
- Virtual environment with required packages:
  - ultralytics
  - opencv-python
  - requests

## Usage

### Basic Usage
```bash
# With your trained PPE detection model
python camera_detect.py --weights /path/to/ppe-detection.pt

# Or place ppe-detection.pt in this directory and run:
python camera_detect.py
```

### Command Line Options
```bash
python camera_detect.py [OPTIONS]

Options:
  -w, --weights PATH    Path to model weights (.pt file). Default: ppe-detection.pt
  -d, --device DEVICE   Camera device index or path. Default: 0
  -v, --verbose         Show detailed console output
  --no-display         Run without camera display window (headless mode)
  -h, --help           Show help message
```

### Examples
```bash
# Standard operation with visual monitoring
python camera_detect.py --weights ppe-detection.pt

# Verbose mode with detailed console output
python camera_detect.py --weights ppe-detection.pt --verbose

# Use different camera with minimal console output
python camera_detect.py --weights ppe-detection.pt --device 1

# Test with built-in YOLO model
python camera_detect.py --weights yolov8n.pt

# Headless operation (no camera window, API alerts only)
python camera_detect.py --weights ppe-detection.pt --no-display
```

## Getting PPE Detection Weights

### Option 1: Use Pre-trained Model
If you have a custom PPE detection model (`.pt` file), place it in this directory or specify its path with `--weights`.

### Option 2: Train Your Own
Follow the [Ultralytics documentation](https://docs.ultralytics.com/) to train a custom PPE detection model.

### Option 3: Test Setup (Built-in Model)
To verify your setup works, you can test with a built-in YOLO model:
```bash
python camera_detect.py --weights yolov8n.pt
```
Note: This won't detect PPE violations but will test camera and basic detection.

## Configuration

### API Endpoint
Edit the `API_URL` variable in `camera_detect.py` to point to your alert server:
```python
API_URL = "http://192.168.1.8:8000/alert"  # Replace with your server
```

### Detection Classes
Customize the violation classes in the detection loop:
```python
if label in ["No_Helmet", "No_Vest"]:  # Add or modify classes here
```

## Visual Interface

The camera window displays a comprehensive safety monitoring interface:

### Status Header
- **🔴 SAFETY VIOLATIONS DETECTED**: When PPE violations are found
- **🟢 PERSONNEL DETECTED - PPE COMPLIANT**: When all safety requirements are met
- **🟡 MONITORING ACTIVE**: When area is being monitored but no personnel detected

### Bounding Boxes
- **Red boxes with thick borders**: People detected (potential PPE violations)
- **Green boxes**: Other objects (chairs, equipment, etc.)
- **Text labels**: Show detection type and confidence level

### Information Panel (Right Side)
- **Personnel count**: Number of people in frame
- **Violation count**: Number of active safety violations
- **Specific violations**: List of detected PPE issues
- **Alert status**: Current state of alert system
- **Timestamp**: Real-time monitoring timestamp

### Violation Counter
- **Bottom right corner**: Shows total number of active violations
- **Red background**: Highlighted when violations are present

## Controls

- Press `q` to quit the camera feed
- Press `Ctrl+C` for emergency stop
- Camera window shows live detection results with safety overlay
- Alerts are sent automatically when violations are detected

## Troubleshooting

### "Weights file not found" Error
- Ensure your `.pt` file exists at the specified path
- Use absolute paths to avoid confusion
- Check file permissions

### Camera Issues
- Try different device indices (0, 1, 2, etc.)
- Ensure camera is not being used by another application
- Check camera permissions

### Network/API Issues
- Verify the API endpoint is reachable
- Check network connectivity
- Review server logs for alert processing