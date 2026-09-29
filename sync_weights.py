import os
import shutil
import glob

def sync_yolo_weights():
    downloads_dir = os.path.expanduser("~/Downloads")
    target_dir = os.path.join(os.path.dirname(__file__), "ai_engine", "checkpoints")
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, "best_muzzle_yolo.pt")

    print(f"[*] Scanning Downloads folder: {downloads_dir}")

    # Search for downloaded weights
    patterns = [
        os.path.join(downloads_dir, "best.pt"),
        os.path.join(downloads_dir, "best*.pt"),
        os.path.join(downloads_dir, "*muzzle*.pt")
    ]

    found_file = None
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            found_file = matches[0]
            break

    if found_file and os.path.exists(found_file):
        print(f"[+] Found downloaded YOLO weights at: {found_file}")
        shutil.copy2(found_file, target_file)
        print(f"[SUCCESS] Custom YOLO Muzzle Weights synced to: {target_file}")
        return True
    else:
        print("[!] No 'best.pt' found in Downloads yet.")
        print("    Kaggle notebook mein 'FileLink(r\"runs/detect/cattle_muzzle_yolo/weights/best.pt\")' run karke download karein.")
        return False

if __name__ == "__main__":
    sync_yolo_weights()
