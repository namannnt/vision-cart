"""
Color Detection Layer
Extracts HSV color histogram from product image for additional matching signal
"""
import cv2
import numpy as np


def extract_color_histogram(image_bgr: np.ndarray, bins=(8, 8, 8)) -> np.ndarray:
    """
    Extract normalized HSV histogram from a BGR image.
    Returns a flat 1D numpy array of shape (bins[0]*bins[1]*bins[2],)
    """
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1, 2], None, list(bins),
                        [0, 180, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist.flatten().astype(np.float32)


def color_similarity(hist1: np.ndarray, hist2: np.ndarray) -> float:
    """
    Bhattacharyya distance converted to similarity score [0, 1].
    1.0 = identical colors, 0.0 = completely different.
    """
    dist = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
    return float(1.0 - dist)


def dominant_colors(image_bgr: np.ndarray, k: int = 3):
    """
    Return top-k dominant colors (BGR) using k-means.
    """
    data = image_bgr.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(data, k, None, criteria, 3,
                                    cv2.KMEANS_RANDOM_CENTERS)
    counts = np.bincount(labels.flatten())
    order = np.argsort(counts)[::-1]
    return centers[order].astype(np.uint8)
