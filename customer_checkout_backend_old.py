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
from utils.segmentation_crop import apply_segmentation_mask, crop_to_mask, fallback_crop_no_yolo
from utils.validation import validate_detection
from utils.load_database import load_database
from utils.color_layer import extract_color_histogram, color_similarity
from utils.shape_layer import extract_shape_features, shape_similarity, size_gate
from utils.accuracy_boost import AccuracyBooster, top_k_matching
from utils.coin_size_estimator import (
    detect_coin, pixels_per_mm, estimate_product_real_diameter_mm,
    real_size_gate, draw_coin_overlay
)

class CheckoutCounter:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔧 Device: {self.device.upper()}")
        
        # Load models
        print("📦 Loading AI models...")
        self.yolo_model = YOLO("yolo11x-seg.pt")
        
        # Load database
        self.product_ids, self.db_embeddings, self.prices, self.stocks, \
            self.color_hists, self.shape_feats, self.real_diameters, self.parent_ids = load_database()
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
        self.cooldown_seconds = 8  # Prevent duplicate scans (increased to 8 seconds for stability)
        self.detection_count = {}  # Track detection count per product
        self.recent_detections = []  # Track last 10 detections to prevent oscillation
        # Multi-frame voting buffer: {product_name: count}
        self.vote_buffer: dict = {}
        self.vote_required = 3  # product must appear in 3 consecutive detections (increased for stability)
    
    def detect_and_add_to_cart(self, frame):
        """
        Detect product in frame and add to cart if valid
        Returns: (detected, product_name, confidence, message)
        """
        try:
            # Run YOLO detection
            results = self.yolo_model(frame, conf=0.10, verbose=False)

            # Skip person class (0) — pick largest non-person masked object
            SKIP_CLASSES = {0}
            best_idx = None
            best_area = -1
            if results[0].masks is not None:
                boxes = results[0].boxes
                for i in range(len(results[0].masks)):
                    cls = int(boxes.cls[i]) if boxes is not None else -1
                    if cls in SKIP_CLASSES:
                        continue
                    m = results[0].masks.data[i].cpu().numpy()
                    area = m.sum()
                    if area > best_area:
                        best_area = area
                        best_idx = i

            if best_idx is not None:
                # YOLO found a product
                mask = results[0].masks.data[best_idx].cpu().numpy()
                mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
                clean_img, binary_mask = apply_segmentation_mask(frame, mask)
                final_crop = crop_to_mask(clean_img, mask)
            else:
                # YOLO fallback — GrabCut (runs in separate thread, won't block feed)
                final_crop, binary_mask = fallback_crop_no_yolo(frame)
                if final_crop is None or final_crop.size == 0:
                    return False, None, 0, "No object detected"
            if final_crop is None or final_crop.size == 0:
                return False, None, 0, "Invalid crop"
            
            # Validation (only when YOLO detected, not fallback)
            if best_idx is not None:
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
                self.vote_buffer.clear()
                return False, None, score, f"Unknown product (score: {score:.2f})"

            # --- Color layer boost ---
            query_color = extract_color_histogram(final_crop)
            if self.color_hists[idx] is not None:
                c_sim = color_similarity(query_color, self.color_hists[idx])
                color_boost = c_sim * 0.05
            else:
                color_boost = 0.0

            # --- Shape layer boost ---
            query_shape = extract_shape_features(final_crop, binary_mask)
            if self.shape_feats[idx] is not None:
                s_sim = shape_similarity(query_shape, self.shape_feats[idx])
                shape_boost = s_sim * 0.03
            else:
                shape_boost = 0.0

            # --- PARENT-AWARE SIZE DISAMBIGUATION ---
            # If the matched product has a parent_id, find all siblings (same parent).
            # Use coin measurement to pick the correct size variant.
            matched_parent = self.parent_ids[idx] if idx < len(self.parent_ids) else ""

            if matched_parent:
                # Get all siblings with same parent
                siblings = [
                    i for i, pid in enumerate(self.parent_ids)
                    if pid == matched_parent
                ]

                if len(siblings) > 1:
                    # Multiple size variants exist — use coin to disambiguate
                    coin = detect_coin(frame)
                    if coin is not None:
                        ppm = pixels_per_mm(coin[2])
                        query_diameter_mm = estimate_product_real_diameter_mm(binary_mask, ppm)

                        if query_diameter_mm > 5.0:
                            # Find sibling whose registered diameter is closest
                            best_sib_idx = None
                            best_diff = float('inf')
                            for sib_i in siblings:
                                reg_diam = self.real_diameters[sib_i]
                                if reg_diam > 0:
                                    diff = abs(query_diameter_mm - reg_diam)
                                    if diff < best_diff:
                                        best_diff = diff
                                        best_sib_idx = sib_i

                            if best_sib_idx is not None:
                                idx = best_sib_idx  # override with coin-confirmed variant
                                score = float(
                                    __import__('sklearn.metrics.pairwise', fromlist=['cosine_similarity'])
                                    .cosine_similarity(query_emb, self.db_embeddings[best_sib_idx:best_sib_idx+1])[0][0]
                                )
                    else:
                        # No coin — use STRICT size_gate + shape matching among siblings
                        # This prevents detecting both sizes when only one is present
                        best_sib_idx = None
                        best_sib_score = -1.0
                        
                        for sib_i in siblings:
                            if self.shape_feats[sib_i] is not None:
                                # Use STRICTER tolerance for size gate (0.25 instead of 0.45)
                                if size_gate(query_shape, self.shape_feats[sib_i], tolerance=0.25):
                                    from sklearn.metrics.pairwise import cosine_similarity as _cos
                                    s = float(_cos(query_emb, self.db_embeddings[sib_i:sib_i+1])[0][0])
                                    
                                    # Also check shape similarity score
                                    shape_sim = shape_similarity(query_shape, self.shape_feats[sib_i])
                                    
                                    # Combined score: embedding + shape (weighted)
                                    combined = s * 0.7 + shape_sim * 0.3
                                    
                                    if combined > best_sib_score:
                                        best_sib_score = combined
                                        best_sib_idx = sib_i
                        
                        if best_sib_idx is not None:
                            idx = best_sib_idx
                            score = best_sib_score
                        else:
                            # NO sibling passed strict size gate — ambiguous detection
                            self.vote_buffer.clear()
                            return False, None, score, "⚠️ Ambiguous size - Place ₹1 coin in frame for accurate detection"
            else:
                # No parent group — use original size gate logic
                if self.shape_feats[idx] is not None:
                    if not size_gate(query_shape, self.shape_feats[idx], tolerance=0.45):
                        passed_idx = None
                        for candidate_idx in [self.product_ids.index(lbl)
                                              for lbl in top_k_labels
                                              if lbl in self.product_ids]:
                            if self.shape_feats[candidate_idx] is not None:
                                if size_gate(query_shape, self.shape_feats[candidate_idx], tolerance=0.45):
                                    passed_idx = candidate_idx
                                    break
                        if passed_idx is not None:
                            idx = passed_idx
                            score = float(
                                __import__('sklearn.metrics.pairwise', fromlist=['cosine_similarity'])
                                .cosine_similarity(query_emb, self.db_embeddings[passed_idx:passed_idx+1])[0][0]
                            )
                        else:
                            self.vote_buffer.clear()
                            return False, None, score, "Size mismatch — ambiguous product"

                # Coin gate for non-parent products
                coin = detect_coin(frame)
                if coin is not None:
                    ppm = pixels_per_mm(coin[2])
                    query_diameter_mm = estimate_product_real_diameter_mm(binary_mask, ppm)
                    if query_diameter_mm > 5.0:
                        from sklearn.metrics.pairwise import cosine_similarity as _cos
                        best_coin_idx = None
                        best_coin_score = -1.0
                        for lbl in top_k_labels:
                            if lbl not in self.product_ids:
                                continue
                            cidx = self.product_ids.index(lbl)
                            if real_size_gate(query_diameter_mm, self.real_diameters[cidx]):
                                s = float(_cos(query_emb, self.db_embeddings[cidx:cidx+1])[0][0])
                                if s > best_coin_score:
                                    best_coin_score = s
                                    best_coin_idx = cidx
                        if best_coin_idx is not None:
                            idx = best_coin_idx
                            score = best_coin_score
                        elif self.real_diameters[idx] > 5.0:
                            self.vote_buffer.clear()
                            return False, None, score, f"Size mismatch (measured {query_diameter_mm:.1f}mm)"

            # Fused score
            fused_score = min(score + color_boost + shape_boost, 1.0)

            if fused_score < 0.60:
                self.vote_buffer.clear()
                return False, None, fused_score, f"Low fused score ({fused_score:.2f})"

            score = fused_score
            product_name = self.product_ids[idx]

            # --- Multi-frame voting — require N consistent detections ---
            # Resets if a different product appears
            if self.vote_buffer.get("product") != product_name:
                self.vote_buffer = {"product": product_name, "count": 1}
            else:
                self.vote_buffer["count"] += 1

            if self.vote_buffer["count"] < self.vote_required:
                return False, product_name, score, f"Confirming... ({self.vote_buffer['count']}/{self.vote_required})"

            # Confirmed — check for oscillation (same product detected multiple times recently)
            self.recent_detections.append(product_name)
            if len(self.recent_detections) > 10:
                self.recent_detections.pop(0)
            
            # If this product was detected in last 5 detections, it might be oscillating
            recent_count = self.recent_detections[-5:].count(product_name)
            if recent_count >= 3:
                self.vote_buffer.clear()
                return False, product_name, score, "⚠️ Already detected recently - Remove item to scan again"
            
            # Reset vote buffer
            self.vote_buffer.clear()
            
            # Get product info
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
            
            # Check if already in cart (exact same product)
            for item in self.cart:
                if item['name'] == product_name:
                    return False, product_name, score, f"⚠️ {product_name} already in cart"

            # Check if a different size variant of same parent is already in cart
            # (different size = allowed, same size = blocked above)
            # This message is informational only — we still add it
            sibling_in_cart = None
            if matched_parent:
                for item in self.cart:
                    item_idx = self.product_ids.index(item['name']) if item['name'] in self.product_ids else -1
                    if item_idx >= 0 and self.parent_ids[item_idx] == matched_parent:
                        sibling_in_cart = item['name']
                        break
            
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

            if sibling_in_cart:
                return True, product_name, score, f"Added {product_name}{warning} (different size from {sibling_in_cart})"
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
        self.vote_buffer.clear()
        self.recent_detections.clear()
    
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
                self.color_hists, self.shape_feats, self.real_diameters, self.parent_ids = load_database()
            
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
