"""
Quick test script to verify size detection is working correctly
"""
import cv2
from customer_checkout_backend import CheckoutCounter

print("="*80)
print("🧪 SIZE DETECTION TEST")
print("="*80)

counter = CheckoutCounter()

print(f"\n✅ Loaded {len(counter.product_ids)} products")
print(f"✅ Parent groups: {list(counter.parent_groups.keys())}")

# Show vaseline products
print("\n📦 Vaseline Products:")
for idx, pid in enumerate(counter.product_ids):
    if 'vaseline' in pid.lower():
        parent = counter.parent_ids[idx] if idx < len(counter.parent_ids) else "None"
        size = counter.real_diameters[idx] if idx < len(counter.real_diameters) else 0.0
        print(f"  - {pid:25s} | Parent: {parent:15s} | Size: {size:6.1f}mm")

print("\n" + "="*80)
print("🎯 TESTING DETECTION")
print("="*80)

from config import CAMERA_INDEX
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

if not cap.isOpened():
    print(f"❌ Could not open camera {CAMERA_INDEX}")
    exit(1)

print(f"\n✅ Camera opened: {CAMERA_INDEX}")
print("\nInstructions:")
print("  1. Place ONE vaseline product in frame")
print("  2. (Optional) Place ₹1 coin in corner for best accuracy")
print("  3. Watch the detection messages")
print("  4. Press 'q' to quit, 'c' to clear cart")
print("\n" + "="*80 + "\n")

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    display = frame.copy()
    
    # Run detection every 5 frames
    if frame_count % 5 == 0:
        detected, product, confidence, message = counter.detect_and_add_to_cart(frame)
        
        # Display result
        if detected:
            print(f"✅ ADDED: {product} (confidence: {confidence:.2%})")
            cv2.putText(display, f"ADDED: {product}", (20, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        else:
            # Show status message
            status_color = (0, 165, 255) if "Confirming" in message else (100, 100, 100)
            cv2.putText(display, message[:50], (20, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
    
    # Show cart
    cart_text = f"Cart: {len(counter.cart)} items | Total: Rs.{counter.get_cart_total():.2f}"
    cv2.putText(display, cart_text, (20, display.shape[0] - 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Show cart items
    y_offset = 100
    for item in counter.cart:
        item_text = f"{item['name']} - Rs.{item['price']:.2f}"
        cv2.putText(display, item_text, (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        y_offset += 30
    
    cv2.imshow("Size Detection Test", display)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        counter.clear_cart()
        print("\n🗑️  Cart cleared\n")

cap.release()
cv2.destroyAllWindows()

print("\n" + "="*80)
print("✅ Test completed!")
print("="*80)
