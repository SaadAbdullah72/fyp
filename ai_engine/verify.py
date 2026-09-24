import os
import argparse
import torch
import numpy as np
from PIL import Image
import torchvision.transforms as transforms

from utils.preprocess import MuzzlePreprocessor
from models.backbone import MuzzleBiometricNet
from utils.biometric_hasher import BiometricHasher

class MuzzleVerificationEngine:
    def __init__(self, weights_path: str = None, backbone: str = "resnet50", device: str = None):
        self.device = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))
        print(f"[*] Initializing Muzzle Verification Engine on: {self.device}")
        
        self.preprocessor = MuzzlePreprocessor(target_size=(224, 224))
        self.model = MuzzleBiometricNet(backbone_name=backbone, embedding_size=512, pretrained=True)
        
        if weights_path and os.path.exists(weights_path):
            print(f"[*] Loading fine-tuned weights from: {weights_path}")
            checkpoint = torch.load(weights_path, map_location=self.device)
            if "model_state_dict" in checkpoint:
                self.model.load_state_dict(checkpoint["model_state_dict"])
            else:
                self.model.load_state_dict(checkpoint)
        else:
            print("[!] Using ImageNet pretrained backbone (Fine-tuning recommended on cattle dataset)")

        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def extract_embedding(self, image_input) -> np.ndarray:
        """
        Processes image through CLAHE enhancement -> backbone -> 512-D normalized vector.
        """
        # 1. Preprocess & enhance ridges
        enhanced_bgr = self.preprocessor.preprocess_image(image_input)
        
        # 2. Convert to RGB PIL Image and apply PyTorch transform
        rgb_img = Image.fromarray(enhanced_bgr[:, :, ::-1])
        tensor = self.transform(rgb_img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            embedding = self.model(tensor)
            
        return embedding.squeeze(0).cpu().numpy()

    def compare_muzzles(self, image_path_1: str, image_path_2: str, threshold: float = 0.70) -> dict:
        """
        Compares two cattle muzzle images and determines if they belong to the same animal.
        """
        emb1 = self.extract_embedding(image_path_1)
        emb2 = self.extract_embedding(image_path_2)

        # Cosine similarity between two unit-normalized vectors: dot product
        cosine_sim = float(np.dot(emb1, emb2))
        
        # Angular distance in degrees: theta = arccos(cosine_sim) * 180 / pi
        clamped_sim = np.clip(cosine_sim, -1.0, 1.0)
        angular_distance_deg = float(np.degrees(np.arccos(clamped_sim)))

        is_match = cosine_sim >= threshold
        confidence_percent = max(0.0, min(100.0, (cosine_sim + 1.0) / 2.0 * 100.0))

        hash1 = BiometricHasher.generate_sha256_hash(emb1)
        hash2 = BiometricHasher.generate_sha256_hash(emb2)

        return {
            "is_same_animal": bool(is_match),
            "cosine_similarity": round(cosine_sim, 4),
            "angular_distance_deg": round(angular_distance_deg, 2),
            "match_confidence": f"{round(confidence_percent, 2)}%",
            "threshold_used": threshold,
            "image1_biometric_hash": hash1,
            "image2_biometric_hash": hash2
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Livestock Muzzle Biometric Verification")
    parser.add_argument("--img1", type=str, required=True, help="Path to first muzzle image")
    parser.add_argument("--img2", type=str, required=True, help="Path to second muzzle image")
    parser.add_argument("--threshold", type=float, default=0.70, help="Cosine similarity threshold (default: 0.70)")
    parser.add_argument("--weights", type=str, default=None, help="Path to fine-tuned ArcFace weights .pth")
    args = parser.parse_args()

    engine = MuzzleVerificationEngine(weights_path=args.weights)
    result = engine.compare_muzzles(args.img1, args.img2, threshold=args.threshold)
    
    print("\n" + "="*50)
    print("      LIVESTOCK BIOMETRIC VERIFICATION RESULT     ")
    print("="*50)
    print(f"Match Status:       {'[MATCH] SAME ANIMAL' if result['is_same_animal'] else '[MISMATCH] DIFFERENT ANIMALS'}")
    print(f"Cosine Similarity:  {result['cosine_similarity']} (Threshold: {result['threshold_used']})")
    print(f"Angular Distance:   {result['angular_distance_deg']}°")
    print(f"Confidence:         {result['match_confidence']}")
    print(f"Image 1 Hash:       {result['image1_biometric_hash']}")
    print(f"Image 2 Hash:       {result['image2_biometric_hash']}")
    print("="*50 + "\n")
