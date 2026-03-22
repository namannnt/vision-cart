"""
VisionCart Accuracy Testing Suite
Run automated tests and generate accuracy report
"""

import cv2
import torch
import numpy as np
from PIL import Image
from ultralytics import YOLO
from torchvision import transforms
import time
import json
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.clip import clip_loader
from models.dinov2 import dino_loader
from utils.clip_embedding import get_clip_embedding
from utils.dino_embedding import get_dino_embedding
from utils.embedding_fusion import fuse_embeddings
from utils.segmentation_crop import apply_segmentation_mask, crop_to_mask
from utils.validation import validate_detection
from utils.load_database import load_database
from utils.accuracy_boost import AccuracyBooster, top_k_matching

class AccuracyTester:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load models
        print("Loading models...")
        self.yolo_model = YOLO("yolo11x-seg.pt")
        
        # Load database
        self.product_ids, self.db_embeddings, self.prices, self.stocks = load_database()
        
        if len(self.product_ids) == 0:
            print("❌ No products in database!")
            exit()
        
        print(f"✅ Loaded {len(self.product_ids)} products")
        
        # Initialize booster
        self.booster = AccuracyBooster(history_size=5, emb_history_size=3)
        
        # DINO transform
        self.dino_transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Test results
        self.test_results = {}
    
    def test_product(self, product_name, num_attempts=20):
        """
        Test a specific product multiple times
        Returns: (correct_count, total_attempts, accuracy)
        """
        print(f"\n{'='*60}")
        print(f"Testing: {product_name}")
        print(f"{'='*60}")
        print(f"Attempts: {num_attempts}")
        print("Place the product in front of camera and press SPACE for each test")
        print("Press ESC to skip this product")
        print(f"{'='*60}\n")
        
        cap = cv2.VideoCapture(2)  # iVCam
        
        if not cap.isOpened():
            print("❌ Could not open camera")
            return 0, 0, 0.0
        
        correct = 0
        total = 0
        detection_times = []
        
        for attempt in range(num_attempts):
            print(f"\nAttempt {attempt + 1}/{num_attempts}")
            print("Press SPACE to capture...")
            
            captured = False
            
            while not captured:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                display = frame.copy()
                cv2.putText(display, f"Test: {product_name} | Attempt: {attempt+1}/{num_attempts}", 
                            (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display, "Press SPACE to capture | ESC to skip", 
                            (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(display, f"Correct: {correct}/{total}", 
                            (20, display.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow("Accuracy Test", display)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == 32:  # SPACE
                    captured = True
                    test_frame = frame.copy()
                elif key == 27:  # ESC
                    cap.release()
                    cv2.destroyAllWindows()
                    return correct, total, (correct/total*100 if total > 0 else 0)
            
            # Process captured frame
            start_time = time.time()
            
            try:
                results = self.yolo_model(test_frame, conf=0.6, verbose=False)
                
                if results[0].masks is not None and len(results[0].masks) > 0:
                    mask = results[0].masks.data[0].cpu().numpy()
                    mask = cv2.resize(mask, (test_frame.shape[1], test_frame.shape[0]))
                    
                    clean_img, binary_mask = apply_segmentation_mask(test_frame, mask)
                    final_crop = crop_to_mask(clean_img, mask)
                    
                    if final_crop is not None and final_crop.size > 0:
                        is_valid, reason = validate_detection(results, test_frame, final_crop, binary_mask)
                        
                        if is_valid:
                            # Generate embedding
                            final_crop = self.booster.brightness_normalize(final_crop)
                            pil_crop = Image.fromarray(cv2.cvtColor(final_crop, cv2.COLOR_BGR2RGB))
                            
                            clip_emb = get_clip_embedding(pil_crop, clip_loader.model, clip_loader.preprocess, self.device)
                            dino_tensor = self.dino_transform(pil_crop).unsqueeze(0)
                            dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, self.device)
                            query_emb = fuse_embeddings(clip_emb, dino_emb)
                            
                            # Match
                            idx, score, is_known, top_k_labels = top_k_matching(
                                query_emb, self.db_embeddings, self.product_ids, k=3, threshold=0.85
                            )
                            
                            detection_time = (time.time() - start_time) * 1000  # ms
                            detection_times.append(detection_time)
                            
                            if is_known:
                                detected_product = self.product_ids[idx]
                                total += 1
                                
                                if detected_product == product_name:
                                    correct += 1
                                    print(f"✅ CORRECT: {detected_product} (Score: {score:.3f}, Time: {detection_time:.1f}ms)")
                                else:
                                    print(f"❌ WRONG: Detected '{detected_product}' instead of '{product_name}' (Score: {score:.3f})")
                            else:
                                total += 1
                                print(f"❌ UNKNOWN (Score: {score:.3f})")
                        else:
                            print(f"⚠️ Invalid detection: {reason}")
                else:
                    print(f"⚠️ No object detected")
            
            except Exception as e:
                print(f"❌ Error: {e}")
        
        cap.release()
        cv2.destroyAllWindows()
        
        accuracy = (correct / total * 100) if total > 0 else 0
        avg_time = np.mean(detection_times) if len(detection_times) > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"Results for {product_name}:")
        print(f"  Correct: {correct}/{total}")
        print(f"  Accuracy: {accuracy:.2f}%")
        print(f"  Avg Detection Time: {avg_time:.1f}ms")
        print(f"{'='*60}")
        
        return correct, total, accuracy, avg_time
    
    def generate_report(self):
        """Generate final accuracy report"""
        print("\n" + "="*60)
        print("VISIONCART ACCURACY REPORT")
        print("="*60)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Device: {self.device.upper()}")
        print(f"Products in Database: {len(self.product_ids)}")
        print("="*60)
        
        print("\nPer-Product Results:")
        print("-"*60)
        print(f"{'Product':<20} {'Attempts':<10} {'Correct':<10} {'Accuracy':<10}")
        print("-"*60)
        
        total_correct = 0
        total_attempts = 0
        
        for product, data in self.test_results.items():
            correct = data['correct']
            attempts = data['attempts']
            accuracy = data['accuracy']
            
            print(f"{product:<20} {attempts:<10} {correct:<10} {accuracy:.2f}%")
            
            total_correct += correct
            total_attempts += attempts
        
        overall_accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
        
        print("-"*60)
        print(f"{'OVERALL':<20} {total_attempts:<10} {total_correct:<10} {overall_accuracy:.2f}%")
        print("="*60)
        
        # Save report
        report = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'device': self.device,
            'products_tested': len(self.test_results),
            'total_attempts': total_attempts,
            'total_correct': total_correct,
            'overall_accuracy': overall_accuracy,
            'per_product': self.test_results
        }
        
        with open('testing/accuracy_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n✅ Report saved: testing/accuracy_report.json")
        
        return overall_accuracy

def main():
    print("="*60)
    print("VISIONCART ACCURACY TESTING SUITE")
    print("="*60)
    print("This will test each product multiple times")
    print("and generate an accuracy report")
    print("="*60 + "\n")
    
    tester = AccuracyTester()
    
    print("\nRegistered Products:")
    for i, pid in enumerate(tester.product_ids, 1):
        print(f"  {i}. {pid}")
    
    print("\n" + "="*60)
    input("Press ENTER to start testing...")
    
    # Test each product
    for product in tester.product_ids:
        correct, total, accuracy, avg_time = tester.test_product(product, num_attempts=20)
        
        tester.test_results[product] = {
            'correct': correct,
            'attempts': total,
            'accuracy': accuracy,
            'avg_time': avg_time
        }
        
        print(f"\n✅ {product} testing completed!")
        
        cont = input("\nContinue to next product? (y/n): ")
        if cont.lower() != 'y':
            break
    
    # Generate final report
    overall = tester.generate_report()
    
    print("\n" + "="*60)
    print("TESTING COMPLETED!")
    print(f"Overall System Accuracy: {overall:.2f}%")
    print("="*60)

if __name__ == "__main__":
    main()
