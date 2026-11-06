import cv2
import numpy as np

class MuzzleLBPDescriptor:
    """
    Local Binary Pattern (LBP) Dermatoglyphic Micro-Texture Descriptor.
    Ref: Kumar et al. (2018) Section 7 Benchmark on Handcrafted Texture Descriptors.
    
    Extracts invariant micro-ridge groove histograms across spatial blocks
    to provide an orthogonal verification signal alongside deep CNN features.
    """
    def __init__(self, grid_x: int = 4, grid_y: int = 4, num_bins: int = 16):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.num_bins = num_bins
        self.output_dim = grid_x * grid_y * num_bins  # 4 * 4 * 16 = 256-D

    def compute_lbp(self, gray: np.ndarray) -> np.ndarray:
        """
        Fast vectorized 8-neighbor basic LBP transform.
        """
        h, w = gray.shape
        # Pad with replicate border to keep same shape
        padded = cv2.copyMakeBorder(gray, 1, 1, 1, 1, cv2.BORDER_REPLICATE)
        center = padded[1:-1, 1:-1]

        # 8 neighbors
        n0 = padded[1:-1, 2:] >= center
        n1 = padded[:-2, 2:] >= center
        n2 = padded[:-2, 1:-1] >= center
        n3 = padded[:-2, :-2] >= center
        n4 = padded[1:-1, :-2] >= center
        n5 = padded[2:, :-2] >= center
        n6 = padded[2:, 1:-1] >= center
        n7 = padded[2:, 2:] >= center

        lbp = (n0 << 7) | (n1 << 6) | (n2 << 5) | (n3 << 4) | (n4 << 3) | (n5 << 2) | (n6 << 1) | n7
        return lbp.astype(np.uint8)

    def extract_descriptor(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Extracts spatially-pooled, L2-normalized 256-D LBP histogram.
        """
        if len(img_bgr.shape) == 3:
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_bgr

        # Resize to fixed standard for texture alignment (e.g. 128x128)
        gray = cv2.resize(gray, (128, 128), interpolation=cv2.INTER_AREA)
        lbp_map = self.compute_lbp(gray)

        h, w = lbp_map.shape
        cell_h = h // self.grid_y
        cell_w = w // self.grid_x

        histograms = []
        for i in range(self.grid_y):
            for j in range(self.grid_x):
                cell = lbp_map[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
                # Quantize 256 LBP values into num_bins (16 bins)
                hist, _ = np.histogram(cell, bins=self.num_bins, range=(0, 256))
                # L1 normalize per cell
                cell_norm = np.linalg.norm(hist) + 1e-7
                histograms.extend((hist / cell_norm).tolist())

        descriptor = np.array(histograms, dtype=np.float32)
        # Global L2 normalize
        total_norm = np.linalg.norm(descriptor)
        if total_norm > 0:
            descriptor = descriptor / total_norm

        return descriptor

    def compute_similarity(self, desc1: np.ndarray, desc2: np.ndarray) -> float:
        """
        Histogram intersection / cosine similarity between two LBP texture descriptors.
        """
        return float(np.dot(desc1, desc2))
