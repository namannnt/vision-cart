"""
Customer Checkout Backend V2 - ULTIMATE SIZE DISAMBIGUATION
============================================================
State-of-the-art solution combining:
1. Hierarchical matching (parent-first, then size)
2. Strict size-based filtering BEFORE embedding comparison
3. Confidence penalty for ambiguous cases
4. Multi-stage verification pipeline
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
from utils.accuracy_boost import AccuracyBooster
from utils.coin_size_estimator import (
    detect_coin, pixels_per_mm, estimate_product_real_diameter_mm,
    real_size_gate, draw_coin_overlay
)
from sklearn.metrics.pairwise import cosine_similarity

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
        
        # Build parent group index for fast lookup
        self.parent_groups = self._build_parent_index()
        
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
        self.cooldown_seconds = 8
        self.detection_count = {}
        self.recent_detections = []
        
        # Multi-frame voting buffer
        self.vote_buffer: dict = {}
        self.vote_required = 3
    
    def _build_parent_index(self):
        """Build index: parent_id -> [product_indices]"""
        groups = {}
        for idx, parent in enumerate(self.parent_ids):
            if parent:
                if parent not in groups:
                    groups[parent] = []
                groups[parent].append(idx)
        return groups
    
    def _size_based_filtering(self, query_shape, query_diameter_mm, coin_present, candidate_indices):
        """
        STAGE 1: Size-based filtering BEFORE embedding comparison
        This is the KEY to preventing wrong size detection
        
        Returns: filtered_indices (only products that pass size check)
        """
        if not candidate_indices:
            return []
        
        filtered = []
        
        for idx in candidate_indices:
            # Method 1: Coin-based real size (MOST ACCURATE)
            if coin_present and query_diameter_mm > 5.0 and self.real_diameters[idx] > 5.0:
                if real_size_gate(query_diameter_mm, self.real_diameters[idx], tolerance_mm=10.0):
                    filtered.append(idx)
                    continue
                else:
                    # Size mismatch — skip this candidate
                    continue
            
            # Method 2: Frame-based size ratio (FALLBACK)
            if self.shape_feats[idx] is not None:
                # Use VERY STRICT tolerance for parent groups
                if size_gate(query_shape, self.shape_feats[idx], tolerance=0.20):
                    filtered.append(idx)
                    continue
            else:
                # No size data — allow it (benefit of doubt)
                filtered.append(idx)
        
        return filtered
    
    def _hierarchical_matching(self, query_emb, query_shape, query_color, query_diameter_mm, coin_present):
        """
        STAGE 2: Hierarchical matching with size-first filtering
        
        Pipeline:
        1. Get top-K candidates by embedding similarity
        2. Group by parent_id
        3. For each parent group, filter by SIZE first
        4. Then pick best embedding match from size-filtered candidates
        
        Returns: (best_idx, confidence, message)
        """
        # Step 1: Get top-K candidates (K=5 for better coverage)
        all_sims = cosine_similarity(query_emb, self.db_embeddings)[0]
        top_k = 5
        top_indices = all_sims.argsort()[-top_k:][::-1]
        top_scores = all_sims[top_indices]
        
        # Check if best match is even reasonable
        if top_scores[0] < 0.55:
            return None, top_scores[0], "Unknown product (low similarity)"
        
        # Step 2: Group candidates by parent
        parent_candidates = {}  # parent_id -> [(idx, score), ...]
        no_parent_candidates = []  # [(idx, score), ...]
        
        for idx, score in zip(top_indices, top_scores):
            parent = self.parent_ids[idx] if idx < len(self.parent_ids) else ""
            if parent:
                if parent not in parent_candidates:
                    parent_candidates[parent] = []
                parent_candidates[parent].append((idx, score))
            else:
                no_parent_candidates.append((idx, score))
        
        # Step 3: For each parent group, apply SIZE FILTERING first
        best_idx = None
        best_score = -1.0
        best_message = ""
        
        # Process parent groups
        for parent, candidates in parent_candidates.items():
            candidate_indices = [idx for idx, _ in candidates]
            
            # SIZE FILTERING (this is the magic!)
            size_filtered = self._size_based_filtering(
                query_shape, query_diameter_mm, coin_present, candidate_indices
            )
            
            if not size_filtered:
                # No candidate passed size check in this parent group
                if coin_present:
                    best_message = f"⚠️ Size mismatch - Detected {query_diameter_mm:.1f}mm but no matching variant"
                else:
                    best_message = f"⚠️ Ambiguous size - Place ₹1 coin for accurate detection"
                continue
            
            # Now pick best embedding match from size-filtered candidates
            for idx in size_filtered:
                score = float(all_sims[idx])
                
                # Add color and shape boost
                if self.color_hists[idx] is not None:
                    c_sim = color_similarity(query_color, self.color_hists[idx])
                    score += c_sim * 0.05
                
                if self.shape_feats[idx] is not None:
                    s_sim = shape_similarity(query_shape, self.shape_feats[idx])
                    score += s_sim * 0.03
                
                score = min(score, 1.0)
                
                if score > best_score:
                    best_score = score
                    best_idx = idx
                    best_message = "Matched with size verification"
        
        # Process non-parent products
        if no_parent_candidates:
            for idx, score in no_parent_candidates:
                # Apply size gate for non-parent products too
                if self.shape_feats[idx] is not None:
                    if not size_gate(query_shape, self.shape_feats[idx], tolerance=0.35):
                        continue
                
                # Add boosts
                if self.color_hists[idx] is not None:
                    c_sim = color_similarity(query_color, self.color_hists[idx])
                    score += c_sim * 0.05
                
                if self.shape_feats[idx] is not None:
                    s_sim = shape_similarity(query_shape, self.shape_feats[idx])
                    score += s_sim * 0.03
                
                score = min(score, 1.0)
                
                if score > best_score:
                    best_score = score
                    best_idx = idx
                    best_message = "Matched (no size variants)"
        
        # Final threshold check
        if best_idx is not None and best_score >= 0.60:
            return best_idx, best_score, best_message
        else:
            return None, best_score, best_message if best_message else "Low confidence match"
    
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
                mask = results[0].masks.data[best_idx].cpu().numpy()
                mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
                clean_img, binary_mask = apply_segmentation_mask(frame, mask)
                final_crop = crop_to_mask(clean_img, mask)
            else:
                final_crop, binary_mask = fallback_crop_no_yolo(frame)
                if final_crop is None or final_crop.size == 0:
                    return False, None, 0, "No object detected"
            
            if final_crop is None or final_crop.size == 0:
                return False, None, 0, "Invalid crop"
            
            # Validation
            if best_idx is not None:
                is_valid, reason = validate_detection(results, frame, final_crop, binary_mask)
                if not is_valid:
                    return False, None, 0, f"Invalid: {reason}"
            
            # Extract features
            final_crop = self.booster.brightness_normalize(final_crop)
            pil_crop = Image.fromarray(cv2.cvtColor(final_crop, cv2.COLOR_BGR2RGB))

            clip_emb = get_clip_embedding(pil_crop, clip_loader.model, clip_loader.preprocess, self.device)
            dino_tensor = self.dino_transform(pil_crop).unsqueeze(0)
            dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, self.device)
            query_emb = fuse_embeddings(clip_emb, dino_emb)
            query_emb = self.booster.embedding_smoothing(query_emb)
            
            query_color = extract_color_histogram(final_crop)
            query_shape = extract_shape_features(final_crop, binary_mask)
            
            # Coin detection
            coin = detect_coin(frame)
            coin_present = coin is not None
            query_diameter_mm = 0.0
            
            if coin_present:
                ppm = pixels_per_mm(coin[2])
                query_diameter_mm = estimate_product_real_diameter_mm(binary_mask, ppm)
            
            # HIERARCHICAL MATCHING (the ultimate solution!)
            idx, score, message = self._hierarchical_matching(
                query_emb, query_shape, query_color, query_diameter_mm, coin_present
            )
            
            if idx is None:
                self.vote_buffer.clear()
                return False, None, score, message
            
            product_name = self.product_ids[idx]
            
            # Multi-frame voting
            if self.vote_buffer.get("product") != product_name:
                self.vote_buffer = {"product": product_name, "count": 1}
            else:
                self.vote_buffer["count"] += 1

            if self.vote_buffer["count"] < self.vote_required:
                return False, product_name, score, f"Confirming... ({self.vote_buffer['count']}/{self.vote_required})"

            # Oscillation check
            self.recent_detections.append(product_name)
            if len(self.recent_detections) > 10:
                self.recent_detections.pop(0)
            
            recent_count = self.recent_detections[-5:].count(product_name)
            if recent_count >= 3:
                self.vote_buffer.clear()
                return False, product_name, score, "⚠️ Already detected recently - Remove item"
            
            self.vote_buffer.clear()
            
            # Get product info
            price = self.prices[idx]
            stock = self.stocks[idx]
            
            # Check stock
            if stock <= 0:
                return False, product_name, score, "OUT OF STOCK"
            
            # Cooldown check
            current_time = time.time()
            if (product_name == self.last_detected_product and 
                current_time - self.last_detection_time < self.cooldown_seconds):
                return False, product_name, score, "⏳ Cooldown active - Remove item"
            
            # Check if already in cart
            for item in self.cart:
                if item['name'] == product_name:
                    return False, product_name, score, f"⚠️ {product_name} already in cart"
            
            # Add to cart
            self.cart.append({
                'name': product_name,
                'price': price,
                'confidence': score,
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'quantity': 1
            })
            
            # Update tracking
            self.last_detected_product = product_name
            self.last_detection_time = current_time

            # Low stock warning
            warning = ""
            if stock <= 3:
                warning = f" (Only {stock} left!)"

            size_info = f" [{query_diameter_mm:.1f}mm]" if coin_present else ""
            return True, product_name, score, f"Added to cart{size_info}{warning}"
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, None, 0, f"Error: {str(e)}"
    
    def get_cart_total(self):
        """Calculate cart total"""
        return sum(item['price'] * item.get('quantity', 1) for item in self.cart)
    
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
                qty = item.get('quantity', 1)
                cursor.execute("""
                    UPDATE products 
                    SET stock = stock - ? 
                    WHERE product_id = ?
                """, (qty, item['name']))
            
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
            
            # Reload stocks
            self.product_ids, self.db_embeddings, self.prices, self.stocks, \
                self.color_hists, self.shape_feats, self.real_diameters, self.parent_ids = load_database()
            self.parent_groups = self._build_parent_index()
            
            return True, bill
        
        except Exception as e:
            return False, f"Error: {str(e)}"
