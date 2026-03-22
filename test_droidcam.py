"""
Test DroidCam connection
"""
import cv2

print("Testing camera indices...")
print("="*50)

for i in range(5):
    print(f"\nTrying camera index {i}...")
    cap = cv2.VideoCapture(i)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"✅ Camera {i} working!")
            print(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
            
            cv2.imshow(f"Camera {i} - Press any key", frame)
            cv2.waitKey(2000)
            cv2.destroyAllWindows()
        cap.release()
    else:
        print(f"❌ Camera {i} not available")

print("\n" + "="*50)
print("Test completed!")
print("Use the working camera index in your apps")
print("="*50)
