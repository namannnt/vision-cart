"""
Shape & Size Detection Layer
Extracts shape complexity and physical size ratio from segmented product.

KEY INSIGHT for similar products (e.g. Vaseline 20gm vs 45gm):
- Cosine similarity is scale-invariant → ignores size differences
- We use ABSOLUTE size_ratio comparison as a hard gate instead
- Products with same visual appearance but different physical sizes
  will have different size_ratios when held at consistent distance
"""
import cv2
import numpy as np


def extract_shape_features(image_bgr: np.ndarray, binary_mask: np.ndarray = None) -> np.ndarray:
    """
    Extract shape features: aspect_ratio, extent, solidity, size_ratio.
    Returns a 1D float32 array of shape (4,)

    size_ratio = contour_area / frame_area  (key discriminator for size variants)
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
    extent = float(area) / (rect_area + 1e-6)
    hull_area = cv2.contourArea(cv2.convexHull(cnt))
    solidity = float(area) / (hull_area + 1e-6)
    img_area = image_bgr.shape[0] * image_bgr.shape[1]
    size_ratio = float(area) / (img_area + 1e-6)

    return np.array([aspect_ratio, extent, solidity, size_ratio], dtype=np.float32)


def shape_similarity(feat1: np.ndarray, feat2: np.ndarray) -> float:
    """
    Cosine similarity between shape feature vectors (aspect_ratio, extent, solidity only).
    Excludes size_ratio — size is handled separately via size_gate().
    Returns score in [0, 1].
    """
    # Only use first 3 features (shape, not size) for cosine similarity
    f1 = feat1[:3]
    f2 = feat2[:3]
    n1 = np.linalg.norm(f1)
    n2 = np.linalg.norm(f2)
    if n1 < 1e-6 or n2 < 1e-6:
        return 0.5
    return float(np.dot(f1, f2) / (n1 * n2))


def size_gate(query_feat: np.ndarray, db_feat: np.ndarray,
              tolerance: float = 0.40) -> bool:
    """
    Hard gate: returns False if the size_ratio difference is too large.

    This is the KEY discriminator for same-brand different-size products
    (e.g. Vaseline 20gm vs 45gm). A 45gm container occupies ~2x more
    frame area than a 20gm container at the same camera distance.

    tolerance=0.40 means: if registered size_ratio is 0.10 and query is 0.18,
    relative difference = |0.18-0.10|/0.10 = 0.80 → BLOCKED (> 0.40)

    Set tolerance higher (0.6) if camera distance varies a lot.
    """
    if db_feat is None or query_feat is None:
        return True  # no data → don't block

    db_size = float(db_feat[3])
    query_size = float(query_feat[3])

    if db_size < 1e-4:
        return True  # can't compare

    relative_diff = abs(query_size - db_size) / db_size
    return relative_diff <= tolerance


def size_bucket(size_ratio: float) -> str:
    if size_ratio < 0.05:
        return "small"
    elif size_ratio < 0.15:
        return "medium"
    else:
        return "large"
