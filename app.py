import os
import sys

root_dir = os.path.abspath(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Initialize ZeroGPU function to satisfy Hugging Face requirement
try:
    import spaces
    @spaces.GPU
    def init_zerogpu():
        import torch
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[*] ZeroGPU function initialized on: {dev}")
        return True
    init_zerogpu()
except Exception as e:
    print(f"[*] ZeroGPU notice: {e}")

import uvicorn
from web_app.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"[*] Starting MuzzleScan FastAPI server on 0.0.0.0:{port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
