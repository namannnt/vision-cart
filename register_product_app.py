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
from utils.register_product import register_product, is_duplicate, get_all_embeddings
from database import VisionCartDB

# Initialize
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load models
print("Loading YOLO model...")
yolo_model = YOLO("yolo11x-seg.pt")

print("Loading CLIP and DINOv2 models...")
# Models already loaded in clip_loader and dino_loader

# Initialize database
db = VisionCartDB()

# DINO transform
dino_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

print("\n" + "="*50)
print("PRODUCT REGISTRATION SYSTEM")
print("="*50)

# Open webcam
cap = cv2.VideoCapture(2)  # iVCam

if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

print("\nInstructions:")
print("1. Show product clearly in front of camera")
print("2. Press 'r' to register product")
print("3. Press 'q' to quit")

current_crop = None
current_embedding = None
is_valid_frame = False

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    try:
        # Run detection
        results = yolo_model(frame, conf=0.6, verbose=False)
        
        # Show detection
        annotated_frame = results[0].plot()
        
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
                        is_valid_frame = True
                        current_crop = final_crop.copy()
                        
                        # Show valid crop
                        cv2.rectangle(final_crop, (0, 0), (final_crop.shape[1]-1, final_crop.shape[0]-1), (0, 255, 0), 3)
                        cv2.putText(final_crop, "READY - Press 'R' to Register", (10, 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        cv2.imshow("Product Crop", final_crop)
                        
                        # Generate embedding
                        pil_crop = Image.fromarray(cv2.cvtColor(current_crop, cv2.COLOR_BGR2RGB))
                        clip_emb = get_clip_embedding(pil_crop, clip_loader.model, clip_loader.preprocess, device)
                        dino_tensor = dino_transform(pil_crop).unsqueeze(0)
                        dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, device)
                        current_embedding = fuse_embeddings(clip_emb, dino_emb, alpha=0.6)
                    else:
                        is_valid_frame = False
                        cv2.putText(annotated_frame, f"Invalid: {reason}", (10, 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow("Registration Camera", annotated_frame)
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Handle keys
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    
    elif key == ord('r') and is_valid_frame and current_embedding is not None:
        print("\n" + "="*50)
        print("REGISTERING PRODUCT")
        print("="*50)
        
        # Check for duplicates
        existing_embeddings = get_all_embeddings()
        
        if len(existing_embeddings) > 0:
            if is_duplicate(current_embedding, existing_embeddings, threshold=0.95):
                print("❌ DUPLICATE DETECTED!")
                print("This product is already registered.")
                continue
        
        # Get product details
        product_id = input("Enter Product ID/Name: ")
        price = float(input("Enter Price: "))
        stock = int(input("Enter Stock Quantity: "))
        
        # Save image
        image_path = f"data/registered_products/{product_id}.jpg"
        cv2.imwrite(image_path, current_crop)
        
        # Register
        success, message = register_product(product_id, price, stock, current_embedding)
        
        if success:
            print(f"✅ {message}")
            print(f"Image saved: {image_path}")
        else:
            print(f"❌ {message}")
        
        print("="*50 + "\n")

cap.release()
cv2.destroyAllWindows()
print("\nRegistration system closed!")
