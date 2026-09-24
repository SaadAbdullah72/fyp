import os
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm

from dataset import CattleMuzzleDataset
from models.backbone import MuzzleBiometricNet
from models.arcface_loss import ArcMarginProduct

def train_arcface(
    data_dir: str,
    epochs: int = 25,
    batch_size: int = 16,
    lr: float = 1e-4,
    embedding_dim: int = 512,
    margin_s: float = 64.0,
    margin_m: float = 0.50,
    save_dir: str = "checkpoints"
):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Training ArcFace Cattle Muzzle Model on device: {device}")

    os.makedirs(save_dir, exist_ok=True)

    # 1. Dataset & DataLoader
    dataset = CattleMuzzleDataset(root_dir=data_dir, is_train=True)
    num_classes = len(dataset.class_to_idx)
    
    if num_classes < 2:
        print(f"[!] Error: Need at least 2 distinct animal classes in {data_dir}. Found: {num_classes}")
        print("    Ensure your dataset is organized as: data_dir/cow_1/xxx.jpg, data_dir/cow_2/yyy.jpg")
        return

    print(f"[*] Loaded dataset with {len(dataset)} images across {num_classes} unique animals.")
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)

    # 2. Network Models
    backbone = MuzzleBiometricNet(backbone_name="resnet50", embedding_size=embedding_dim, pretrained=True).to(device)
    metric_fc = ArcMarginProduct(in_features=embedding_dim, out_features=num_classes, s=margin_s, m=margin_m).to(device)

    # 3. Loss & Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(list(backbone.parameters()) + list(metric_fc.parameters()), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    # 4. Training Loop
    best_loss = float('inf')

    for epoch in range(1, epochs + 1):
        backbone.train()
        metric_fc.train()
        running_loss = 0.0
        correct = 0
        total = 0

        pbar = tqdm(dataloader, desc=f"Epoch {epoch}/{epochs}")
        for images, labels in pbar:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            # Forward pass: Extract 512-D embeddings and pass through ArcFace
            embeddings = backbone(images)
            outputs = metric_fc(embeddings, labels)

            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            pbar.set_postfix({
                'loss': f"{loss.item():.4f}",
                'acc': f"{100. * correct / total:.2f}%"
            })

        scheduler.step()
        epoch_loss = running_loss / total
        epoch_acc = 100. * correct / total
        print(f"[*] Epoch {epoch} Complete - Loss: {epoch_loss:.4f} - Training Accuracy: {epoch_acc:.2f}%")

        # Save Best Checkpoint
        if epoch_loss < best_loss:
            best_loss = epoch_loss
            save_path = os.path.join(save_dir, "best_muzzle_arcface.pth")
            torch.save({
                'epoch': epoch,
                'model_state_dict': backbone.state_dict(),
                'metric_fc_state_dict': metric_fc.state_dict(),
                'loss': epoch_loss,
                'classes': dataset.class_to_idx
            }, save_path)
            print(f"[*] Saved new best model to {save_path}")

    print("[*] Training pipeline completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Livestock ArcFace Model")
    parser.add_argument("--data_dir", type=str, default="data/cropped_muzzles", help="Path to cropped muzzles dataset")
    parser.add_argument("--epochs", type=int, default=25, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    args = parser.parse_args()

    train_arcface(data_dir=args.data_dir, epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)
