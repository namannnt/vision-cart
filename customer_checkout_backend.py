"""
Customer Checkout Backend - Auto Detection & Billing
Runs in background, detects products and updates cart
"""
import cv2
import torch
import numpy as np
from PIL import Image
from ultralytics import YOLO
from torchvision import transforms
import time
import json
from datetime import datetime

from models.clip import clip_loader
from models.dinov2 import dino_loader
from utils.clip_embedding import get_clip_embedding
from utils.dino_embedding import get_dino_embedding
from utils.embedding_fusion import fuse_embeddings
from utils.segmentation_crop import apply_segmentation_mask, crop_to_mask
from utils.validation import validate_detection
from utils.load_database import load_database
from utils.color_layer import extract_color_histogram, color_similarity
from utils.shape_layer import extract_shape_features, shape_similarity
from utils.accuracy_boost import AccuracyBooster, top_k_matching

class CheckoutCounter:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔧 Device: {self.device.upper()}")
        
        # Load models
        print("📦 Loading AI models...")
        self.yolo_model = YOLO("yolo11x-seg.pt")
        
        # Load database
        self.product_ids, self.db_embeddings, self.prices, self.stocks, \
            self.color_hists, self.shape_feats = load_database()
        print(f"✅ Loaded {len(self.product_ids)} products")
        
        # Initialize booster
        self.booster = AccuracyBooster(history_size=5, emb_history_size=3)
        
        # DINO transform
        self.dino_transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Cart and detection tracking
        self.cart = []
        self.last_detected_product = None
        self.last_detection_time = 0
        self.cooldown_seconds = 5  # Prevent duplicate scans (increased to 5 seconds)
        self.detection_count = {}  # Track detection count per product
    
    def detect_and_add_to_cart(self, frame):
        """
        Detect product in frame and add to cart if valid
        Returns: (detected, product_name, confidence, message)
        """
        try:
            # Run YOLO detection
            results = self.yolo_model(frame, conf=0.25, verbose=False)
            
            if results[0].masks is None or len(results[0].masks) == 0:
                return False, None, 0, "No object detected"
            
            # Segmentation
            mask = results[0].masks.data[0].cpu().numpy()
            mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
            
            clean_img, binary_mask = apply_segmentation_mask(frame, mask)
            final_crop = crop_to_mask(clean_img, mask)
            
            if final_crop is None or final_crop.size == 0:
                return False, None, 0, "Invalid crop"
            
            # Validation
            is_valid, reason = validate_detection(results, frame, final_crop, binary_mask)
            
            if not is_valid:
                return False, None, 0, f"Invalid: {reason}"
            
            # Generate embedding
            final_crop = self.booster.brightness_normalize(final_crop)
            pil_crop = Image.fromarray(cv2.cvtColor(final_crop, cv2.COLOR_BGR2RGB))

            clip_emb = get_clip_embedding(pil_crop, clip_loader.model, clip_loader.preprocess, self.device)
            dino_tensor = self.dino_transform(pil_crop).unsqueeze(0)
            dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, self.device)
            query_emb = fuse_embeddings(clip_emb, dino_emb)

            # Smoothing
            query_emb = self.booster.embedding_smoothing(query_emb)

            # Match — visual embedding (primary)
            idx, score, is_known, top_k_labels = top_k_matching(
                query_emb, self.db_embeddings, self.product_ids, k=3, threshold=0.60
            )

            if not is_known:
                return False, None, score, f"Unknown product (score: {score:.2f})"

            # --- Color layer boost ---
            query_color = extract_color_histogram(final_crop)
            if self.color_hists[idx] is not None:
                c_sim = color_similarity(query_color, self.color_hists[idx])
                color_boost = c_sim * 0.05  # small bonus
            else:
                color_boost = 0.0

            # --- Shape layer boost ---
            query_shape = extract_shape_features(final_crop, binary_mask)
            if self.shape_feats[idx] is not None:
                s_sim = shape_similarity(query_shape, self.shape_feats[idx])
                shape_boost = s_sim * 0.03  # small bonus
            else:
                shape_boost = 0.0

            # Fused score — visual is primary, color+shape are additive bonuses
            fused_score = min(score + color_boost + shape_boost, 1.0)

            # Final threshold check
            if fused_score < 0.60:
                return False, None, fused_score, f"Low fused score ({fused_score:.2f})"

            score = fused_score
            
            # Get product info
            product_name = self.product_ids[idx]
            price = self.prices[idx]
            stock = self.stocks[idx]
            
            # Check stock
            if stock <= 0:
                return False, product_name, score, "OUT OF STOCK"
            
            # Cooldown check (prevent duplicate scans)
            current_time = time.time()
            if (product_name == self.last_detected_product and 
                current_time - self.last_detection_time < self.cooldown_seconds):
                return False, product_name, score, "⏳ Cooldown active - Remove item to scan again"
            
            # Check if already in cart (prevent duplicates)
            for item in self.cart:
                if item['name'] == product_name:
                    return False, product_name, score, "⚠️ Already in cart - Remove item first"
            
            # Add to cart
            self.cart.append({
                'name': product_name,
                'price': price,
                'confidence': score,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
            # Update tracking
            self.last_detected_product = product_name
            self.last_detection_time = current_time
            
            # Low stock warning
            warning = ""
            if stock <= 3:
                warning = f" (Only {stock} left!)"
            
            return True, product_name, score, f"Added to cart{warning}"
        
        except Exception as e:
            return False, None, 0, f"Error: {str(e)}"
    
    def get_cart_total(self):
        """Calculate cart total"""
        return sum(item['price'] for item in self.cart)
    
    def clear_cart(self):
        """Clear cart"""
        self.cart = []
        self.last_detected_product = None
    
    def remove_last_item(self):
        """Remove last item from cart"""
        if len(self.cart) > 0:
            return self.cart.pop()
        return None
    
    def checkout(self):
        """Complete checkout and update inventory"""
        import sqlite3
        
        if len(self.cart) == 0:
            return False, "Cart is empty"
        
        try:
            conn = sqlite3.connect("database/visioncart.db")
            cursor = conn.cursor()
            
            for item in self.cart:
                cursor.execute("""
                    UPDATE products 
                    SET stock = stock - 1 
                    WHERE product_id = ?
                """, (item['name'],))
            
            conn.commit()
            conn.close()
            
            # Generate bill
            total = self.get_cart_total()
            bill = {
                'items': self.cart.copy(),
                'total': total,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Clear cart
            self.clear_cart()
            
            # Reload stocks from DB so in-memory is fresh
            self.product_ids, self.db_embeddings, self.prices, self.stocks, \
                self.color_hists, self.shape_feats = load_database()
            
            return True, bill
        
        except Exception as e:
            return False, f"Error: {str(e)}"

def main():
    print("="*60)
    print("🛒 VISIONCART CUSTOMER CHECKOUT COUNTER")
    print("="*60)
    
    counter = CheckoutCounter()
    
    cap = cv2.VideoCapture(2)  # iVCam
    
    if not cap.isOpened():
        print("❌ Could not open camera")
        return
    
    print("\n✅ System ready!")
    print("📸 Place items in scanning area")
    print("Press 'c' to checkout | 'r' to remove last | 'q' to quit")
    print("="*60 + "\n")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        display = frame.copy()
        
        # Auto-detect
        detected, product, confidence, message = counter.detect_and_add_to_cart(frame)
        
        if detected:
            print(f"✅ {product} added! (Confidence: {confidence:.2%})")
            cv2.putText(display, f"ADDED: {product}", 
                        (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        
        # Display cart
        cart_text = f"Cart: {len(counter.cart)} items | Total: Rs.{counter.get_cart_total():.2f}"
        cv2.putText(display, cart_text, 
                    (20, display.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.imshow("VisionCart Checkout Counter", display)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('c'):
            success, result = counter.checkout()
            if success:
                print("\n" + "="*60)
                print("✅ CHECKOUT COMPLETE!")
                print("="*60)
                print(f"Total: ₹{result['total']:.2f}")
                print(f"Items: {len(result['items'])}")
                print("="*60 + "\n")
            else:
                print(f"❌ {result}")
        elif key == ord('r'):
            removed = counter.remove_last_item()
            if removed:
                print(f"❌ Removed: {removed['name']}")
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
