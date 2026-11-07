import os
import sys

root_dir = os.path.abspath(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import gradio as gr
from web_app.app import app as fastapi_app

# ZeroGPU function requirement for Hugging Face ZeroGPU runtime
try:
    import spaces
    import torch
    @spaces.GPU
    def zerogpu_inference():
        device = "cuda" if torch.cuda.is_available() else "cpu"
        return f"ZeroGPU active on {device}"
except Exception as e:
    print(f"[*] ZeroGPU fallback: {e}")

# Mount FastAPI inside Gradio app to satisfy Hugging Face ZeroGPU SDK while preserving full HalalChain Web App
app = gr.mount_gradio_app(fastapi_app, gr.Blocks(title="HalalChain AI"), path="/gradio")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    print(f"[*] Starting HalalChain Server on 0.0.0.0:{port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)


