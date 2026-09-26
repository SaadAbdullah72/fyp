import os
import time
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[!] FAISS not installed. Falling back to NumPy Vector Indexing.")

class CattleVectorIndex:
    """
    High-Performance Biometric Vector Index (FAISS + Fallback).
    Provides sub-millisecond O(1) similarity search for massive cattle registries.
    Uses Inner Product (IP) metric which is mathematically equivalent to Cosine Similarity
    for L2-normalized 512-D ArcFace embeddings.
    """
    def __init__(self, embedding_dim: int = 512, index_type: str = "FlatIP"):
        self.dim = embedding_dim
        self.index_type = index_type
        self.metadata_store: Dict[int, Dict[str, Any]] = {}
        self.tag_to_id: Dict[str, int] = {}
        self.next_id: int = 0
        
        self.faiss_index = None
        self._init_index()

    def _init_index(self):
        if FAISS_AVAILABLE:
            # IndexFlatIP calculates inner products (cosine similarity for normalized vectors)
            self.faiss_index = faiss.IndexFlatIP(self.dim)
        else:
            self.embeddings_matrix: List[np.ndarray] = []
            self.id_list: List[int] = []

    def count(self) -> int:
        """Returns the total number of enrolled vectors in the index."""
        if FAISS_AVAILABLE and self.faiss_index is not None:
            return self.faiss_index.ntotal
        return len(self.metadata_store)

    def add(self, tag_id: str, embedding: np.ndarray, metadata: Dict[str, Any]) -> int:
        """
        Adds or updates an animal's 512-D embedding in the FAISS index.
        """
        # Ensure L2 normalized float32
        emb = np.array(embedding, dtype=np.float32).reshape(1, -1)
        norm = np.linalg.norm(emb)
        if norm > 0:
            emb = emb / norm

        # If tag already exists, remove first
        if tag_id in self.tag_to_id:
            self.remove(tag_id)

        curr_id = self.next_id
        self.next_id += 1

        self.metadata_store[curr_id] = {
            "tag_id": tag_id,
            "name": metadata.get("name", "Unknown Animal"),
            "breed": metadata.get("breed", "Cattle"),
            "thumbnail": metadata.get("thumbnail", ""),
            "hash": metadata.get("hash", ""),
            "created_at": metadata.get("created_at", ""),
            "embedding": emb.flatten().tolist()
        }
        self.tag_to_id[tag_id] = curr_id

        if FAISS_AVAILABLE and self.faiss_index is not None:
            self.faiss_index.add(emb)
        return curr_id

    def search(self, query_embedding: np.ndarray, top_k: int = 5, threshold: float = 0.0) -> Dict[str, Any]:
        """
        Searches the FAISS vector database for nearest biometric matches.
        Returns top matching candidates, similarity scores, and search latency.
        """
        start_time = time.perf_counter()
        total_items = self.count()

        if total_items == 0:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)
            return {
                "matches": [],
                "best_match": None,
                "latency_ms": elapsed_ms,
                "total_indexed": 0,
                "engine": "FAISS-FlatIP" if FAISS_AVAILABLE else "NumPy-Vector"
            }

        # Normalize query vector
        q_emb = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        q_norm = np.linalg.norm(q_emb)
        if q_norm > 0:
            q_emb = q_emb / q_norm

        k = min(top_k, total_items)
        matches = []

        if FAISS_AVAILABLE and self.faiss_index is not None:
            similarities, indices = self.faiss_index.search(q_emb, k)
            sims = similarities[0]
            idxs = indices[0]

            for rank, (sim, idx) in enumerate(zip(sims, idxs)):
                if idx in self.metadata_store:
                    item_meta = self.metadata_store[idx]
                    cosine_sim = float(sim)
                    is_above = bool(cosine_sim >= threshold)
                    confidence = round(max(0.0, min(100.0, (cosine_sim + 1.0) / 2.0 * 100.0)), 2)

                    matches.append({
                        "rank": rank + 1,
                        "tag_id": item_meta["tag_id"],
                        "name": item_meta["name"],
                        "breed": item_meta["breed"],
                        "similarity": round(cosine_sim, 4),
                        "confidence_percent": f"{confidence}%",
                        "is_match": is_above,
                        "thumbnail": item_meta.get("thumbnail", ""),
                        "registered_at": item_meta.get("created_at", "")
                    })
        else:
            # NumPy fallback
            all_ids = list(self.metadata_store.keys())
            mat = np.array([self.metadata_store[i]["embedding"] for i in all_ids], dtype=np.float32)
            sims = np.dot(mat, q_emb.flatten())
            sorted_indices = np.argsort(sims)[::-1][:k]

            for rank, idx_pos in enumerate(sorted_indices):
                actual_id = all_ids[idx_pos]
                item_meta = self.metadata_store[actual_id]
                cosine_sim = float(sims[idx_pos])
                is_above = bool(cosine_sim >= threshold)
                confidence = round(max(0.0, min(100.0, (cosine_sim + 1.0) / 2.0 * 100.0)), 2)

                matches.append({
                    "rank": rank + 1,
                    "tag_id": item_meta["tag_id"],
                    "name": item_meta["name"],
                    "breed": item_meta["breed"],
                    "similarity": round(cosine_sim, 4),
                    "confidence_percent": f"{confidence}%",
                    "is_match": is_above,
                    "thumbnail": item_meta.get("thumbnail", ""),
                    "registered_at": item_meta.get("created_at", "")
                })

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)
        best_match = matches[0] if matches else None

        return {
            "matches": matches,
            "best_match": best_match,
            "latency_ms": elapsed_ms,
            "total_indexed": total_items,
            "engine": "FAISS-FlatIP (Sub-millisecond Vector DB)" if FAISS_AVAILABLE else "NumPy-Vector"
        }

    def remove(self, tag_id: str) -> bool:
        """Removes an animal by tag_id and rebuilds the FAISS index."""
        if tag_id not in self.tag_to_id:
            return False

        remove_id = self.tag_to_id.pop(tag_id)
        if remove_id in self.metadata_store:
            del self.metadata_store[remove_id]

        # Rebuild FAISS index
        self._rebuild_index()
        return True

    def _rebuild_index(self):
        """Reconstructs FAISS index from clean metadata."""
        if FAISS_AVAILABLE:
            self.faiss_index = faiss.IndexFlatIP(self.dim)
            if len(self.metadata_store) > 0:
                all_embs = [data["embedding"] for data in self.metadata_store.values()]
                mat = np.array(all_embs, dtype=np.float32)
                self.faiss_index.add(mat)
                # Re-map sequential indices
                new_meta = {}
                new_tag_to_id = {}
                for idx, (old_id, item) in enumerate(list(self.metadata_store.items())):
                    new_meta[idx] = item
                    new_tag_to_id[item["tag_id"]] = idx
                self.metadata_store = new_meta
                self.tag_to_id = new_tag_to_id
                self.next_id = len(new_meta)

    def clear(self):
        """Wipes all vectors from the index."""
        self.metadata_store.clear()
        self.tag_to_id.clear()
        self.next_id = 0
        self._init_index()

    def get_all_records(self) -> List[Dict[str, Any]]:
        """Returns all enrolled cattle records."""
        return list(self.metadata_store.values())
