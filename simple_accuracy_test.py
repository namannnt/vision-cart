"""
Simple Accuracy Test - Manual Testing
Show products and see if they're recognized correctly
"""
import cv2
import torch
import numpy as np
from PIL import Image
from ultralytics import YOLO
from torchvision import transforms
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from models.clip import clip_loader
from models.dinov2 import dino_loader
from utils.clip_embedding import get_clip_embedding
from utils.dino_embedding import get_dino_embedding
from utils.embedding_fusion import fuse_embeddings
from utils.segmentation_crop import apply_segmentation_mask, crop_to_mask
from utils.validation import validate_detection
from utils.load_database import load_database
from utils.accuracy_boost import top_k_matching

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load models
print("Loading models...")
yolo_model = YOLO("yolo11x-seg.pt")

# Load database
product_ids, db_embeddings, prices, stocks = load_database()
print(f"✅ Loaded {len(product_ids)} products")

# DINO transform
dino_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

print("\n" + "="*60)
print("SIMPLE ACCURACY TEST")
print("="*60)
print("Show products to camera and check if recognized correctly")
print("Press 'q' to quit")
print("="*60 + "\n")

cap = cv2.VideoCapture(2)  # iVCam

if not cap.isOpened():
    print("❌ Could not open camera")
    exit()

correct = 0
total = 0

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    display = frame.copy()
    
    try:
        results = yolo_model(frame, conf=0.6, verbose=False)
        
        if results[0].masks is not None and len(results[0].masks) > 0:
            mask = results[0].masks.data[0].cpu().numpy()
            mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
            
            clean_img, binary_mask = apply_segmentation_mask(frame, mask)
            final_crop = crop_to_mask(clean_img, mask)
            
            if final_crop is not None and final_crop.size > 0:
                is_valid, reason = validate_detection(results, frame, final_crop, binary_mask)
                
                if is_valid:
                    pil_crop = Image.fromarray(cv2.cvtColor(final_crop, cv2.COLOR_BGR2RGB))
                    
                    clip_emb = get_clip_embedding(pil_crop, clip_loader.model, clip_loader.preprocess, device)
                    dino_tensor = dino_transform(pil_crop).unsqueeze(0)
                    dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, device)
                    query_emb = fuse_embeddings(clip_emb, dino_emb)
                    
                    idx, score, is_known, top_k_labels = top_k_matching(
                        query_emb, db_embeddings, product_ids, k=3, threshold=0.85
                    )
                    
                    if is_known:
                        detected = product_ids[idx]
                        price = prices[idx]
                        
                        if score > 0.90:
                            color = (0, 255, 0)
                            conf = "HIGH"
                        elif score > 0.85:
                            color = (0, 255, 255)
                            conf = "MEDIUM"
                        else:
                            color = (0, 165, 255)
                            conf = "LOW"
                        
                        cv2.putText(display, f"Product: {detected}", 
                                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                        cv2.putText(display, f"Price: Rs.{price:.2f}", 
                                    (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                        cv2.putText(display, f"Confidence: {score:.3f} ({conf})", 
                                    (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                        cv2.putText(display, f"Top-3: {', '.join(top_k_labels)}", 
                                    (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    else:
                        cv2.putText(display, "UNKNOWN PRODUCT", 
                                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        cv2.putText(display, f"Score: {score:.3f} (Too Low)", 
                                    (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                else:
                    cv2.putText(display, f"Invalid: {reason}", 
                                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    except Exception as e:
        cv2.putText(display, f"Error: {str(e)[:50]}", 
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    cv2.imshow("Simple Accuracy Test - Press 'q' to quit", display)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\n✅ Test completed!")
