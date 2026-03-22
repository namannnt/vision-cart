import torch

def get_dino_embedding(image_tensor, model, device):
    """
    Get DINOv2 embedding for an image
    image_tensor: preprocessed tensor
    """
    with torch.no_grad():
        if device == "cuda":
            image_tensor = image_tensor.cuda()
        emb = model(image_tensor)
        emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.cpu().numpy()
