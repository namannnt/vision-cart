import cv2
import numpy as np

def validate_detection(results, frame, final_crop, binary_mask):
    """
    Validate detection using 5 rules (RELAXED for flat objects)
    Returns: (is_valid, reason)
    """
    
    # RULE 1 — Confidence Threshold (relaxed for non-standard products)
    if len(results[0].boxes.conf) == 0:
        return False, "No detection"
    
    if results[0].boxes.conf[0] < 0.10:  # Very relaxed — YOLO runs at conf=0.10
        return False, "Low confidence"
    
    # RULE 2 — Area Threshold (RELAXED)
    h, w, _ = frame.shape
    crop_area = final_crop.shape[0] * final_crop.shape[1]
    frame_area = h * w
    
    if crop_area / frame_area < 0.03:  # Lowered from 0.05
        return False, "Area too small"
    
    # RULE 3 — Aspect Ratio Check (RELAXED)
    ratio = final_crop.shape[1] / final_crop.shape[0]
    
    if ratio < 0.3 or ratio > 3.0:  # Relaxed from 0.4-2.5
        return False, "Invalid aspect ratio"
    
    # RULE 4 — Blur Detection (RELAXED)
    gray = cv2.cvtColor(final_crop, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    if blur_score < 40:  # Relaxed — flat tins can have lower variance
        return False, "Image too blurry"
    
    # RULE 5 — Empty Mask Check (RELAXED)
    if cv2.countNonZero(binary_mask) < 500:  # Lowered from 1000
        return False, "Mask too small"
    
    return True, "Valid"
