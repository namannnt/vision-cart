"""
Simple YOLO Detection Test
Shows live camera with background removed (segmented product only)
"""

import cv2
from ultralytics import YOLO
from utils.segmentation_crop import apply_segmentation_mask, crop_to_mask
from config import CAMERA_INDEX

print("Loading YOLO model...")
model = YOLO("yolo11x-seg.pt")
print("Model loaded!")

print("\n" + "="*50)
print("YOLO SEGMENTATION TEST")
print("="*50)
print(f"Using Camera Index: {CAMERA_INDEX}")
print("Press 'q' to quit")
print("="*50 + "\n")

# Open camera
cap = cv2.VideoCapture(1)  # Camo Cam

if not cap.isOpened():
    print(f"Error: Could not open camera {CAMERA_INDEX}")
    print("Run 'python test_droidcam.py' to find correct camera index")
    exit()

print("Camo Cam started!\n")

frame_count = 0

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    frame_count += 1
    
    # Show frame count for debugging
    if frame_count % 30 == 0:
        print(f"Processing frame {frame_count}...")
    
    # Run YOLO detection
    results = model(frame, conf=0.6, verbose=False)
    
    # Show original with bounding boxes
    annotated = results[0].plot()
    cv2.imshow("Original - YOLO Detection", annotated)
    cv2.waitKey(1)  # Force window update
    
    # If object detected with mask
    if results[0].masks is not None and len(results[0].masks) > 0:
        # Get first mask
        mask = results[0].masks.data[0].cpu().numpy()
        mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
        
        # Apply segmentation (background removal)
        clean_img, binary_mask = apply_segmentation_mask(frame, mask)
        
        # Crop to object
        final_crop = crop_to_mask(clean_img, mask)
        
        # Show results
        if final_crop is not None and final_crop.size > 0:
            cv2.imshow("Background Removed", clean_img)
            cv2.imshow("Cropped Product", final_crop)
            cv2.waitKey(1)  # Force window update
    
    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\nTest completed!")
