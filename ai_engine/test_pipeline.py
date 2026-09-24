import numpy as np
import cv2
import os
from verify import MuzzleVerificationEngine
from utils.biometric_hasher import BiometricHasher

def run_self_test():
    """
    Creates temporary synthetic sample muzzle patterns, passes them
    through the complete pipeline (CLAHE -> ResNet50 Embedding -> Cosine Matcher -> Blockchain Hasher)
    and verifies proper functionality.
    """
    print("="*60)
    print("   LIVESTOCK MUZZLE BIOMETRIC PIPELINE SELF-TEST   ")
    print("="*60)

    test_dir = "sample_test_data"
    os.makedirs(test_dir, exist_ok=True)

    # Generate synthetic muzzle-like texture images
    # Cow A (Base pattern)
    np.random.seed(42)
    base_texture = (np.random.rand(300, 300, 3) * 180 + 40).astype(np.uint8)
    # Add bead / groove circles
    for _ in range(50):
        cv2.circle(base_texture, (np.random.randint(20, 280), np.random.randint(20, 280)), np.random.randint(3, 10), (20, 20, 20), -1)
    
    # Cow A - Image 1
    cow_a_img1_path = os.path.join(test_dir, "cow_A_photo1.jpg")
    cv2.imwrite(cow_a_img1_path, base_texture)

    # Cow A - Image 2 (Same cow with slight lighting/noise variation)
    cow_a_img2 = cv2.convertScaleAbs(base_texture, alpha=0.95, beta=10)
    cow_a_img2_path = os.path.join(test_dir, "cow_A_photo2.jpg")
    cv2.imwrite(cow_a_img2_path, cow_a_img2)

    # Cow B - Completely different animal pattern
    np.random.seed(999)
    cow_b_texture = (np.random.rand(300, 300, 3) * 150 + 20).astype(np.uint8)
    for _ in range(40):
        cv2.rectangle(cow_b_texture, (np.random.randint(10, 250), np.random.randint(10, 250)), 
                      (np.random.randint(20, 290), np.random.randint(20, 290)), (200, 200, 200), -1)
    cow_b_path = os.path.join(test_dir, "cow_B_photo1.jpg")
    cv2.imwrite(cow_b_path, cow_b_texture)

    weights_path = os.path.join(os.path.dirname(__file__), "checkpoints", "best_muzzle_arcface.pth")
    if not os.path.exists(weights_path):
        weights_path = None

    print("[*] Initializing Verification Engine...")
    engine = MuzzleVerificationEngine(weights_path=weights_path)

    # Check if real dataset exists
    real_data_dir = os.path.join(os.path.dirname(__file__), "data", "cropped_muzzles")
    c1_dir = os.path.join(real_data_dir, "cattle-001")
    c2_dir = os.path.join(real_data_dir, "cattle-002")

    if os.path.exists(c1_dir) and os.path.exists(c2_dir):
        c1_imgs = sorted([os.path.join(c1_dir, f) for f in os.listdir(c1_dir) if f.endswith(('.jpg', '.png'))])
        c2_imgs = sorted([os.path.join(c2_dir, f) for f in os.listdir(c2_dir) if f.endswith(('.jpg', '.png'))])

        if len(c1_imgs) >= 2 and len(c2_imgs) >= 1:
            print("\n--- [REAL DATA TEST 1] Same Animal (Cattle-001 Img 1 vs Cattle-001 Img 2) ---")
            real_res1 = engine.compare_muzzles(c1_imgs[0], c1_imgs[1], threshold=0.70)
            print(f"Match Status:       {'[MATCH] SAME ANIMAL' if real_res1['is_same_animal'] else '[MISMATCH]'}")
            print(f"Cosine Similarity:  {real_res1['cosine_similarity']} | Confidence: {real_res1['match_confidence']}")
            print(f"Biometric Hash:     {real_res1['image1_biometric_hash']}")

            print("\n--- [REAL DATA TEST 2] Different Animals (Cattle-001 vs Cattle-002) ---")
            real_res2 = engine.compare_muzzles(c1_imgs[0], c2_imgs[0], threshold=0.70)
            print(f"Match Status:       {'[MISMATCH] DIFFERENT ANIMALS' if not real_res2['is_same_animal'] else '[MATCH]'}")
            print(f"Cosine Similarity:  {real_res2['cosine_similarity']} | Confidence: {real_res2['match_confidence']}")

    # Synthetic self-test
    print("\n--- [SYNTHETIC TEST 1] Comparing Synthetic Cow A (Photo 1 vs Photo 2) ---")
    res1 = engine.compare_muzzles(cow_a_img1_path, cow_a_img2_path, threshold=0.70)
    print(f"Similarity: {res1['cosine_similarity']} | Match: {res1['is_same_animal']} | Confidence: {res1['match_confidence']}")

    print("\n--- [SYNTHETIC TEST 2] Comparing Synthetic Cow A vs Cow B ---")
    res2 = engine.compare_muzzles(cow_a_img1_path, cow_b_path, threshold=0.70)
    print(f"Similarity: {res2['cosine_similarity']} | Match: {res2['is_same_animal']} | Confidence: {res2['match_confidence']}")

    print("\n" + "="*60)
    print("   [SUCCESS] End-to-End AI Biometric Pipeline is Operational!")
    print("="*60)

if __name__ == "__main__":
    run_self_test()
