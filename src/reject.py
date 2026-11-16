"""Confidence gating, Energy-based OOD scoring, and validation-only threshold calibration."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F


@dataclass
class RejectionDecision:
    accepted: bool
    predicted_label: str
    raw_top_class: str
    confidence: float
    energy_score: float
    entropy: float
    threshold_used: float
    gate_method: str
    reason: str


@dataclass
class RejectionConfig:
    gate_method: str  # "msp" or "msp_and_energy"
    msp_threshold: float
    energy_threshold: Optional[float] = None
    energy_temperature: float = 1.0
    calibrated_on: str = "validation"
    target_val_coverage: float = 0.90
    val_selective_accuracy: float = 0.0
    val_coverage: float = 0.0

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as fh:
            json.dump(asdict(self), fh, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "RejectionConfig":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Rejection config not found: {p}")
        with p.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls(**data)


def compute_scores_from_logits(
    logits: torch.Tensor,
    temperature: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute softmax probabilities, MSP confidence, predicted indices, energy scores, and entropy.

    Energy score follows Liu et al. (NeurIPS 2020): E(x) = -T * logsumexp(f(x) / T).
    Lower (more negative) energy indicates stronger in-distribution support;
    higher (less negative) energy indicates higher OOD likelihood.
    We also expose negated_energy = -E(x) so higher values correlate with ID acceptance.
    """
    if temperature <= 0.0:
        raise ValueError(f"temperature must be > 0, got {temperature}.")
    if logits.ndim == 1:
        logits = logits.unsqueeze(0)
    if logits.size(0) == 0:
        raise ValueError("Cannot compute scores on empty logits tensor.")

    probs = F.softmax(logits, dim=-1)
    msp, pred_idx = torch.max(probs, dim=-1)
    energy = -temperature * torch.logsumexp(logits / temperature, dim=-1)
    entropy = -(probs * torch.clamp(probs, min=1e-12).log()).sum(dim=-1)

    return (
        probs.detach().cpu().numpy(),
        msp.detach().cpu().numpy(),
        pred_idx.detach().cpu().numpy(),
        energy.detach().cpu().numpy(),
        entropy.detach().cpu().numpy(),
    )


def calibrate_thresholds_on_validation(
    val_logits: torch.Tensor,
    val_labels: np.ndarray,
    target_coverage: float = 0.90,
    temperature: float = 1.0,
    gate_method: str = "msp_and_energy",
) -> RejectionConfig:
    """Calibrate acceptance thresholds strictly on known-species validation data.

    Never accepts test or OOD test data. Selects threshold(s) achieving >= target_coverage
    while maximizing validation selective accuracy (with a minimum MSP floor of 0.50
    when feasible, or best accuracy-coverage point).
    """
    if val_logits.size(0) == 0:
        raise ValueError("Validation logits cannot be empty during threshold calibration.")
    if len(val_labels) != val_logits.size(0):
        raise ValueError(
            f"Validation labels length ({len(val_labels)}) != logits rows ({val_logits.size(0)})."
        )
    if not (0.0 < target_coverage <= 1.0):
        raise ValueError(f"target_coverage must be in (0, 1], got {target_coverage}.")

    _, msp, pred_idx, energy, _ = compute_scores_from_logits(val_logits, temperature=temperature)
    correct = (pred_idx == val_labels).astype(np.float64)

    candidate_thresholds = np.round(np.linspace(0.30, 0.95, 66), 4)
    best_thresh = 0.50
    best_score = -1.0
    best_cov = 0.0
    best_sel_acc = 0.0

    for thresh in candidate_thresholds:
        accepted_mask = msp >= thresh
        cov = float(np.mean(accepted_mask))
        if cov == 0.0:
            continue
        sel_acc = float(np.mean(correct[accepted_mask]))
        # Prefer thresholds that stay near/above target_coverage while maximizing selective accuracy
        penalty = max(0.0, target_coverage - cov) * 2.0
        objective = sel_acc - penalty
        if objective > best_score:
            best_score = objective
            best_thresh = float(thresh)
            best_cov = cov
            best_sel_acc = sel_acc

    # Also compute energy cutoff corresponding to the accepted validation quantile
    energy_thresh: Optional[float] = None
    if gate_method == "msp_and_energy":
        # Accept samples whose energy <= calibrated upper percentile (e.g. 95th pct of correctly classified val)
        correct_mask = correct == 1.0
        ref_energy = energy[correct_mask] if np.any(correct_mask) else energy
        energy_thresh = float(np.quantile(ref_energy, min(0.98, max(0.80, target_coverage + 0.05))))

        combined_mask = (msp >= best_thresh) & (energy <= energy_thresh)
        if np.any(combined_mask):
            best_cov = float(np.mean(combined_mask))
            best_sel_acc = float(np.mean(correct[combined_mask]))

    return RejectionConfig(
        gate_method=gate_method,
        msp_threshold=round(best_thresh, 4),
        energy_threshold=round(energy_thresh, 4) if energy_thresh is not None else None,
        energy_temperature=temperature,
        calibrated_on="validation_manifest.csv",
        target_val_coverage=target_coverage,
        val_selective_accuracy=round(best_sel_acc, 4),
        val_coverage=round(best_cov, 4),
    )


def evaluate_rejection_rule(
    logits: torch.Tensor,
    idx_to_class: Dict[int, str],
    config: RejectionConfig,
) -> RejectionDecision:
    """Apply the calibrated confidence/energy abstention rule to a single image's logits."""
    _, msp_arr, pred_idx_arr, energy_arr, entropy_arr = compute_scores_from_logits(
        logits, temperature=config.energy_temperature
    )
    confidence = float(msp_arr[0])
    pred_idx = int(pred_idx_arr[0])
    energy_val = float(energy_arr[0])
    entropy_val = float(entropy_arr[0])
    raw_top_class = idx_to_class.get(pred_idx, f"Class_{pred_idx}")

    msp_pass = confidence >= config.msp_threshold
    energy_pass = True
    if config.gate_method == "msp_and_energy" and config.energy_threshold is not None:
        energy_pass = energy_val <= config.energy_threshold

    if msp_pass and energy_pass:
        return RejectionDecision(
            accepted=True,
            predicted_label=raw_top_class,
            raw_top_class=raw_top_class,
            confidence=confidence,
            energy_score=energy_val,
            entropy=entropy_val,
            threshold_used=config.msp_threshold,
            gate_method=config.gate_method,
            reason=(
                f"Accepted: confidence {confidence:.2%} >= calibrated threshold {config.msp_threshold:.2%}"
                + (
                    f" and energy {energy_val:.3f} <= {config.energy_threshold:.3f}."
                    if config.energy_threshold is not None
                    else "."
                )
            ),
        )

    reasons: List[str] = []
    if not msp_pass:
        reasons.append(
            f"max softmax confidence ({confidence:.2%}) is below calibrated threshold ({config.msp_threshold:.2%})"
        )
    if not energy_pass and config.energy_threshold is not None:
        reasons.append(
            f"OOD energy score ({energy_val:.3f}) exceeds calibrated in-distribution limit ({config.energy_threshold:.3f})"
        )

    return RejectionDecision(
        accepted=False,
        predicted_label="UNCERTAIN",
        raw_top_class=raw_top_class,
        confidence=confidence,
        energy_score=energy_val,
        entropy=entropy_val,
        threshold_used=config.msp_threshold,
        gate_method=config.gate_method,
        reason="Rejected (UNCERTAIN): " + "; ".join(reasons) + ".",
    )
