import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models

class MuzzleBiometricNet(nn.Module):
    """
    Deep Feature Extractor Backbone for Livestock Muzzle Recognition.
    Transforms raw muzzle images into 512-dimensional L2-normalized biometric embeddings.
    """
    def __init__(self, backbone_name: str = "resnet50", embedding_size: int = 512, pretrained: bool = True):
        super(MuzzleBiometricNet, self).__init__()
        self.backbone_name = backbone_name
        self.embedding_size = embedding_size

        if backbone_name == "resnet50":
            weights = models.ResNet50_Weights.DEFAULT if pretrained else None
            resnet = models.resnet50(weights=weights)
            in_features = resnet.fc.in_features
            resnet.fc = nn.Identity()
            self.backbone = resnet
            self.fc = nn.Linear(in_features, embedding_size, bias=False)
            self.bn = nn.BatchNorm1d(embedding_size)
        elif backbone_name == "mobilenet_v3":
            weights = models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
            mobilenet = models.mobilenet_v3_large(weights=weights)
            in_features = mobilenet.classifier[0].in_features
            mobilenet.classifier = nn.Identity()
            self.backbone = mobilenet
            self.fc = nn.Linear(in_features, embedding_size, bias=False)
            self.bn = nn.BatchNorm1d(embedding_size)
        else:
            raise ValueError(f"Unsupported backbone: {backbone_name}")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Extracts L2-normalized 512-D embedding vectors.
        """
        features = self.backbone(x)
        embeddings = self.bn(self.fc(features))
        # Normalize to unit sphere (L2 norm = 1) for cosine similarity & ArcFace
        normalized_embeddings = F.normalize(embeddings, p=2, dim=1)
        return normalized_embeddings
