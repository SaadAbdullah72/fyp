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

# Define standard Gradio Blocks with active @spaces.GPU hook
with gr.Blocks(title="HalalChain AI") as demo:
    btn = gr.Button("ZeroGPU Keepalive")
    out = gr.Textbox()
    btn.click(predict_muzzle, outputs=out)

# Mount FastAPI app onto Gradio
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






