---
title: Livestock Muzzle Biometric System
emoji: 🐮
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# 🐮 Livestock Muzzle Biometric Identification & Verification System

Deep Learning biometric identification and anti-duplicate registration pipeline for cattle based on muzzle point prints, powered by fine-tuned **ResNet-50 + ArcFace** loss and **YOLOv8** muzzle detection.

---

## 🌟 Key Features

1. **Smart Cattle Registration (AI Anti-Duplicate Protection):**
   - Automatically computes 512-D ArcFace deep biometric embeddings.
   - Compares with all existing database records using cosine similarity.
   - **Blocks Duplicate Registrations:** If the same cattle is registered with a different photo or name, duplicate fraud is detected and blocked.
   - **Enrolls New Cattle:** Auto-assigns unique Tag IDs and cryptographic SHA-256 biometric hashes.

2. **Direct 1-to-1 Muzzle Comparison:**
   - Real-time side-by-side comparison (Photo A vs Photo B).
   - Generates cosine similarity score, angular separation (degrees), and match confidence.

3. **Search & Verify in Farm Database:**
   - Scan any muzzle photo to lookup and identify enrolled cattle.

4. **Biometric Feature Extraction:**
   - Contrast-Limited Adaptive Histogram Equalization (CLAHE) for ridge grooving enhancement.
   - Deep Metric Learning using ArcFace (Additive Angular Margin).
   - Cryptographic SHA-256 Biometric Hasher.

---

## 🚀 Running Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python run_app.py
```
Open your browser at `http://127.0.0.1:8000`.

---

## 🐳 Docker Deployment

```bash
docker build -t muzzle-scan .
docker run -p 7860:7860 muzzle-scan
```
Open `http://localhost:7860`.
