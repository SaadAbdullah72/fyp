import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class DenoisingAutoEncoderLayer(nn.Module):
    """
    Single Denoising Auto-Encoder layer for Stacked DAE (Kumar et al. 2018).
    Corrupts inputs with noise during training to learn robust, invariant representations.
    """
    def __init__(self, in_features: int, out_features: int, noise_factor: float = 0.15):
        super(DenoisingAutoEncoderLayer, self).__init__()
        self.noise_factor = noise_factor
        self.encoder = nn.Linear(in_features, out_features)
        self.bn = nn.BatchNorm1d(out_features)
        self.decoder = nn.Linear(out_features, in_features)

    def forward(self, x: torch.Tensor, add_noise: bool = True) -> tuple:
        if self.training and add_noise:
            # Corrupt input with Gaussian and dropout noise to simulate field variations
            noise = torch.randn_like(x) * self.noise_factor
            corrupted = x + noise
            # Masking noise
            mask = (torch.rand_like(x) > 0.10).float()
            corrupted = corrupted * mask
        else:
            corrupted = x

        latent = F.leaky_relu(self.bn(self.encoder(corrupted)), negative_slope=0.1)
        reconstruction = self.decoder(latent)
        return latent, reconstruction

class StackedDenoisingAutoEncoder(nn.Module):
    """
    Stacked Denoising Auto-Encoder (SDAE) architecture (Kumar et al. 2018, Section 5).
    Compresses deep feature embeddings into a robust, noise-invariant manifold
    neutralizing motion blur, lighting shifts, and head angle dynamics.
    
    Structure: 512-D (ArcFace input) -> 384-D -> 256-D (Purified Biometric Core) -> 384-D -> 512-D
    """
    def __init__(self, input_dim: int = 512, hidden_dim: int = 384, latent_dim: int = 256, noise_factor: float = 0.15):
        super(StackedDenoisingAutoEncoder, self).__init__()
        self.input_dim = input_dim
        self.latent_dim = latent_dim

        # Layer 1: 512 -> 384
        self.dae1 = DenoisingAutoEncoderLayer(input_dim, hidden_dim, noise_factor)
        # Layer 2: 384 -> 256 (Purified Core Manifold)
        self.dae2 = DenoisingAutoEncoderLayer(hidden_dim, latent_dim, noise_factor)

        # Non-linear projection head with L2 Normalization
        self.projector = nn.Sequential(
            nn.Linear(latent_dim, input_dim),
            nn.BatchNorm1d(input_dim),
            nn.ReLU(),
            nn.Linear(input_dim, input_dim)
        )

        # Initialize with quasi-identity projection so untrained initialization preserves embedding fidelity
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.orthogonal_(m.weight, gain=1.0)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """
        Extracts purified, noise-stripped latent representation (256-D).
        """
        h1, _ = self.dae1(x, add_noise=False)
        h2, _ = self.dae2(h1, add_noise=False)
        return F.normalize(h2, p=2, dim=-1)

    def denoise_and_project(self, x: torch.Tensor) -> torch.Tensor:
        """
        Passes raw deep embedding through SDAE layers and projects back
        into high-dimensional 512-D invariant space.
        """
        latent = self.encode(x)
        projected = self.projector(latent)
        # Residual skip connection ensures deep spatial semantics are preserved while noise is stripped
        fused = x + 0.35 * projected
        return F.normalize(fused, p=2, dim=-1)

    def forward(self, x: torch.Tensor) -> tuple:
        h1, rec1 = self.dae1(x, add_noise=self.training)
        h2, rec2 = self.dae2(h1, add_noise=self.training)
        denoised = self.denoise_and_project(x)
        return denoised, (rec1, rec2)
