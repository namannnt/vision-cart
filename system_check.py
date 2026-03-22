"""
VisionCart System Check
Verify all components are working correctly
"""
import sys
import os

print("="*60)
print("VISIONCART SYSTEM CHECK")
print("="*60)

# 1. Python Version
print("\n1. Python Version:")
print(f"   {sys.version}")

# 2. PyTorch & CUDA
print("\n2. PyTorch & GPU:")
try:
    import torch
    print(f"   PyTorch: {torch.__version__}")
    print(f"   CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   CUDA Version: {torch.version.cuda}")
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("   ⚠️  WARNING: CUDA not available (using CPU)")
        print("   For RTX 4060, install: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Required Libraries
print("\n3. Required Libraries:")
required = {
    'cv2': 'opencv-python',
    'numpy': 'numpy',
    'PIL': 'Pillow',
    'ultralytics': 'ultralytics',
    'clip': 'git+https://github.com/openai/CLIP.git',
    'sklearn': 'scikit-learn',
    'streamlit': 'streamlit',
    'sqlite3': 'built-in'
}

for module, package in required.items():
    try:
        __import__(module)
        print(f"   ✅ {module} ({package})")
    except ImportError:
        print(f"   ❌ {module} ({package}) - NOT INSTALLED")

# 4. YOLO Model
print("\n4. YOLO Model:")
if os.path.exists("yolo11x-seg.pt"):
    size = os.path.getsize("yolo11x-seg.pt") / (1024*1024)
    print(f"   ✅ yolo11x-seg.pt ({size:.1f} MB)")
else:
    print("   ❌ yolo11x-seg.pt NOT FOUND")

# 5. Database
print("\n5. Database:")
if os.path.exists("database/visioncart.db"):
    import sqlite3
    conn = sqlite3.connect("database/visioncart.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"   ✅ database/visioncart.db")
    print(f"   Products registered: {count}")
else:
    print("   ❌ database/visioncart.db NOT FOUND")

# 6. Registered Products
print("\n6. Registered Products:")
if os.path.exists("database/visioncart.db"):
    import sqlite3
    conn = sqlite3.connect("database/visioncart.db")
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, price, stock FROM products")
    products = cursor.fetchall()
    conn.close()
    
    if len(products) == 0:
        print("   ⚠️  No products registered")
        print("   Run: python register_product_app.py")
    else:
        for pid, price, stock in products:
            print(f"   ✅ {pid}: ₹{price} (Stock: {stock})")

# 7. Camera
print("\n7. Camera Test:")
try:
    import cv2
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("   ✅ Camera 0 (Default) - Available")
        cap.release()
    else:
        print("   ❌ Camera 0 - Not available")
    
    # Try iVCam (index 2)
    cap = cv2.VideoCapture(2)
    if cap.isOpened():
        print("   ✅ Camera 2 (iVCam) - Available")
        cap.release()
    else:
        print("   ⚠️  Camera 2 (iVCam) - Not available")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 8. Directory Structure
print("\n8. Directory Structure:")
dirs = [
    "data/registered_products",
    "data/embeddings",
    "data/samples",
    "models/clip",
    "models/dinov2",
    "models/yolo",
    "database",
    "ui",
    "utils"
]

for d in dirs:
    if os.path.exists(d):
        print(f"   ✅ {d}/")
    else:
        print(f"   ❌ {d}/ - MISSING")

print("\n" + "="*60)
print("SYSTEM CHECK COMPLETE")
print("="*60)
