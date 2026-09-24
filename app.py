import os
import sys
import uvicorn

# Ensure root is in python path
root_dir = os.path.abspath(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from web_app.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"[*] Starting MuzzleScan FastAPI server on 0.0.0.0:{port}...")
    uvicorn.run("web_app.app:app", host="0.0.0.0", port=port, reload=False)
