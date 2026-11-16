"""Canonical Computer Vision Architecture & Technologies catalog with real disk verification."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from src.config import (
    ARTIFACTS_DIR,
    CHECKPOINT_PATH,
    CLASS_MAPPING_PATH,
    DATASET_REPORTS_DIR,
    METRICS_REPORTS_DIR,
    MODEL_METADATA_PATH,
    REJECTION_CONFIG_PATH,
    ROOT_DIR,
    TRAINING_HISTORY_PATH,
)


@dataclass(frozen=True)
class CVTechnologyCard:
    key: str
    short_title: str
    full_name: str
    category: str
    summary: str
    what_is_this: str
    why_used: str
    how_it_works: str
    where_used_in_medileaf: str
    module_path: str
    what_happens_when_runs: str
    status: str  # "IMPLEMENTED" | "VERIFIED" | "NOT IMPLEMENTED"
    status_detail: str


def _file_exists(rel_path: str) -> bool:
    return (ROOT_DIR / rel_path).exists()


def _model_is_verified() -> bool:
    if not CHECKPOINT_PATH.exists() or not MODEL_METADATA_PATH.exists():
        return False
    try:
        meta = json.loads(MODEL_METADATA_PATH.read_text(encoding="utf-8"))
        return meta.get("status") == "READY"
    except Exception:
        return False


def _eval_is_verified() -> bool:
    return (METRICS_REPORTS_DIR / "evaluation_summary.json").exists()


def _dataset_is_verified() -> bool:
    return (DATASET_REPORTS_DIR / "dataset_metadata.json").exists()


def get_cv_technologies() -> List[CVTechnologyCard]:
    """Return all 12 CV technologies with honest, artifact-verified statuses."""
    model_ok = _model_is_verified()
    eval_ok = _eval_is_verified()
    data_ok = _dataset_is_verified()
    rej_ok = REJECTION_CONFIG_PATH.exists() and eval_ok
    train_hist_ok = TRAINING_HISTORY_PATH.exists() and model_ok

    def _status(implemented: bool, verified: bool) -> str:
        if not implemented:
            return "NOT IMPLEMENTED"
        return "VERIFIED" if verified else "IMPLEMENTED"

    return [
        CVTechnologyCard(
            key="cnn",
            short_title="CNN",
            full_name="Convolutional Neural Network",
            category="Deep Learning Backbone",
            summary="Spatial feature extractor learning leaf veins, margins, and texture patterns.",
            what_is_this="A deep neural network architecture built with convolutional filters that detect hierarchical visual patterns (edges, venation, lobes, and leaf surface textures) directly from RGB pixel grids.",
            why_used="Medicinal plant leaves have fine morphological cues—serrated margins, midrib angles, and secondary vein branching—that spatial convolutions capture far more reliably than handcrafted color histograms.",
            how_it_works="Convolutional kernels slide across the 224x224 image to build feature maps, followed by batch normalization, non-linear activations (ReLU), pooling layers, and a final linear classifier.",
            where_used_in_medileaf="Core feature extraction and classification stage for every uploaded leaf image during both training and real-time inference.",
            module_path="src/model.py · build_resnet50_classifier()",
            what_happens_when_runs="The 3x224x224 leaf tensor passes through 50 convolutional/residual layers to produce raw class logits across all known training species.",
            status=_status(_file_exists("src/model.py"), model_ok),
            status_detail="Executed & checkpoint verified" if model_ok else "Implemented in src/model.py; awaiting GPU training checkpoint",
        ),
        CVTechnologyCard(
            key="resnet50",
            short_title="ResNet50",
            full_name="50-Layer Residual Network",
            category="CNN Architecture",
            summary="50-layer residual CNN with skip connections preventing vanishing gradients.",
            what_is_this="A 50-layer deep convolutional architecture introduced by He et al. that uses identity skip (residual) connections across bottleneck blocks.",
            why_used="Deeper networks learn richer botanical representations, and residual shortcut connections allow stable gradient flow during fine-tuning without degradation.",
            how_it_works="Each bottleneck block computes F(x) + x, allowing gradients to flow directly through skip pathways while learning fine residual refinements for leaf shapes and textures.",
            where_used_in_medileaf="Selected fixed CNN classifier architecture across training, Colab notebook, OOD evaluation, and Streamlit inference.",
            module_path="src/model.py · torchvision.models.resnet50",
            what_happens_when_runs="Extracts a 2048-dimensional leaf embedding vector before the Dropout(0.3) + Linear(2048, num_known_classes) classification head.",
            status=_status(_file_exists("src/model.py"), model_ok),
            status_detail="Trained ResNet50 weights verified" if model_ok else "ResNet50 architecture implemented; awaiting best_model.pth",
        ),
        CVTechnologyCard(
            key="transfer_learning",
            short_title="Transfer Learning",
            full_name="Two-Stage Transfer Learning & Fine-Tuning",
            category="Training Strategy",
            summary="ImageNet IMAGENET1K_V2 weights adapted via head warmup and selective unfreezing.",
            what_is_this="Reusing visual representations learned on 1.2M ImageNet images and adapting them to Indian medicinal leaf species via staged training.",
            why_used="Training a 25M-parameter CNN from scratch on thousands of leaf photos risks overfitting; ImageNet filters already encode strong edge, texture, and shape priors.",
            how_it_works="Stage 1 freezes the backbone and trains only the new classification head. Stage 2 selectively unfreezes layer3, layer4, and fc with differential learning rates and ReduceLROnPlateau.",
            where_used_in_medileaf="Two-stage training loop with early stopping and validation checkpoint selection.",
            module_path="src/train.py · run_training() / src/model.py",
            what_happens_when_runs="Freezes/unfreezes ResNet50 parameter groups, optimizes CrossEntropyLoss with AdamW, and saves the lowest validation-loss checkpoint.",
            status=_status(_file_exists("src/train.py"), train_hist_ok),
            status_detail="Training history & checkpoint verified" if train_hist_ok else "Two-stage trainer implemented; run Colab GPU notebook to execute",
        ),
        CVTechnologyCard(
            key="preprocessing",
            short_title="Image Preprocessing",
            full_name="Deterministic ResNet50 Image Preprocessing",
            category="Computer Vision Pipeline",
            summary="EXIF orientation, RGB conversion, 256 resize, 224x224 crop, ImageNet normalization.",
            what_is_this="Standardized pixel-level preparation ensuring every uploaded leaf photograph matches the exact spatial resolution and color statistics expected by ResNet50.",
            why_used="Mismatched preprocessing between training and Streamlit inference silently destroys accuracy and distorts confidence scores.",
            how_it_works="Applies EXIF auto-orientation, converts to 3-channel RGB, resizes shorter side to 256px, center-crops to 224x224, converts to float32 tensor [0,1], and normalizes with ImageNet mean/std.",
            where_used_in_medileaf="Shared identically across validation, known test, held-out OOD evaluation, Colab notebook, and Streamlit inference.",
            module_path="src/data.py · get_eval_transforms()",
            what_happens_when_runs="Transforms any validated JPG/PNG upload into an exact (1, 3, 224, 224) normalized PyTorch tensor.",
            status=_status(_file_exists("src/data.py"), data_ok or model_ok),
            status_detail="Verified on dataset/evaluation pipeline" if (data_ok or model_ok) else "Deterministic transforms active in src/data.py & src/inference.py",
        ),
        CVTechnologyCard(
            key="augmentation",
            short_title="Data Augmentation",
            full_name="Training-Only Geometric & Photometric Augmentation",
            category="Generalization",
            summary="RandomResizedCrop, H/V flips, +/-20 deg rotation, and ColorJitter on training split only.",
            what_is_this="On-the-fly random transformations applied strictly to training images so the network learns invariant leaf features across camera angles and lighting.",
            why_used="Mendeley field leaf images have varying backgrounds, orientations, and lighting; augmentation prevents memorizing background artifacts.",
            how_it_works="Applies RandomResizedCrop(224, scale=(0.75,1.0)), RandomHorizontalFlip(0.5), RandomVerticalFlip(0.2), RandomRotation(20), and mild ColorJitter during training epochs only.",
            where_used_in_medileaf="Training DataLoader only — validation, test, OOD, and inference never apply random augmentation.",
            module_path="src/data.py · get_train_transforms()",
            what_happens_when_runs="Generates a fresh randomly oriented/lit 224x224 view of each training leaf image on every epoch.",
            status=_status(_file_exists("src/data.py"), train_hist_ok),
            status_detail="Executed across training epochs" if train_hist_ok else "Configured in src/data.py; executed during src/train.py",
        ),
        CVTechnologyCard(
            key="softmax",
            short_title="Softmax Probability",
            full_name="Softmax Class Probability & Maximum Confidence",
            category="Decision Scoring",
            summary="Converts raw CNN logits into normalized class probabilities and extracts MSP.",
            what_is_this="The softmax function maps unnormalized logit scores z_i into a probability distribution summing to 1.0 across all known training species.",
            why_used="Raw logits vary in scale across batches; Maximum Softmax Probability (MSP = max_i P(y=i|x)) provides an interpretable baseline confidence score.",
            how_it_works="Computes exp(z_i) / sum_j exp(z_j) over the K known classes and extracts the top predicted class index, MSP confidence, and predictive entropy.",
            where_used_in_medileaf="Confidence calculation step immediately after the ResNet50 forward pass.",
            module_path="src/reject.py · compute_scores_from_logits()",
            what_happens_when_runs="Outputs probabilities, MSP confidence, predicted class index, and Shannon entropy for downstream abstention checks.",
            status=_status(_file_exists("src/reject.py"), eval_ok),
            status_detail="Calibrated & evaluated on test/OOD splits" if eval_ok else "Implemented in src/reject.py & src/inference.py",
        ),
        CVTechnologyCard(
            key="rejection",
            short_title="Confidence Rejection",
            full_name="Validation-Calibrated Confidence Gating (Reject Option)",
            category="Uncertainty Handling",
            summary="Abstains with UNCERTAIN whenever calibrated MSP or Energy criteria fail.",
            what_is_this="A selective classification decision layer that chooses between returning a known species label or abstaining with UNCERTAIN.",
            why_used="A standard closed-set CNN always forces one of its trained labels even on unrecognizable or blurry photos. Abstention prevents overconfident guessing.",
            how_it_works="Grid-searches MSP threshold and energy cutoff strictly on validation_manifest.csv to optimize selective accuracy at target coverage, never tuning on test/OOD sets.",
            where_used_in_medileaf="Every evaluation run and every user prediction on the Leaf Identification page.",
            module_path="src/reject.py · calibrate_thresholds_on_validation(), evaluate_rejection_rule()",
            what_happens_when_runs="Accepts prediction only if MSP >= calibrated threshold AND Energy <= calibrated limit; otherwise returns UNCERTAIN with reason.",
            status=_status(_file_exists("src/reject.py"), rej_ok),
            status_detail="Validation thresholds calibrated & evaluated" if rej_ok else "Abstention gate implemented; calibration runs at end of training",
        ),
        CVTechnologyCard(
            key="ood",
            short_title="OOD Detection",
            full_name="Out-of-Distribution & Held-Out Species Evaluation",
            category="Open-Set Safety",
            summary="MSP + Energy score (-T*logsumexp) evaluated on completely unseen held-out species.",
            what_is_this="Detecting inputs drawn from outside the training species distribution—specifically leaf species withheld completely from training, validation, and calibration.",
            why_used="Evaluating only on known species hides open-set failure; held-out species testing measures how often unfamiliar plants are safely rejected vs falsely accepted.",
            how_it_works="Computes free energy E(x) = -T * logsumexp(logits / T) alongside MSP, comparing separation between known_test and ood_test via AUROC and AUPR.",
            where_used_in_medileaf="Species-isolated OOD split and evaluation protocol.",
            module_path="scripts/prepare_dataset.py, src/reject.py, src/evaluate.py",
            what_happens_when_runs="Scores held-out unseen species and reports OOD Rejection Rate, OOD False Acceptance Rate, and MSP vs Energy AUROC/AUPR.",
            status=_status(_file_exists("src/evaluate.py"), eval_ok),
            status_detail="Held-out OOD AUROC/AUPR verified" if eval_ok else "OOD isolation & Energy scorer implemented; awaiting evaluation run",
        ),
        CVTechnologyCard(
            key="evaluation",
            short_title="Model Evaluation",
            full_name="Classification, Selective Accuracy & Abstention Analytics",
            category="Metrics & Reporting",
            summary="Accuracy, Macro P/R/F1, Confusion Matrix, Coverage, Selective Accuracy, AUROC/AUPR.",
            what_is_this="Quantitative assessment covering both closed-set species classification and selective abstention behavior across known and held-out OOD test sets.",
            why_used="Accuracy alone is misleading with a reject option—we must track how many known leaves are accepted (Coverage) and how accurate those accepted predictions are (Selective Accuracy).",
            how_it_works="Evaluates known_test_manifest.csv and ood_test_manifest.csv, clearly stating rejection rate denominators and saving CSV/JSON reports and Matplotlib figures.",
            where_used_in_medileaf="Populates Model Analytics charts, KPI cards, and CA-1 academic reports.",
            module_path="src/evaluate.py · run_evaluation()",
            what_happens_when_runs="Generates evaluation_summary.json, per_class_metrics.csv, decision_log.csv, confusion_matrix.png, and OOD ROC/PR curves.",
            status=_status(_file_exists("src/evaluate.py"), eval_ok),
            status_detail="Evaluation summary & figures generated" if eval_ok else "Evaluation suite implemented; pending trained checkpoint",
        ),
        CVTechnologyCard(
            key="pytorch",
            short_title="PyTorch",
            full_name="PyTorch + Torchvision Deep Learning Framework",
            category="Core Framework",
            summary="Tensors, DataLoaders, autograd, ResNet50 weights, and no_grad inference.",
            what_is_this="The core open-source deep learning framework powering dataset loading, GPU tensor operations, backpropagation, checkpoint serialization, and inference.",
            why_used="Required by the fixed CA-1 technology stack for transparent, reproducible model engineering and Torchvision ResNet50 support.",
            how_it_works="Loads IMAGENET1K_V2 weights, executes mixed/GPU training loops with AdamW and ReduceLROnPlateau, and runs eval-mode torch.no_grad() inference.",
            where_used_in_medileaf="Across data loading, model architecture, training, rejection scoring, evaluation, and Streamlit inference.",
            module_path="src/data.py, src/model.py, src/train.py, src/inference.py",
            what_happens_when_runs="Executes tensor transforms, forward/backward passes on GPU/CPU, and deterministic inference.",
            status=_status(_file_exists("src/train.py"), model_ok),
            status_detail="Verified in training & inference" if model_ok else "Integrated in src/*.py; awaiting Python/GPU runtime execution",
        ),
        CVTechnologyCard(
            key="opencv_pillow",
            short_title="OpenCV & Pillow",
            full_name="OpenCV (cv2) & Pillow (PIL) Image Engineering",
            category="Image I/O & Validation",
            summary="Corrupted-file detection, EXIF orientation, RGB decoding, and dataset auditing.",
            what_is_this="Dual-library image verification and decoding using OpenCV byte decoding and Pillow image verification/EXIF transposition.",
            why_used="Real datasets and user uploads can contain zero-byte, truncated, CMYK/RGBA, or wrongly rotated images that would crash naive pipelines.",
            how_it_works="cv2.imdecode checks raw byte decodability; PIL Image.verify() catches structural corruption; ImageOps.exif_transpose() and .convert('RGB') standardize orientation and channels.",
            where_used_in_medileaf="Dataset inventory inspection and every upload validation on Leaf Identification.",
            module_path="src/data.py · validate_image_bytes(), scripts/inspect_dataset.py",
            what_happens_when_runs="Rejects empty, oversized, unsupported, or corrupted uploads cleanly before touching the neural network.",
            status=_status(_file_exists("src/data.py") and _file_exists("scripts/inspect_dataset.py"), data_ok),
            status_detail="Verified on dataset archive audit" if data_ok else "Dual OpenCV+Pillow validation active in src/data.py",
        ),
        CVTechnologyCard(
            key="sklearn",
            short_title="Scikit-learn",
            full_name="Scikit-learn Metrics & Stratified Splitting",
            category="Statistical Validation",
            summary="Stratified train/val/test splitting, P/R/F1, confusion matrix, and ROC/PR AUROC.",
            what_is_this="Python's standard machine learning metrics and data-splitting library used for reproducible stratification and evaluation.",
            why_used="Ensures balanced class representation across known splits and rigorous computation of Macro F1, Confusion Matrix, AUROC, and AUPR.",
            how_it_works="Uses train_test_split(stratify=...) on known classes after isolating held-out OOD species, and computes sklearn.metrics reports on test predictions.",
            where_used_in_medileaf="Species-wise dataset splitting and OOD/known evaluation reporting.",
            module_path="scripts/prepare_dataset.py, src/evaluate.py",
            what_happens_when_runs="Produces stratified manifests and exact precision, recall, F1, confusion matrix, AUROC, and AUPR numbers.",
            status=_status(_file_exists("scripts/prepare_dataset.py") and _file_exists("src/evaluate.py"), eval_ok),
            status_detail="Metrics & splits verified" if eval_ok else "Implemented in prepare_dataset.py & evaluate.py",
        ),
    ]


if __name__ == "__main__":
    from dataclasses import asdict
    print(json.dumps([asdict(item) for item in get_cv_technologies()]))

