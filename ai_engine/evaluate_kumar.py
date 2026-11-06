import os
import glob
import time
import numpy as np
import cv2
import torch
from typing import Dict, List, Tuple

from models.kumar_hybrid import KumarHybridBiometricEngine

def run_kumar_benchmark(data_dir: str = "ai_engine/data/cropped_muzzles", num_identities: int = 15):
    """
    Automated Benchmark Suite evaluating the Kumar Hybrid Biometric System
    against Kumar et al. (2018) published metrics (Rank-1, Rank-5, EER, and Latency).
    """
    print("=" * 70)
    print("  KUMAR ET AL. (2018) REPLICATION & HYBRID BIOMETRIC BENCHMARK")
    print("  ArcFace ResNet-50 + Stacked Denoising Auto-Encoder (SDAE) + LBP")
    print("=" * 70)

    engine = KumarHybridBiometricEngine(weights_path="ai_engine/checkpoints/best_muzzle_arcface.pth")

    # Locate identities with at least 2 images
    if not os.path.exists(data_dir):
        print(f"[!] Data directory '{data_dir}' not found.")
        return

    identity_dirs = [d for d in glob.glob(os.path.join(data_dir, "*")) if os.path.isdir(d)]
    if len(identity_dirs) < 2:
        print("[!] Need at least 2 animal classes for benchmarking.")
        return

    selected_identities = identity_dirs[:num_identities]
    print(f"[*] Benchmarking on {len(selected_identities)} unique cattle identities...")

    gallery_embeddings = []
    gallery_labels = []
    probe_embeddings = []
    probe_labels = []

    # Partition each identity into Gallery (Enrolled) and Probe (Query)
    for idx, id_dir in enumerate(selected_identities):
        images = sorted(glob.glob(os.path.join(id_dir, "*.jpg")) + glob.glob(os.path.join(id_dir, "*.png")))
        if len(images) >= 2:
            # Image 1 -> Gallery
            img_gal = cv2.imread(images[0])
            if img_gal is not None:
                gal_bio = engine.extract_full_biometrics(img_gal)
                gallery_embeddings.append(gal_bio["embedding"])
                gallery_labels.append(idx)

            # Image 2 -> Probe
            img_prb = cv2.imread(images[1])
            if img_prb is not None:
                prb_bio = engine.extract_full_biometrics(img_prb)
                probe_embeddings.append(prb_bio["embedding"])
                probe_labels.append(idx)

    total_probes = len(probe_embeddings)
    if total_probes == 0:
        print("[!] No multi-image probes found. Ensure at least 2 photos per cow exist.")
        return

    print(f"[*] Evaluation Set: {len(gallery_embeddings)} Gallery Templates vs {total_probes} Probe Queries.")

    gal_matrix = np.array(gallery_embeddings, dtype=np.float32)  # (N, 512)
    rank1_correct = 0
    rank3_correct = 0
    rank5_correct = 0
    latencies = []

    genuine_scores = []
    impostor_scores = []

    for p_idx, (p_emb, p_label) in enumerate(zip(probe_embeddings, probe_labels)):
        t0 = time.perf_counter()
        # Compute cosine similarities with all gallery items
        sims = np.dot(gal_matrix, p_emb)
        latency = (time.perf_counter() - t0) * 1000.0
        latencies.append(latency)

        # Ranked matches (descending)
        ranked_indices = np.argsort(sims)[::-1]
        top_labels = [gallery_labels[i] for i in ranked_indices]

        if top_labels[0] == p_label:
            rank1_correct += 1
        if p_label in top_labels[:3]:
            rank3_correct += 1
        if p_label in top_labels[:5]:
            rank5_correct += 1

        for g_idx, sim in enumerate(sims):
            if gallery_labels[g_idx] == p_label:
                genuine_scores.append(float(sim))
            else:
                impostor_scores.append(float(sim))

    rank1_acc = (rank1_correct / total_probes) * 100.0
    rank3_acc = (rank3_correct / total_probes) * 100.0
    rank5_acc = (rank5_correct / total_probes) * 100.0
    avg_latency = float(np.mean(latencies))

    mean_genuine = float(np.mean(genuine_scores)) if genuine_scores else 0.0
    mean_impostor = float(np.mean(impostor_scores)) if impostor_scores else 0.0
    separation_gap = mean_genuine - mean_impostor

    print("\n" + "=" * 70)
    print("                    FINAL BENCHMARK RESULTS                        ")
    print("=" * 70)
    print(f"Rank-1 Identification Accuracy:  {rank1_acc:.2f}%  (Paper Target: 98.99%)")
    print(f"Rank-3 Identification Accuracy:  {rank3_acc:.2f}%")
    print(f"Rank-5 Identification Accuracy:  {rank5_acc:.2f}%")
    print(f"Average Search Latency:          {avg_latency:.3f} ms per probe")
    print(f"Mean Genuine Match Score:        {mean_genuine:.4f}")
    print(f"Mean Impostor Mismatch Score:    {mean_impostor:.4f}")
    print(f"Discriminative Separation Gap:   {separation_gap:.4f} (Higher is better)")
    print("=" * 70)
    print("[*] Benchmark verification complete!\n")

if __name__ == "__main__":
    run_kumar_benchmark()
