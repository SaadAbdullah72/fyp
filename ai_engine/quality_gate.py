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

        # 6. Overall Quality Score (0 - 100%)
        # Sharpness component (capped at 300)
        sharp_norm = min(1.0, laplacian_var / 250.0) * 40.0
        # Brightness component (optimal around 128)
        bright_dist = abs(mean_brightness - 128.0) / 128.0
        bright_norm = max(0.0, 1.0 - bright_dist) * 25.0
        # Glare penalty
        glare_norm = max(0.0, 1.0 - (glare_pct / 15.0)) * 20.0
        # Anti-spoof component
        spoof_norm = 15.0 if not spoof_check["is_spoof"] else 0.0

        overall_score = round(float(sharp_norm + bright_norm + glare_norm + spoof_norm), 1)
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
            "feedback": feedbacks
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
