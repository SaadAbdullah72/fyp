import cv2
import numpy as np

class KumarArtefactFilter:
    """
    Kumar et al. (2018) Low-Pass & Artefact Suppression Preprocessor.
    Ref: Section 4 - "Pre-processed using the low pass filtering technique to remove
    the noises and other artefacts from the captured muzzle point image database."
    
    Eliminates camera sensor grain, high-frequency motion artifacts, and sweat specularities
    while maintaining immutable ridge structures and pore grooves.
    """
    def __init__(self, filter_strength: int = 5, clip_limit: float = 2.5):
        self.filter_strength = filter_strength
        self.clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))

    def suppress_sweat_glare(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Suppresses specular highlight artifacts caused by natural muzzle moisture or camera flash.
        """
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        # Identify extreme saturated specular highlights
        _, glare_mask = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY)
        if np.count_nonzero(glare_mask) > 0:
            # Dilate slightly and inpaint glare using Navier-Stokes based inpainting
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            glare_mask = cv2.dilate(glare_mask, kernel, iterations=1)
            inpainted = cv2.inpaint(img_bgr, glare_mask, 3, cv2.INPAINT_NS)
            return inpainted
        return img_bgr

    def apply_low_pass_edge_preserving(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Low-pass filter that suppresses high-frequency camera noise and blur artifacts
        while strictly preserving bead groove boundaries (Bilateral Formulation).
        """
        d = self.filter_strength
        # sigmaColor controls how much neighboring pixel values are mixed
        # sigmaSpace controls the spatial neighborhood size
        filtered = cv2.bilateralFilter(img_bgr, d=d, sigmaColor=35, sigmaSpace=35)
        return filtered

    def filter_and_enhance(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Complete Kumar Artefact Pipeline:
        1. Specular sweat/moisture glare suppression.
        2. Bilateral low-pass artifact removal.
        3. LAB CLAHE ridge enhancement without amplifying noise.
        """
        # Step 1: Suppress extreme glare specularities
        no_glare = self.suppress_sweat_glare(img_bgr)

        # Step 2: Low-pass filter for artifact and noise suppression
        low_pass = self.apply_low_pass_edge_preserving(no_glare)

        # Step 3: Enhance ridge micro-texture in LAB luminance space
        lab = cv2.cvtColor(low_pass, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        enhanced_l = self.clahe.apply(l)
        enhanced_lab = cv2.merge((enhanced_l, a, b))
        output_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

        return output_bgr
