import cv2
import torch
import numpy as np
from PIL import Image
from ultralytics import YOLO
from torchvision import transforms

def capture_and_process_product():
    """
    Open camera, capture product, process with AI pipeline
    Returns: (success, product_data, error_message)
    product_data = {
        'crop': final_crop,
        'embedding': fused_embedding,
        'image_path': None
    }
    """
    try:
        # Import AI modules
        from models.clip import clip_loader
        from models.dinov2 import dino_loader
        from utils.clip_embedding import get_clip_embedding
        from utils.dino_embedding import get_dino_embedding
        from utils.embedding_fusion import fuse_embeddings
        from utils.segmentation_crop import apply_segmentation_mask, crop_to_mask
        from utils.validation import validate_detection
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        # Load models
        print("Loading YOLO model...")
        yolo_model = YOLO("yolo11x-seg.pt")
        
        # DINO transform
        dino_transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        print("Models loaded!")
        print("\n" + "="*50)
        print("CAMERA CAPTURE MODE")
        print("="*50)
        print("Instructions:")
        print("  - Hold product CLOSE to camera (fill the frame)")
        print("  - Keep background CLEAN and simple")
        print("  - Avoid showing hands/face in frame")
        print("  - Good lighting is important")
        print("  - Press SPACE to capture")
        print("  - Press ESC to cancel")
        print("="*50 + "\n")
        
        # Open camera
        cap = cv2.VideoCapture(2)  # iVCam
        
        if not cap.isOpened():
            return False, None, "Could not open camera"
        
        captured_frame = None
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Display instructions
            display_frame = frame.copy()
            cv2.putText(display_frame, "Press SPACE to capture | ESC to cancel", 
                        (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow("Camera - Capture Product", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 32:  # SPACE
                captured_frame = frame.copy()
                print("✅ Image captured!")
                break
            elif key == 27:  # ESC
                cap.release()
                cv2.destroyAllWindows()
                return False, None, "Capture cancelled by user"
        
        cap.release()
        cv2.destroyAllWindows()
        
        if captured_frame is None:
            return False, None, "No image captured"
        
        # Process with AI pipeline
        print("\n🔍 Processing with YOLO...")
        results = yolo_model(captured_frame, conf=0.25, verbose=False)  # Minimum confidence
        
        if results[0].masks is None or len(results[0].masks) == 0:
            return False, None, "No object detected. Make sure: 1) Plain white background 2) Product fills frame 3) Good lighting"
        
        # Segmentation
        mask = results[0].masks.data[0].cpu().numpy()
        mask = cv2.resize(mask, (captured_frame.shape[1], captured_frame.shape[0]))
        clean_img, binary_mask = apply_segmentation_mask(captured_frame, mask)
        final_crop = crop_to_mask(clean_img, mask)
        
        # Validation
        is_valid, reason = validate_detection(results, captured_frame, final_crop, binary_mask)
        
        if not is_valid:
            return False, None, f"Invalid detection: {reason}"
        
        print("✅ Product detected and segmented!")
        
        # Show cropped product
        cv2.imshow("Detected Product - Press any key", final_crop)
        cv2.waitKey(2000)  # Show for 2 seconds
        cv2.destroyAllWindows()
        
        # Generate embeddings
        print("🧠 Generating AI embeddings...")
        pil_crop = Image.fromarray(cv2.cvtColor(final_crop, cv2.COLOR_BGR2RGB))
        
        clip_emb = get_clip_embedding(pil_crop, clip_loader.model, clip_loader.preprocess, device)
        dino_tensor = dino_transform(pil_crop).unsqueeze(0)
        dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, device)
        fused_embedding = fuse_embeddings(clip_emb, dino_emb, alpha=0.6)
        
        print(f"✅ Embedding generated! Shape: {fused_embedding.shape}")
        
        product_data = {
            'crop': final_crop,
            'embedding': fused_embedding,
            'image_path': None
        }
        
        return True, product_data, None
    
    except Exception as e:
        return False, None, str(e)
