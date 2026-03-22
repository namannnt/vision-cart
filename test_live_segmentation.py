import cv2
from ultralytics import YOLO
from utils.segmentation_crop import apply_segmentation_mask, crop_to_mask
from utils.validation import validate_detection

# Load model
print("Loading YOLO11x-seg model...")
model = YOLO("yolo11x-seg.pt")
print("Model loaded!")

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

print("\nLive segmentation with validation started!")
print("Press 'q' to quit")
print("Press 's' to save valid crop")

frame_count = 0
valid_count = 0
rejected_count = 0

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Failed to capture frame")
        break
    
    frame_count += 1
    
    try:
        # Run detection
        results = model(frame, conf=0.6, verbose=False)
        
        # Show original with detections
        annotated_frame = results[0].plot()
        
        # Add stats
        cv2.putText(annotated_frame, f"Valid: {valid_count} | Rejected: {rejected_count}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Live Detection", annotated_frame)
        
        # If objects detected and masks available
        if results[0].masks is not None and len(results[0].masks) > 0:
            # Process first detected object
            mask = results[0].masks.data[0].cpu().numpy()
            mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
            
            # Apply mask and crop
            clean_img, binary_mask = apply_segmentation_mask(frame, mask)
            
            # Check if crop is valid
            if clean_img is not None and clean_img.size > 0:
                final_crop = crop_to_mask(clean_img, mask)
                
                if final_crop is not None and final_crop.size > 0 and final_crop.shape[0] > 0 and final_crop.shape[1] > 0:
                    # VALIDATION PIPELINE
                    is_valid, reason = validate_detection(results, frame, final_crop, binary_mask)
                    
                    if is_valid:
                        valid_count += 1
                        # Show valid crop with green border
                        cv2.rectangle(final_crop, (0, 0), (final_crop.shape[1]-1, final_crop.shape[0]-1), (0, 255, 0), 3)
                        cv2.putText(final_crop, "VALID", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        cv2.imshow("Clean Crop", final_crop)
                    else:
                        rejected_count += 1
                        # Show rejected reason
                        rejected_img = final_crop.copy()
                        cv2.rectangle(rejected_img, (0, 0), (rejected_img.shape[1]-1, rejected_img.shape[0]-1), (0, 0, 255), 3)
                        cv2.putText(rejected_img, f"REJECTED: {reason}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        cv2.imshow("Clean Crop", rejected_img)
    
    except Exception as e:
        print(f"Error processing frame: {e}")
        pass
    
    # Quit on 'q'
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        if 'final_crop' in locals() and is_valid:
            cv2.imwrite(f"data/samples/saved_crop_{frame_count}.jpg", final_crop)
            print(f"Saved valid crop: saved_crop_{frame_count}.jpg")

cap.release()
cv2.destroyAllWindows()
print(f"\nStats:")
print(f"Total frames: {frame_count}")
print(f"Valid crops: {valid_count}")
print(f"Rejected: {rejected_count}")
print("Live segmentation stopped!")
