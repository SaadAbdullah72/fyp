import cv2
import numpy as np
from ultralytics import YOLO
import os

class LivestockMuzzleDetector:
    """
    Automated Livestock Muzzle/Nose Detector using YOLO & Adaptive Muzzle Anchoring.
    Locates the cattle muzzle in raw field images and safely crops it for ArcFace biometrics.
    Guarantees that pre-cropped close-up muzzle images are preserved without destructive chopping.
    """
    def __init__(self, model_weights: str = "yolov8n.pt"):
        print(f"[*] Initializing YOLO Muzzle Detector with: {model_weights}")
        self.model = YOLO(model_weights)

    def is_already_cropped_muzzle(self, image: np.ndarray) -> bool:
        """
        Determines whether the input image is already a close-up muzzle crop.
        Muzzle close-ups typically have an aspect ratio near square/portrait (0.55 to 1.75)
        and high ridge texture energy across the central area rather than a distant full cow body.
        """
        h, w = image.shape[:2]
        aspect = w / float(h) if h > 0 else 1.0
        
        # If aspect ratio is normal camera framing of cattle face/muzzle (0.55 - 1.75)
        if 0.55 <= aspect <= 1.75:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            center_roi = gray[int(h*0.20):int(h*0.80), int(w*0.20):int(w*0.80)]
            if center_roi.std() > 10:
                return True
        return False

    def detect_and_crop(self, image_input, save_crop_path: str = None) -> np.ndarray:
        """
        Detects cattle muzzle region in raw field images.
        If the image is already a close-up muzzle capture (such as dataset photos or close-up user uploads),
        it preserves the photo INTACT to guarantee that genuine ridge patterns and both nostrils are not chopped off.
        Only crops if a wide-angle scene with a small distant animal is detected.
        """
        if isinstance(image_input, str):
            image = cv2.imread(image_input)
            if image is None:
                raise ValueError(f"Could not load image: {image_input}")
        else:
            image = image_input.copy()

        h, w, _ = image.shape

        # 1. If already a close-up muzzle photo, PRESERVE IT INTACT!
        # Destructive re-cropping with thresholding strips genuine nostril/ridge anatomy.
        if self.is_already_cropped_muzzle(image):
            if save_crop_path:
                os.makedirs(os.path.dirname(os.path.abspath(save_crop_path)), exist_ok=True)
                cv2.imwrite(save_crop_path, image)
            return image

        # 2. Run YOLO inference to check for full cow in scene
        results = self.model(image, verbose=False)
        detected_cow_box = None

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                # If cow/sheep/horse detected with confidence >= 0.30
                if cls_id in [19, 18, 17] and conf >= 0.30:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    box_w = x2 - x1
                    box_h = y2 - y1
                    # Only crop if detected animal is small in the scene (distant animal)
                    if box_w < w * 0.85 and box_h < h * 0.85:
                        muzzle_y1 = max(0, int(y1 + box_h * 0.45))
                        muzzle_y2 = min(h, y2)
                        muzzle_x1 = max(0, int(x1 + box_w * 0.15))
                        muzzle_x2 = min(w, int(x2 - box_w * 0.15))
                        detected_cow_box = [muzzle_x1, muzzle_y1, muzzle_x2, muzzle_y2]
                        break
            if detected_cow_box:
                break

        # 3. If a full cow was detected in a wide image, crop the muzzle
        if detected_cow_box:
            cx1, cy1, cx2, cy2 = detected_cow_box
            cropped = image[cy1:cy2, cx1:cx2]
            if cropped.shape[0] >= 64 and cropped.shape[1] >= 64:
                if save_crop_path:
                    os.makedirs(os.path.dirname(os.path.abspath(save_crop_path)), exist_ok=True)
                    cv2.imwrite(save_crop_path, cropped)
                return cropped

        # 4. Fallback: preserve original image intact
        if save_crop_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_crop_path)), exist_ok=True)
            cv2.imwrite(save_crop_path, image)

        return image

if __name__ == "__main__":
    detector = LivestockMuzzleDetector()
    print("[*] Safe Livestock Muzzle Detector ready!")
