"""
VisionCart Configuration
Change CAMERA_INDEX to use DroidCam or other camera
"""

# Camera Configuration
CAMERA_INDEX = 1  # iVCam

# Model Configuration
YOLO_MODEL = "yolo11x-seg.pt"
YOLO_CONFIDENCE = 0.25  # Minimum for flat objects

# Detection Configuration
DETECTION_COOLDOWN = 3  # seconds between auto-detections
SIMILARITY_THRESHOLD = 0.85  # product matching threshold
DUPLICATE_THRESHOLD = 0.95  # duplicate detection threshold

# Validation Thresholds (Relaxed for flat objects)
CONFIDENCE_THRESHOLD = 0.5  # Lowered from 0.65
AREA_THRESHOLD = 0.03  # Lowered from 0.05
ASPECT_RATIO_MIN = 0.3  # Lowered from 0.4
ASPECT_RATIO_MAX = 3.0  # Increased from 2.5
BLUR_THRESHOLD = 80  # Lowered from 100
MASK_MIN_PIXELS = 500  # Lowered from 1000

# Accuracy Boost
MULTI_FRAME_HISTORY = 5
EMBEDDING_SMOOTHING = 3
TOP_K_MATCHES = 3

# Database
DB_PATH = "database/visioncart.db"

print(f"✅ Config loaded: Using Camera Index {CAMERA_INDEX}")
