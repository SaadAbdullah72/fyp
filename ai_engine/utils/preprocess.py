import cv2
import numpy as np
from PIL import Image

class MuzzlePreprocessor:
    """
    Preprocessor for Livestock Muzzle (Nose Print) Images.
    Enhances ridge grooves, pores, and bead patterns using CLAHE
    and standardizes dimensions for ArcFace feature extraction.
    """
    def __init__(self, target_size=(224, 224), clip_limit=3.0, tile_grid_size=(8, 8)):
        self.target_size = target_size
        self.clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    def enhance_texture(self, image_bgr: np.ndarray) -> np.ndarray:
        """
        Applies CLAHE on the luminance channel (LAB color space)
        to make faint muzzle ridge patterns and pores distinct without blowing out highlights.
        """
        # Convert BGR to LAB color space
        lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        
        # Apply CLAHE to L-channel
        cl = self.clahe.apply(l_channel)
        
        # Merge channels back and convert to BGR
        limg = cv2.merge((cl, a_channel, b_channel))
        enhanced_bgr = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        return enhanced_bgr

    def preprocess_image(self, image_path_or_array) -> np.ndarray:
        """
        Loads, enhances, resizes, and normalizes an input muzzle image.
        Returns: Normalized BGR numpy array ready for PyTorch tensor conversion.
        """
        if isinstance(image_path_or_array, str):
            image = cv2.imread(image_path_or_array)
            if image is None:
                raise ValueError(f"Could not load image from {image_path_or_array}")
        elif isinstance(image_path_or_array, np.ndarray):
            image = image_path_or_array.copy()
        elif isinstance(image_path_or_array, Image.Image):
            image = cv2.cvtColor(np.array(image_path_or_array), cv2.COLOR_RGB2BGR)
        else:
            raise TypeError("Unsupported image format")

        # 1. Texture enhancement via CLAHE
        enhanced = self.enhance_texture(image)

        # 2. Resize to target dimension (e.g. 224x224) using Lanczos/Cubic interpolation
        resized = cv2.resize(enhanced, self.target_size, interpolation=cv2.INTER_CUBIC)

        return resized
