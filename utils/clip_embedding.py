import torch

def get_clip_embedding(image, model, preprocess, device):
    """
    Get CLIP embedding for an image
    image: PIL Image
    """
    image = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = model.encode_image(image)
        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
    return embedding.cpu().numpy()
