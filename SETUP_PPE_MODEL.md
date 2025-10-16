# Setting Up Proper PPE Detection Model

## Current Status
The system currently uses a **simulated PPE detection** because the standard YOLOv8n model is trained on COCO dataset (80 common objects like person, car, chair) and does NOT include PPE items.

## ⚠️ Important Note
The green boxes you see showing "helmet" and "vest" are **simulated** based on person detection. For production use, you need a real PPE-trained model.

---

## 🎯 Solution Options

### Option 1: Download Pre-trained PPE Model (Recommended - Easiest)

#### From Roboflow Universe (Free)
```bash
# 1. Install roboflow
pip install roboflow

# 2. Download PPE dataset and model
python3 << 'EOF'
from roboflow import Roboflow
rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace("roboflow-universe").project("ppe-jjbue")
dataset = project.version(6).download("yolov8")
EOF

# 3. The model will be downloaded to ./PPE-6/
# Copy the weights to backend folder
cp PPE-6/weights/best.pt backend/ppe_yolov8n.pt
```

Popular PPE Datasets on Roboflow:
- `ppe-jjbue` - Helmet, Vest, Person detection
- `construction-site-safety` - Hard hat, Safety vest, Person, NO-Hardhat, NO-Safety Vest
- `safety-equipment-detection` - Multiple PPE items

#### From Ultralytics Hub (Free)
1. Go to https://hub.ultralytics.com/
2. Search for "PPE" or "Safety Equipment" models
3. Download the `.pt` file
4. Place it in `/backend/` folder as `ppe_yolov8n.pt`

### Option 2: Train Your Own Model

#### Step 1: Collect PPE Dataset
```bash
# Use Roboflow to annotate images or download existing dataset
# Recommended datasets:
# - Hard Hat Detection: https://universe.roboflow.com/roboflow-universe/hard-hat-sample
# - Construction Safety: https://universe.roboflow.com/mohamed-traore-2ekkp/construction-site-safety
```

#### Step 2: Train YOLOv8 on PPE
```python
from ultralytics import YOLO

# Load a pretrained model
model = YOLO('yolov8n.pt')

# Train on your PPE dataset
results = model.train(
    data='path/to/ppe_dataset/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='ppe_detection'
)

# Export trained model
model.export(format='pytorch')
```

#### Step 3: Dataset Structure
```
ppe_dataset/
├── data.yaml          # Dataset configuration
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

**data.yaml example:**
```yaml
path: ../ppe_dataset
train: train/images
val: valid/images
test: test/images

nc: 5  # number of classes
names: ['helmet', 'vest', 'gloves', 'goggles', 'safety_shoes']
```

### Option 3: Use Pre-trained Model from GitHub

```bash
cd backend

# Option 3a: Download from popular PPE detection repo
wget https://github.com/safietyai/PPE-Detection-YOLO-Deep_SORT/raw/main/yolov5_ppe.pt -O ppe_yolov8n.pt

# Option 3b: Use construction safety model
wget https://github.com/AnshulSood11/PPE-Detection-YOLO-Deep_SORT/releases/download/v1.0/best.pt -O ppe_yolov8n.pt
```

---

## 🔧 Configuration

### Update backend/.env
```env
# PPE Detection Settings
YOLO_MODEL_PATH=ppe_yolov8n.pt
PPE_CONFIDENCE_THRESHOLD=0.6
PPE_CLASSES=helmet,vest,gloves,goggles,safety_shoes

# Camera Settings  
CAMERA_INDEX=0
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720
CAMERA_FPS=30
```

### Verify Model Classes
After downloading a model, check its classes:
```python
from ultralytics import YOLO
model = YOLO('ppe_yolov8n.pt')
print(model.names)  # Should show: {0: 'helmet', 1: 'vest', ...}
```

---

## 🎬 Quick Start with Sample Model

### Download a working PPE model:
```bash
cd /home/klassy/Desktop/AI-Safety-Monitor/backend

# Download from Roboflow (requires API key - it's free)
# 1. Sign up at https://roboflow.com
# 2. Get API key from Account settings
# 3. Run:

pip install roboflow
python3 << 'EOF'
from roboflow import Roboflow
rf = Roboflow(api_key="YOUR_ROBOFLOW_API_KEY")
project = rf.workspace("roboflow-universe").project("ppe-zfiec")
version = project.version(1)
dataset = version.download("yolov8")
EOF

# The model will be at: PPE-1/weights/best.pt
cp PPE-1/weights/best.pt ppe_yolov8n.pt
```

### Restart Backend
```bash
# Stop current backend (Ctrl+C)
# Restart with new model
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

---

## 📊 Expected Model Classes

Your PPE model should detect these classes:
1. **helmet / hardhat** - Safety helmet/hard hat
2. **vest / safety-vest** - High-visibility safety vest
3. **gloves** - Safety gloves
4. **goggles / safety-glasses** - Eye protection
5. **safety_shoes / boots** - Safety footwear
6. **person** - Person without PPE (optional)
7. **NO-Hardhat** - Person without helmet (optional)
8. **NO-Safety Vest** - Person without vest (optional)

---

## 🧪 Testing Your Model

```python
from ultralytics import YOLO
import cv2

# Load model
model = YOLO('ppe_yolov8n.pt')

# Test on image
img = cv2.imread('test_image.jpg')
results = model(img)

# Print detections
for r in results:
    print(r.boxes.cls)  # Class IDs
    print(r.names)      # Class names
```

---

## 🔗 Useful Resources

- **Roboflow Universe PPE Datasets**: https://universe.roboflow.com/search?q=ppe
- **Ultralytics Hub**: https://hub.ultralytics.com/
- **YOLOv8 Training Docs**: https://docs.ultralytics.com/modes/train/
- **Sample PPE Detection Project**: https://github.com/safietyai/PPE-Detection-YOLO-Deep_SORT

---

## ⚡ Quick Test Command

```bash
# Test if your model works
cd backend
python3 -c "
from ultralytics import YOLO
model = YOLO('ppe_yolov8n.pt')
print('Model classes:', model.names)
"
```

---

## 🐛 Troubleshooting

**Problem**: Model not detecting PPE items
- **Solution**: Verify model file exists and classes match expected PPE items

**Problem**: Low accuracy
- **Solution**: Lower confidence threshold in settings (try 0.4 instead of 0.6)

**Problem**: "Model not found" error
- **Solution**: Ensure `ppe_yolov8n.pt` is in `/backend/` directory

---

## 💡 For Demo Purposes

The current **simulated detection** will:
- ✅ Detect persons using standard YOLOv8
- ✅ Simulate helmet/vest boxes (green/yellow rectangles)
- ✅ Show PPE compliance status
- ⚠️ NOT accurate - for demo only

**Replace with real model for production use!**
