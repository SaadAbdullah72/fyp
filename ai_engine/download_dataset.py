import os
import shutil
import kagglehub

def download_cattle_dataset():
    """
    Downloads Cattle Biometrics / Muzzle dataset via kagglehub
    and sets up the folder structure for ArcFace training.
    """
    print("[*] Downloading Cattle Biometric Dataset via KaggleHub...")
    
    target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "cropped_muzzles"))
    os.makedirs(target_dir, exist_ok=True)

    try:
        # Download latest version of cattle identification/muzzle dataset
        path = kagglehub.dataset_download("jatinsharma576/muzzle-dataset")
        print(f"[*] Dataset downloaded to temporary cache: {path}")

        print(f"[*] Moving and organizing dataset into: {target_dir}")
        # Locate root containing cattle-* directories
        cattle_root = path
        for root, dirs, files in os.walk(path):
            if any(d.startswith("cattle-") for d in dirs):
                cattle_root = root
                break

        # Copy cattle folders directly into our project data directory
        for item in os.listdir(cattle_root):
            s = os.path.join(cattle_root, item)
            d = os.path.join(target_dir, item)
            if os.path.isdir(s) and item.startswith("cattle-"):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)

        print(f"\n[SUCCESS] Dataset ready in '{target_dir}'!")
        print(f"Total animals found: {len([d for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))])}")

    except Exception as e:
        print(f"\n[!] Notice: {e}")
        print("\nAgr automatic download mein error aye toh manually Kaggle se zip download karke:")
        print(f"'{target_dir}' folder mein extract kar dein.")

if __name__ == "__main__":
    download_cattle_dataset()
