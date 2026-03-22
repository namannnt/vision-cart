"""
Multi-View Product Registration for Cylindrical Objects
Register bottles from multiple angles for better recognition
"""
import cv2
import torch
import numpy as np
from PIL import Image
from ultralytics import YOLO
from torchvision import transforms

from models.clip import clip_loader
from models.dinov2 import dino_loader
from utils.clip_embedding import get_clip_embedding
from utils.dino_embedding import get_dino_embedding
from utils.embedding_fusion import fuse_embeddings
from utils.segmentation_crop import apply_segmentation_mask, crop_to_mask
from utils.validation import validate_detection
from utils.register_product import register_product, is_duplicate, get_all_embeddings

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load models
print("Loading models...")
yolo_model = YOLO("yolo11x-seg.pt")

# DINO transform
dino_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

print("\n" + "="*60)
print("MULTI-VIEW BOTTLE REGISTRATION")
print("="*60)
print("\n📋 Instructions for Cylindrical Objects:")
print("  1. We'll capture 3 views of the same bottle")
print("  2. View 1: Front label facing camera")
print("  3. View 2: Rotate 45° left")
print("  4. View 3: Rotate 45° right")
print("  5. All 3 views will be averaged for better recognition")
print("\n💡 Tips:")
print("  - Plain white background")
print("  - Good lighting (no reflections)")
print("  - Keep bottle upright")
print("  - Distance: 30-40cm")
print("="*60 + "\n")

# Get product details first
product_id = input("Enter Product ID/Name: ")
price = float(input("Enter Price: "))
stock = int(input("Enter Stock Quantity: "))

print(f"\n✅ Product: {product_id}")
print(f"✅ Price: ₹{price}")
print(f"✅ Stock: {stock}")
print("\nNow we'll capture 3 views...")

# Open camera
cap = cv2.VideoCapture(2)  # iVCam

if not cap.isOpened():
    print("❌ Could not open camera")
    exit()

embeddings = []
crops = []

for view_num in range(1, 4):
    if view_num == 1:
        instruction = "View 1: Front label facing camera"
    elif view_num == 2:
        instruction = "View 2: Rotate bottle 45° LEFT"
    else:
        instruction = "View 3: Rotate bottle 45° RIGHT"
    
    print(f"\n{'='*60}")
    print(f"📸 {instruction}")
    print(f"{'='*60}")
    print("Press 'c' to capture | 'q' to quit")
    
    captured = False
    
    while not captured:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        display = frame.copy()
        cv2.putText(display, instruction, 
                    (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display, "Press 'C' to capture", 
                    (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Multi-View Registration", display)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('c'):
            captured = True
            capture_frame = frame.copy()
            print("✅ Captured!")
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            print("❌ Registration cancelled")
            exit()
    
    # Process captured frame
    print("🔍 Processing...")
    
    try:
        results = yolo_model(capture_frame, conf=0.25, verbose=False)
        
        if results[0].masks is None or len(results[0].masks) == 0:
            print(f"❌ No object detected in view {view_num}")
            print("Please try again with better lighting/background")
            view_num -= 1
            continue
        
        mask = results[0].masks.data[0].cpu().numpy()
        mask = cv2.resize(mask, (capture_frame.shape[1], capture_frame.shape[0]))
        
        clean_img, binary_mask = apply_segmentation_mask(capture_frame, mask)
        final_crop = crop_to_mask(clean_img, mask)
        
        is_valid, reason = validate_detection(results, capture_frame, final_crop, binary_mask)
        
        if not is_valid:
            print(f"⚠️ Invalid detection: {reason}")
            print("Please try again")
            view_num -= 1
            continue
        
        # Generate embedding
        pil_crop = Image.fromarray(cv2.cvtColor(final_crop, cv2.COLOR_BGR2RGB))
        
        clip_emb = get_clip_embedding(pil_crop, clip_loader.model, clip_loader.preprocess, device)
        dino_tensor = dino_transform(pil_crop).unsqueeze(0)
        dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, device)
        fused_emb = fuse_embeddings(clip_emb, dino_emb, alpha=0.6)
        
        embeddings.append(fused_emb)
        crops.append(final_crop)
        
        print(f"✅ View {view_num} processed successfully!")
        
        # Show crop
        cv2.imshow(f"View {view_num} - Captured", final_crop)
        cv2.waitKey(1000)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        view_num -= 1
        continue

cap.release()
cv2.destroyAllWindows()

# Average embeddings
print("\n🧠 Averaging embeddings from all views...")
averaged_embedding = np.mean(embeddings, axis=0)

print(f"✅ Multi-view embedding shape: {averaged_embedding.shape}")

# Check for duplicates
existing_embeddings = get_all_embeddings()

if len(existing_embeddings) > 0:
    if is_duplicate(averaged_embedding, existing_embeddings, threshold=0.90):
        print("\n❌ DUPLICATE DETECTED!")
        print("This product (or very similar) is already registered.")
        exit()

# Save best view image
image_path = f"data/registered_products/{product_id}.jpg"
cv2.imwrite(image_path, crops[0])  # Save front view

# Register
print("\n💾 Registering product...")
success, message = register_product(product_id, price, stock, averaged_embedding)

if success:
    print(f"\n{'='*60}")
    print("✅ SUCCESS!")
    print(f"{'='*60}")
    print(f"Product: {product_id}")
    print(f"Price: ₹{price}")
    print(f"Stock: {stock}")
    print(f"Image: {image_path}")
    print(f"Views captured: 3")
    print(f"Embedding: Multi-view averaged")
    print(f"{'='*60}")
else:
    print(f"\n❌ {message}")

print("\n✅ Registration complete!")
