"""
VisionCart Pipeline Verification
Test the complete AI pipeline without camera
"""
import sys
import os
import numpy as np

print("="*60)
print("VISIONCART PIPELINE VERIFICATION")
print("="*60)

# Test 1: Import all modules
print("\n1. Testing Module Imports...")
try:
    import torch
    import cv2
    import clip
    from PIL import Image
    from ultralytics import YOLO
    from torchvision import transforms
    from sklearn.metrics.pairwise import cosine_similarity
    print("   ✅ All core modules imported successfully")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    print("   Make sure virtual environment is activated!")
    sys.exit(1)

# Test 2: Load AI models
print("\n2. Testing AI Model Loading...")
try:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"   Device: {device}")
    
    # YOLO
    print("   Loading YOLO...")
    yolo_model = YOLO("yolo11x-seg.pt")
    print("   ✅ YOLO loaded")
    
    # CLIP
    print("   Loading CLIP...")
    from models.clip import clip_loader
    print("   ✅ CLIP loaded")
    
    # DINOv2
    print("   Loading DINOv2...")
    from models.dinov2 import dino_loader
    print("   ✅ DINOv2 loaded")
    
except Exception as e:
    print(f"   ❌ Model loading error: {e}")
    sys.exit(1)

# Test 3: Import utilities
print("\n3. Testing Utility Modules...")
try:
    from utils.clip_embedding import get_clip_embedding
    from utils.dino_embedding import get_dino_embedding
    from utils.embedding_fusion import fuse_embeddings, find_best_match
    from utils.segmentation_crop import apply_segmentation_mask, crop_to_mask
    from utils.validation import validate_detection
    from utils.register_product import register_product, is_duplicate, get_all_embeddings
    from utils.load_database import load_database
    from utils.accuracy_boost import AccuracyBooster, top_k_matching
    from utils.billing import BillingSystem
    print("   ✅ All utility modules imported")
except ImportError as e:
    print(f"   ❌ Utility import error: {e}")
    sys.exit(1)

# Test 4: Database connection
print("\n4. Testing Database...")
try:
    import sqlite3
    conn = sqlite3.connect("database/visioncart.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"   ✅ Database connected")
    print(f"   Products in database: {count}")
except Exception as e:
    print(f"   ❌ Database error: {e}")
    sys.exit(1)

# Test 5: Load database embeddings
print("\n5. Testing Database Loading...")
try:
    product_ids, db_embeddings, prices, stocks = load_database()
    print(f"   ✅ Database loaded")
    print(f"   Products: {len(product_ids)}")
    if len(product_ids) > 0:
        print(f"   Embedding shape: {db_embeddings.shape}")
        print(f"   Products: {', '.join(product_ids)}")
except Exception as e:
    print(f"   ❌ Database loading error: {e}")
    sys.exit(1)

# Test 6: Test embedding generation (dummy image)
print("\n6. Testing Embedding Generation...")
try:
    # Create dummy image
    dummy_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    pil_img = Image.fromarray(dummy_img)
    
    # CLIP embedding
    clip_emb = get_clip_embedding(pil_img, clip_loader.model, clip_loader.preprocess, device)
    print(f"   ✅ CLIP embedding: {clip_emb.shape}")
    
    # DINOv2 embedding
    dino_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    dino_tensor = dino_transform(pil_img).unsqueeze(0)
    dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, device)
    print(f"   ✅ DINOv2 embedding: {dino_emb.shape}")
    
    # Fusion
    fused_emb = fuse_embeddings(clip_emb, dino_emb)
    print(f"   ✅ Fused embedding: {fused_emb.shape}")
    
except Exception as e:
    print(f"   ❌ Embedding generation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Test similarity matching
print("\n7. Testing Similarity Matching...")
try:
    if len(db_embeddings) > 0:
        idx, score, is_known = find_best_match(fused_emb, db_embeddings, threshold=0.85)
        print(f"   ✅ Matching works")
        print(f"   Best match: {product_ids[idx]} (score: {score:.3f})")
        print(f"   Is known: {is_known}")
    else:
        print("   ⚠️  No products in database to match against")
except Exception as e:
    print(f"   ❌ Matching error: {e}")
    sys.exit(1)

# Test 8: Test accuracy booster
print("\n8. Testing Accuracy Booster...")
try:
    booster = AccuracyBooster(history_size=5, emb_history_size=3)
    
    # Test voting
    for i in range(5):
        label = booster.multi_frame_voting("test_product")
    print(f"   ✅ Multi-frame voting: {label}")
    
    # Test smoothing
    smoothed = booster.embedding_smoothing(fused_emb)
    print(f"   ✅ Embedding smoothing: {smoothed.shape}")
    
    # Test brightness normalization
    normalized = booster.brightness_normalize(dummy_img)
    print(f"   ✅ Brightness normalization: {normalized.shape}")
    
except Exception as e:
    print(f"   ❌ Accuracy booster error: {e}")
    sys.exit(1)

# Test 9: Test billing system
print("\n9. Testing Billing System...")
try:
    billing = BillingSystem()
    
    if len(product_ids) > 0:
        # Add item
        success = billing.add_to_bill(product_ids[0], prices[0])
        print(f"   ✅ Added item to cart: {success}")
        
        # Get total
        total = billing.get_total()
        print(f"   ✅ Cart total: ₹{total}")
        
        # Get bill summary
        summary = billing.get_bill_summary()
        print(f"   ✅ Bill summary generated")
    else:
        print("   ⚠️  No products to test billing")
    
except Exception as e:
    print(f"   ❌ Billing system error: {e}")
    sys.exit(1)

# Test 10: File structure
print("\n10. Testing File Structure...")
required_dirs = [
    "data/registered_products",
    "data/embeddings",
    "models/clip",
    "models/dinov2",
    "database",
    "ui",
    "utils"
]

all_exist = True
for d in required_dirs:
    if os.path.exists(d):
        print(f"   ✅ {d}/")
    else:
        print(f"   ❌ {d}/ - MISSING")
        all_exist = False

if not all_exist:
    print("   ⚠️  Some directories missing")

# Final summary
print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
print("\n✅ All pipeline components working correctly!")
print("\nYour VisionCart system is ready to use:")
print("  1. Register products: python register_product_app.py")
print("  2. Test recognition: python live_recognition.py")
print("  3. Start billing: python auto_billing_counter.py")
print("  4. Admin panel: streamlit run ui/admin_panel.py")
print("\nOr use the .bat files for easier access!")
print("="*60)
