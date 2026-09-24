import uvicorn
import webbrowser
import threading
import time
import os
import sys

def open_browser():
    time.sleep(1.5)
    print("\n[*] Opening web dashboard in default browser: http://127.0.0.1:8000")
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("=" * 65)
    print("  LIVESTOCK MUZZLE BIOMETRIC INTELLIGENCE DASHBOARD")
    print("  Powered by ResNet50 + ArcFace (Fine-Tuned) & CLAHE Enhancement")
    print("=" * 65)
    print("[*] Starting FastAPI server on http://127.0.0.1:8000 ...")
    
    # Auto-open browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run("web_app.app:app", host="127.0.0.1", port=8000, reload=False, log_level="info")
