from ultralytics import YOLO

# Load model
print("Loading YOLO11x-seg model...")
model = YOLO("yolo11x-seg.pt")
print("Model loaded successfully!")

print("\nStarting webcam detection...")
print("Press 'q' to quit")

# Webcam test
model.predict(
    source=0,        # webcam
    conf=0.6,
    show=True
)
