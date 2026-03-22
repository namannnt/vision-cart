import cv2

print("Scanning camera indices 0-5...")
for i in range(6):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"  ✅ Camera index {i} WORKS - resolution: {int(cap.get(3))}x{int(cap.get(4))}")
        else:
            print(f"  ⚠️  Camera index {i} opens but no frame")
        cap.release()
    else:
        print(f"  ❌ Camera index {i} - not found")

print("\nDone. Use the working index in web_api.py (cv2.VideoCapture(INDEX))")
