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
        Muzzle close-ups typically have an aspect ratio near 1:1 (0.7 to 1.4)
        and dark/textured central distribution rather than whole animal body.
        """
        h, w = image.shape[:2]
        aspect = w / float(h) if h > 0 else 1.0
        
        # If aspect ratio is square-ish (0.70 - 1.40)
        if 0.70 <= aspect <= 1.40:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            center_roi = gray[int(h*0.20):int(h*0.80), int(w*0.20):int(w*0.80)]
            if center_roi.std() > 15:
                return True
        return False

    def extract_clean_muzzle_roi(self, image: np.ndarray) -> np.ndarray:
        """
        Anatomical Planum Nasolabiale Extractor:
        Locates the bilateral nostrils and tightly crops the central ridge print plate,
        ignoring peripheral non-biometric noise (mouth lip, tongue, chin, forehead, background).
        """
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        smooth = cv2.bilateralFilter(gray, 9, 75, 75)

        search_roi = smooth[:int(h * 0.80), :]
        mean_val = float(np.mean(search_roi))
        thresh = max(18, int(mean_val * 0.45))
        _, mask = cv2.threshold(search_roi, thresh, 255, cv2.THRESH_BINARY_INV)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_a = (h * w) * 0.007
        max_a = (h * w) * 0.18

        left_cands = []
        right_cands = []
        center_x = w // 2

        for c in cnts:
            a = cv2.contourArea(c)
            if min_a < a < max_a:
                x, y, bw, bh = cv2.boundingRect(c)
                cx = x + bw // 2
                cy = y + bh // 2
                cand = {'x': x, 'y': y, 'w': bw, 'h': bh, 'cx': cx, 'cy': cy, 'area': a}
                if cx < center_x:
                    left_cands.append(cand)
                else:
                    right_cands.append(cand)

        if left_cands and right_cands:
            left = max(left_cands, key=lambda i: i['area'])
            right = max(right_cands, key=lambda i: i['area'])
            d = right['cx'] - left['cx']
            if d > w * 0.15:
                # Isolate the Planum Nasolabiale:
                # Top: slightly above nostrils
                # Bottom: right below the main ridge plate (cuts off mouth, tongue, chin)
                # Left/Right: tightly bounded by nostril wings (cuts off cheek/background)
                x1 = max(0, int(left['cx'] - 0.35 * d))
                x2 = min(w, int(right['cx'] + 0.35 * d))
                y1 = max(0, int(min(left['cy'], right['cy']) - 0.25 * d))
                y2 = min(h, int(max(left['cy'], right['cy']) + 1.25 * d))

                roi = image[y1:y2, x1:x2]
                if roi.shape[0] >= 64 and roi.shape[1] >= 64:
                    return roi

        return image

    def detect_and_crop(self, image_input, save_crop_path: str = None) -> np.ndarray:
        """
        Detects cattle muzzle region in raw field images.
        If already a close-up crop or no whole body detected, isolates the clean muzzle ROI.
        """
        if isinstance(image_input, str):
            image = cv2.imread(image_input)
            if image is None:
                raise ValueError(f"Could not load image: {image_input}")
        else:
            image = image_input.copy()

        h, w, _ = image.shape

        # 1. If already a square-ish close-up muzzle, isolate the clean ridge ROI and return
        if self.is_already_cropped_muzzle(image):
            clean_roi = self.extract_clean_muzzle_roi(image)
            return clean_roi

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
                    # Only crop if detected animal is not already filling the entire frame
                    if box_w < w * 0.90 or box_h < h * 0.90:
                        muzzle_y1 = max(0, int(y1 + box_h * 0.45))
                        muzzle_y2 = min(h, y2)
                        muzzle_x1 = max(0, int(x1 + box_w * 0.15))
                        muzzle_x2 = min(w, int(x2 - box_w * 0.15))
                        detected_cow_box = [muzzle_x1, muzzle_y1, muzzle_x2, muzzle_y2]
                        break
            if detected_cow_box:
                break

        # 3. If a full cow was detected in a wide image, crop the muzzle and refine ROI
        if detected_cow_box:
            cx1, cy1, cx2, cy2 = detected_cow_box
            cropped = image[cy1:cy2, cx1:cx2]
            if cropped.shape[0] >= 64 and cropped.shape[1] >= 64:
                refined = self.extract_clean_muzzle_roi(cropped)
                if save_crop_path:
                    os.makedirs(os.path.dirname(os.path.abspath(save_crop_path)), exist_ok=True)
                    cv2.imwrite(save_crop_path, refined)
                return refined

        # 4. Fallback: try extracting clean ROI from full image
        clean_full = self.extract_clean_muzzle_roi(image)
        if save_crop_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_crop_path)), exist_ok=True)
            cv2.imwrite(save_crop_path, clean_full)

        return clean_full

if __name__ == "__main__":
    detector = LivestockMuzzleDetector()
    print("[*] Safe Livestock Muzzle Detector ready!")
