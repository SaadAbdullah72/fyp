import os
import sys
import torch
from ultralytics import YOLO

def main():
    print("=" * 60)
    print("  YOLOv8 Cattle Muzzle Detector - Fine-Tuning Pipeline")
    print("=" * 60)

    # 1. Dataset Path
    dataset_dir = r"C:\Users\Hp\Downloads\archive (2)"
    if not os.path.exists(dataset_dir):
        print(f"[!] Dataset folder not found at: {dataset_dir}")
        print("Please ensure the archive (2) dataset is present.")
        return

    # 2. Prepare standardized data.yaml with absolute paths
    yaml_content = f"""path: {dataset_dir.replace(chr(92), '/')}
train: train/images
val: valid/images
test: test/images

nc: 1
names: ['Muzzle']
"""
    yaml_file = os.path.join(dataset_dir, "custom_muzzle_data.yaml")
    with open(yaml_file, "w") as f:
        f.write(yaml_content)
    print(f"[*] Generated YAML config at: {yaml_file}")

    # 3. Device selection
    device = "0" if torch.cuda.is_available() else "cpu"
    print(f"[*] Training Device: {device.upper()}")
    if device == "cpu":
        print("[!] Note: Training on CPU is slower. For 5-minute GPU training, upload to Google Colab or Kaggle.")

    # 4. Load Pretrained YOLOv8 Nano
    print("[*] Loading base pretrained model (yolov8n.pt)...")
    model = YOLO("yolov8n.pt")

    # 5. Start Training
    epochs = 30 if device == "cpu" else 50
    batch_size = 8 if device == "cpu" else 16
    print(f"[*] Starting training for {epochs} epochs (Batch size: {batch_size})...")

    results = model.train(
        data=yaml_file,
        epochs=epochs,
        imgsz=640,
        batch=batch_size,
        device=device,
        workers=2,
        name="cattle_muzzle_detector",
        save=True,
        project="ai_engine/runs"
    )

    print("\n" + "=" * 60)
    print("  TRAINING COMPLETE!")
    print("=" * 60)
    best_weights = os.path.join("ai_engine", "runs", "cattle_muzzle_detector", "weights", "best.pt")
    target_weights = os.path.join("ai_engine", "checkpoints", "best_muzzle_yolo.pt")

    if os.path.exists(best_weights):
        os.makedirs(os.path.dirname(target_weights), exist_ok=True)
        import shutil
        shutil.copy(best_weights, target_weights)
        print(f"[SUCCESS] Trained weights saved to: {target_weights}")
        print("System will now automatically use this model for exact muzzle bounding box pinpointing!")
    else:
        print(f"[!] Check runs folder for best.pt: {best_weights}")

if __name__ == "__main__":
    main()
