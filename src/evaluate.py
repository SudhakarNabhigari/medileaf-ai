"""Comprehensive evaluation for known-species classification, confidence rejection, and held-out OOD detection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from src.config import (
    CHECKPOINT_PATH,
    CLASS_MAPPING_PATH,
    FIGURES_REPORTS_DIR,
    KNOWN_TEST_MANIFEST_PATH,
    METRICS_REPORTS_DIR,
    OOD_TEST_MANIFEST_PATH,
    REJECTION_CONFIG_PATH,
    VAL_MANIFEST_PATH,
    ensure_project_directories,
)
from src.data import create_dataloader, get_eval_transforms
from src.model import load_checkpoint
from src.reject import (
    RejectionConfig,
    calibrate_thresholds_on_validation,
    compute_scores_from_logits,
    evaluate_rejection_rule,
)


@torch.no_grad()
def collect_logits_and_metadata(
    model: torch.nn.Module,
    loader: torch.utils.data.DataLoader,
    device: torch.device,
) -> Tuple[torch.Tensor, np.ndarray, List[str], List[str]]:
    model.eval()
    logits_list: List[torch.Tensor] = []
    labels_list: List[np.ndarray] = []
    species_list: List[str] = []
    paths_list: List[str] = []

    for images, labels, species, filepaths in loader:
        images = images.to(device, non_blocking=True)
        logits = model(images)
        logits_list.append(logits.cpu())
        labels_list.append(labels.numpy())
        species_list.extend(list(species))
        paths_list.extend(list(filepaths))

    return (
        torch.cat(logits_list, dim=0),
        np.concatenate(labels_list, axis=0),
        species_list,
        paths_list,
    )


def plot_confusion_matrix(
    cm: np.ndarray,
    class_names: List[str],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    size = max(8, min(18, len(class_names) * 0.35))
    fig, ax = plt.subplots(figsize=(size, size * 0.85), dpi=150)
    im = ax.imshow(cm, interpolation="nearest", cmap="Greens")
    ax.set_title("Known-Species Confusion Matrix (Raw Closed-Set Predictions)")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    if len(class_names) <= 30:
        ticks = np.arange(len(class_names))
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(class_names, rotation=90, fontsize=7)
        ax.set_yticklabels(class_names, fontsize=7)
    ax.set_xlabel("Predicted Class")
    ax.set_ylabel("True Class")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close(fig)


def plot_ood_curves(
    id_scores: np.ndarray,
    ood_scores: np.ndarray,
    score_name: str,
    output_path: Path,
) -> Tuple[float, float]:
    """Plot ROC & PR curves where positive class (1) = In-Distribution (known), negative (0) = OOD."""
    y_true = np.concatenate([np.ones_like(id_scores), np.zeros_like(ood_scores)])
    y_scores = np.concatenate([id_scores, ood_scores])

    auroc = float(roc_auc_score(y_true, y_scores))
    aupr = float(average_precision_score(y_true, y_scores))

    fpr, tpr, _ = roc_curve(y_true, y_scores)
    prec, rec, _ = precision_recall_curve(y_true, y_scores)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), dpi=150)
    axes[0].plot(fpr, tpr, color="#13823D", lw=2, label=f"{score_name} (AUROC = {auroc:.4f})")
    axes[0].plot([0, 1], [0, 1], linestyle="--", color="#9CA3AF")
    axes[0].set_title("ID vs Held-Out OOD ROC Curve")
    axes[0].set_xlabel("False Positive Rate (OOD Falsely Accepted)")
    axes[0].set_ylabel("True Positive Rate (Known Accepted)")
    axes[0].grid(alpha=0.25)
    axes[0].legend()

    axes[1].plot(rec, prec, color="#064E32", lw=2, label=f"{score_name} (AUPR = {aupr:.4f})")
    axes[1].set_title("ID vs Held-Out OOD Precision-Recall")
    axes[1].set_xlabel("Recall")
    axes[1].set_ylabel("Precision")
    axes[1].grid(alpha=0.25)
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close(fig)
    return auroc, aupr


def plot_confidence_ood_histogram(
    known_msp: np.ndarray,
    ood_msp: np.ndarray,
    known_energy: np.ndarray,
    ood_energy: np.ndarray,
    msp_threshold: float,
    output_path: Path,
) -> None:
    """Plot Known-Test vs Held-Out OOD distributions of MSP confidence and Free Energy."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), dpi=150)

    axes[0].hist(known_msp, bins=20, alpha=0.65, color="#13823D", label="Known Test", density=True)
    axes[0].hist(ood_msp, bins=20, alpha=0.65, color="#F4B740", label="Held-Out OOD", density=True)
    axes[0].axvline(msp_threshold, color="#053821", linestyle="--", linewidth=1.8, label=f"Calibrated tau={msp_threshold:.2f}")
    axes[0].set_title("MSP Confidence: Known vs Held-Out OOD")
    axes[0].set_xlabel("Maximum Softmax Probability")
    axes[0].set_ylabel("Density")
    axes[0].legend()
    axes[0].grid(alpha=0.2)

    axes[1].hist(-known_energy, bins=20, alpha=0.65, color="#13823D", label="Known Test (-E)", density=True)
    axes[1].hist(-ood_energy, bins=20, alpha=0.65, color="#F4B740", label="Held-Out OOD (-E)", density=True)
    axes[1].set_title("Negated Free Energy (-E): Known vs Held-Out OOD")
    axes[1].set_xlabel("Negated Energy (-E)")
    axes[1].set_ylabel("Density")
    axes[1].legend()
    axes[1].grid(alpha=0.2)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close(fig)


def run_evaluation(
    batch_size: int = 32,
    num_workers: int = 2,
    recalibrate_from_val: bool = False,
) -> Dict[str, object]:
    ensure_project_directories()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model, idx_to_class, _ = load_checkpoint(CHECKPOINT_PATH, CLASS_MAPPING_PATH, device=device)
    class_to_idx = {label: idx for idx, label in idx_to_class.items()}
    eval_transform = get_eval_transforms()

    if recalibrate_from_val or not REJECTION_CONFIG_PATH.exists():
        val_loader = create_dataloader(
            VAL_MANIFEST_PATH, class_to_idx, eval_transform, batch_size=batch_size, num_workers=num_workers
        )
        val_logits, val_labels, _, _ = collect_logits_and_metadata(model, val_loader, device)
        rej_cfg = calibrate_thresholds_on_validation(val_logits, val_labels)
        rej_cfg.save(REJECTION_CONFIG_PATH)
    else:
        rej_cfg = RejectionConfig.load(REJECTION_CONFIG_PATH)

    # Evaluate Known Test Partition
    known_loader = create_dataloader(
        KNOWN_TEST_MANIFEST_PATH, class_to_idx, eval_transform, batch_size=batch_size, num_workers=num_workers
    )
    known_logits, known_labels, known_species, known_paths = collect_logits_and_metadata(
        model, known_loader, device
    )
    _, known_msp, known_preds, known_energy, _ = compute_scores_from_logits(
        known_logits, temperature=rej_cfg.energy_temperature
    )

    known_decisions = [
        evaluate_rejection_rule(known_logits[i : i + 1], idx_to_class, rej_cfg)
        for i in range(known_logits.size(0))
    ]
    known_accepted_mask = np.array([d.accepted for d in known_decisions], dtype=bool)

    closed_set_acc = float(accuracy_score(known_labels, known_preds))
    macro_precision = float(precision_score(known_labels, known_preds, average="macro", zero_division=0))
    macro_recall = float(recall_score(known_labels, known_preds, average="macro", zero_division=0))
    macro_f1 = float(f1_score(known_labels, known_preds, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(known_labels, known_preds, average="weighted", zero_division=0))

    coverage = float(np.mean(known_accepted_mask)) if len(known_accepted_mask) > 0 else 0.0
    known_rejection_rate = 1.0 - coverage
    selective_accuracy = (
        float(accuracy_score(known_labels[known_accepted_mask], known_preds[known_accepted_mask]))
        if np.any(known_accepted_mask)
        else 0.0
    )

    ordered_classes = [idx_to_class[i] for i in range(len(idx_to_class))]
    cls_report = classification_report(
        known_labels,
        known_preds,
        labels=list(range(len(ordered_classes))),
        target_names=ordered_classes,
        output_dict=True,
        zero_division=0,
    )
    per_class_rows = [
        {
            "species": cls_name,
            "precision": round(cls_report[cls_name]["precision"], 6),
            "recall": round(cls_report[cls_name]["recall"], 6),
            "f1_score": round(cls_report[cls_name]["f1-score"], 6),
            "support": int(cls_report[cls_name]["support"]),
        }
        for cls_name in ordered_classes
    ]
    pd.DataFrame(per_class_rows).to_csv(METRICS_REPORTS_DIR / "per_class_metrics.csv", index=False)

    cm = confusion_matrix(known_labels, known_preds, labels=list(range(len(ordered_classes))))
    pd.DataFrame(cm, index=ordered_classes, columns=ordered_classes).to_csv(
        METRICS_REPORTS_DIR / "confusion_matrix.csv"
    )
    plot_confusion_matrix(cm, ordered_classes, FIGURES_REPORTS_DIR / "confusion_matrix.png")

    # Evaluate Held-Out OOD Species Partition
    ood_metrics: Dict[str, object] = {}
    decision_records: List[Dict[str, object]] = []

    for i, d in enumerate(known_decisions):
        decision_records.append(
            {
                "split": "known_test",
                "filepath": known_paths[i],
                "true_species": known_species[i],
                "predicted_label": d.predicted_label,
                "raw_top_class": d.raw_top_class,
                "accepted": d.accepted,
                "correct_raw": bool(known_preds[i] == known_labels[i]),
                "confidence": round(d.confidence, 6),
                "energy_score": round(d.energy_score, 6),
                "reason": d.reason,
            }
        )

    if OOD_TEST_MANIFEST_PATH.exists() and len(pd.read_csv(OOD_TEST_MANIFEST_PATH)) > 0:
        ood_loader = create_dataloader(
            OOD_TEST_MANIFEST_PATH,
            class_to_idx=None,
            transform=eval_transform,
            batch_size=batch_size,
            num_workers=num_workers,
            is_ood=True,
        )
        ood_logits, _, ood_species, ood_paths = collect_logits_and_metadata(model, ood_loader, device)
        _, ood_msp, _, ood_energy, _ = compute_scores_from_logits(
            ood_logits, temperature=rej_cfg.energy_temperature
        )
        ood_decisions = [
            evaluate_rejection_rule(ood_logits[i : i + 1], idx_to_class, rej_cfg)
            for i in range(ood_logits.size(0))
        ]
        ood_accepted_mask = np.array([d.accepted for d in ood_decisions], dtype=bool)
        ood_false_acceptance_rate = float(np.mean(ood_accepted_mask))
        ood_rejection_rate = 1.0 - ood_false_acceptance_rate

        msp_auroc, msp_aupr = plot_ood_curves(
            known_msp, ood_msp, "MSP Confidence", FIGURES_REPORTS_DIR / "ood_msp_curves.png"
        )
        energy_auroc, energy_aupr = plot_ood_curves(
            -known_energy, -ood_energy, "Negative Energy (-E)", FIGURES_REPORTS_DIR / "ood_energy_curves.png"
        )
        plot_confidence_ood_histogram(
            known_msp,
            ood_msp,
            known_energy,
            ood_energy,
            rej_cfg.msp_threshold,
            FIGURES_REPORTS_DIR / "confidence_ood_distribution.png",
        )

        total_samples = len(known_accepted_mask) + len(ood_accepted_mask)
        combined_rejected = int(np.sum(~known_accepted_mask) + np.sum(~ood_accepted_mask))
        overall_rejection_rate = combined_rejected / max(total_samples, 1)

        ood_metrics = {
            "ood_test_count": int(len(ood_accepted_mask)),
            "ood_rejection_rate": round(ood_rejection_rate, 6),
            "ood_false_acceptance_rate": round(ood_false_acceptance_rate, 6),
            "overall_rejection_rate_combined": round(overall_rejection_rate, 6),
            "msp_ood_auroc": round(msp_auroc, 6),
            "msp_ood_aupr": round(msp_aupr, 6),
            "energy_ood_auroc": round(energy_auroc, 6),
            "energy_ood_aupr": round(energy_aupr, 6),
            "mean_ood_confidence": round(float(np.mean(ood_msp)), 6),
        }

        for i, d in enumerate(ood_decisions):
            decision_records.append(
                {
                    "split": "ood_test",
                    "filepath": ood_paths[i],
                    "true_species": ood_species[i],
                    "predicted_label": d.predicted_label,
                    "raw_top_class": d.raw_top_class,
                    "accepted": d.accepted,
                    "correct_raw": False,
                    "confidence": round(d.confidence, 6),
                    "energy_score": round(d.energy_score, 6),
                    "reason": d.reason,
                }
            )

    pd.DataFrame(decision_records).to_csv(METRICS_REPORTS_DIR / "decision_log.csv", index=False)

    summary_metrics = {
        "known_test_count": int(len(known_labels)),
        "closed_set_accuracy": round(closed_set_acc, 6),
        "macro_precision": round(macro_precision, 6),
        "macro_recall": round(macro_recall, 6),
        "macro_f1": round(macro_f1, 6),
        "weighted_f1": round(weighted_f1, 6),
        "mean_known_confidence": round(float(np.mean(known_msp)), 6) if len(known_msp) > 0 else 0.0,
        "known_coverage": round(coverage, 6),
        "known_acceptance_rate": round(coverage, 6),
        "known_rejection_rate": round(known_rejection_rate, 6),
        "selective_accuracy": round(selective_accuracy, 6),
        "rejection_threshold_msp": rej_cfg.msp_threshold,
        "rejection_threshold_energy": rej_cfg.energy_threshold,
        "gate_method": rej_cfg.gate_method,
        "denominator_notes": {
            "known_rejection_rate": "Rejected known_test samples / Total known_test samples",
            "ood_rejection_rate": "Rejected ood_test samples / Total ood_test samples",
            "overall_rejection_rate_combined": "(Rejected known_test + Rejected ood_test) / (Total known_test + Total ood_test)",
        },
        **ood_metrics,
    }

    with (METRICS_REPORTS_DIR / "evaluation_summary.json").open("w", encoding="utf-8") as fh:
        json.dump(summary_metrics, fh, indent=2)

    return summary_metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate MEDILEAF.AI known & held-out OOD performance.")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--recalibrate", action="store_true")
    args = parser.parse_args()
    results = run_evaluation(
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        recalibrate_from_val=args.recalibrate,
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
