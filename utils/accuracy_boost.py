import numpy as np
import cv2
from collections import deque

class AccuracyBooster:
    """
    Accuracy boost techniques for live recognition
    """
    
    def __init__(self, history_size=5, emb_history_size=3):
        self.label_history = deque(maxlen=history_size)
        self.emb_history = deque(maxlen=emb_history_size)
    
    def multi_frame_voting(self, label):
        """
        Multi-frame voting for stable predictions
        Returns most common label from last N frames
        """
        self.label_history.append(label)
        
        if len(self.label_history) < 3:
            return label
        
        # Find most common label
        label_counts = {}
        for lbl in self.label_history:
            label_counts[lbl] = label_counts.get(lbl, 0) + 1
        
        final_label = max(label_counts, key=label_counts.get)
        return final_label
    
    def embedding_smoothing(self, embedding):
        """
        Smooth embeddings across frames to reduce jitter
        """
        self.emb_history.append(embedding)
        
        if len(self.emb_history) < 2:
            return embedding
        
        # Average last N embeddings
        smoothed = np.mean(list(self.emb_history), axis=0)
        return smoothed
    
    def brightness_normalize(self, image):
        """
        Normalize brightness for consistent features
        """
        normalized = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
        return normalized
    
    def reset(self):
        """
        Reset history (call when no detection)
        """
        self.label_history.clear()
        self.emb_history.clear()


def top_k_matching(query_emb, database_embeddings, product_ids, k=3, threshold=0.70):
    """
    Top-K matching instead of Top-1
    Returns best match if top-K has consensus
    Threshold lowered to 0.70 for cylindrical objects (bottles)
    """
    from sklearn.metrics.pairwise import cosine_similarity
    
    if len(database_embeddings) == 0:
        return None, 0.0, False, []
    
    # Get all similarities
    sims = cosine_similarity(query_emb, database_embeddings)[0]
    
    # Get top-K indices
    top_k_indices = sims.argsort()[-k:][::-1]
    top_k_scores = sims[top_k_indices]
    top_k_labels = [product_ids[i] for i in top_k_indices]
    
    # Best match
    best_idx = top_k_indices[0]
    best_score = top_k_scores[0]
    best_label = top_k_labels[0]
    
    # Check if top-K has consensus (same product appears multiple times)
    label_counts = {}
    for label in top_k_labels:
        label_counts[label] = label_counts.get(label, 0) + 1
    
    # If best label appears at least 2 times in top-3, boost confidence
    consensus_boost = 0.0
    if label_counts.get(best_label, 0) >= 2:
        consensus_boost = 0.02  # Small boost for consensus
    
    final_score = min(best_score + consensus_boost, 1.0)
    is_known = final_score >= threshold
    
    return best_idx, final_score, is_known, top_k_labels
