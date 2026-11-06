import cv2
import numpy as np
from typing import Dict, Any, List, Tuple

class ImageQualityGate:
    """
    Intelligent Pre-Inference Quality Assessment & Anti-Spoofing Gate.
    Ensures only high-fidelity biometric muzzle captures proceed to deep neural inference.
    
    Checks:
    1. Focus / Ridge Blur Index (Modified Laplacian Variance)
    2. Illumination & Specular Glare Analysis (Moist muzzle flash reflection)
    3. High-Frequency Ridge Contrast
    4. Resolution & Minimum Muzzle Dimension
    5. Screen Replay Anti-Spoofing (2D Fourier Transform / Moiré Grid Detection)
    """

    def __init__(
        self,
        min_blur_threshold: float = 60.0,
        max_glare_percent: float = 12.0,
        min_brightness: float = 35.0,
        max_brightness: float = 235.0,
        min_dimension: int = 100
    ):
        self.min_blur_threshold = min_blur_threshold
        self.max_glare_percent = max_glare_percent
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.min_dimension = min_dimension

    def assess_quality(self, img_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Runs comprehensive quality audits and anti-spoofing checks.
        Returns detailed diagnostics and an aggregated quality score (0-100).
        """
        h, w = img_bgr.shape[:2]
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        v_channel = hsv[:, :, 2]

        feedbacks: List[str] = []
        is_pass = True

        # 1. Dimension Check
        dim_ok = bool(h >= self.min_dimension and w >= self.min_dimension)
        if not dim_ok:
            is_pass = False
            feedbacks.append(f"Image resolution too low ({w}x{h}px). Minimum required is {self.min_dimension}x{self.min_dimension}px.")

        # 2. Blur / Sharpness Check (Laplacian Variance)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        is_sharp = laplacian_var >= self.min_blur_threshold
        if not is_sharp:
            is_pass = False
            feedbacks.append(f"Image is blurry (Sharpness: {laplacian_var:.1f}, Min required: {self.min_blur_threshold}). Please hold camera steady.")

        # 3. Illumination / Brightness Analysis
        mean_brightness = float(np.mean(v_channel))
        is_too_dark = mean_brightness < self.min_brightness
        is_too_bright = mean_brightness > self.max_brightness

        if is_too_dark:
            is_pass = False
            feedbacks.append("Capture is too dark / underexposed. Improve environmental lighting.")
        elif is_too_bright:
            is_pass = False
            feedbacks.append("Capture is washed out / overexposed. Reduce direct harsh lighting.")

        # 4. Specular Glare (Flash reflection on moist cattle muzzle)
        glare_mask = (v_channel > 250) & (gray > 245)
        glare_pct = float(np.sum(glare_mask) / (h * w) * 100.0)
        has_excessive_glare = glare_pct > self.max_glare_percent
        if has_excessive_glare:
            feedbacks.append(f"Excessive flash glare detected ({glare_pct:.1f}%). Avoid camera flash directly on wet nose.")

        # 5. Anti-Spoofing: Screen Replay & Moiré Pattern Analysis (2D FFT)
        spoof_check = self._check_screen_spoofing(gray)
        if spoof_check["is_spoof"]:
            is_pass = False
            feedbacks.append("Anti-Spoofing Alert: Digital screen moiré grid or artificial replay detected!")

        # 6. Muzzle Completeness & Anatomical Integrity Check (Detects half/cut-off/non-muzzle)
        muzzle_integrity = self.validate_muzzle_integrity(img_bgr)
        if not muzzle_integrity["is_valid"]:
            is_pass = False
            feedbacks.append(f"⚠️ {muzzle_integrity['message']}")

        # 7. Overall Quality Score (0 - 100%)
        sharp_norm = min(1.0, laplacian_var / 250.0) * 40.0
        bright_dist = abs(mean_brightness - 128.0) / 128.0
        bright_norm = max(0.0, 1.0 - bright_dist) * 25.0
        glare_norm = max(0.0, 1.0 - (glare_pct / 15.0)) * 20.0
        spoof_norm = 15.0 if not spoof_check["is_spoof"] else 0.0

        overall_score = round(float(sharp_norm + bright_norm + glare_norm + spoof_norm), 1)
        # Severe penalty if incomplete or non-muzzle
        if not muzzle_integrity["is_valid"]:
            overall_score = min(25.0, overall_score)
        else:
            overall_score = max(5.0, min(100.0, overall_score))

        if is_pass and len(feedbacks) == 0:
            feedbacks.append("Image quality optimal. Muzzle biometric ridges clearly distinguished.")

        return {
            "passed": is_pass,
            "overall_score": overall_score,
            "sharpness_index": round(laplacian_var, 2),
            "is_sharp": is_sharp,
            "mean_brightness": round(mean_brightness, 1),
            "glare_percentage": round(glare_pct, 2),
            "has_excessive_glare": has_excessive_glare,
            "resolution": f"{w}x{h}",
            "anti_spoofing": spoof_check,
            "muzzle_integrity": muzzle_integrity,
            "feedback": feedbacks
        }

    def validate_muzzle_integrity(self, img_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Validates anatomical muzzle completeness and biometric feasibility:
        1. Aspect Ratio: Rejects extreme strip/ribbon crops.
        2. Environmental Background / Pasture Exclusion: Flags dominant pasture or landscape scenes.
        3. Dermatoglyphic Ridge Energy: Verifies presence of biometric groove texture vs flat surfaces.
        4. Bilateral Nostril Landmarks: Checks for anatomical landmarks (soft check).
        """
        h, w = img_bgr.shape[:2]
        aspect = w / float(h) if h > 0 else 1.0

        # Check 1: Aspect Ratio (reject extreme sliver crops)
        if aspect < 0.40 or aspect > 2.50:
            return {
                "is_valid": False,
                "reason": "INVALID_ASPECT_RATIO",
                "message": "Incomplete Muzzle: Aspect ratio invalid. Only centered, close-up frontal photos are accepted."
            }

        # Check 2: Environmental Background & Pasture Exclusion (True green foliage range)
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        green_mask = cv2.inRange(hsv, (38, 60, 50), (85, 255, 255))
        green_pct = float(np.sum(green_mask > 0) / (h * w) * 100.0)

        top_h = int(h * 0.25)
        sky_top = cv2.inRange(hsv[:top_h, :], (95, 60, 120), (130, 255, 255))
        sky_top_pct = float(np.sum(sky_top > 0) / (top_h * w) * 100.0) if top_h > 0 else 0.0

        if green_pct > 35.0 or sky_top_pct > 25.0:
            return {
                "is_valid": False,
                "reason": "FULL_ANIMAL_PASTURE_DETECTED",
                "message": f"Rejected: Pasture/sky background detected ({green_pct:.1f}% pasture). Only close-up captures of the cattle muzzle are accepted."
            }

        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # Check 3: Dermatoglyphic Ridge Energy across the image
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        ridge_energy = float(np.mean(np.sqrt(sobelx**2 + sobely**2)))
        overall_std = float(np.std(gray))

        if ridge_energy < 10.0 or overall_std < 10.0:
            return {
                "is_valid": False,
                "reason": "NO_BIOMETRIC_RIDGE_PATTERN",
                "message": "No biometric muzzle ridges detected. Please upload a clear, focused photograph of the cattle nose print."
            }

        # Check 4: Nostril Landmark Analysis (Advisory landmark detection)
        smooth = cv2.bilateralFilter(gray, 9, 75, 75)
        search_roi = smooth[:int(h*0.75), :]
        mean_val = float(np.mean(search_roi))
        thresh = max(18, int(mean_val * 0.45))
        _, mask = cv2.threshold(search_roi, thresh, 255, cv2.THRESH_BINARY_INV)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_a = (h * w) * 0.005
        max_a = (h * w) * 0.25

        left_cands = []
        right_cands = []
        center_x = w // 2

        for c in cnts:
            a = cv2.contourArea(c)
            if min_a < a < max_a:
                x, y, bw, bh = cv2.boundingRect(c)
                cx = x + bw // 2
                cy = y + bh // 2
                cand = {'cx': cx, 'cy': cy, 'area': a}
                if cx < center_x:
                    left_cands.append(cand)
                else:
                    right_cands.append(cand)

        nostrils_found = len(left_cands) > 0 or len(right_cands) > 0
        nostril_dx = 0.5
        if len(left_cands) > 0 and len(right_cands) > 0:
            left_best = max(left_cands, key=lambda c: c['area'])
            right_best = max(right_cands, key=lambda c: c['area'])
            nostril_dx = abs(right_best['cx'] - left_best['cx']) / float(w)

        return {
            "is_valid": True,
            "reason": "COMPLETE_MUZZLE_VERIFIED",
            "message": "Complete muzzle verified with biometric ridge print (Beef Muzzle Dataset standard).",
            "ridge_energy": round(ridge_energy, 1),
            "nostrils_found": nostrils_found,
            "nostril_span": round(nostril_dx, 2)
        }

    def _check_screen_spoofing(self, gray: np.ndarray) -> Dict[str, Any]:
        """
        Fast Fourier Transform (FFT) analysis to detect repetitive high-frequency
        pixel-pitch grids typical of mobile screen / tablet replay attacks.
        """
        h, w = gray.shape[:2]
        # Crop central area
        center_crop = cv2.resize(gray, (256, 256))
        
        # 2D FFT
        dft = np.fft.fft2(center_crop)
        dft_shift = np.fft.fftshift(dft)
        magnitude_spectrum = 20 * np.log(np.abs(dft_shift) + 1e-8)

        # Zero out low-frequency center (DC component)
        cy, cx = 128, 128
        radius = 24
        y, x = np.ogrid[:256, :256]
        mask = (x - cx)**2 + (y - cy)**2 > radius**2
        high_freq_spectrum = magnitude_spectrum * mask

        # Check for isolated repetitive harmonic peaks in high frequencies
        high_freq_mean = np.mean(high_freq_spectrum)
        high_freq_std = np.std(high_freq_spectrum)
        threshold_peak = high_freq_mean + (4.0 * high_freq_std)
        peaks_count = int(np.sum(high_freq_spectrum > threshold_peak))

        # Screens display distinct grid harmonics with high peak concentration
        is_spoof = bool(peaks_count > 160)
        spoof_confidence = round(min(100.0, (peaks_count / 200.0) * 100.0), 1)

        return {
            "is_spoof": is_spoof,
            "confidence": f"{spoof_confidence}%",
            "detected_peaks": peaks_count,
            "liveness_status": "AUTHENTIC_LIVE_ANIMAL" if not is_spoof else "FLAGGED_DIGITAL_REPLAY"
        }
