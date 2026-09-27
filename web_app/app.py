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
    """Safely extracts muzzle ROI for wide field images, and preserves pre-cropped muzzle captures intact."""
    if detector is not None:
        try:
            return detector.detect_and_crop(img_bgr)
        except Exception as e:
            print(f"[!] Detection crop warning: {e}")
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
    """Pre-scan diagnostics endpoint: checks blur, lighting, resolution, and anti-spoofing."""
    try:
        content = await file.read()
        bgr = bytes_to_cv2(content)
        assessment = quality_gate.assess_quality(bgr)
        score = float(assessment.get("overall_score", 0.0))
        passed = bool(assessment.get("passed", False) and score >= 50.0)
        return {
            "status": "success",
            "passed": passed,
            "meets_production_threshold": passed,
            "score": round(score, 1),
            "min_required": 50.0,
            "assessment": assessment
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/compare")
async def compare_muzzles(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    file3: Optional[UploadFile] = File(None),
    threshold: float = 0.60
):
    """
    Direct Biometric Verification & Duplicate Check (Supports 2 or 3 Muzzle Captures):
    1. Pre-inference Quality Gate (Min 50% score required per photo).
    2. Deep 512-D ArcFace Cosine Alignment across all pairs.
    3. Pairwise Cross-Consistency Matrix (Shot 1 vs 2, 1 vs 3, 2 vs 3).
    4. Centroid Master Vector & Duplicate Check against Enrolled Farm Database!
    5. Grad-CAM Attention Heatmaps & Visual Correspondence Canvas.
    """
    try:
        upload_files = [file1, file2]
        if file3 is not None and file3.filename:
            upload_files.append(file3)

        raw_bgrs = []
        qualities = []
        scores = []
        for i, uf in enumerate(upload_files):
            b_data = await uf.read()
            bgr = prepare_muzzle_crop(bytes_to_cv2(b_data))
            q = quality_gate.assess_quality(bgr)
            score = float(q.get("overall_score", 0.0))

            if (not q.get("passed", False)) or score < 50.0:
                integrity = q.get("muzzle_integrity", {})
                reason = integrity.get("message") if not integrity.get("is_valid", True) else f"Photo {i+1} clarity scored {score:.1f}% (Minimum 50.0% required)."
                return JSONResponse(status_code=400, content={
                    "status": "quality_rejected",
                    "message": f"Biometric Muzzle Rejected! {reason} Please capture a clear, centered frontal photo with both nostrils visible.",
                    "failed_slot": i + 1,
                    "scores": [score],
                    "min_required": 50.0,
                    "muzzle_integrity": integrity
                })

            raw_bgrs.append(bgr)
            qualities.append(q)
            scores.append(score)

        # Extract embeddings and thumbnails
        embs = [engine.extract_embedding(b) for b in raw_bgrs]
        thumbs = [cv2_to_base64(cv2.resize(b, (200, 200))) for b in raw_bgrs]
        hashes = [BiometricHasher.generate_sha256_hash(e) for e in embs]

        # XAI Visualizations
        xai_res = [xai_engine.generate_attention_heatmap(b) for b in raw_bgrs]
        heatmaps = [cv2_to_base64(x["overlay_bgr"]) for x in xai_res]
        ridges = [cv2_to_base64(x["ridge_color"]) for x in xai_res]

        if len(upload_files) >= 3:
            # 3-Shot Multi-Angle Cross-Comparison
            sim12 = float(np.dot(embs[0], embs[1]))
            sim13 = float(np.dot(embs[0], embs[2]))
            sim23 = float(np.dot(embs[1], embs[2]))

            pairwise = [
                {"pair": "Shot 1 vs Shot 2", "similarity": round(sim12, 4), "is_match": bool(sim12 >= threshold)},
                {"pair": "Shot 1 vs Shot 3", "similarity": round(sim13, 4), "is_match": bool(sim13 >= threshold)},
                {"pair": "Shot 2 vs Shot 3", "similarity": round(sim23, 4), "is_match": bool(sim23 >= threshold)}
            ]

            min_sim = min(sim12, sim13, sim23)
            avg_sim = (sim12 + sim13 + sim23) / 3.0
            is_match = bool(min_sim >= threshold)

            corr_canvas = xai_engine.generate_pairwise_correspondence(raw_bgrs[0], raw_bgrs[1], sim12, bool(sim12 >= threshold))
            primary_sim = avg_sim
        else:
            # 2-Shot Comparison
            sim12 = float(np.dot(embs[0], embs[1]))
            is_match = bool(sim12 >= threshold)
            pairwise = [
                {"pair": "Photo 1 vs Photo 2", "similarity": round(sim12, 4), "is_match": is_match}
            ]
            min_sim = sim12
            avg_sim = sim12
            primary_sim = sim12
            corr_canvas = xai_engine.generate_pairwise_correspondence(raw_bgrs[0], raw_bgrs[1], sim12, is_match)

        confidence_pct = round(max(0.0, min(100.0, (primary_sim + 1.0) / 2.0 * 100.0)), 2)
        clamped_sim = float(np.clip(primary_sim, -1.0, 1.0))
        angular_dist = round(float(np.degrees(np.arccos(clamped_sim))), 2)

        # Centroid Master Template & Farm Database Duplicate Check
        master_emb = np.mean(embs, axis=0)
        master_emb = master_emb / np.linalg.norm(master_emb)
        master_hash = BiometricHasher.generate_sha256_hash(master_emb)

        search_res = vector_index.search(master_emb, top_k=1, threshold=0.65)
        best_candidate = search_res["best_match"]
        enrolled_duplicate = None
        if best_candidate and best_candidate.get("is_match") and vector_index.count() > 0:
            matched_cow = REGISTRY.get(best_candidate["tag_id"], {})
            enrolled_duplicate = {
                "tag_id": best_candidate["tag_id"],
                "name": best_candidate["name"],
                "breed": matched_cow.get("breed", "Cattle"),
                "similarity": round(best_candidate["similarity"], 4),
                "confidence": round(max(0.0, min(100.0, (best_candidate["similarity"] + 1.0) / 2.0 * 100.0)), 1),
                "thumbnail": matched_cow.get("thumbnail", ""),
                "registered_at": matched_cow.get("created_at", "")
            }

        print(f"[COMPARE] {len(upload_files)} Shots | Min Sim: {min_sim:.4f} | Avg Sim: {avg_sim:.4f} | Match: {is_match} | Duplicate: {enrolled_duplicate is not None}")

        return {
            "status": "success",
            "is_match": is_match,
            "match_status": "MATCH_VERIFIED" if is_match else "MISMATCH_DIFFERENT_ANIMALS",
            "shots_count": len(upload_files),
            "primary_similarity": round(primary_sim, 4),
            "cosine_similarity": round(primary_sim, 4),
            "min_similarity": round(min_sim, 4),
            "avg_similarity": round(avg_sim, 4),
            "confidence_percent": f"{confidence_pct}%",
            "angular_distance_deg": angular_dist,
            "threshold": threshold,
            "pairwise_breakdown": pairwise,
            "quality_scores": [round(s, 1) for s in scores],
            "enrolled_duplicate": enrolled_duplicate,
            "xai": {
                "heatmaps": heatmaps,
                "ridges": ridges,
                "heatmap1": heatmaps[0],
                "heatmap2": heatmaps[1],
                "heatmap3": heatmaps[2] if len(heatmaps) >= 3 else None,
                "ridge1": ridges[0],
                "ridge2": ridges[1],
                "ridge3": ridges[2] if len(ridges) >= 3 else None,
                "correspondence_canvas": cv2_to_base64(corr_canvas)
            },
            "images": [
                {"thumbnail": thumbs[i], "hash": hashes[i], "quality": scores[i], "liveness": qualities[i].get("anti_spoofing", {}).get("liveness_status", "AUTHENTIC_LIVE_ANIMAL")}
                for i in range(len(upload_files))
            ],
            "image1": {"hash": hashes[0], "score": scores[0], "liveness": qualities[0].get("anti_spoofing", {}).get("liveness_status", "AUTHENTIC_LIVE_ANIMAL")},
            "image2": {"hash": hashes[1], "score": scores[1], "liveness": qualities[1].get("anti_spoofing", {}).get("liveness_status", "AUTHENTIC_LIVE_ANIMAL")},
            "image3": {"hash": hashes[2], "score": scores[2], "liveness": qualities[2].get("anti_spoofing", {}).get("liveness_status", "AUTHENTIC_LIVE_ANIMAL")} if len(upload_files) >= 3 else None,
            "quality_analysis": {
                "image1": qualities[0],
                "image2": qualities[1],
                "image3": qualities[2] if len(upload_files) >= 3 else None
            },
            "master_hash": master_hash
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/scan")
async def scan_muzzle(file: UploadFile = File(...), threshold: float = 0.60):
    """
    Scans a muzzle image with Full Suite:
    1. Pre-inference Strict 50% Quality Gate & Screen Replay Anti-Spoofing.
    2. Deep 512-D ArcFace Biometric Embedding.
    3. Grad-CAM Deep Attention Heatmap generation.
    4. FAISS Sub-Millisecond Vector Search over enrolled database.
    5. Returns Top Matches, Search Latency (ms), and XAI overlays.
    """
    try:
        content = await file.read()
        bgr_img = prepare_muzzle_crop(bytes_to_cv2(content))

        # 1. Quality, Anti-Spoofing & Muzzle Completeness
        q_result = quality_gate.assess_quality(bgr_img)
        score = float(q_result.get("overall_score", 0.0))
        if (not q_result.get("passed", False)) or score < 50.0:
            integrity = q_result.get("muzzle_integrity", {})
            reason = integrity.get("message") if not integrity.get("is_valid", True) else f"Image clarity scored {score:.1f}% (Minimum 50.0% required)."
            return JSONResponse(status_code=400, content={
                "status": "quality_rejected",
                "message": f"Biometric Muzzle Rejected! {reason} Please capture a clear, centered frontal photo of the cattle nose.",
                "quality_score": score,
                "min_required": 50.0,
                "muzzle_integrity": integrity
            })

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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/smart-register")
async def smart_register(
    file: Optional[UploadFile] = File(None),
    file1: Optional[UploadFile] = File(None),
    file2: Optional[UploadFile] = File(None),
    file3: Optional[UploadFile] = File(None),
    name: str = Form(...),
    breed: str = Form("Sahiwal Cattle"),
    tag_id: Optional[str] = Form(None),
    threshold: float = Form(0.65)
):
    """
    Production-Grade Smart Cattle Registration with:
    1. Multi-Shot Muzzle Enrollment (3 captures: center, angle A, angle B).
    2. Strict Pre-Inference Quality Gate (Min 50% score required per shot).
    3. Biometric Internal Consistency Verification across shots.
    4. Centroid Master Embedding Normalization.
    5. FAISS Vector Search for Strict Anti-Duplicate Protection (Threshold 0.65).
    """
    try:
        # Collect uploaded files (support 3-shot multi-image or fallback single file)
        upload_files = []
        for f in [file1, file2, file3, file]:
            if f is not None and f.filename:
                upload_files.append(f)

        if not upload_files:
            return JSONResponse(status_code=400, content={
                "status": "error",
                "message": "No muzzle images provided for registration."
            })

        raw_bgr_list = []
        quality_results = []
        for i, uf in enumerate(upload_files):
            b_data = await uf.read()
            bgr = prepare_muzzle_crop(bytes_to_cv2(b_data))
            q_res = quality_gate.assess_quality(bgr)
            q_score = float(q_res.get("overall_score", 0.0))

            # Strict 50% Quality & Muzzle Completeness Enforcement
            if (not q_res.get("passed", False)) or q_score < 50.0:
                integrity = q_res.get("muzzle_integrity", {})
                reason = integrity.get("message") if not integrity.get("is_valid", True) else f"Shot {i+1} clarity scored {q_score:.1f}% (Minimum 50.0% required)."
                return JSONResponse(status_code=400, content={
                    "status": "quality_rejected",
                    "message": f"Biometric Muzzle Rejected! {reason} Please capture a complete frontal photo with both nostrils visible.",
                    "failed_slot": i + 1,
                    "scores": [q_score],
                    "min_required": 50.0,
                    "muzzle_integrity": integrity
                })

            raw_bgr_list.append(bgr)
            quality_results.append(q_res)

        # Extract 512-D embeddings for all shots
        embeddings = []
        thumbnails = []
        for bgr in raw_bgr_list:
            emb = engine.extract_embedding(bgr)
            embeddings.append(emb)
            thumbnails.append(cv2_to_base64(cv2.resize(bgr, (200, 200))))

        # If multiple shots provided, verify internal consistency (must belong to same animal)
        if len(embeddings) >= 2:
            pairwise_sims = []
            for i in range(len(embeddings)):
                for j in range(i + 1, len(embeddings)):
                    sim = float(np.dot(embeddings[i], embeddings[j]))
                    pairwise_sims.append(sim)
            min_pair_sim = min(pairwise_sims)
            if min_pair_sim < 0.38:
                return JSONResponse(status_code=400, content={
                    "status": "inconsistent_muzzles",
                    "message": f"Biometric Inconsistency Warning: The uploaded photos do not appear to be from the same animal (Pairwise match: {min_pair_sim:.3f} < 0.38). Please ensure all shots belong to the same cattle.",
                    "min_similarity": round(min_pair_sim, 3)
                })

        # Calculate Normalized Centroid Master Template Vector
        master_emb = np.mean(embeddings, axis=0)
        master_emb = master_emb / np.linalg.norm(master_emb)

        # Cryptographic Biometric SHA-256 Hash
        bio_hash = BiometricHasher.generate_sha256_hash(master_emb)
        primary_bgr = raw_bgr_list[0]
        primary_thumb = thumbnails[0]

        # Grad-CAM Attention Heatmap for primary muzzle shot
        xai_res = xai_engine.generate_attention_heatmap(primary_bgr)
        heatmap_thumb = cv2_to_base64(cv2.resize(xai_res["overlay_bgr"], (200, 200)))

        # FAISS Vector Search for Duplicates against existing database
        search_res = vector_index.search(master_emb, top_k=1, threshold=threshold)
        best_candidate = search_res["best_match"]
        is_duplicate = (best_candidate is not None and best_candidate["is_match"]) and (vector_index.count() > 0)

        avg_quality = round(float(np.mean([q.get("overall_score", 0.0) for q in quality_results])), 1)

        if is_duplicate:
            # Animal already registered!
            sim_score = best_candidate["similarity"]
            conf = round(max(0.0, min(100.0, (sim_score + 1.0) / 2.0 * 100.0)), 1)
            clamped_sim = float(np.clip(sim_score, -1.0, 1.0))
            angular_dist = round(float(np.degrees(np.arccos(clamped_sim))), 2)

            matched_cow = REGISTRY.get(best_candidate["tag_id"], {})
            print(f"[FAISS DUPLICATE REJECTED] '{name}' matches '{best_candidate['name']}' (sim={sim_score:.4f}, latency={search_res['latency_ms']}ms)")

            matched_thumb_bgr = matched_cow.get("raw_crop", primary_bgr)
            xai_corr = xai_engine.generate_pairwise_correspondence(primary_bgr, matched_thumb_bgr, sim_score, True)
            corr_b64 = cv2_to_base64(xai_corr)

            return {
                "status": "already_registered",
                "message": f"Sorry! This animal is ALREADY registered as '{best_candidate['name']}'!",
                "similarity": round(sim_score, 4),
                "confidence": conf,
                "angular_distance_deg": angular_dist,
                "threshold": threshold,
                "shots_count": len(upload_files),
                "quality_scores": [round(float(q.get("overall_score", 0)), 1) for q in quality_results],
                "average_quality": avg_quality,
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
                "uploaded_thumbnail": primary_thumb,
                "gallery": thumbnails,
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
                "embedding": [float(x) for x in master_emb],
                "hash": bio_hash,
                "thumbnail": primary_thumb,
                "gallery": thumbnails,
                "raw_crop": cv2.resize(primary_bgr, (240, 240)),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "quality_score": avg_quality,
                "shots_enrolled": len(upload_files)
            }

            # Add to FAISS Vector Index & In-memory Registry
            vector_index.add(final_tag, master_emb, cow_record)
            REGISTRY[final_tag] = cow_record

            print(f"[FAISS NEW ENROLLED] '{name}' registered as '{final_tag}' with {len(upload_files)} shots (Latency: {search_res['latency_ms']}ms)")

            return {
                "status": "new_registered",
                "message": f"New animal '{name.strip()}' enrolled with {len(upload_files)}-Shot Master Template!",
                "tag_id": final_tag,
                "name": name.strip(),
                "breed": breed.strip() if breed else "Cattle",
                "biometric_hash": bio_hash,
                "thumbnail": primary_thumb,
                "gallery": thumbnails,
                "shots_count": len(upload_files),
                "quality_scores": [round(float(q.get("overall_score", 0)), 1) for q in quality_results],
                "average_quality": avg_quality,
                "vector_search": {
                    "engine": search_res["engine"],
                    "latency_ms": search_res["latency_ms"],
                    "total_indexed": vector_index.count()
                },
                "xai": {
                    "heatmap_thumbnail": heatmap_thumb
                },
                "total_registered": vector_index.count(),
                "embedding_sample": [round(float(x), 4) for x in master_emb[:12]],
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
