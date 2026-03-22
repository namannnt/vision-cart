from ultralytics import YOLO

# Load model
print("Loading YOLO11x-seg model...")
model = YOLO("yolo11x-seg.pt")
print("Model loaded successfully!")

# Test on image
print("\nTesting on sample image...")
results = model("data/samples/test.jpg", conf=0.6)
results[0].show()

print("\nYOLO Output Structure:")
print("- boxes: bounding box coordinates")
print("- masks: pixel-level segmentation masks")
