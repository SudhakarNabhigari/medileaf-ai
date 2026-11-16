"""Unified ResNet50 + confidence-gating inference pipeline for CLI and Streamlit."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch

from src.config import (
    CHECKPOINT_PATH,
    CLASS_MAPPING_PATH,
    REJECTION_CONFIG_PATH,
    SUPPORTED_EXTENSIONS,
)
from src.data import get_eval_transforms, validate_image_bytes, validate_image_file
from src.model import load_checkpoint
from src.reject import RejectionConfig, compute_scores_from_logits, evaluate_rejection_rule


@dataclass
class PredictionOutput:
    status: str  # "ACCEPTED", "UNCERTAIN", "MODEL_NOT_READY", "INVALID_IMAGE"
    accepted: bool
    predicted_species: str
    raw_top_class: Optional[str]
    confidence: Optional[float]
    energy_score: Optional[float]
    entropy: Optional[float]
    threshold_used: Optional[float]
    gate_method: Optional[str]
    reason: str
    top_k: List[Dict[str, object]]
    image_width: int = 0
    image_height: int = 0

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class MediLeafPredictor:
    """Loads fine-tuned ResNet50 checkpoint, class mapping, and calibrated reject rule."""

    def __init__(
        self,
        checkpoint_path: Path = CHECKPOINT_PATH,
        class_mapping_path: Path = CLASS_MAPPING_PATH,
        rejection_config_path: Path = REJECTION_CONFIG_PATH,
        device: Optional[torch.device] = None,
    ) -> None:
        self.checkpoint_path = Path(checkpoint_path)
        self.class_mapping_path = Path(class_mapping_path)
        self.rejection_config_path = Path(rejection_config_path)
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.transform = get_eval_transforms()

        self.model: Optional[torch.nn.Module] = None
        self.idx_to_class: Dict[int, str] = {}
        self.rejection_config: Optional[RejectionConfig] = None
        self.ready_error: Optional[str] = None

        self._try_load()

    def _try_load(self) -> None:
        if not self.checkpoint_path.exists():
            self.ready_error = (
                f"Model checkpoint missing at '{self.checkpoint_path}'. "
                "Model training is pending (train via Google Colab GPU or src/train.py)."
            )
            return
        if not self.class_mapping_path.exists():
            self.ready_error = (
                f"Class mapping missing at '{self.class_mapping_path}'. "
                "Run scripts/prepare_dataset.py and model training first."
            )
            return

        try:
            model, idx_to_class, ckpt = load_checkpoint(
                self.checkpoint_path,
                class_mapping_path=self.class_mapping_path,
                device=self.device,
            )
            if self.rejection_config_path.exists():
                rej_cfg = RejectionConfig.load(self.rejection_config_path)
            else:
                # Fallback only if checkpoint trained without separate file; still honest & logged
                rej_cfg = RejectionConfig(
                    gate_method="msp",
                    msp_threshold=0.70,
                    calibrated_on="default_uncalibrated_fallback",
                )
            self.model = model
            self.idx_to_class = idx_to_class
            self.rejection_config = rej_cfg
            self.ready_error = None
        except Exception as exc:
            self.model = None
            self.ready_error = f"Failed loading trained model artifacts: {exc}"

    @property
    def is_ready(self) -> bool:
        return self.model is not None and self.rejection_config is not None and self.ready_error is None

    @torch.no_grad()
    def predict_bytes(
        self,
        image_bytes: bytes,
        filename: str = "upload.jpg",
        allowed_extensions: Tuple[str, ...] = SUPPORTED_EXTENSIONS,
        top_k: int = 3,
    ) -> PredictionOutput:
        validation = validate_image_bytes(
            image_bytes,
            filename=filename,
            allowed_extensions=allowed_extensions,
        )
        if not validation.is_valid or validation.image is None:
            return PredictionOutput(
                status="INVALID_IMAGE",
                accepted=False,
                predicted_species="INVALID",
                raw_top_class=None,
                confidence=None,
                energy_score=None,
                entropy=None,
                threshold_used=None,
                gate_method=None,
                reason=validation.error_message or "Invalid image upload.",
                top_k=[],
            )

        if not self.is_ready or self.model is None or self.rejection_config is None:
            return PredictionOutput(
                status="MODEL_NOT_READY",
                accepted=False,
                predicted_species="TRAINING_PENDING",
                raw_top_class=None,
                confidence=None,
                energy_score=None,
                entropy=None,
                threshold_used=None,
                gate_method=None,
                reason=self.ready_error or "Trained ResNet50 model artifacts are not available.",
                top_k=[],
                image_width=validation.width,
                image_height=validation.height,
            )

        tensor = self.transform(validation.image).unsqueeze(0).to(self.device)
        self.model.eval()
        logits = self.model(tensor)

        probs_np, _, _, _, _ = compute_scores_from_logits(
            logits, temperature=self.rejection_config.energy_temperature
        )
        decision = evaluate_rejection_rule(logits, self.idx_to_class, self.rejection_config)

        k = min(top_k, len(self.idx_to_class))
        probs_1d = probs_np[0]
        top_indices = probs_1d.argsort()[::-1][:k]
        top_k_list = [
            {
                "species": self.idx_to_class[int(idx)],
                "confidence": round(float(probs_1d[idx]), 6),
            }
            for idx in top_indices
        ]

        return PredictionOutput(
            status="ACCEPTED" if decision.accepted else "UNCERTAIN",
            accepted=decision.accepted,
            predicted_species=decision.predicted_label,
            raw_top_class=decision.raw_top_class,
            confidence=round(decision.confidence, 6),
            energy_score=round(decision.energy_score, 6),
            entropy=round(decision.entropy, 6),
            threshold_used=decision.threshold_used,
            gate_method=decision.gate_method,
            reason=decision.reason,
            top_k=top_k_list if decision.accepted else [],
            image_width=validation.width,
            image_height=validation.height,
        )

    def predict_file(self, filepath: str | Path, top_k: int = 3) -> PredictionOutput:
        validation = validate_image_file(filepath)
        if not validation.is_valid:
            return PredictionOutput(
                status="INVALID_IMAGE",
                accepted=False,
                predicted_species="INVALID",
                raw_top_class=None,
                confidence=None,
                energy_score=None,
                entropy=None,
                threshold_used=None,
                gate_method=None,
                reason=validation.error_message or "Invalid image file.",
                top_k=[],
            )
        return self.predict_bytes(Path(filepath).read_bytes(), filename=Path(filepath).name, top_k=top_k)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "ERROR", "reason": "Usage: python -m src.inference <image_path>"}))
        sys.exit(1)
    predictor = MediLeafPredictor()
    result = predictor.predict_file(sys.argv[1])
    print(json.dumps(result.to_dict(), indent=2))
