import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading DINOv2 model on {device}...")
dino = torch.hub.load("facebookresearch/dinov2", "dinov2_vitb14")
dino.eval()
if device == "cuda":
    dino = dino.cuda()
print("DINOv2 model loaded successfully!")
