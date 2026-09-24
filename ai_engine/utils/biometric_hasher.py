import hashlib
import numpy as np
import torch

class BiometricHasher:
    """
    Transforms continuous high-dimensional biometric embeddings (512-D)
    into deterministic cryptographic representations for Blockchain (Solidity ERC-721 / IPFS).
    """
    @staticmethod
    def vector_to_bytes(embedding: np.ndarray) -> bytes:
        """
        Converts float32 numpy array or PyTorch tensor into raw byte string.
        """
        if isinstance(embedding, torch.Tensor):
            embedding = embedding.detach().cpu().numpy()
        
        # Round to 6 decimal places to prevent micro floating-point variance
        rounded = np.round(embedding.flatten(), decimals=6).astype(np.float32)
        return rounded.tobytes()

    @staticmethod
    def generate_sha256_hash(embedding: np.ndarray) -> str:
        """
        Generates standard SHA-256 hexadecimal hash (0x...) for IPFS / off-chain indexing.
        """
        raw_bytes = BiometricHasher.vector_to_bytes(embedding)
        sha = hashlib.sha256(raw_bytes).hexdigest()
        return f"0x{sha}"

    @staticmethod
    def generate_robust_binary_hash(embedding: np.ndarray) -> str:
        """
        Sign-based binarization (Locality Sensitive Hashing representation).
        Converts 512-D float vector to a 512-bit (64 hex characters) binary hash string.
        Very useful for fast bitwise Hamming distance comparisons.
        """
        if isinstance(embedding, torch.Tensor):
            embedding = embedding.detach().cpu().numpy()
        
        binary_bits = (embedding.flatten() > 0).astype(np.uint8)
        # Pack bits into bytes
        packed_bytes = np.packbits(binary_bits).tobytes()
        return "0x" + packed_bytes.hex()
