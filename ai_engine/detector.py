import cv2
import numpy as np
from ultralytics import YOLO
import os

class LivestockMuzzleDetector:
    """
    Automated Livestock Muzzle/Nose Detector using YOLO.
    Locates the cattle muzzle in raw field images and crops it for ArcFace biometrics.
    """
    def __init__(self, model_weights: str = "yolov8n.pt"):
        print(f"[*] Initializing YOLO Muzzle Detector with: {model_weights}")
        self.model = YOLO(model_weights)

    def detect_and_crop(self, image_input, save_crop_path: str = None) -> np.ndarray:
        """
        Detects cow/livestock face and crops the lower third (muzzle region).
        Returns cropped BGR numpy image.
        """
        if isinstance(image_input, str):
            image = cv2.imread(image_input)
            if image is None:
                raise ValueError(f"Could not load image: {image_input}")
        else:
            image = image_input.copy()

        h, w, _ = image.shape

        # Run inference
        results = self.model(image, verbose=False)
        
        # Default fallback crop: center-focused lower region
        crop_box = [int(w * 0.25), int(h * 0.35), int(w * 0.75), int(h * 0.85)]

        # Check if animal/cow detected in YOLO standard classes (19: cow, 18: sheep, etc.)
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0].item())
                # If cow/sheep/horse detected
                if cls_id in [19, 18, 17]:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    box_h = y2 - y1
                    # Muzzle is typically situated in the lower 45% of the head/body bbox
                    muzzle_y1 = int(y1 + box_h * 0.50)
                    muzzle_y2 = y2
                    muzzle_x1 = int(x1 + (x2 - x1) * 0.15)
                    muzzle_x2 = int(x2 - (x2 - x1) * 0.15)
                    crop_box = [muzzle_x1, muzzle_y1, muzzle_x2, muzzle_y2]
                    break

        cx1, cy1, cx2, cy2 = crop_box
        # Ensure valid bounds
        cx1, cy1 = max(0, cx1), max(0, cy1)
        cx2, cy2 = min(w, cx2), min(h, cy2)

        cropped_muzzle = image[cy1:cy2, cx1:cx2]

        if save_crop_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_crop_path)), exist_ok=True)
            cv2.imwrite(save_crop_path, cropped_muzzle)
            print(f"[*] Cropped muzzle saved to: {save_crop_path}")

        return cropped_muzzle

if __name__ == "__main__":
    detector = LivestockMuzzleDetector()
    print("[*] YOLO Muzzle Detector ready!")
