"""
VisionCart - Automatic Billing Counter
Continuous scanning: Place products, they get detected and added to cart automatically
"""

import cv2
import torch
import numpy as np
from PIL import Image
from ultralytics import YOLO
from torchvision import transforms
import time
from datetime import datetime
import sqlite3

# Import AI modules
from models.clip import clip_loader
from models.dinov2 import dino_loader
from utils.clip_embedding import get_clip_embedding
from utils.dino_embedding import get_dino_embedding
from utils.embedding_fusion import fuse_embeddings
from utils.segmentation_crop import apply_segmentation_mask, crop_to_mask
from utils.validation import validate_detection
from utils.load_database import load_database
from utils.accuracy_boost import AccuracyBooster, top_k_matching

# Initialize
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load models
print("Loading AI models...")
yolo_model = YOLO("yolo11x-seg.pt")

# Load database
print("Loading product database...")
product_ids, db_embeddings, prices, stocks = load_database()

if len(product_ids) == 0:
    print("\n❌ No products in database!")
    print("Please register products first using: python ui/admin_panel.py")
    exit()

print(f"✅ Loaded {len(product_ids)} products")

# Initialize systems
booster = AccuracyBooster(history_size=5, emb_history_size=3)

# DINO transform
dino_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Cart management
cart = []
cart_product_ids = set()

def add_to_cart(product_id, price):
    """Add item to cart if not already present"""
    if product_id not in cart_product_ids:
        cart.append({
            'product_id': product_id,
            'price': price,
            'time': datetime.now().strftime("%H:%M:%S")
        })
        cart_product_ids.add(product_id)
        return True
    return False

def get_cart_total():
    """Calculate total amount"""
    return sum(item['price'] for item in cart)

def print_bill():
    """Print final bill"""
    print("\n" + "="*50)
    print("BILL RECEIPT")
    print("="*50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    for i, item in enumerate(cart, 1):
        print(f"{i}. {item['product_id']:<20} ₹{item['price']:>8.2f} ({item['time']})")
    
    print("="*50)
    print(f"{'TOTAL':<20} ₹{get_cart_total():>8.2f}")
    print("="*50)
    print("Thank you for shopping with VisionCart!")
    print("="*50 + "\n")

def update_stock(product_id):
    """Update stock in database"""
    conn = sqlite3.connect("database/visioncart.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock = stock - 1 WHERE product_id=?", (product_id,))
    conn.commit()
    conn.close()

print("\n" + "="*60)
print("VISIONCART - AUTOMATIC BILLING COUNTER")
print("="*60)
print("🎥 Camera will start in continuous scanning mode")
print("📦 Place products one by one in front of camera")
print("✅ Products will be automatically detected and added to cart")
print("="*60)
print("\nControls:")
print("  'c' - Checkout & Print Bill")
print("  'r' - Remove last item from cart")
print("  'x' - Clear entire cart")
print("  'q' - Quit")
print("="*60 + "\n")

input("Press ENTER to start scanning...")

# Open camera
cap = cv2.VideoCapture(2)  # iVCam

if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

frame_count = 0
last_detection_time = 0
detection_cooldown = 3  # seconds between detections

print("\n🎥 Camo Cam started! Place products in front of camera...\n")

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    frame_count += 1
    display_frame = frame.copy()
    current_time = time.time()
    
    # Display cart info
    cv2.putText(display_frame, f"Cart Items: {len(cart)} | Total: Rs.{get_cart_total():.2f}", 
                (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    cv2.putText(display_frame, "C=Checkout | R=Remove | X=Clear | Q=Quit", 
                (20, display_frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    try:
        # Only scan if cooldown period passed
        if current_time - last_detection_time > detection_cooldown:
            
            # Run detection with minimum confidence
            results = yolo_model(frame, conf=0.25, verbose=False)
            
            # Process detection
            if results[0].masks is not None and len(results[0].masks) > 0:
                mask = results[0].masks.data[0].cpu().numpy()
                mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
                
                clean_img, binary_mask = apply_segmentation_mask(frame, mask)
                
                if clean_img is not None and clean_img.size > 0:
                    final_crop = crop_to_mask(clean_img, mask)
                    
                    if final_crop is not None and final_crop.size > 0 and final_crop.shape[0] > 0 and final_crop.shape[1] > 0:
                        # Validate
                        is_valid, reason = validate_detection(results, frame, final_crop, binary_mask)
                        
                        if is_valid:
                            # Brightness Normalization
                            final_crop = booster.brightness_normalize(final_crop)
                            
                            # Generate embedding
                            pil_crop = Image.fromarray(cv2.cvtColor(final_crop, cv2.COLOR_BGR2RGB))
                            clip_emb = get_clip_embedding(pil_crop, clip_loader.model, clip_loader.preprocess, device)
                            dino_tensor = dino_transform(pil_crop).unsqueeze(0)
                            dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, device)
                            query_emb = fuse_embeddings(clip_emb, dino_emb)
                            
                            # Embedding Smoothing
                            query_emb = booster.embedding_smoothing(query_emb)
                            
                            # Top-K Matching
                            idx, score, is_known, top_k_labels = top_k_matching(
                                query_emb, db_embeddings, product_ids, k=3, threshold=0.85
                            )
                            
                            if is_known:
                                raw_label = product_ids[idx]
                                
                                # Multi-Frame Voting
                                final_label = booster.multi_frame_voting(raw_label)
                                
                                # Get product info
                                final_idx = product_ids.index(final_label)
                                price = prices[final_idx]
                                stock = stocks[final_idx]
                                
                                # Display detection
                                color = (0, 255, 0) if score > 0.90 else (0, 255, 255)
                                cv2.putText(display_frame, f"Detected: {final_label}", 
                                            (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                                cv2.putText(display_frame, f"Price: Rs.{price:.2f} | Conf: {score:.2f}", 
                                            (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                                
                                # Auto-add to cart
                                if stock > 0:
                                    if add_to_cart(final_label, price):
                                        print(f"✅ Added to cart: {final_label} - ₹{price:.2f} (Confidence: {score:.2f})")
                                        last_detection_time = current_time
                                        
                                        # Reload database for updated stock
                                        product_ids, db_embeddings, prices, stocks = load_database()
                                    else:
                                        cv2.putText(display_frame, "Already in cart!", 
                                                    (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                                else:
                                    cv2.putText(display_frame, "OUT OF STOCK!", 
                                                (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                    print(f"⚠️ {final_label} is OUT OF STOCK!")
                            else:
                                cv2.putText(display_frame, "Unknown Product", 
                                            (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        else:
                            booster.reset()
            else:
                booster.reset()
    
    except Exception as e:
        print(f"Error: {e}")
        booster.reset()
    
    cv2.imshow("VisionCart - Auto Billing Counter", display_frame)
    
    # Handle keys
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    
    elif key == ord('c'):  # Checkout
        if len(cart) > 0:
            cap.release()
            cv2.destroyAllWindows()
            
            print("\n💳 Processing checkout...")
            
            # Update stock for all items
            for item in cart:
                update_stock(item['product_id'])
            
            # Print bill
            print_bill()
            
            print("✅ Payment successful! Stock updated.")
            print("\nPress ENTER to start new transaction or Ctrl+C to exit...")
            
            try:
                input()
                # Reset for new transaction
                cart.clear()
                cart_product_ids.clear()
                booster.reset()
                
                # Reopen camera
                cap = cv2.VideoCapture(0)
                print("\n🎥 Camera restarted! Ready for next customer...\n")
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                exit()
        else:
            print("⚠️ Cart is empty!")
    
    elif key == ord('r'):  # Remove last item
        if len(cart) > 0:
            removed = cart.pop()
            cart_product_ids.remove(removed['product_id'])
            print(f"🗑️ Removed: {removed['product_id']}")
    
    elif key == ord('x'):  # Clear cart
        cart.clear()
        cart_product_ids.clear()
        booster.reset()
        print("🗑️ Cart cleared!")

cap.release()
cv2.destroyAllWindows()

print("\n\nThank you for using VisionCart!")
