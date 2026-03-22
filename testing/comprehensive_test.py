"""
VisionCart Comprehensive Testing Suite
Professional testing with detailed metrics and report generation
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

class ComprehensiveTester:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔧 Device: {self.device.upper()}")
        
        # Load models
        print("📦 Loading AI models...")
        self.yolo_model = YOLO("yolo11x-seg.pt")
        
        # Load database
        self.product_ids, self.db_embeddings, self.prices, self.stocks = load_database()
        print(f"✅ Loaded {len(self.product_ids)} products from database")
        
        # Initialize booster
        self.booster = AccuracyBooster(history_size=5, emb_history_size=3)
        
        # DINO transform
        self.dino_transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Test results storage
        self.test_results = {
            'detection_accuracy': {},
            'recognition_accuracy': {},
            'performance_metrics': {},
            'stress_test_results': {},
            'error_handling': {}
        }
    
    def test_scenario_1_correct_product(self, product_name, attempts=20):
        """
        Scenario 1: Correct Product Recognition
        Expected: Product should be recognized correctly
        """
        print(f"\n{'='*60}")
        print(f"📋 SCENARIO 1: Correct Product Recognition")
        print(f"Product: {product_name}")
        print(f"Attempts: {attempts}")
        print(f"{'='*60}")
        
        cap = cv2.VideoCapture(2)  # iVCam
        if not cap.isOpened():
            return {'error': 'Camera not available'}
        
        correct = 0
        detected = 0
        detection_times = []
        confidence_scores = []
        
        for i in range(attempts):
            print(f"\n🔍 Attempt {i+1}/{attempts} - Press SPACE to capture...")
            
            captured = False
            while not captured:
                ret, frame = cap.read()
                if not ret:
                    break
                
                display = frame.copy()
                cv2.putText(display, f"Test: {product_name} | {i+1}/{attempts}", 
                            (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(display, "Press SPACE to capture | ESC to skip", 
                            (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(display, f"Correct: {correct}/{detected}", 
                            (20, display.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow("Comprehensive Test", display)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 32:  # SPACE
                    captured = True
                    test_frame = frame.copy()
                elif key == 27:  # ESC
                    cap.release()
                    cv2.destroyAllWindows()
                    return self._calculate_results(correct, detected, detection_times, confidence_scores)
            
            # Process frame
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
                            final_crop = self.booster.brightness_normalize(final_crop)
                            pil_crop = Image.fromarray(cv2.cvtColor(final_crop, cv2.COLOR_BGR2RGB))
                            
                            clip_emb = get_clip_embedding(pil_crop, clip_loader.model, clip_loader.preprocess, self.device)
                            dino_tensor = self.dino_transform(pil_crop).unsqueeze(0)
                            dino_emb = get_dino_embedding(dino_tensor, dino_loader.dino, self.device)
                            query_emb = fuse_embeddings(clip_emb, dino_emb)
                            
                            idx, score, is_known, top_k_labels = top_k_matching(
                                query_emb, self.db_embeddings, self.product_ids, k=3, threshold=0.85
                            )
                            
                            detection_time = (time.time() - start_time) * 1000
                            detection_times.append(detection_time)
                            
                            if is_known:
                                detected += 1
                                detected_product = self.product_ids[idx]
                                confidence_scores.append(score)
                                
                                if detected_product == product_name:
                                    correct += 1
                                    print(f"✅ CORRECT: {detected_product} (Score: {score:.3f}, Time: {detection_time:.1f}ms)")
                                else:
                                    print(f"❌ WRONG: Got '{detected_product}' instead of '{product_name}' (Score: {score:.3f})")
                            else:
                                print(f"⚠️ UNKNOWN (Score: {score:.3f})")
                        else:
                            print(f"⚠️ Invalid: {reason}")
                else:
                    print(f"⚠️ No detection")
            
            except Exception as e:
                print(f"❌ Error: {e}")
        
        cap.release()
        cv2.destroyAllWindows()
        
        return self._calculate_results(correct, detected, detection_times, confidence_scores)
    
    def _calculate_results(self, correct, detected, times, scores):
        """Calculate test results"""
        detection_rate = (detected / 20 * 100) if detected > 0 else 0
        recognition_accuracy = (correct / detected * 100) if detected > 0 else 0
        avg_time = np.mean(times) if len(times) > 0 else 0
        avg_confidence = np.mean(scores) if len(scores) > 0 else 0
        
        return {
            'correct': correct,
            'detected': detected,
            'attempts': 20,
            'detection_rate': detection_rate,
            'recognition_accuracy': recognition_accuracy,
            'avg_detection_time': avg_time,
            'avg_confidence': avg_confidence
        }

    
    def generate_professional_report(self):
        """Generate professional testing report"""
        report = {
            'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'system_info': {
                'device': self.device,
                'products_in_database': len(self.product_ids),
                'ai_models': ['YOLO11x-seg', 'CLIP ViT-B/32', 'DINOv2 ViT-B/14']
            },
            'test_results': self.test_results,
            'summary': {}
        }
        
        # Calculate overall metrics
        all_correct = sum([r['correct'] for r in self.test_results['recognition_accuracy'].values()])
        all_detected = sum([r['detected'] for r in self.test_results['recognition_accuracy'].values()])
        all_attempts = sum([r['attempts'] for r in self.test_results['recognition_accuracy'].values()])
        
        report['summary'] = {
            'overall_detection_rate': (all_detected / all_attempts * 100) if all_attempts > 0 else 0,
            'overall_recognition_accuracy': (all_correct / all_detected * 100) if all_detected > 0 else 0,
            'end_to_end_accuracy': (all_correct / all_attempts * 100) if all_attempts > 0 else 0
        }
        
        # Save report
        with open('testing/comprehensive_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print report
        self._print_report(report)
        
        return report
    
    def _print_report(self, report):
        """Print formatted report"""
        print("\n" + "="*70)
        print("🎯 VISIONCART COMPREHENSIVE TEST REPORT")
        print("="*70)
        print(f"📅 Date: {report['test_date']}")
        print(f"🔧 Device: {report['system_info']['device'].upper()}")
        print(f"📦 Products Tested: {report['system_info']['products_in_database']}")
        print("="*70)
        
        print("\n📊 PER-PRODUCT RESULTS:")
        print("-"*70)
        print(f"{'Product':<20} {'Attempts':<10} {'Detected':<10} {'Correct':<10} {'Accuracy':<10}")
        print("-"*70)
        
        for product, data in report['test_results']['recognition_accuracy'].items():
            print(f"{product:<20} {data['attempts']:<10} {data['detected']:<10} {data['correct']:<10} {data['recognition_accuracy']:.1f}%")
        
        print("-"*70)
        
        print("\n🎯 OVERALL SYSTEM PERFORMANCE:")
        print("-"*70)
        summary = report['summary']
        print(f"Detection Rate:          {summary['overall_detection_rate']:.2f}%")
        print(f"Recognition Accuracy:    {summary['overall_recognition_accuracy']:.2f}%")
        print(f"End-to-End Accuracy:     {summary['end_to_end_accuracy']:.2f}%")
        print("-"*70)
        
        print("\n✅ Report saved: testing/comprehensive_report.json")
        print("="*70)

def main():
    print("="*70)
    print("🚀 VISIONCART COMPREHENSIVE TESTING SUITE")
    print("="*70)
    print("\nThis will run professional-grade tests:")
    print("  ✅ Scenario 1: Correct Product Recognition")
    print("  ✅ Detection Rate Measurement")
    print("  ✅ Recognition Accuracy Calculation")
    print("  ✅ Performance Metrics Collection")
    print("  ✅ Professional Report Generation")
    print("="*70 + "\n")
    
    tester = ComprehensiveTester()
    
    print("\n📋 Products in Database:")
    for i, pid in enumerate(tester.product_ids, 1):
        print(f"  {i}. {pid}")
    
    print("\n" + "="*70)
    input("Press ENTER to start testing...")
    
    # Test each product
    for product in tester.product_ids:
        results = tester.test_scenario_1_correct_product(product, attempts=20)
        tester.test_results['recognition_accuracy'][product] = results
        
        print(f"\n✅ {product} testing completed!")
        print(f"   Detection Rate: {results['detection_rate']:.1f}%")
        print(f"   Recognition Accuracy: {results['recognition_accuracy']:.1f}%")
        print(f"   Avg Time: {results['avg_detection_time']:.1f}ms")
        
        cont = input("\nContinue to next product? (y/n): ")
        if cont.lower() != 'y':
            break
    
    # Generate report
    tester.generate_professional_report()
    
    print("\n🎉 TESTING COMPLETED!")
    print("="*70)

if __name__ == "__main__":
    main()
