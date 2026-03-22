import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def fuse_embeddings(clip_emb, dino_emb, alpha=0.6):
    """
    Fuse CLIP and DINOv2 embeddings
    alpha = 0.6 (CLIP dominant, DINO support)
    
    Since CLIP (512) and DINO (768) have different dimensions,
    we concatenate them instead of weighted sum
    """
    # Concatenate embeddings
    fused = np.concatenate([clip_emb, dino_emb], axis=1)
    return fused

def find_best_match(query_emb, database_embeddings, threshold=0.70):
    """
    Find best matching product from database
    Returns: (best_idx, best_score, is_known)
    Threshold lowered to 0.70 for cylindrical objects (bottles)
    """
    if len(database_embeddings) == 0:
        return None, 0.0, False
    
    sims = cosine_similarity(query_emb, database_embeddings)
    best_idx = sims.argmax()
    best_score = sims[0][best_idx]
    
    # Confidence rule
    is_known = best_score >= threshold
    
    return best_idx, best_score, is_known
