import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class ArcMarginProduct(nn.Module):
    """
    ArcFace: Additive Angular Margin Loss for Deep Face / Muzzle Biometric Recognition.
    Reference: Deng et al. 'ArcFace: Additive Angular Margin Loss for Deep Face Recognition' (CVPR 2019)
    
    Args:
        in_features: size of input feature embedding (e.g. 512)
        out_features: number of individual animal identities in training set
        s: norm of input feature (scale factor, default 64.0)
        m: margin angle in radians (default 0.5 rad ~ 28.6 degrees)
        easy_margin: whether to use easy margin formulation
    """
    def __init__(self, in_features: int, out_features: int, s: float = 64.0, m: float = 0.50, easy_margin: bool = False):
        super(ArcMarginProduct, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.s = s
        self.m = m
        self.weight = nn.Parameter(torch.FloatTensor(out_features, in_features))
        nn.init.xavier_uniform_(self.weight)

        self.easy_margin = easy_margin
        self.cos_m = math.cos(m)
        self.sin_m = math.sin(m)
        self.th = math.cos(math.pi - m)
        self.mm = math.sin(math.pi - m) * m

    def forward(self, input_features: torch.Tensor, labels: torch.Tensor = None) -> torch.Tensor:
        """
        Args:
            input_features: (batch_size, in_features)
            labels: (batch_size,) - Ground truth class labels (Required during training)
        """
        # 1. Normalize weights and input features to unit sphere
        cosine = F.linear(F.normalize(input_features), F.normalize(self.weight))
        
        if labels is None:
            # Inference mode: return scaled cosine logits
            return cosine * self.s

        # 2. cos(theta + m) = cos(theta)*cos(m) - sin(theta)*sin(m)
        sine = torch.sqrt(1.0 - torch.clamp(cosine ** 2, 0.0, 1.0))
        phi = cosine * self.cos_m - sine * self.sin_m

        if self.easy_margin:
            phi = torch.where(cosine > 0, phi, cosine)
        else:
            phi = torch.where(cosine > self.th, phi, cosine - self.mm)

        # 3. One-hot target modulation
        one_hot = torch.zeros(cosine.size(), device=input_features.device)
        one_hot.scatter_(1, labels.view(-1, 1).long(), 1.0)
        
        output = (one_hot * phi) + ((1.0 - one_hot) * cosine)
        output *= self.s
        
        return output
