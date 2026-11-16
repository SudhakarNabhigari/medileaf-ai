# MEDILEAF.AI
### Medicinal-Leaf Identifier with a Reject Option
**Tagline:** *Discover Nature. Identify Leaves. Understand with Confidence.*

An academic Computer Vision platform (`CA-1 Course Project`) that fine-tunes a **PyTorch ResNet50** Convolutional Neural Network on Indian medicinal plant leaf photographs and applies **validation-calibrated confidence & energy gating** to abstain with **`UNCERTAIN`** on unfamiliar (out-of-distribution / held-out species) or unreliable inputs.

> **Disclaimer:** MEDILEAF.AI is an academic plant-image identification prototype. Its predictions are not medical advice or confirmation of plant safety. Do not consume, touch, or use any plant based solely on this application's output. Consult a qualified botanist or relevant professional for verification.

---

## Core Architecture & Fixed Stack
- **Language:** Python 3.12
- **Deep Learning:** PyTorch, Torchvision (`ResNet50_Weights.IMAGENET1K_V2`)
- **Vision & Data:** OpenCV, Pillow, NumPy, Pandas, Scikit-learn, Matplotlib
- **Application UI:** Streamlit (`app.py` + `pages/` + `assets/styles/botanical.css`)
- **Auth & Persistence:** SQLite + PBKDF2-HMAC-SHA256 (`auth/authentication.py`)
- **GPU Training:** Google Colab (`notebooks/medicinal_leaf_identifier_colab.ipynb`)

*(Note: This workspace also retains the AI Studio Vite/Express preview wrapper on port 3000 so the live workspace preview renders cleanly and reflects actual disk artifact status without fabricating any model results.)*

---

## Project Structure
```
MEDILEAF.AI/
├── app.py                              # Main Streamlit entry point
├── pages/                              # Modular Streamlit views (Pages 1–8)
│   ├── dashboard.py
│   ├── identify_leaf.py
│   ├── prediction_history.py
│   ├── model_analytics.py
│   ├── dataset_information.py
│   ├── settings.py
│   └── about.py
├── auth/
│   └── authentication.py               # SQLite PBKDF2 auth & prediction history
├── assets/
│   ├── logo/medileaf_logo.svg
│   └── styles/botanical.css            # Reference green-and-white botanical theme
├── src/
│   ├── config.py                       # Hyperparameters, paths, verified Mendeley metadata
│   ├── data.py                         # Image validation, deterministic transforms, DataLoaders
│   ├── model.py                        # ResNet50 architecture & two-stage fine-tuning
│   ├── train.py                        # Training loop, early stopping, LR scheduling
│   ├── reject.py                       # MSP & Energy OOD scoring + validation calibration
│   ├── evaluate.py                     # Classification, selective accuracy, OOD AUROC/AUPR
│   └── inference.py                    # Unified MediLeafPredictor inference API
├── scripts/
│   ├── inspect_dataset.py              # Dataset audit, duplicates, quality & distribution reports
│   └── prepare_dataset.py              # Leakage-free species split (Train/Val/KnownTest/OODTest)
├── notebooks/
│   └── medicinal_leaf_identifier_colab.ipynb
├── tests/
│   ├── test_auth.py
│   ├── test_cv_technologies.py
│   ├── test_data.py
│   ├── test_evaluate.py
│   ├── test_inference.py
│   ├── test_model.py
│   ├── test_pipeline_integrity.py
│   └── test_reject.py
├── data/
│   ├── raw/                            # Place extracted Mendeley dataset here
│   └── processed/                      # Split manifests & configuration
├── artifacts/                          # Trained weights, class mapping, reject thresholds
├── reports/
│   ├── dataset/                        # Inventory, quality & summary reports
│   ├── figures/                        # Training curves, confusion matrix, OOD & confidence plots
│   └── metrics/                        # Evaluation JSON/CSV outputs
├── PROJECT_BLUEPRINT.md
├── requirements.txt
└── README.md
```

---

## Step-by-Step Setup & Execution Guide

### 1. Python Environment Setup (Local Python 3.12)
```bash
python3.12 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Step 1 — Dataset Acquisition & Verification
Download **Indian Medicinal Leaves Image Datasets (Version 3)** from Mendeley Data:
- **URL:** https://data.mendeley.com/datasets/748f8jkphb/3
- **DOI:** `10.17632/748f8jkphb.3`
- **Licence:** CC BY 4.0

Extract the archive under `data/raw/` and run the inspection script:
```bash
python scripts/inspect_dataset.py --raw-dir data/raw
```
This generates `reports/dataset/dataset_inventory.csv`, `class_distribution.csv`, `dataset_summary.md`, `dataset_quality_report.md`, `sample_images_report.md`, and `dataset_metadata.json`.

### 3. Step 2 — Leakage-Free Species Splitting
Split known species (`train`, `validation`, `known_test`) while completely isolating held-out OOD species (`ood_test`):
```bash
python scripts/prepare_dataset.py --ood-ratio 0.2 --seed 42
```

### 4. Step 3 — Train & Fine-Tune ResNet50 (GPU Recommended)
For local GPU training:
```bash
python -m src.train --epochs-head 5 --epochs-finetune 20 --batch-size 32
```
Or open `notebooks/medicinal_leaf_identifier_colab.ipynb` in **Google Colab (T4/L4/A100 GPU)**, run training, and place the exported `artifacts/` and `reports/` back into your local repository.

### 5. Step 4 — Calibrate Rejection Threshold & Evaluate OOD
```bash
python -m src.evaluate
```
Calibrates MSP & Energy thresholds on `validation_manifest.csv` only, evaluates `known_test_manifest.csv` and `ood_test_manifest.csv`, and generates real metrics & plots.

### 6. Step 5 — Launch MEDILEAF.AI Streamlit App
```bash
streamlit run app.py
```

### 7. Step 6 — Run Automated Tests
```bash
pytest -v tests/
```

---

## Known Limitations & Academic Integrity Notes
1. **Closed-World Assumption & OOD Uncertainty:** No confidence or energy threshold can guarantee 100% rejection of all unseen botanical species or adversarial/ambiguous photographs.
2. **Dataset Constraints:** The Mendeley dataset contains varying backgrounds and potential whole-plant or noisy samples; poisonous-species coverage is NOT assumed unless verified in `dataset_summary.md`.
3. **Authentication Scope:** `auth/authentication.py` uses local SQLite with PBKDF2-HMAC-SHA256 password hashing for single-node/academic demo usage; production multi-tenant deployment would require an external identity provider and HTTPS reverse proxy.
4. **No Fake Metrics:** When `artifacts/best_model.pth` or `reports/` files are absent, the UI explicitly displays honest `"Training Pending"` or `"Dataset Not Loaded"` states.
