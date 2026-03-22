import torch
import cv2
from PIL import Image
import numpy as np

# Load models
print("Loading models...")
from models.clip import clip_loader
from models.dinov2 import dino_loader
from utils.clip_embedding import get_clip_embedding
from utils.dino_embedding import get_dino_embedding
from utils.embedding_fusion import fuse_embeddings, find_best_match

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Test image
test_image_path = "data/samples/test.jpg"
print(f"\nLoading test image: {test_image_path}")

try:
    # Load image
    pil_image = Image.open(test_image_path).convert("RGB")
    
    # Get CLIP embedding
    print("Generating CLIP embedding...")
    clip_emb = get_clip_embedding(pil_image, clip_loader.model, clip_loader.preprocess, device)
    print(f"CLIP embedding shape: {clip_emb.shape}")
    
    # Prepare for DINO
    from torchvision import transforms
    dino_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    dino_tensor = dino_transform(pil_image).unsqueeze(0)
    
    # Get DINO embedding
    print("Generating DINOv2 embedding...")
    dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, device)
    print(f"DINO embedding shape: {dino_emb.shape}")
    
    # Fuse embeddings
    print("\nFusing embeddings...")
    fused_emb = fuse_embeddings(clip_emb, dino_emb, alpha=0.6)
    print(f"Fused embedding shape: {fused_emb.shape}")
    
    print("\n✅ Embedding generation successful!")
    print("Ready for product matching!")
    
except FileNotFoundError:
    print(f"\n❌ Error: {test_image_path} not found")
    print("Please add a test image in data/samples/test.jpg")
except Exception as e:
    print(f"\n❌ Error: {e}")
