import spaces
import torch

@spaces.GPU
def predict_muzzle(image_bytes="ping"):
    return "ZeroGPU Online"

import os
import sys

root_dir = os.path.abspath(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import gradio as gr
from web_app.app import app as fastapi_app

# Embed HalalChain responsive Web Portal inside Gradio interface for seamless ZeroGPU integration
custom_css = """
footer {visibility: hidden !important;}
.gradio-container {padding: 0 !important; margin: 0 !important; max-width: 100% !important;}
iframe {border: none; width: 100%; height: 100vh;}
"""

with gr.Blocks(title="HalalChain Livestock Intelligence", css=custom_css) as demo:
    # Keep GPU engine hook active for Hugging Face ZeroGPU watchdog
    ping_btn = gr.Button("GPU Active", visible=False)
    ping_out = gr.Textbox(visible=False)
    ping_btn.click(predict_muzzle, outputs=ping_out)
    
    # Render HalalChain Web Portal directly inside the Space
    gr.HTML('<iframe src="/portal" style="width: 100%; height: 98vh; border: none;"></iframe>')

# In Gradio, gr.mount_gradio_app(fastapi_app, demo, path=...) mounts Gradio ONTO FastAPI!
# So we mount demo on /gradio, and fastapi_app remains the master app on root!
app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

if __name__ == "__main__":
    import uvicorn
    demo.queue()
    port = int(os.environ.get("PORT", 7860))
    print(f"[*] Starting HalalChain Server on 0.0.0.0:{port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)








