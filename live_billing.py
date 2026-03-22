import cv2
import torch
import numpy as np
from PIL import Image
from ultralytics import YOLO
from torchvision import transforms

# Import modules
from models.clip import clip_loader
from models.dinov2 import dino_loader
from utils.clip_embedding import get_clip_embedding
from utils.dino_embedding import get_dino_embedding
from utils.embedding_fusion import fuse_embeddings
from utils.segmentation_crop import apply_segmentation_mask, crop_to_mask
from utils.validation import validate_detection
from utils.load_database import load_database
from utils.accuracy_boost import AccuracyBooster, top_k_matching
from utils.billing import BillingSystem

# Initialize
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load models
print("Loading YOLO model...")
yolo_model = YOLO("yolo11x-seg.pt")

print("Loading database...")
product_ids, db_embeddings, prices, stocks = load_database()

if len(product_ids) == 0:
    print("\n❌ No products in database!")
    print("Please register products first using: python register_product_app.py")
    exit()

print(f"✅ Loaded {len(product_ids)} products from database")
for i, pid in enumerate(product_ids):
    print(f"  - {pid}: ₹{prices[i]} (Stock: {stocks[i]})")

# Initialize systems
booster = AccuracyBooster(history_size=5, emb_history_size=3)
billing = BillingSystem()

# DINO transform
dino_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

print("\n" + "="*50)
print("VISIONCART - LIVE BILLING SYSTEM")
print("="*50)
print("✅ Auto-billing enabled")
print("✅ Stock tracking enabled")
print("✅ Low stock alerts enabled")
print("="*50)
print("Controls:")
print("  'a' - Add detected product to bill")
print("  'b' - Show bill summary")
print("  'c' - Clear bill")
print("  'q' - Quit")
print("="*50 + "\n")

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

frame_count = 0
last_added_product = None
add_cooldown = 0  # Prevent rapid duplicate adds

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    frame_count += 1
    add_cooldown = max(0, add_cooldown - 1)
    display_frame = frame.copy()
    
    current_product = None
    current_price = 0
    
    try:
        # Run detection
        results = yolo_model(frame, conf=0.6, verbose=False)
        
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
                            
                            current_product = final_label
                            current_price = price
                            
                            # Confidence color
                            if score > 0.90:
                                color = (0, 255, 0)
                                conf_text = "HIGH"
                            elif score > 0.85:
                                color = (0, 255, 255)
                                conf_text = "MEDIUM"
                            else:
                                color = (0, 165, 255)
                                conf_text = "LOW"
                            
                            # Display info
                            cv2.putText(display_frame, f"Product: {final_label}", 
                                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                            cv2.putText(display_frame, f"Price: Rs.{price:.2f}", 
                                        (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                            cv2.putText(display_frame, f"Stock: {stock}", 
                                        (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                            cv2.putText(display_frame, f"Confidence: {score:.2f} ({conf_text})", 
                                        (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                            
                            # Check if already in bill
                            if final_label in billing.added_products:
                                cv2.putText(display_frame, "✓ IN CART", 
                                            (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                            else:
                                cv2.putText(display_frame, "Press 'A' to add to cart", 
                                            (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        else:
                            booster.multi_frame_voting("UNKNOWN")
                            cv2.putText(display_frame, "UNKNOWN PRODUCT", 
                                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    else:
                        cv2.putText(display_frame, f"Invalid: {reason}", 
                                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        booster.reset()
        else:
            booster.reset()
        
        # Bill info
        cv2.putText(display_frame, f"Cart Items: {len(billing.bill)} | Total: Rs.{billing.get_total():.2f}", 
                    (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("VisionCart - Live Billing", display_frame)
    
    except Exception as e:
        print(f"Error: {e}")
        booster.reset()
    
    # Handle keys
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q') or key == 27:
        break
    
    elif key == ord('a') and current_product and add_cooldown == 0:
        # Add to bill
        if billing.add_to_bill(current_product, current_price):
            print(f"\n✅ Added to cart: {current_product} (Rs.{current_price:.2f})")
            
            # Update stock
            billing.update_stock(current_product)
            
            # Check low stock
            is_low, new_stock = billing.check_low_stock(current_product)
            if is_low:
                print(f"⚠️  LOW STOCK ALERT: {current_product} (Only {new_stock} left!)")
            
            # Reload database to get updated stock
            product_ids, db_embeddings, prices, stocks = load_database()
            
            add_cooldown = 30  # 30 frames cooldown
        else:
            print(f"ℹ️  {current_product} already in cart")
    
    elif key == ord('b'):
        # Show bill
        print(billing.get_bill_summary())
    
    elif key == ord('c'):
        # Clear bill
        billing.clear_bill()
        print("\n🗑️  Cart cleared!")

cap.release()
cv2.destroyAllWindows()

# Final bill
print(billing.get_bill_summary())
