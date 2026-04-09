"""
Coin-based Real Size Estimator
================================
Uses a ₹1 coin (diameter = 25mm) as a reference object in the frame
to compute the real physical size of a product — independent of camera distance.

How it works:
  1. Detect the coin using circular Hough transform
  2. pixels_per_mm = coin_pixel_diameter / 25.0
  3. product_real_diameter_mm = product_pixel_diameter / pixels_per_mm

This makes size comparison distance-independent.
A Vaseline 20gm tin (~45mm dia) vs 45gm tin (~60mm dia) will always
differ by ~15mm regardless of how far the camera is.
"""

import cv2
import numpy as np
from typing import Optional, Tuple


# ₹1 Indian coin real diameter in mm
COIN_REAL_DIAMETER_MM = 25.0

# Tolerance for real-size matching (mm)
# If registered size is 45mm and query is 48mm → diff=3mm < 8mm → PASS
SIZE_MATCH_TOLERANCE_MM = 8.0


def detect_coin(frame_bgr: np.ndarray) -> Optional[Tuple[int, int, int]]:
    """
    Detect a ₹1 coin in the frame using Hough Circle Transform.
    Returns (cx, cy, radius_px) or None if not found.

    The coin should be placed in the corner of the scanning area.
    It will be detected as the smallest prominent circle in the frame.
    """
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2)

    h, w = gray.shape
    # Coin should be small relative to frame — between 2% and 15% of frame width
    min_r = int(w * 0.02)
    max_r = int(w * 0.12)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=int(w * 0.05),
        param1=80,
        param2=35,
        minRadius=min_r,
        maxRadius=max_r,
    )

    if circles is None:
        return None

    circles = np.round(circles[0, :]).astype(int)

    # Pick the most circular / best candidate
    # Prefer circles in corners (coin is usually placed in a corner)
    best = None
    best_score = -1

    for (cx, cy, r) in circles:
        # Score: prefer smaller circles (coin is small) and corner placement
        corner_score = min(cx, w - cx) + min(cy, h - cy)
        # Lower corner_score = closer to corner = better
        score = 1.0 / (corner_score + 1) + 1.0 / (r + 1)
        if score > best_score:
            best_score = score
            best = (cx, cy, r)

    return best


def pixels_per_mm(coin_radius_px: int) -> float:
    """Convert coin pixel radius to pixels-per-mm scale factor."""
    coin_diameter_px = coin_radius_px * 2
    return coin_diameter_px / COIN_REAL_DIAMETER_MM


def estimate_product_real_diameter_mm(
    product_mask: np.ndarray,
    ppm: float,
) -> float:
    """
    Given a binary product mask and pixels-per-mm scale,
    estimate the product's real diameter in mm.

    Uses the equivalent circle diameter of the mask area.
    """
    area_px = cv2.countNonZero(product_mask)
    if area_px < 10:
        return 0.0

    # Equivalent circle diameter from area
    radius_px = np.sqrt(area_px / np.pi)
    diameter_px = radius_px * 2
    return diameter_px / ppm


def estimate_from_bbox(
    bbox_w_px: int,
    bbox_h_px: int,
    ppm: float,
) -> Tuple[float, float]:
    """
    Estimate real width and height in mm from bounding box pixels.
    Returns (width_mm, height_mm).
    """
    return bbox_w_px / ppm, bbox_h_px / ppm


def real_size_gate(
    query_diameter_mm: float,
    registered_diameter_mm: float,
    tolerance_mm: float = SIZE_MATCH_TOLERANCE_MM,
) -> bool:
    """
    Returns True if sizes are close enough to be the same product.
    Returns False if sizes differ too much (different size variant).

    Example:
        Vaseline 20gm: ~45mm diameter
        Vaseline 45gm: ~60mm diameter
        Difference: 15mm >> 8mm tolerance → BLOCKED ✓
    """
    if registered_diameter_mm < 1.0 or query_diameter_mm < 1.0:
        return True  # no data, don't block
    diff = abs(query_diameter_mm - registered_diameter_mm)
    return diff <= tolerance_mm


def draw_coin_overlay(frame: np.ndarray, coin: Tuple[int, int, int]) -> np.ndarray:
    """Draw coin detection overlay on frame for visual feedback."""
    cx, cy, r = coin
    cv2.circle(frame, (cx, cy), r, (0, 255, 255), 2)
    cv2.circle(frame, (cx, cy), 3, (0, 255, 255), -1)
    cv2.putText(frame, "REF COIN", (cx - 35, cy - r - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    return frame
