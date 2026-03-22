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
