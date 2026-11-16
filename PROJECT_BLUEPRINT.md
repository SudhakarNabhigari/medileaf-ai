# MEDILEAF.AI — Academic & Technical Project Blueprint
**Original Academic Title:** Medicinal-Leaf Identifier with a Reject Option (`Computer Vision Course Project | CA-1`)  
**Product Branding:** MEDILEAF.AI — *Discover Nature. Identify Leaves. Understand with Confidence.*

---

## 1. Requirement Traceability Matrix (Extracted from 7-Page Faculty PDF)

| ID | Faculty PDF Requirement | Target Implementation Module(s) | Verification Criteria |
|---|---|---|---|
| **REQ-01** | Fine-tune a ResNet50 CNN using PyTorch & Torchvision transfer learning to classify supported plant species from leaf images. | `src/model.py`, `src/train.py`, `notebooks/medicinal_leaf_identifier_colab.ipynb` | ResNet50 `fc` layer replaced with `num_known_classes`, two-stage transfer learning (head warmup + selective fine-tuning), `best_model.pth` saved by validation selection. |
| **REQ-02** | Add a confidence-gating / abstention layer that returns `UNCERTAIN` rather than guessing on unfamiliar/unreliable inputs. | `src/reject.py`, `src/inference.py` | Softmax MSP + Energy score implemented; accept iff calibrated validation threshold is satisfied, else return `UNCERTAIN`. |
| **REQ-03** | Calibrate the rejection threshold strictly on validation data — never on test or OOD test data. | `src/reject.py`, `src/train.py`, `src/evaluate.py` | Threshold grid-search uses `validation_manifest.csv` only and saves to `artifacts/rejection_config.json`. |
| **REQ-04** | Evaluate on a completely held-out set of species never seen during training, validation, or threshold calibration. | `scripts/prepare_dataset.py`, `src/evaluate.py` | `ood_test_manifest.csv` species disjoint from `train`, `validation`, and `known_test`; SHA-256 duplicate cross-check passes. |
| **REQ-05** | Use the Indian Medicinal Leaf Dataset (Mendeley Data); verify exact record/version, licence, and actual class contents before making coverage claims. | `scripts/inspect_dataset.py`, `reports/dataset/*` | Verified candidate: Mendeley `748f8jkphb` Version 3 (`10.17632/748f8jkphb.3`, CC BY 4.0). Poisonous-species coverage explicitly unverified until local archive inspection completes. |
| **REQ-06** | Fixed Python + PyTorch + Torchvision + OpenCV + Pillow + NumPy + Pandas + Matplotlib + Scikit-learn + Streamlit stack. Do NOT replace CNN with Gemini/LLM APIs. | `requirements.txt`, `src/*`, `app.py`, `pages/*` | 100% PyTorch ResNet50 inference pipeline; zero LLM vision calls. |
| **REQ-07** | Identical deterministic preprocessing between training evaluation and Streamlit inference (RGB, 224×224, ImageNet normalization). | `src/data.py`, `src/inference.py` | Both `src/evaluate.py` and `src/inference.py` import `get_eval_transforms()` directly from `src/data.py`. |
| **REQ-08** | Comprehensive evaluation & abstention report: Accuracy, per-class P/R/F1, Macro F1, Confusion Matrix, Coverage, Selective Accuracy, Rejection Rate (with denominator), OOD AUROC & AUPR. | `src/evaluate.py`, `reports/metrics/*`, `reports/figures/*` | Actual metrics saved to JSON/CSV and plotted; pending state displayed honestly prior to training. |
| **REQ-09** | Clean botanical Streamlit application with 8 sections, genuine model integration, `UNCERTAIN` handling, and mandatory safety disclaimer. | `app.py`, `pages/*`, `auth/authentication.py`, `assets/styles/botanical.css` | All 8 pages functional, connected to `MediLeafPredictor`, honest empty/pending states, zero fabricated results. |
| **REQ-10** | Reproducibility, automated tests, and honest limitation documentation (CA-1 30-mark readiness). | `tests/*`, `README.md`, `PROJECT_BLUEPRINT.md` | Unit tests covering validation, transforms, model head, rejection logic, OOD isolation, and error handling. |

---

## 2. Dataset Verification & Ambiguity Log

### Verified Mendeley Public API Record (Queried Live)
- **Dataset Title:** Indian Medicinal Leaves Image Datasets
- **Mendeley Record ID & Version:** `748f8jkphb` — Version `3` (Published `2023-05-05`)
- **DOI:** `10.17632/748f8jkphb.3`
- **URL:** `https://data.mendeley.com/datasets/748f8jkphb/3`
- **Contributors:** Pushpa B R, Shobha Rani (Amrita Vishwa Vidyapeetham)
- **Licence:** Creative Commons Attribution 4.0 International (`CC BY 4.0`)
- **Description (from Mendeley):** *"Indian Medicinal plant datasets is a repository that consists of medicinal plants images. The images are captured with varying background without any environment constraints."*

### Explicit Ambiguities & Non-Assumptions
1. **Poisonous Species Coverage:** Neither the faculty PDF nor the Mendeley Version 3 title/description establishes that poisonous plant species are included in the archive. No poisonous-species coverage is claimed unless `scripts/inspect_dataset.py` verifies specific toxic taxa in the extracted folders.
2. **Folder Naming & Leaf vs. Whole-Plant:** Folder names in `data/raw/` must not be assumed to be clean botanical binomials or strictly single-leaf photographs until inspected by `scripts/inspect_dataset.py`.
3. **External Dependencies:** Training ResNet50 requires downloading the dataset archive (~several GB) into `data/raw/` and executing `notebooks/medicinal_leaf_identifier_colab.ipynb` on a CUDA GPU (Google Colab recommended) or local GPU workstation.

---

## 3. Complete 12-Phase Roadmap Mapped to 6 Execution Steps

| Major Step | Original PDF Phases | Key Deliverables |
|---|---|---|
| **Step 1: Dataset Collection & Verification** | Phase 1 (Environment Setup), Phase 2 (Dataset Collection & Understanding) | `requirements.txt`, `scripts/inspect_dataset.py`, `reports/dataset/*` |
| **Step 2: Dataset Preparation & Species Splitting** | Phase 3 (Species Split & Leakage Check), Phase 4 (CV Image Processing) | `scripts/prepare_dataset.py`, `src/data.py`, `data/processed/*_manifest.csv`, `artifacts/class_mapping.json` |
| **Step 3: ResNet50 Model Development & Optimization** | Phase 5 (CNN Development & Fine-Tuning), Phase 6 (Model Optimization) | `src/model.py`, `src/train.py`, `notebooks/medicinal_leaf_identifier_colab.ipynb`, `artifacts/best_model.pth` |
| **Step 4: Confidence Rejection, OOD & Evaluation** | Phase 7 (Confidence Gating), Phase 8 (OOD Detection), Phase 9 (Evaluation) | `src/reject.py`, `src/evaluate.py`, `reports/metrics/*`, `reports/figures/*` |
| **Step 5: Complete MEDILEAF.AI Frontend & Integration** | Phase 10 (Inference Pipeline), Phase 11 (Streamlit Application) | `src/inference.py`, `auth/authentication.py`, `app.py`, `pages/*`, `assets/*` |
| **Step 6: End-to-End Testing & Documentation** | Phase 12 (Integration & System Testing) | `tests/*`, `README.md`, `PROJECT_BLUEPRINT.md`, CA-1 presentation & viva evidence |

---

## 4. Progress Status Tracker (Distinguishing Code Implemented vs. Executed/Verified)

> Status legend: `IMPLEMENTED` (code authored cleanly) · `EXECUTED` (run on real data/runtime) · `VERIFIED` (tests/outputs checked) · `PENDING_EXTERNAL` (awaits dataset archive / Colab GPU training)

| # | Workstream | Current Status | Notes |
|---|---|---|---|
| 1 | Dataset metadata verification (Mendeley API) | `VERIFIED` | Verified `748f8jkphb` v3, DOI `10.17632/748f8jkphb.3`, CC BY 4.0 |
| 2 | Dataset archive inspection (`inspect_dataset.py`) | `IMPLEMENTED` | Awaits local/Colab archive in `data/raw/` to execute |
| 3 | Species splitting & duplicate leakage check (`prepare_dataset.py`) | `IMPLEMENTED` | Reproducible seed + SHA-256 leakage check ready |
| 4 | Image preprocessing & PyTorch Dataset (`src/data.py`) | `IMPLEMENTED` | Deterministic eval transform shared with inference |
| 5 | ResNet50 model & transfer learning (`src/model.py`, `src/train.py`) | `IMPLEMENTED` | Two-stage fine-tuning + Colab GPU notebook ready |
| 6 | Model training & optimization | `PENDING_EXTERNAL` | Requires GPU + Mendeley dataset in Colab/local |
| 7 | Reject mechanism & validation calibration (`src/reject.py`) | `IMPLEMENTED` | MSP + Energy-based OOD scoring implemented |
| 8 | Held-out OOD evaluation & metrics (`src/evaluate.py`) | `IMPLEMENTED` | AUROC, AUPR, Coverage, Selective Accuracy ready |
| 9 | Unified inference pipeline (`src/inference.py`) | `IMPLEMENTED` | Returns `MODEL_NOT_READY` honestly if checkpoint absent |
| 10 | Authentication & prediction history (`auth/authentication.py`) | `VERIFIED` | SQLite + PBKDF2-HMAC-SHA256 verified via `test_auth.py` |
| 11 | Streamlit 8-page MEDILEAF.AI UI (`app.py`, `pages/*`) | `IMPLEMENTED` | Matches reference botanical design + Dark/Light theme + fixed sidebar |
| 12 | Automated test suite (`tests/*`) | `IMPLEMENTED` | 3 stdlib test modules verified now; 5 ML modules ready for PyTorch env |
| 13 | AI Studio live workspace preview (`server.ts`, `src/*`) | `VERIFIED` | Compiles, typechecks & serves 8-page preview reading real workspace state |

---

## 5. Section 23 Verification Checklists

### Checklist A — Technical Requirement Checklist (7-Page Faculty PDF)
- [x] **REQ-PDF-01:** Fine-tuned PyTorch ResNet50 CNN (`src/model.py`, `src/train.py`, `notebooks/medicinal_leaf_identifier_colab.ipynb`).
- [x] **REQ-PDF-02:** Confidence-gating abstention layer returning `UNCERTAIN` (`src/reject.py`).
- [x] **REQ-PDF-03:** Validation-only threshold calibration (`calibrate_thresholds_on_validation` on `validation_manifest.csv`).
- [x] **REQ-PDF-04:** Species-wise split isolating held-out OOD species from training/validation/calibration (`scripts/prepare_dataset.py`).
- [x] **REQ-PDF-05:** Mendeley Indian Medicinal Leaves Dataset v3 (`10.17632/748f8jkphb.3`, `CC BY 4.0`) verified via API; poisonous coverage unverified until archive audit.
- [x] **REQ-PDF-06:** Fixed Python + PyTorch + Torchvision + OpenCV + Pillow + NumPy + Pandas + Matplotlib + Scikit-learn + Streamlit stack preserved; zero LLM vision replacement.
- [x] **REQ-PDF-07:** Identical deterministic preprocessing (`get_eval_transforms()`) shared between evaluation and inference.
- [x] **REQ-PDF-08:** Evaluation & abstention metrics (`Accuracy`, `Precision`, `Recall`, `F1`, `Confusion Matrix`, `Coverage`, `Selective Accuracy`, `Rejection Rate` with explicit denominator, `OOD AUROC/AUPR`).
- [ ] **REQ-PDF-09 (Pending External GPU + Archive):** Execute `scripts/inspect_dataset.py`, `scripts/prepare_dataset.py`, `src/train.py`, and `src/evaluate.py` on the downloaded Mendeley archive.

### Checklist B — Seven-Image Visual Replication Checklist
- [x] **Image 1 (`download_57161a44.png`) -> Home / Dashboard:** Permanent forest-green sidebar (`#053821`) with lime-green active highlight (`#9AE66E`), dark-emerald hero banner with leaf scanner reticle, 4 KPI cards, 3-tile Quick Actions, Recent Activity table, About strip, plus interactive 12-card **Computer Vision Architecture & Technologies** modal explorer.
- [x] **Image 2 (`f4b4f328...png`) -> Leaf Identification:** Dark-emerald `Identify a Leaf` hero banner, honest `Model Training Pending` banner (until `best_model.pth` exists), dashed upload dropzone with scanner-leaf illustration + `Choose Image` button, and 4 bottom feature cards (`Plant Identification`, `Uncertainty Handling`, `Model`, `Dataset`).
- [x] **Image 3 (`9ff64545...png`) -> Prediction History:** `Your Prediction History` emerald banner, 4 real KPI summary cards (`Total Predictions`, `Known (Accepted)`, `Uncertain (Rejected)`, `Last Prediction`), filter/search controls, `No predictions yet` empty state or live records table.
- [x] **Image 4 (`915b797b...png`) -> Model Analytics:** `Model Performance Analytics` banner with `ResNet50 (Transfer Learning)` badge, 6 color-coded KPI cards (`Accuracy`, `Precision`, `Recall`, `F1-Score`, `Coverage`, `Rejection Rate`), `Training & Validation Accuracy`, `Confusion Matrix`, and `OOD Evaluation` rows with info tooltips.
- [x] **Image 5 (`ac836ae5...png`) -> Dataset & Information:** `Dataset & Project Information` banner, striped `Dataset Details` card with `Mendeley Record` external link, `Class Distribution (Top 5)` chart or `Dataset not loaded` card with working `Load & Analyze Dataset` action, and `About the Project` footer card.
- [x] **Image 6 (`c84dfda3...png`) -> Settings & Help:** `Settings` & `Help & Support` pill tabs, 3-card `App Theme` selector (`Light`, `Dark`, `System`), `Notifications` & `Save Prediction History` toggles, `Change Password` + `Logout` buttons, and interactive `Need Help?` accordion.
- [x] **Image 7 (`21c357d4...png`) -> Login / Register:** Split emerald/white card, glowing leaf scanner emblem + 4 feature badges + safety disclaimer on left; centered MediLeaf AI icon, tagline, Login/Register segmented tabs, Email/Username & Password inputs, Remember me, Forgot password, and green Login button on right.

