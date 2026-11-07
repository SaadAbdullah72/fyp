import os
import sys

# Step 1: Import spaces and define an active Gradio interface with @spaces.GPU
import spaces

@spaces.GPU
def predict_muzzle(dummy_input="ping"):
    return f"ZeroGPU Inference Online: {dummy_input}"

root_dir = os.path.abspath(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import gradio as gr
from web_app.app import app as fastapi_app

# Gradio interface wired with @spaces.GPU function so Hugging Face startup crawler detects it directly
with gr.Blocks(title="HalalChain Livestock Intelligence") as demo:
    gr.Markdown("### HalalChain ZeroGPU Engine")
    inp = gr.Textbox(value="ping", visible=False)
    out = gr.Textbox(label="Status")
    btn = gr.Button("Status Check", visible=False)
    btn.click(predict_muzzle, inputs=inp, outputs=out)

# Mount FastAPI application onto root of the Gradio app
app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

# Ensure demo launches on Hugging Face standard entry point
if __name__ == "__main__":
    demo.queue()
    app = demo.app
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    print(f"[*] Starting HalalChain Server on 0.0.0.0:{port}...")
    uvicorn.run(demo.app, host="0.0.0.0", port=port)




