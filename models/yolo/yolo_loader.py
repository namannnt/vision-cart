from ultralytics import YOLO

# Load segmentation model (highest accuracy)
model = YOLO("yolo11x-seg.pt")

print("YOLO11x-seg loaded successfully")
