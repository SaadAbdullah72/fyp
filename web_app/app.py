import os
import sys
import io
import base64
import time
from datetime import datetime
from typing import Optional, Dict, Any, List

import cv2
import numpy as np
from PIL import Image
import torch

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add ai_engine to sys.path
AI_ENGINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai_engine"))
if AI_ENGINE_PATH not in sys.path:
    sys.path.insert(0, AI_ENGINE_PATH)

from verify import MuzzleVerificationEngine
from utils.biometric_hasher import BiometricHasher
from utils.preprocess import MuzzlePreprocessor
from detector import LivestockMuzzleDetector

app = FastAPI(title="Livestock Muzzle Biometric Intelligence System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global In-Memory Registry
REGISTRY: Dict[str, Dict[str, Any]] = {}

# Initialize Verification Engine & YOLO Detector
WEIGHTS_PATH = os.path.join(AI_ENGINE_PATH, "checkpoints", "best_muzzle_arcface.pth")
if not os.path.exists(WEIGHTS_PATH):
    print(f"[!] Warning: Trained checkpoint not found at {WEIGHTS_PATH}.")
    WEIGHTS_PATH = None

print("[*] Starting Muzzle Biometric Engine & Detector...")
engine = MuzzleVerificationEngine(weights_path=WEIGHTS_PATH)
preprocessor = MuzzlePreprocessor(target_size=(224, 224))
try:
    detector = LivestockMuzzleDetector()
except Exception as e:
    detector = None
    print(f"[!] YOLO detector not loaded: {e}")

print("[SUCCESS] All AI Engines are ready!")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Helper function to auto-detect and crop muzzle if image is full cow photo
def prepare_muzzle_crop(img_bgr: np.ndarray) -> np.ndarray:
    h, w = img_bgr.shape[:2]
    # If image is already close-up cropped (e.g. roughly square 512x512 with texture)
    if 0.75 <= w / h <= 1.35 and max(h, w) <= 600:
        return img_bgr
    # If full photo, attempt YOLO detection
    if detector is not None:
        try:
            return detector.detect_and_crop(img_bgr)
        except Exception:
            pass
    return img_bgr

# Helper function to convert cv2 image to base64
def cv2_to_base64(image_bgr: np.ndarray, format: str = "jpeg") -> str:
    _, buffer = cv2.imencode(f".{format}", image_bgr)
    return f"data:image/{format};base64," + base64.b64encode(buffer).decode("utf-8")

# Helper function to read uploaded image bytes to BGR
def bytes_to_cv2(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid or corrupted image format.")
    return img


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h1>Antigravity Biometric Engine</h1><p>Frontend static files loading...</p>")


@app.get("/api/registry")
async def get_registry():
    """Returns list of currently registered cattle in memory."""
    items = []
    for tag_id, data in REGISTRY.items():
        items.append({
            "tag_id": tag_id,
            "name": data.get("name", "Unnamed Animal"),
            "breed": data.get("breed", "Cattle"),
            "hash": data.get("hash", ""),
            "thumbnail": data.get("thumbnail", ""),
            "created_at": data.get("created_at", ""),
            "features_dim": len(data.get("embedding", []))
        })
    return {
        "status": "success",
        "total_registered": len(items),
        "registry": items
    }


@app.post("/api/reset")
async def reset_registry():
    """Wipes all local in-memory records and starts fresh from zero."""
    count = len(REGISTRY)
    REGISTRY.clear()
    return {
        "status": "success",
        "cleared_count": count,
        "message": "Local database wiped completely. Registry reset to 0."
    }


@app.post("/api/compare")
async def compare_two_muzzles(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    threshold: float = 0.35
):
    """
    Direct 1-to-1 Biometric Verification:
    Compares two muzzle images directly without needing database registration.
    """
    try:
        bytes1 = await file1.read()
        bytes2 = await file2.read()
        bgr1 = prepare_muzzle_crop(bytes_to_cv2(bytes1))
        bgr2 = prepare_muzzle_crop(bytes_to_cv2(bytes2))

        # Extract embeddings
        emb1 = engine.extract_embedding(bgr1)
        emb2 = engine.extract_embedding(bgr2)

        # Cosine similarity
        cosine_sim = float(np.dot(emb1, emb2))
        clamped_sim = float(np.clip(cosine_sim, -1.0, 1.0))
        angular_dist = round(float(np.degrees(np.arccos(clamped_sim))), 2)

        is_match = bool(cosine_sim >= threshold)
        confidence_pct = round(max(0.0, min(100.0, (cosine_sim + 1.0) / 2.0 * 100.0)), 2)

        hash1 = BiometricHasher.generate_sha256_hash(emb1)
        hash2 = BiometricHasher.generate_sha256_hash(emb2)

        print(f"[COMPARE] File 1: {file1.filename} vs File 2: {file2.filename} | Sim: {cosine_sim:.4f} | Threshold: {threshold} | Match: {is_match}")

        return {
            "status": "success",
            "is_match": is_match,
            "match_status": "MATCH_VERIFIED" if is_match else "MISMATCH_DIFFERENT_ANIMALS",
            "cosine_similarity": round(cosine_sim, 4),
            "confidence_percent": f"{confidence_pct}%",
            "angular_distance_deg": angular_dist,
            "threshold": threshold,
            "image1": {
                "filename": file1.filename,
                "thumbnail": cv2_to_base64(cv2.resize(bgr1, (200, 200))),
                "hash": hash1
            },
            "image2": {
                "filename": file2.filename,
                "thumbnail": cv2_to_base64(cv2.resize(bgr2, (200, 200))),
                "hash": hash2
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/scan")
async def scan_muzzle(file: UploadFile = File(...), threshold: float = 0.35):
    """
    Scans a muzzle image:
    1. Preprocesses & enhances ridges with CLAHE.
    2. Extracts 512-D L2-normalized embedding via fine-tuned ArcFace ResNet50.
    3. Computes SHA-256 cryptographic hash.
    4. Compares with in-memory enrolled cattle via Cosine Similarity.
    5. Returns MATCH_VERIFIED or FLAGGED_UNREGISTERED.
    """
    try:
        content = await file.read()
        bgr_img = prepare_muzzle_crop(bytes_to_cv2(content))
        
        # 1. Texture enhancement via CLAHE
        enhanced_bgr = preprocessor.enhance_texture(bgr_img)
        enhanced_resized = cv2.resize(enhanced_bgr, (224, 224), interpolation=cv2.INTER_CUBIC)
        
        # 2. Extract Embedding
        rgb_img = Image.fromarray(enhanced_resized[:, :, ::-1])
        tensor = engine.transform(rgb_img).unsqueeze(0).to(engine.device)
        with torch.no_grad():
            embedding_tensor = engine.model(tensor)
        embedding = embedding_tensor.squeeze(0).cpu().numpy()

        # 3. Biometric Hash
        bio_hash = BiometricHasher.generate_sha256_hash(embedding)

        # 4. Compare with enrolled cattle
        best_match_tag = None
        best_match_name = None
        best_similarity = -1.0
        best_match_thumb = None

        for tag_id, cow in REGISTRY.items():
            enrolled_emb = np.array(cow["embedding"], dtype=np.float32)
            sim = float(np.dot(embedding, enrolled_emb))
            if sim > best_similarity:
                best_similarity = sim
                best_match_tag = tag_id
                best_match_name = cow.get("name", "Unknown")
                best_match_thumb = cow.get("thumbnail", "")

        is_match = (best_similarity >= threshold) and (len(REGISTRY) > 0)
        confidence_pct = round(max(0.0, min(100.0, (best_similarity + 1.0) / 2.0 * 100.0)), 2) if len(REGISTRY) > 0 else 0.0
        clamped_sim = np.clip(best_similarity, -1.0, 1.0)
        angular_dist = round(float(np.degrees(np.arccos(clamped_sim))), 2) if len(REGISTRY) > 0 else 90.0

        print(f"[SCAN] File: {file.filename} | Sim: {best_similarity:.4f} | Threshold: {threshold} | Match: {is_match} | RegisteredCount: {len(REGISTRY)}")

        # Create previews
        orig_thumb = cv2_to_base64(cv2.resize(bgr_img, (220, 220)))
        enhanced_thumb = cv2_to_base64(enhanced_resized)

        return {
            "status": "success",
            "is_match": bool(is_match),
            "match_status": "MATCH_VERIFIED" if is_match else ("FLAGGED_UNREGISTERED" if len(REGISTRY) > 0 else "NO_REGISTERED_CATTLE"),
            "best_similarity": round(best_similarity, 4) if len(REGISTRY) > 0 else 0.0,
            "confidence_percent": f"{confidence_pct}%",
            "angular_distance_deg": angular_dist,
            "threshold": threshold,
            "matched_animal": {
                "tag_id": best_match_tag,
                "name": best_match_name,
                "thumbnail": best_match_thumb
            } if is_match else None,
            "closest_animal": {
                "tag_id": best_match_tag,
                "name": best_match_name,
                "similarity": round(best_similarity, 4)
            } if (not is_match and len(REGISTRY) > 0) else None,
            "biometric_hash": bio_hash,
            "embedding_sample": [round(float(x), 4) for x in embedding[:12]],
            "embedding_raw": [float(x) for x in embedding],
            "thumbnails": {
                "original": orig_thumb,
                "enhanced": enhanced_thumb
            }
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class RegisterRequest(BaseModel):
    tag_id: str
    name: str = "Cattle Animal"
    breed: str = "Indigenous Cattle"
    embedding_raw: List[float]
    biometric_hash: str
    thumbnail: str


@app.post("/api/register")
async def register_animal(data: RegisterRequest):
    """Enrolls scanned biometric embedding into in-memory registry."""
    if not data.tag_id.strip():
        raise HTTPException(status_code=400, detail="Tag ID / RFID is required.")

    REGISTRY[data.tag_id] = {
        "tag_id": data.tag_id,
        "name": data.name,
        "breed": data.breed,
        "embedding": data.embedding_raw,
        "hash": data.biometric_hash,
        "thumbnail": data.thumbnail,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return {
        "status": "success",
        "message": f"Animal '{data.tag_id}' enrolled successfully into biometric registry.",
        "total_registered": len(REGISTRY)
    }


@app.post("/api/smart-register")
async def smart_register(
    file: UploadFile = File(...),
    name: str = Form(...),
    breed: str = Form("Sahiwal Cattle"),
    tag_id: Optional[str] = Form(None),
    threshold: float = Form(0.40)
):
    """
    Smart Registration with Automated Duplicate Detection:
    1. Upload muzzle image + animal name
    2. Extract 512-D biometric embedding (ResNet50 + ArcFace)
    3. Check ALL enrolled cattle in registry for cosine similarity
    4. If maximum similarity >= threshold:
       - REJECT: ALREADY_REGISTERED (returns matched animal photo, name, tag, and score)
    5. If no match found:
       - ENROLL: NEW_REGISTERED (saves to local database)
    """
    try:
        content = await file.read()
        bgr_img = prepare_muzzle_crop(bytes_to_cv2(content))

        # Extract embedding
        enhanced_bgr = preprocessor.enhance_texture(bgr_img)
        enhanced_resized = cv2.resize(enhanced_bgr, (224, 224), interpolation=cv2.INTER_CUBIC)
        from PIL import Image as PILImage
        rgb_img = PILImage.fromarray(enhanced_resized[:, :, ::-1])
        tensor = engine.transform(rgb_img).unsqueeze(0).to(engine.device)
        with torch.no_grad():
            embedding_tensor = engine.model(tensor)
        embedding = embedding_tensor.squeeze(0).cpu().numpy()

        bio_hash = BiometricHasher.generate_sha256_hash(embedding)
        thumbnail = cv2_to_base64(cv2.resize(bgr_img, (200, 200)))

        # Check for duplicates against ALL registered animals
        best_match_tag = None
        best_match_name = None
        best_similarity = -1.0
        best_match_thumb = None
        best_match_time = None

        for enrolled_tag, cow in REGISTRY.items():
            enrolled_emb = np.array(cow["embedding"], dtype=np.float32)
            sim = float(np.dot(embedding, enrolled_emb))
            if sim > best_similarity:
                best_similarity = sim
                best_match_tag = enrolled_tag
                best_match_name = cow.get("name", "Unknown")
                best_match_thumb = cow.get("thumbnail", "")
                best_match_time = cow.get("created_at", "")

        is_duplicate = (best_similarity >= threshold) and (len(REGISTRY) > 0)

        if is_duplicate:
            # Animal already registered!
            confidence = round(max(0.0, min(100.0, (best_similarity + 1.0) / 2.0 * 100.0)), 1)
            clamped_sim = float(np.clip(best_similarity, -1.0, 1.0))
            angular_dist = round(float(np.degrees(np.arccos(clamped_sim))), 2)
            print(f"[DUPLICATE REJECTED] '{name}' matches '{best_match_name}' (sim={best_similarity:.4f}, thr={threshold})")
            
            matched_cow = REGISTRY.get(best_match_tag, {})
            return {
                "status": "already_registered",
                "message": f"Sorry! This animal is ALREADY registered as '{best_match_name}'!",
                "similarity": round(best_similarity, 4),
                "confidence": confidence,
                "angular_distance_deg": angular_dist,
                "threshold": threshold,
                "uploaded_name": name.strip(),
                "uploaded_thumbnail": thumbnail,
                "matched_animal": {
                    "tag_id": best_match_tag,
                    "name": best_match_name,
                    "breed": matched_cow.get("breed", "Cattle"),
                    "registered_at": best_match_time,
                    "thumbnail": best_match_thumb,
                    "hash": matched_cow.get("hash", "")
                },
                "total_registered": len(REGISTRY)
            }
        else:
            # New animal — enroll it
            if not tag_id or not tag_id.strip():
                import uuid
                final_tag = f"CATTLE-{str(uuid.uuid4())[:8].upper()}"
            else:
                final_tag = tag_id.strip().upper()

            REGISTRY[final_tag] = {
                "tag_id": final_tag,
                "name": name.strip(),
                "breed": breed.strip() if breed else "Cattle",
                "embedding": [float(x) for x in embedding],
                "hash": bio_hash,
                "thumbnail": thumbnail,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            print(f"[NEW ENROLLED] '{name}' registered as '{final_tag}' (closest sim={best_similarity:.4f})")
            return {
                "status": "new_registered",
                "message": f"New animal '{name.strip()}' registered successfully!",
                "tag_id": final_tag,
                "name": name.strip(),
                "breed": breed.strip() if breed else "Cattle",
                "biometric_hash": bio_hash,
                "thumbnail": thumbnail,
                "total_registered": len(REGISTRY),
                "embedding_sample": [round(float(x), 4) for x in embedding[:12]],
                "closest_existing": {
                    "name": best_match_name,
                    "similarity": round(best_similarity, 4)
                } if (best_match_name is not None and len(REGISTRY) > 1) else None
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/registry/{tag_id}")
async def delete_animal(tag_id: str):
    """Deletes an animal from the in-memory registry."""
    if tag_id in REGISTRY:
        cow = REGISTRY.pop(tag_id)
        return {
            "status": "success",
            "message": f"Animal '{cow.get('name')}' ({tag_id}) removed from registry.",
            "total_registered": len(REGISTRY)
        }
    raise HTTPException(status_code=404, detail=f"Animal '{tag_id}' not found.")


@app.get("/api/samples")
async def get_samples():
    """Provides real dataset samples for 1-click viva/demo testing."""
    samples = []
    base_dir = os.path.join(AI_ENGINE_PATH, "data", "cropped_muzzles")
    
    test_cases = [
        {"tag": "Cattle-001 (Photo 1)", "animal": "Cattle-001", "folder": "cattle-001", "idx": 0, "type": "genuine_1"},
        {"tag": "Cattle-001 (Photo 2)", "animal": "Cattle-001", "folder": "cattle-001", "idx": 1, "type": "genuine_2"},
        {"tag": "Cattle-002 (Photo 1)", "animal": "Cattle-002", "folder": "cattle-002", "idx": 0, "type": "impostor_1"},
        {"tag": "Cattle-003 (Photo 1)", "animal": "Cattle-003", "folder": "cattle-003", "idx": 0, "type": "impostor_2"}
    ]

    for item in test_cases:
        folder_path = os.path.join(base_dir, item["folder"])
        if os.path.exists(folder_path):
            files = sorted([f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png'))])
            if len(files) > item["idx"]:
                img_path = os.path.join(folder_path, files[item["idx"]])
                img = cv2.imread(img_path)
                if img is not None:
                    thumb = cv2_to_base64(cv2.resize(img, (140, 140)))
                    samples.append({
                        "label": item["tag"],
                        "animal": item["animal"],
                        "type": item["type"],
                        "path": img_path,
                        "thumbnail": thumb
                    })

    return {"status": "success", "samples": samples}


@app.get("/api/sample-image")
async def get_sample_image(path: str):
    """Serves raw image bytes for selected sample."""
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Sample image not found.")
    return FileResponse(path)
