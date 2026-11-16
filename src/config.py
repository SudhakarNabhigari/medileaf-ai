"""Central configuration, verified dataset metadata, and path definitions for MEDILEAF.AI."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

ARTIFACTS_DIR = ROOT_DIR / "artifacts"
REPORTS_DIR = ROOT_DIR / "reports"
DATASET_REPORTS_DIR = REPORTS_DIR / "dataset"
METRICS_REPORTS_DIR = REPORTS_DIR / "metrics"
FIGURES_REPORTS_DIR = REPORTS_DIR / "figures"

ASSETS_DIR = ROOT_DIR / "assets"
DATABASE_PATH = ROOT_DIR / "medileaf.db"

# Artifact file paths
CHECKPOINT_PATH = ARTIFACTS_DIR / "best_model.pth"
CLASS_MAPPING_PATH = ARTIFACTS_DIR / "class_mapping.json"
TRAINING_HISTORY_PATH = ARTIFACTS_DIR / "training_history.csv"
TRAINING_CONFIG_PATH = ARTIFACTS_DIR / "training_config.json"
MODEL_METADATA_PATH = ARTIFACTS_DIR / "model_metadata.json"
REJECTION_CONFIG_PATH = ARTIFACTS_DIR / "rejection_config.json"

# Processed manifest paths
TRAIN_MANIFEST_PATH = PROCESSED_DATA_DIR / "train_manifest.csv"
VAL_MANIFEST_PATH = PROCESSED_DATA_DIR / "validation_manifest.csv"
KNOWN_TEST_MANIFEST_PATH = PROCESSED_DATA_DIR / "known_test_manifest.csv"
OOD_TEST_MANIFEST_PATH = PROCESSED_DATA_DIR / "ood_test_manifest.csv"
SPLIT_CONFIG_PATH = PROCESSED_DATA_DIR / "split_configuration.json"

# Image & preprocessing constants (ResNet50 IMAGENET1K_V2 standard)
IMAGE_SIZE: int = 224
RESIZE_SHORTER_SIDE: int = 256
IMAGENET_MEAN: Tuple[float, float, float] = (0.485, 0.456, 0.406)
IMAGENET_STD: Tuple[float, float, float] = (0.229, 0.224, 0.225)
SUPPORTED_EXTENSIONS: Tuple[str, ...] = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
UI_SUPPORTED_EXTENSIONS: Tuple[str, ...] = (".jpg", ".jpeg", ".png")
MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

RANDOM_SEED: int = 42

SAFETY_DISCLAIMER: str = (
    "MEDILEAF.AI is an academic plant-image identification prototype. "
    "Its predictions are not medical advice or confirmation of plant safety. "
    "Do not consume, touch, or use any plant based solely on this application's output. "
    "Consult a qualified botanist or relevant professional for verification."
)

# Verified live via Mendeley Data public API (https://data.mendeley.com/public-api/datasets/748f8jkphb?version=3)
VERIFIED_DATASET_METADATA: Dict[str, str] = {
    "dataset_name": "Indian Medicinal Leaves Image Datasets",
    "source": "Mendeley Data",
    "record_id": "748f8jkphb",
    "version": "3",
    "doi": "10.17632/748f8jkphb.3",
    "url": "https://data.mendeley.com/datasets/748f8jkphb/3",
    "licence": "CC BY 4.0 (Creative Commons Attribution 4.0 International)",
    "contributors": "Pushpa B R, Shobha Rani (Amrita Vishwa Vidyapeetham)",
    "publish_date": "2023-05-05",
    "poisonous_coverage_status": "Unverified — inspect extracted local archive before claiming poisonous-species coverage.",
}


@dataclass(frozen=True)
class TrainingHyperparameters:
    seed: int = RANDOM_SEED
    image_size: int = IMAGE_SIZE
    batch_size: int = 32
    num_workers: int = 2
    epochs_head: int = 5
    epochs_finetune: int = 20
    lr_head: float = 1e-3
    lr_backbone: float = 1e-4
    lr_classifier_finetune: float = 5e-4
    weight_decay: float = 1e-4
    label_smoothing: float = 0.05
    dropout: float = 0.3
    early_stopping_patience: int = 5
    lr_scheduler_patience: int = 2
    lr_scheduler_factor: float = 0.5
    unfreeze_layers: Tuple[str, ...] = ("layer3", "layer4", "fc")
    target_val_coverage: float = 0.90
    energy_temperature: float = 1.0


def ensure_project_directories() -> None:
    """Create standard project directories if they do not exist."""
    for path in (
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        ARTIFACTS_DIR,
        DATASET_REPORTS_DIR,
        METRICS_REPORTS_DIR,
        FIGURES_REPORTS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)
