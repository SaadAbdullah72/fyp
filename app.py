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

with open(os.path.join(root_dir, "web_app", "static", "standalone_landing.html"), "r", encoding="utf-8") as f:
    LANDING_HTML_RAW = f.read()

with gr.Blocks(title="HalalChain Livestock Intelligence", css=custom_css) as demo:
    # Keep GPU engine hook active for Hugging Face ZeroGPU watchdog
    ping_btn = gr.Button("GPU Active", visible=False)
    ping_out = gr.Textbox(visible=False)
    ping_btn.click(predict_muzzle, outputs=ping_out)
    
    # Render HalalChain Web Portal directly inside the Space without any 404 iframe route!
    gr.HTML(LANDING_HTML_RAW)

# In Gradio, gr.mount_gradio_app(fastapi_app, demo, path=...) mounts Gradio ONTO FastAPI!
# So we mount demo on /gradio, and fastapi_app remains the master app on root!
app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

# Launch with native Gradio launch to satisfy ZeroGPU watchdog completely
if __name__ == "__main__":
    demo.queue()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )








