"""
VisionCart Stress Testing
Test system under various conditions
"""

import cv2
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ultralytics import YOLO

print("="*60)
print("VISIONCART STRESS TEST")
print("="*60)
print("\nTest Scenarios:")
print("1. Different Lighting Conditions")
print("2. Different Angles")
print("3. Fast Camera Movement")
print("4. Multiple Products")
print("5. Partial Occlusion")
print("="*60 + "\n")

# Load model
print("Loading YOLO model...")
model = YOLO("yolo11x-seg.pt")
print("Model loaded!\n")

# Open camera
cap = cv2.VideoCapture(2)  # iVCam

if not cap.isOpened():
    print("❌ Could not open camera")
    exit()

print("Camera started!")
print("\nInstructions:")
print("  - Test different lighting (bright, dim, shadows)")
print("  - Test different angles (top, side, tilted)")
print("  - Move camera quickly")
print("  - Show multiple products together")
print("  - Partially hide products")
print("\nPress 'q' to quit")
print("="*60 + "\n")

frame_count = 0
detection_count = 0
fps_list = []
start_time = time.time()

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    frame_count += 1
    frame_start = time.time()
    
    # Run detection
    results = model(frame, conf=0.6, verbose=False)
    
    frame_time = (time.time() - frame_start) * 1000  # ms
    fps = 1000 / frame_time if frame_time > 0 else 0
    fps_list.append(fps)
    
    # Count detections
    if results[0].masks is not None and len(results[0].masks) > 0:
        detection_count += 1
    
    # Display
    annotated = results[0].plot()
    
    # Stats overlay
    cv2.putText(annotated, f"FPS: {fps:.1f}", 
                (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(annotated, f"Detection Time: {frame_time:.1f}ms", 
                (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(annotated, f"Detections: {detection_count}/{frame_count}", 
                (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    cv2.imshow("Stress Test - Try Different Conditions", annotated)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Final stats
total_time = time.time() - start_time
avg_fps = np.mean(fps_list) if len(fps_list) > 0 else 0
detection_rate = (detection_count / frame_count * 100) if frame_count > 0 else 0

print("\n" + "="*60)
print("STRESS TEST RESULTS")
print("="*60)
print(f"Total Frames: {frame_count}")
print(f"Total Time: {total_time:.2f}s")
print(f"Average FPS: {avg_fps:.1f}")
print(f"Detection Rate: {detection_rate:.1f}%")
print(f"Detections: {detection_count}")
print("="*60)
print("\n✅ Stress test completed!")
