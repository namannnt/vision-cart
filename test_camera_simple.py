import cv2

print("Testing camera index 2...")

cap = cv2.VideoCapture(2)

if not cap.isOpened():
    print("❌ Camera 2 not opening!")
    exit()

print("✅ Camera opened!")
print("Press 'q' to quit")

frame_count = 0

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("❌ Failed to read frame!")
        break
    
    frame_count += 1
    
    # Show frame
    cv2.putText(frame, f"Frame: {frame_count}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow("iVCam Test", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"\nTest completed! Total frames: {frame_count}")
