import cv2
import numpy as np

def apply_segmentation_mask(image, mask):
    """
    image: original BGR image
    mask: YOLO segmentation mask (H, W)
    Returns: (masked_image, binary_mask)
    """
    
    # Hard Threshold + Morphology
    binary_mask = (mask > 0.75).astype(np.uint8) * 255
    
    kernel = np.ones((5,5), np.uint8)
    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
    
    # Mask ko 3 channel me convert karo
    binary_mask_3ch = cv2.cvtColor(binary_mask, cv2.COLOR_GRAY2BGR)
    
    # Background remove
    masked_image = cv2.bitwise_and(image, binary_mask_3ch)
    
    return masked_image, binary_mask

def crop_to_mask(image, mask):
    """
    Tight crop around the mask using largest contour
    """
    # Hard Threshold + Morphology
    binary_mask = (mask > 0.75).astype(np.uint8) * 255
    
    kernel = np.ones((5,5), np.uint8)
    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
    
    # Largest Contour Crop
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) == 0:
        return image
    
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    
    final_crop = image[y:y+h, x:x+w]
    
    return final_crop


def fallback_crop_no_yolo(frame_bgr):
    """
    Fallback segmentation when YOLO detects nothing.
    Uses center-region assumption: product is roughly centered in frame.
    Applies GrabCut to isolate foreground, then crops to largest contour.
    Returns: (clean_img, binary_mask) or (None, None) if failed.
    """
    h, w = frame_bgr.shape[:2]

    # Define a rect covering the center 60% of the frame
    margin_x = int(w * 0.15)
    margin_y = int(h * 0.15)
    rect = (margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)

    mask_gc = np.zeros((h, w), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    try:
        cv2.grabCut(frame_bgr, mask_gc, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
    except Exception:
        return None, None

    # Foreground mask
    fg_mask = np.where((mask_gc == cv2.GC_FGD) | (mask_gc == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)

    kernel = np.ones((7, 7), np.uint8)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, None

    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    if area < 500:
        return None, None

    x, y, cw, ch = cv2.boundingRect(largest)
    clean_img = cv2.bitwise_and(frame_bgr, frame_bgr, mask=fg_mask)
    crop = clean_img[y:y+ch, x:x+cw]
    binary_mask = fg_mask[y:y+ch, x:x+cw]

    return crop, binary_mask
