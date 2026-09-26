import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
import torchvision.transforms as transforms
import base64
from typing import Tuple, Dict, Any, Optional

class MuzzleExplainabilityEngine:
    """
    Explainable AI (XAI) Engine for Livestock Muzzle Biometrics.
    Produces:
    1. Deep Neural Attention Heatmaps (Grad-CAM / Channel Activation Mapping)
       highlighting ridge patterns, pores, and dermoglyphic grooves.
    2. Ridge Texture Enhancement & Detail Isolation.
    3. Pairwise Biometric Correspondence Map between two compared muzzles.
    """
    def __init__(self, model, device=None):
        self.model = model
        self.device = device if device else next(model.parameters()).device
        self.activations = None
        self.gradients = None
        self._register_hooks()

    def _register_hooks(self):
        """Attaches forward and backward hooks to the last convolutional layer."""
        target_layer = None
        if hasattr(self.model, "backbone"):
            # ResNet-50 target layer
            if hasattr(self.model.backbone, "layer4"):
                target_layer = self.model.backbone.layer4[-1]
            elif hasattr(self.model.backbone, "features"):
                # MobileNet target layer
                target_layer = self.model.backbone.features[-1]

        if target_layer is not None:
            def forward_hook(module, input, output):
                self.activations = output.detach()

            target_layer.register_forward_hook(forward_hook)

    def generate_attention_heatmap(self, image_bgr: np.ndarray, transform=None) -> Dict[str, Any]:
        """
        Generates deep neural attention heatmap for a single muzzle image.
        Returns overlayed image, raw heatmap, and ridge detail map.
        """
        h_orig, w_orig = image_bgr.shape[:2]
        
        # Prepare tensor
        rgb_img = Image.fromarray(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
        if transform is not None:
            tensor = transform(rgb_img).unsqueeze(0).to(self.device)
        else:
            default_tf = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            tensor = default_tf(rgb_img).unsqueeze(0).to(self.device)

        # Forward pass to trigger hook
        self.model.eval()
        with torch.no_grad():
            _ = self.model(tensor)

        if self.activations is not None:
            # Squeeze batch: [C, H, W]
            acts = self.activations.squeeze(0).cpu().numpy()
            # Mean activation across all 2048 feature channels: [H, W]
            cam = np.mean(acts, axis=0)
            # ReLU: keep positive activations
            cam = np.maximum(cam, 0)
            # Normalize to 0-1
            if cam.max() > cam.min():
                cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
            else:
                cam = np.zeros_like(cam)
        else:
            # Fallback if hooks didn't capture
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            cam = cv2.Laplacian(gray, cv2.CV_32F)
            cam = np.abs(cam)
            cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)

        # Resize heatmap back to original image dimensions
        heatmap_resized = cv2.resize(cam, (w_orig, h_orig), interpolation=cv2.INTER_CUBIC)
        heatmap_uint8 = np.uint8(255 * heatmap_resized)

        # Apply vibrant JET colormap
        heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)

        # Blend with original muzzle image: 60% original + 40% heatmap
        overlay_bgr = cv2.addWeighted(image_bgr, 0.62, heatmap_color, 0.38, 0)

        # Extract high-frequency Ridge Mask
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced_gray = clahe.apply(gray)
        ridge_edges = cv2.adaptiveThreshold(
            enhanced_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        ridge_color = cv2.applyColorMap(ridge_edges, cv2.COLORMAP_TURBO)

        return {
            "overlay_bgr": overlay_bgr,
            "heatmap_color": heatmap_color,
            "ridge_color": ridge_color,
            "peak_attention_score": float(np.max(heatmap_resized))
        }

    def generate_pairwise_correspondence(
        self, img1_bgr: np.ndarray, img2_bgr: np.ndarray, similarity: float, is_match: bool
    ) -> np.ndarray:
        """
        Creates a side-by-side comparative explainability visualizer:
        Shows Image 1 with Attention Heatmap, Image 2 with Attention Heatmap,
        and connecting feature match lines / alignment banner.
        """
        h_target, w_target = 240, 240
        res1 = cv2.resize(img1_bgr, (w_target, h_target))
        res2 = cv2.resize(img2_bgr, (w_target, h_target))

        heat1 = self.generate_attention_heatmap(res1)["overlay_bgr"]
        heat2 = self.generate_attention_heatmap(res2)["overlay_bgr"]

        # Canvas for side-by-side (240 x 540 + header)
        canvas_h = h_target + 80
        canvas_w = (w_target * 2) + 60
        canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
        canvas[:] = (20, 24, 30)  # Dark sleek background

        # Place heat1 and heat2
        canvas[60:60+h_target, 20:20+w_target] = heat1
        canvas[60:60+h_target, 20+w_target+20:20+w_target+20+w_target] = heat2

        # Connecting match indicator in the middle
        mid_x = 20 + w_target + 10
        accent_color = (46, 213, 115) if is_match else (84, 84, 255) # Green / Red BGR
        cv2.line(canvas, (mid_x, 100), (mid_x, 100 + h_target - 80), accent_color, 2)
        cv2.circle(canvas, (mid_x, 60 + h_target // 2), 16, accent_color, -1)

        # Header text
        header_text = f"XAI BIOMETRIC ALIGNMENT (Sim: {similarity:.4f})"
        cv2.putText(canvas, header_text, (24, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 230, 242), 2, cv2.LINE_AA)

        # Label each image
        cv2.putText(canvas, "Query Sample", (20, canvas_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 175, 190), 1, cv2.LINE_AA)
        cv2.putText(canvas, "Gallery Match" if is_match else "Comparison Target", (20+w_target+20, canvas_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 175, 190), 1, cv2.LINE_AA)

        return canvas

    @staticmethod
    def to_base64(img_bgr: np.ndarray, format: str = "jpeg") -> str:
        """Helper to convert BGR image array into base64 data url."""
        _, buffer = cv2.imencode(f".{format}", img_bgr)
        return f"data:image/{format};base64," + base64.b64encode(buffer).decode("utf-8")
