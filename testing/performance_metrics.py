"""
VisionCart Performance Metrics
Measure latency and throughput
"""

import cv2
import torch
import time
import numpy as np
from PIL import Image
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ultralytics import YOLO
from torchvision import transforms
from models.clip import clip_loader
from models.dinov2 import dino_loader
from utils.clip_embedding import get_clip_embedding
from utils.dino_embedding import get_dino_embedding
from utils.embedding_fusion import fuse_embeddings
from utils.segmentation_crop import apply_segmentation_mask, crop_to_mask

print("="*60)
print("VISIONCART PERFORMANCE METRICS")
print("="*60)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")

# Load models
print("\nLoading models...")
yolo_model = YOLO("yolo11x-seg.pt")

dino_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

print("Models loaded!")

# Open camera
cap = cv2.VideoCapture(2)  # iVCam

if not cap.isOpened():
    print("❌ Could not open camera")
    exit()

print("\n" + "="*60)
print("Measuring performance...")
print("Place a product in front of camera")
print("Press SPACE to measure | ESC to quit")
print("="*60 + "\n")

measurements = {
    'yolo_detection': [],
    'segmentation': [],
    'clip_embedding': [],
    'dino_embedding': [],
    'total_pipeline': []
}

measurement_count = 0

while measurement_count < 50:  # 50 measurements
    ret, frame = cap.read()
    
    if not ret:
        break
    
    display = frame.copy()
    cv2.putText(display, f"Measurements: {measurement_count}/50", 
                (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(display, "Press SPACE to measure", 
                (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.imshow("Performance Test", display)
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == 32:  # SPACE
        pipeline_start = time.time()
        
        try:
            # YOLO Detection
            t1 = time.time()
            results = yolo_model(frame, conf=0.6, verbose=False)
            yolo_time = (time.time() - t1) * 1000
            
            if results[0].masks is not None and len(results[0].masks) > 0:
                # Segmentation
                t2 = time.time()
                mask = results[0].masks.data[0].cpu().numpy()
                mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
                clean_img, binary_mask = apply_segmentation_mask(frame, mask)
                final_crop = crop_to_mask(clean_img, mask)
                seg_time = (time.time() - t2) * 1000
                
                if final_crop is not None and final_crop.size > 0:
                    pil_crop = Image.fromarray(cv2.cvtColor(final_crop, cv2.COLOR_BGR2RGB))
                    
                    # CLIP Embedding
                    t3 = time.time()
                    clip_emb = get_clip_embedding(pil_crop, clip_loader.model, clip_loader.preprocess, device)
                    clip_time = (time.time() - t3) * 1000
                    
                    # DINO Embedding
                    t4 = time.time()
                    dino_tensor = dino_transform(pil_crop).unsqueeze(0)
                    dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, device)
                    dino_time = (time.time() - t4) * 1000
                    
                    total_time = (time.time() - pipeline_start) * 1000
                    
                    # Store measurements
                    measurements['yolo_detection'].append(yolo_time)
                    measurements['segmentation'].append(seg_time)
                    measurements['clip_embedding'].append(clip_time)
                    measurements['dino_embedding'].append(dino_time)
                    measurements['total_pipeline'].append(total_time)
                    
                    measurement_count += 1
                    
                    print(f"Measurement {measurement_count}: Total={total_time:.1f}ms (YOLO={yolo_time:.1f}ms, Seg={seg_time:.1f}ms, CLIP={clip_time:.1f}ms, DINO={dino_time:.1f}ms)")
        
        except Exception as e:
            print(f"Error: {e}")
    
    elif key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()

# Calculate statistics
print("\n" + "="*60)
print("PERFORMANCE REPORT")
print("="*60)

for component, times in measurements.items():
    if len(times) > 0:
        avg = np.mean(times)
        std = np.std(times)
        min_t = np.min(times)
        max_t = np.max(times)
        
        print(f"\n{component.replace('_', ' ').title()}:")
        print(f"  Average: {avg:.2f}ms")
        print(f"  Std Dev: {std:.2f}ms")
        print(f"  Min: {min_t:.2f}ms")
        print(f"  Max: {max_t:.2f}ms")

print("\n" + "="*60)
print("✅ Performance testing completed!")
print("="*60)
