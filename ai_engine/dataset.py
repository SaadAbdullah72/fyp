import os
import glob
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset
from PIL import Image
import torchvision.transforms as transforms
from utils.preprocess import MuzzlePreprocessor

class CattleMuzzleDataset(Dataset):
    """
    Dataset loader for Cattle Muzzle images organized in folders:
    root_dir/
        ├── cow_001/
        │   ├── 01.jpg
        │   └── 02.jpg
        ├── cow_002/
        ...
    """
    def __init__(self, root_dir: str, is_train: bool = True, target_size=(224, 224)):
        self.root_dir = root_dir
        self.is_train = is_train
        self.preprocessor = MuzzlePreprocessor(target_size=target_size)
        
        self.image_paths = []
        self.labels = []
        self.class_to_idx = {}

        if os.path.exists(root_dir):
            classes = sorted([d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))])
            self.class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}

            for cls_name in classes:
                cls_dir = os.path.join(root_dir, cls_name)
                for ext in ('*.jpg', '*.jpeg', '*.png', '*.bmp'):
                    for img_file in glob.glob(os.path.join(cls_dir, ext)):
                        self.image_paths.append(img_file)
                        self.labels.append(self.class_to_idx[cls_name])

        # Training vs Evaluation augmentations
        if self.is_train:
            self.transform = transforms.Compose([
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomRotation(degrees=10),
                transforms.ColorJitter(brightness=0.15, contrast=0.15),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        else:
            self.transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]

        # 1. Texture enhancement via CLAHE
        enhanced_bgr = self.preprocessor.preprocess_image(img_path)
        rgb_img = Image.fromarray(enhanced_bgr[:, :, ::-1])

        # 2. PyTorch tensor transformations
        tensor_img = self.transform(rgb_img)

        return tensor_img, torch.tensor(label, dtype=torch.long)
