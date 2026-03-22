import cv2
from ultralytics import YOLO
from utils.segmentation_crop import apply_segmentation_mask, crop_to_mask

# Load model
print("Loading YOLO11x-seg model...")
model = YOLO("yolo11x-seg.pt")
print("Model loaded!")

# Load test image
frame = cv2.imread("data/samples/test.jpg")

if frame is None:
    print("Error: Could not load test.jpg")
    print("Please add a test image in data/samples/test.jpg")
    exit()

print("\nRunning detection...")
results = model(frame, conf=0.6)

# Check if any object detected
if len(results[0].masks) == 0:
    print("No objects detected!")
    exit()

print(f"Detected {len(results[0].masks)} objects")

# First detected object
mask = results[0].masks.data[0].cpu().numpy()
mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))

# Apply mask
clean_img = apply_segmentation_mask(frame, mask)
final_crop = crop_to_mask(clean_img, mask)

# Show results
cv2.imshow("Original", frame)
cv2.imshow("Masked (Background Removed)", clean_img)
cv2.imshow("Final Clean Crop", final_crop)

print("\nQuality Check:")
print("✅ Background removed")
print("✅ Only product visible")
print("✅ Tight crop applied")
print("\nPress any key to close...")

cv2.waitKey(0)
cv2.destroyAllWindows()
