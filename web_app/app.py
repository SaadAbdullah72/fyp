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
from xai_heatmap import MuzzleExplainabilityEngine
from vector_index import CattleVectorIndex
from quality_gate import ImageQualityGate

app = FastAPI(
    title="Livestock Muzzle Biometric Intelligence System",
    description="Next-Gen Cattle Biometric Platform with FAISS Vector Search, Grad-CAM XAI Heatmaps, and Quality Gate.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Storage: Dual FAISS Vector Index + Fast Metadata Map
vector_index = CattleVectorIndex(embedding_dim=512)
quality_gate = ImageQualityGate()
REGISTRY: Dict[str, Dict[str, Any]] = {}

# Initialize Verification Engine & YOLO Detector
WEIGHTS_PATH = os.path.join(AI_ENGINE_PATH, "checkpoints", "best_muzzle_arcface.pth")
if not os.path.exists(WEIGHTS_PATH):
    print(f"[!] Warning: Trained checkpoint not found at {WEIGHTS_PATH}.")
    WEIGHTS_PATH = None

print("[*] Starting Muzzle Biometric Engine & Detector...")
engine = MuzzleVerificationEngine(weights_path=WEIGHTS_PATH)
preprocessor = MuzzlePreprocessor(target_size=(224, 224))
xai_engine = MuzzleExplainabilityEngine(engine.model, device=engine.device)

try:
    detector = LivestockMuzzleDetector()
except Exception as e:
    detector = None
    print(f"[!] YOLO detector not loaded: {e}")

print("[SUCCESS] Deep AI Engines (FAISS, Grad-CAM XAI, Quality Gate) Ready!")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def prepare_muzzle_crop(img_bgr: np.ndarray) -> np.ndarray:
    """Auto-detects and crops muzzle if full cow image, else preserves aspect."""
    h, w = img_bgr.shape[:2]
    if 0.75 <= w / h <= 1.35 and max(h, w) <= 600:
        return img_bgr
    if detector is not None:
        try:
            return detector.detect_and_crop(img_bgr)
        except Exception:
            pass
    return img_bgr


def cv2_to_base64(image_bgr: np.ndarray, format: str = "jpeg") -> str:
    _, buffer = cv2.imencode(f".{format}", image_bgr)
    return f"data:image/{format};base64," + base64.b64encode(buffer).decode("utf-8")


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
    return HTMLResponse("<h1>Antigravity Biometric Engine 2.0</h1><p>Frontend static files loading...</p>")


@app.get("/api/system-status")
async def get_system_status():
    """Reports real-time engine health, FAISS status, and hardware accelerator."""
    return {
        "status": "healthy",
        "faiss_engine": vector_index.index_type,
        "indexed_vectors": vector_index.count(),
        "device": str(engine.device),
        "backbone": "ResNet-50 + ArcFace (512-D)",
        "xai_module": "Grad-CAM / Channel Activation Map Active",
        "quality_gate": "Laplacian Blur + Specular Glare + 2D FFT Anti-Spoof Active"
    }


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
            "quality_score": data.get("quality_score", 95.0),
            "features_dim": len(data.get("embedding", []))
        })
    return {
        "status": "success",
        "total_registered": len(items),
        "registry": items
    }


@app.post("/api/reset")
async def reset_registry():
    """Wipes all local in-memory records and FAISS index."""
    count = len(REGISTRY)
    REGISTRY.clear()
    vector_index.clear()
    return {
        "status": "success",
        "cleared_count": count,
        "message": "Local database & FAISS index wiped completely. Registry reset to 0."
    }


@app.post("/api/quality-check")
async def check_image_quality(file: UploadFile = File(...)):
    """Pre-scan diagnostics endpoint: checks blur, lighting, and anti-spoofing."""
    try:
        content = await file.read()
        bgr = bytes_to_cv2(content)
        assessment = quality_gate.assess_quality(bgr)
        return {"status": "success", "assessment": assessment}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/compare")
async def compare_two_muzzles(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    threshold: float = 0.35
):
    """
    Direct 1-to-1 Biometric Verification with:
    1. Pre-inference Quality Gate & Anti-Spoofing on both images.
    2. Deep 512-D ArcFace Cosine Alignment.
    3. Grad-CAM Attention Heatmaps for both muzzles.
    4. Side-by-side Biometric Alignment Correspondence Visualization.
    """
    try:
        bytes1 = await file1.read()
        bytes2 = await file2.read()
        bgr1 = prepare_muzzle_crop(bytes_to_cv2(bytes1))
        bgr2 = prepare_muzzle_crop(bytes_to_cv2(bytes2))

        # 1. Quality & Anti-Spoofing Check
        q1 = quality_gate.assess_quality(bgr1)
        q2 = quality_gate.assess_quality(bgr2)

        # 2. Extract embeddings
        emb1 = engine.extract_embedding(bgr1)
        emb2 = engine.extract_embedding(bgr2)

        # 3. Cosine similarity
        cosine_sim = float(np.dot(emb1, emb2))
        clamped_sim = float(np.clip(cosine_sim, -1.0, 1.0))
        angular_dist = round(float(np.degrees(np.arccos(clamped_sim))), 2)

        is_match = bool(cosine_sim >= threshold)
        confidence_pct = round(max(0.0, min(100.0, (cosine_sim + 1.0) / 2.0 * 100.0)), 2)

        hash1 = BiometricHasher.generate_sha256_hash(emb1)
        hash2 = BiometricHasher.generate_sha256_hash(emb2)

        # 4. Generate XAI Visualizations
        xai1 = xai_engine.generate_attention_heatmap(bgr1)
        xai2 = xai_engine.generate_attention_heatmap(bgr2)
        corr_canvas = xai_engine.generate_pairwise_correspondence(bgr1, bgr2, cosine_sim, is_match)

        print(f"[COMPARE] File 1: {file1.filename} vs File 2: {file2.filename} | Sim: {cosine_sim:.4f} | Thr: {threshold} | Match: {is_match}")

        return {
            "status": "success",
            "is_match": is_match,
            "match_status": "MATCH_VERIFIED" if is_match else "MISMATCH_DIFFERENT_ANIMALS",
            "cosine_similarity": round(cosine_sim, 4),
            "confidence_percent": f"{confidence_pct}%",
            "angular_distance_deg": angular_dist,
            "threshold": threshold,
            "quality_analysis": {
                "image1": q1,
                "image2": q2
            },
            "xai": {
                "heatmap1": cv2_to_base64(xai1["overlay_bgr"]),
                "heatmap2": cv2_to_base64(xai2["overlay_bgr"]),
                "ridge1": cv2_to_base64(xai1["ridge_color"]),
                "ridge2": cv2_to_base64(xai2["ridge_color"]),
                "correspondence_canvas": cv2_to_base64(corr_canvas)
            },
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
    Scans a muzzle image with Full Suite:
    1. Pre-inference Quality Gate & Screen Replay Anti-Spoofing.
    2. Deep 512-D ArcFace Biometric Embedding.
    3. Grad-CAM Deep Attention Heatmap generation.
    4. FAISS Sub-Millisecond Vector Search over enrolled database.
    5. Returns Top Matches, Search Latency (ms), and XAI overlays.
    """
    try:
        content = await file.read()
        bgr_img = prepare_muzzle_crop(bytes_to_cv2(content))

        # 1. Quality & Anti-Spoofing
        q_result = quality_gate.assess_quality(bgr_img)

        # 2. Texture enhancement & Embedding
        enhanced_bgr = preprocessor.enhance_texture(bgr_img)
        enhanced_resized = cv2.resize(enhanced_bgr, (224, 224), interpolation=cv2.INTER_CUBIC)
        
        rgb_img = Image.fromarray(enhanced_resized[:, :, ::-1])
        tensor = engine.transform(rgb_img).unsqueeze(0).to(engine.device)
        with torch.no_grad():
            embedding_tensor = engine.model(tensor)
        embedding = embedding_tensor.squeeze(0).cpu().numpy()

        # 3. Biometric Hash
        bio_hash = BiometricHasher.generate_sha256_hash(embedding)

        # 4. Grad-CAM Attention Heatmap
        xai_res = xai_engine.generate_attention_heatmap(bgr_img)

        # 5. High-Speed FAISS Vector Search
        search_res = vector_index.search(embedding, top_k=5, threshold=threshold)
        best_match_item = search_res["best_match"]
        is_match = (best_match_item is not None and best_match_item["is_match"]) and (vector_index.count() > 0)
        best_similarity = best_match_item["similarity"] if best_match_item else -1.0

        confidence_pct = round(max(0.0, min(100.0, (best_similarity + 1.0) / 2.0 * 100.0)), 2) if vector_index.count() > 0 else 0.0
        clamped_sim = np.clip(best_similarity, -1.0, 1.0)
        angular_dist = round(float(np.degrees(np.arccos(clamped_sim))), 2) if vector_index.count() > 0 else 90.0

        print(f"[SCAN - FAISS] File: {file.filename} | Sim: {best_similarity:.4f} | Latency: {search_res['latency_ms']}ms | Match: {is_match}")

        # Visualizations
        orig_thumb = cv2_to_base64(cv2.resize(bgr_img, (220, 220)))
        enhanced_thumb = cv2_to_base64(enhanced_resized)
        heatmap_thumb = cv2_to_base64(cv2.resize(xai_res["overlay_bgr"], (220, 220)))
        ridge_thumb = cv2_to_base64(cv2.resize(xai_res["ridge_color"], (220, 220)))

        return {
            "status": "success",
            "is_match": bool(is_match),
            "match_status": "MATCH_VERIFIED" if is_match else ("FLAGGED_UNREGISTERED" if vector_index.count() > 0 else "NO_REGISTERED_CATTLE"),
            "best_similarity": round(best_similarity, 4) if vector_index.count() > 0 else 0.0,
            "confidence_percent": f"{confidence_pct}%",
            "angular_distance_deg": angular_dist,
            "threshold": threshold,
            "quality_gate": q_result,
            "vector_search": {
                "engine": search_res["engine"],
                "latency_ms": search_res["latency_ms"],
                "total_indexed": search_res["total_indexed"],
                "candidates": search_res["matches"]
            },
            "matched_animal": {
                "tag_id": best_match_item["tag_id"],
                "name": best_match_item["name"],
                "breed": best_match_item["breed"],
                "thumbnail": best_match_item.get("thumbnail", "")
            } if is_match else None,
            "closest_animal": {
                "tag_id": best_match_item["tag_id"],
                "name": best_match_item["name"],
                "similarity": best_match_item["similarity"]
            } if (not is_match and best_match_item is not None) else None,
            "biometric_hash": bio_hash,
            "embedding_sample": [round(float(x), 4) for x in embedding[:12]],
            "embedding_raw": [float(x) for x in embedding],
            "thumbnails": {
                "original": orig_thumb,
                "enhanced": enhanced_thumb,
                "heatmap": heatmap_thumb,
                "ridge": ridge_thumb
            }
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/smart-register")
async def smart_register(
    file: UploadFile = File(...),
    name: str = Form(...),
    breed: str = Form("Sahiwal Cattle"),
    tag_id: Optional[str] = Form(None),
    threshold: float = Form(0.40)
):
    """
    Smart Cattle Registration with Anti-Duplicate AI & FAISS Vector Engine:
    1. Pre-inference Quality Gate & Liveness Audit.
    2. Extract 512-D ArcFace embedding & SHA-256 hash.
    3. Generate Grad-CAM Attention Heatmap.
    4. Query FAISS Vector Database for duplicate check.
    5. If Duplicate detected:
       - REJECT: ALREADY_REGISTERED (returns matched animal photo, XAI alignment map, and score).
    6. If unique:
       - ENROLL: Adds vector to FAISS Index & saves record.
    """
    try:
        content = await file.read()
        bgr_img = prepare_muzzle_crop(bytes_to_cv2(content))

        # 1. Quality & Anti-Spoofing Assessment
        q_result = quality_gate.assess_quality(bgr_img)

        # 2. Texture enhancement & Embedding
        enhanced_bgr = preprocessor.enhance_texture(bgr_img)
        enhanced_resized = cv2.resize(enhanced_bgr, (224, 224), interpolation=cv2.INTER_CUBIC)
        
        rgb_img = Image.fromarray(enhanced_resized[:, :, ::-1])
        tensor = engine.transform(rgb_img).unsqueeze(0).to(engine.device)
        with torch.no_grad():
            embedding_tensor = engine.model(tensor)
        embedding = embedding_tensor.squeeze(0).cpu().numpy()

        bio_hash = BiometricHasher.generate_sha256_hash(embedding)
        thumbnail = cv2_to_base64(cv2.resize(bgr_img, (200, 200)))

        # 3. Grad-CAM Attention Heatmap
        xai_res = xai_engine.generate_attention_heatmap(bgr_img)
        heatmap_thumb = cv2_to_base64(cv2.resize(xai_res["overlay_bgr"], (200, 200)))

        # 4. FAISS Vector Search for Duplicates
        search_res = vector_index.search(embedding, top_k=1, threshold=threshold)
        best_candidate = search_res["best_match"]
        is_duplicate = (best_candidate is not None and best_candidate["is_match"]) and (vector_index.count() > 0)

        if is_duplicate:
            # Animal already registered!
            sim_score = best_candidate["similarity"]
            conf = round(max(0.0, min(100.0, (sim_score + 1.0) / 2.0 * 100.0)), 1)
            clamped_sim = float(np.clip(sim_score, -1.0, 1.0))
            angular_dist = round(float(np.degrees(np.arccos(clamped_sim))), 2)

            matched_cow = REGISTRY.get(best_candidate["tag_id"], {})
            print(f"[FAISS DUPLICATE REJECTED] '{name}' matches '{best_candidate['name']}' (sim={sim_score:.4f}, latency={search_res['latency_ms']}ms)")

            # Create XAI Pairwise Alignment Visualizer between new upload and existing record
            matched_thumb_bgr = None
            if "raw_crop" in matched_cow:
                matched_thumb_bgr = matched_cow["raw_crop"]
            else:
                matched_thumb_bgr = bgr_img # fallback
            
            xai_corr = xai_engine.generate_pairwise_correspondence(bgr_img, matched_thumb_bgr, sim_score, True)
            corr_b64 = cv2_to_base64(xai_corr)

            return {
                "status": "already_registered",
                "message": f"Sorry! This animal is ALREADY registered as '{best_candidate['name']}'!",
                "similarity": round(sim_score, 4),
                "confidence": conf,
                "angular_distance_deg": angular_dist,
                "threshold": threshold,
                "quality_gate": q_result,
                "vector_search": {
                    "engine": search_res["engine"],
                    "latency_ms": search_res["latency_ms"],
                    "total_indexed": search_res["total_indexed"]
                },
                "xai": {
                    "heatmap_upload": heatmap_thumb,
                    "correspondence_canvas": corr_b64
                },
                "uploaded_name": name.strip(),
                "uploaded_thumbnail": thumbnail,
                "matched_animal": {
                    "tag_id": best_candidate["tag_id"],
                    "name": best_candidate["name"],
                    "breed": matched_cow.get("breed", "Cattle"),
                    "registered_at": matched_cow.get("created_at", ""),
                    "thumbnail": matched_cow.get("thumbnail", ""),
                    "hash": matched_cow.get("hash", "")
                },
                "total_registered": vector_index.count()
            }
        else:
            # New unique animal — enroll it
            if not tag_id or not tag_id.strip():
                import uuid
                final_tag = f"CATTLE-{str(uuid.uuid4())[:8].upper()}"
            else:
                final_tag = tag_id.strip().upper()

            cow_record = {
                "tag_id": final_tag,
                "name": name.strip(),
                "breed": breed.strip() if breed else "Cattle",
                "embedding": [float(x) for x in embedding],
                "hash": bio_hash,
                "thumbnail": thumbnail,
                "raw_crop": cv2.resize(bgr_img, (240, 240)),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "quality_score": q_result["overall_score"]
            }

            # Add to FAISS Vector Index & Registry
            vector_index.add(final_tag, embedding, cow_record)
            REGISTRY[final_tag] = cow_record

            print(f"[FAISS NEW ENROLLED] '{name}' registered as '{final_tag}' (Latency: {search_res['latency_ms']}ms)")

            return {
                "status": "new_registered",
                "message": f"New animal '{name.strip()}' registered successfully!",
                "tag_id": final_tag,
                "name": name.strip(),
                "breed": breed.strip() if breed else "Cattle",
                "biometric_hash": bio_hash,
                "thumbnail": thumbnail,
                "quality_gate": q_result,
                "vector_search": {
                    "engine": search_res["engine"],
                    "latency_ms": search_res["latency_ms"],
                    "total_indexed": vector_index.count()
                },
                "xai": {
                    "heatmap_thumbnail": heatmap_thumb
                },
                "total_registered": vector_index.count(),
                "embedding_sample": [round(float(x), 4) for x in embedding[:12]],
                "closest_existing": {
                    "name": best_candidate["name"],
                    "similarity": round(best_candidate["similarity"], 4)
                } if (best_candidate is not None and vector_index.count() > 1) else None
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/registry/{tag_id}")
async def delete_animal(tag_id: str):
    """Deletes an animal from both in-memory registry and FAISS vector index."""
    if tag_id in REGISTRY:
        cow = REGISTRY.pop(tag_id)
        vector_index.remove(tag_id)
        return {
            "status": "success",
            "message": f"Animal '{cow.get('name')}' ({tag_id}) removed from registry & FAISS index.",
            "total_registered": vector_index.count()
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
