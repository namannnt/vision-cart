import torch
import clip
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading CLIP model on {device}...")
model, preprocess = clip.load("ViT-B/32", device=device)
model.eval()
print("CLIP model loaded successfully!")
