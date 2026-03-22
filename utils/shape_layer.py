"""
Shape & Size Detection Layer
Extracts shape complexity and physical size ratio from segmented product
"""
import cv2
import numpy as np


def extract_shape_features(image_bgr: np.ndarray, binary_mask: np.ndarray = None) -> np.ndarray:
    """
    Extract shape features: aspect ratio, extent, solidity, size_ratio.
    Returns a 1D float32 array of shape (4,)
    """
    if binary_mask is not None:
        contours, _ = cv2.findContours(binary_mask.astype(np.uint8),
                                       cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return np.zeros(4, dtype=np.float32)

    cnt = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(cnt)
    x, y, w, h = cv2.boundingRect(cnt)

    aspect_ratio = float(w) / (h + 1e-6)
    rect_area = w * h
    extent = float(area) / (rect_area + 1e-6)          # how much of bbox is filled
    hull_area = cv2.contourArea(cv2.convexHull(cnt))
    solidity = float(area) / (hull_area + 1e-6)         # convexity measure
    img_area = image_bgr.shape[0] * image_bgr.shape[1]
    size_ratio = float(area) / (img_area + 1e-6)        # relative size in frame

    return np.array([aspect_ratio, extent, solidity, size_ratio], dtype=np.float32)


def shape_similarity(feat1: np.ndarray, feat2: np.ndarray) -> float:
    """
    Cosine similarity between two shape feature vectors.
    Returns score in [0, 1].
    """
    n1 = np.linalg.norm(feat1)
    n2 = np.linalg.norm(feat2)
    if n1 < 1e-6 or n2 < 1e-6:
        return 0.5  # neutral if features are zero
    return float(np.dot(feat1, feat2) / (n1 * n2))


def size_bucket(size_ratio: float) -> str:
    """
    Classify product into size bucket based on frame area ratio.
    Useful for differentiating small/medium/large packets.
    """
    if size_ratio < 0.05:
        return "small"
    elif size_ratio < 0.15:
        return "medium"
    else:
        return "large"
