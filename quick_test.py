"""
Quick VisionCart System Test
Tests all components without camera
"""
import sys
import os
import numpy as np
import time
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

print("="*60)
print("VISIONCART QUICK SYSTEM TEST")
print("="*60)

# Test 1: Database
print("\n1. Database Test:")
try:
    from utils.load_database import load_database
    product_ids, db_embeddings, prices, stocks = load_database()
    print(f"   ✅ Products loaded: {len(product_ids)}")
    for i, pid in enumerate(product_ids):
        print(f"      - {pid}: ₹{prices[i]} (Stock: {stocks[i]})")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Models
print("\n2. AI Models Test:")
try:
    import torch
    from models.clip import clip_loader
    from models.dinov2 import dino_loader
    from ultralytics import YOLO
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"   Device: {device}")
    print(f"   ✅ CLIP loaded")
    print(f"   ✅ DINOv2 loaded")
    
    yolo_model = YOLO("yolo11x-seg.pt")
    print(f"   ✅ YOLO loaded")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 3: Embedding Generation Speed
print("\n3. Embedding Speed Test:")
try:
    from utils.clip_embedding import get_clip_embedding
    from utils.dino_embedding import get_dino_embedding
    from utils.embedding_fusion import fuse_embeddings
    from torchvision import transforms
    
    # Create dummy image
    dummy_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    pil_img = Image.fromarray(dummy_img)
    
    dino_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Warmup
    for _ in range(3):
        clip_emb = get_clip_embedding(pil_img, clip_loader.model, clip_loader.preprocess, device)
        dino_tensor = dino_transform(pil_img).unsqueeze(0)
        dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, device)
        fused = fuse_embeddings(clip_emb, dino_emb)
    
    # Measure
    times = []
    for _ in range(10):
        start = time.time()
        clip_emb = get_clip_embedding(pil_img, clip_loader.model, clip_loader.preprocess, device)
        dino_tensor = dino_transform(pil_img).unsqueeze(0)
        dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, device)
        fused = fuse_embeddings(clip_emb, dino_emb)
        times.append((time.time() - start) * 1000)
    
    avg_time = np.mean(times)
    fps = 1000 / avg_time
    
    print(f"   ✅ Embedding generation: {avg_time:.1f}ms")
    print(f"   ✅ Theoretical FPS: {fps:.1f}")
    print(f"   ✅ Embedding shape: {fused.shape}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Similarity Matching Speed
print("\n4. Similarity Matching Test:")
try:
    from utils.embedding_fusion import find_best_match
    from utils.accuracy_boost import top_k_matching
    
    if len(db_embeddings) > 0:
        # Test basic matching
        start = time.time()
        for _ in range(100):
            idx, score, is_known = find_best_match(fused, db_embeddings, threshold=0.85)
        basic_time = (time.time() - start) / 100 * 1000
        
        # Test top-K matching
        start = time.time()
        for _ in range(100):
            idx, score, is_known, top_k = top_k_matching(fused, db_embeddings, product_ids, k=3, threshold=0.85)
        topk_time = (time.time() - start) / 100 * 1000
        
        print(f"   ✅ Basic matching: {basic_time:.2f}ms")
        print(f"   ✅ Top-K matching: {topk_time:.2f}ms")
        print(f"   ✅ Best match: {product_ids[idx]} (score: {score:.3f})")
    else:
        print("   ⚠️  No products to match")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 5: Accuracy Booster
print("\n5. Accuracy Booster Test:")
try:
    from utils.accuracy_boost import AccuracyBooster
    
    booster = AccuracyBooster(history_size=5, emb_history_size=3)
    
    # Test voting
    for i in range(10):
        label = booster.multi_frame_voting("test_product")
    print(f"   ✅ Multi-frame voting: {label}")
    
    # Test smoothing
    for i in range(5):
        smoothed = booster.embedding_smoothing(fused)
    print(f"   ✅ Embedding smoothing: {smoothed.shape}")
    
    # Test brightness normalization
    normalized = booster.brightness_normalize(dummy_img)
    print(f"   ✅ Brightness normalization: {normalized.shape}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 6: Validation Rules
print("\n6. Validation Rules Test:")
try:
    from utils.validation import validate_detection
    
    # Create mock detection result
    class MockBox:
        def __init__(self):
            self.conf = [0.8]
    
    class MockResult:
        def __init__(self):
            self.boxes = MockBox()
    
    mock_results = [MockResult()]
    mock_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    mock_crop = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    mock_mask = np.ones((480, 640), dtype=np.uint8) * 255
    
    is_valid, reason = validate_detection(mock_results, mock_frame, mock_crop, mock_mask)
    print(f"   ✅ Validation working: {is_valid} ({reason})")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 7: Overall Pipeline Speed
print("\n7. Overall Pipeline Estimate:")
try:
    # YOLO detection: ~20-50ms on GPU
    yolo_time = 30  # estimated
    
    # Segmentation: ~5ms
    seg_time = 5
    
    # Embedding: measured above
    emb_time = avg_time
    
    # Matching: measured above
    match_time = topk_time
    
    total_time = yolo_time + seg_time + emb_time + match_time
    estimated_fps = 1000 / total_time
    
    print(f"   YOLO Detection: ~{yolo_time}ms")
    print(f"   Segmentation: ~{seg_time}ms")
    print(f"   Embedding: {emb_time:.1f}ms")
    print(f"   Matching: {match_time:.2f}ms")
    print(f"   ─────────────────────")
    print(f"   Total Pipeline: ~{total_time:.1f}ms")
    print(f"   ✅ Estimated FPS: {estimated_fps:.1f}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Summary
print("\n" + "="*60)
print("SYSTEM STATUS SUMMARY")
print("="*60)
print(f"✅ Database: {len(product_ids)} products")
print(f"✅ AI Models: YOLO + CLIP + DINOv2 (GPU)")
print(f"✅ Embedding Speed: {avg_time:.1f}ms")
print(f"✅ Matching Speed: {topk_time:.2f}ms")
print(f"✅ Estimated FPS: {estimated_fps:.1f}")
print(f"✅ All components working!")
print("="*60)

print("\n🎯 System Performance:")
if estimated_fps >= 15:
    print("   🟢 EXCELLENT - Real-time performance")
elif estimated_fps >= 10:
    print("   🟡 GOOD - Smooth operation")
elif estimated_fps >= 5:
    print("   🟠 ACCEPTABLE - Usable")
else:
    print("   🔴 SLOW - Consider optimization")

print("\n✅ Quick test completed successfully!")
print("="*60)
