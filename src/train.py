"""Two-stage ResNet50 transfer learning & fine-tuning script for MEDILEAF.AI."""

from __future__ import annotations

import argparse
import json
import random
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from src.config import (
    ARTIFACTS_DIR,
    CHECKPOINT_PATH,
    CLASS_MAPPING_PATH,
    FIGURES_REPORTS_DIR,
    MODEL_METADATA_PATH,
    REJECTION_CONFIG_PATH,
    TRAINING_CONFIG_PATH,
    TRAINING_HISTORY_PATH,
    TRAIN_MANIFEST_PATH,
    VAL_MANIFEST_PATH,
    TrainingHyperparameters,
    ensure_project_directories,
)
from src.data import create_dataloader, get_eval_transforms, get_train_transforms
from src.model import (
    build_resnet50_classifier,
    count_trainable_parameters,
    freeze_backbone,
    save_checkpoint,
    unfreeze_layers,
)
from src.reject import calibrate_thresholds_on_validation


def set_reproducible_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def train_one_epoch(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> Tuple[float, float]:
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels, _, _ in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)
        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        running_loss += float(loss.item()) * images.size(0)
        preds = torch.argmax(logits, dim=1)
        correct += int((preds == labels).sum().item())
        total += int(images.size(0))

    avg_loss = running_loss / max(total, 1)
    avg_acc = correct / max(total, 1)
    return avg_loss, avg_acc


@torch.no_grad()
def evaluate_validation(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Tuple[float, float, torch.Tensor, np.ndarray]:
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_logits: List[torch.Tensor] = []
    all_labels: List[np.ndarray] = []

    for images, labels, _, _ in loader:
        images = images.to(device, non_blocking=True)
        labels_dev = labels.to(device, non_blocking=True)

        logits = model(images)
        loss = criterion(logits, labels_dev)

        running_loss += float(loss.item()) * images.size(0)
        preds = torch.argmax(logits, dim=1)
        correct += int((preds == labels_dev).sum().item())
        total += int(images.size(0))

        all_logits.append(logits.cpu())
        all_labels.append(labels.numpy())

    avg_loss = running_loss / max(total, 1)
    avg_acc = correct / max(total, 1)
    logits_tensor = torch.cat(all_logits, dim=0) if all_logits else torch.empty((0, 0))
    labels_arr = np.concatenate(all_labels, axis=0) if all_labels else np.array([], dtype=np.int64)
    return avg_loss, avg_acc, logits_tensor, labels_arr


def plot_training_curves(history_df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), dpi=150)

    epochs = history_df["epoch"]
    axes[0].plot(epochs, history_df["train_loss"], label="Train Loss", color="#13823D", linewidth=2)
    axes[0].plot(epochs, history_df["val_loss"], label="Validation Loss", color="#F4B740", linewidth=2)
    axes[0].set_title("Training & Validation Loss")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Cross-Entropy Loss")
    axes[0].grid(alpha=0.25)
    axes[0].legend()

    axes[1].plot(epochs, history_df["train_acc"], label="Train Accuracy", color="#13823D", linewidth=2)
    axes[1].plot(epochs, history_df["val_acc"], label="Validation Accuracy", color="#F4B740", linewidth=2)
    axes[1].set_title("Training & Validation Accuracy")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")
    axes[1].set_ylim(0.0, 1.02)
    axes[1].grid(alpha=0.25)
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close(fig)


def run_training(hp: TrainingHyperparameters) -> Dict[str, object]:
    ensure_project_directories()
    if not TRAIN_MANIFEST_PATH.exists() or not VAL_MANIFEST_PATH.exists():
        raise FileNotFoundError(
            "Split manifests not found. Run scripts/prepare_dataset.py before training."
        )
    if not CLASS_MAPPING_PATH.exists():
        raise FileNotFoundError(
            "artifacts/class_mapping.json not found. Run scripts/prepare_dataset.py first."
        )

    set_reproducible_seed(hp.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with CLASS_MAPPING_PATH.open("r", encoding="utf-8") as fh:
        mapping_payload = json.load(fh)
    class_to_idx: Dict[str, int] = mapping_payload.get("class_to_idx", mapping_payload)
    num_classes = len(class_to_idx)

    train_loader = create_dataloader(
        TRAIN_MANIFEST_PATH,
        class_to_idx=class_to_idx,
        transform=get_train_transforms(hp.image_size),
        batch_size=hp.batch_size,
        shuffle=True,
        num_workers=hp.num_workers,
    )
    val_loader = create_dataloader(
        VAL_MANIFEST_PATH,
        class_to_idx=class_to_idx,
        transform=get_eval_transforms(hp.image_size),
        batch_size=hp.batch_size,
        shuffle=False,
        num_workers=hp.num_workers,
    )

    model = build_resnet50_classifier(num_classes=num_classes, pretrained=True, dropout=hp.dropout)
    model.to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=hp.label_smoothing)
    history_rows: List[Dict[str, object]] = []
    best_val_loss = float("inf")
    best_val_acc = 0.0
    best_epoch = 0
    global_epoch = 0
    start_time = time.time()

    # Stage 1: Train newly attached classification head
    freeze_backbone(model)
    head_trainable, total_params = count_trainable_parameters(model)
    optimizer_head = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=hp.lr_head,
        weight_decay=hp.weight_decay,
    )

    for _ in range(hp.epochs_head):
        global_epoch += 1
        tr_loss, tr_acc = train_one_epoch(model, train_loader, criterion, optimizer_head, device)
        val_loss, val_acc, _, _ = evaluate_validation(model, val_loader, criterion, device)
        history_rows.append(
            {
                "epoch": global_epoch,
                "stage": "head_warmup",
                "train_loss": round(tr_loss, 6),
                "train_acc": round(tr_acc, 6),
                "val_loss": round(val_loss, 6),
                "val_acc": round(val_acc, 6),
                "lr": hp.lr_head,
            }
        )
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_val_acc = val_acc
            best_epoch = global_epoch
            save_checkpoint(
                model,
                CHECKPOINT_PATH,
                class_to_idx=class_to_idx,
                epoch=global_epoch,
                val_accuracy=val_acc,
                val_loss=val_loss,
                extra_metadata={"dropout": hp.dropout, "stage": "head_warmup"},
            )

    # Stage 2: Selectively unfreeze layer3, layer4, and fc with differential learning rates
    unfreeze_layers(model, hp.unfreeze_layers)
    ft_trainable, _ = count_trainable_parameters(model)
    backbone_params = [
        p for n, p in model.named_parameters() if p.requires_grad and not n.startswith("fc.")
    ]
    head_params = [
        p for n, p in model.named_parameters() if p.requires_grad and n.startswith("fc.")
    ]
    optimizer_ft = torch.optim.AdamW(
        [
            {"params": backbone_params, "lr": hp.lr_backbone},
            {"params": head_params, "lr": hp.lr_classifier_finetune},
        ],
        weight_decay=hp.weight_decay,
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer_ft,
        mode="min",
        factor=hp.lr_scheduler_factor,
        patience=hp.lr_scheduler_patience,
    )

    no_improve_epochs = 0
    for _ in range(hp.epochs_finetune):
        global_epoch += 1
        tr_loss, tr_acc = train_one_epoch(model, train_loader, criterion, optimizer_ft, device)
        val_loss, val_acc, _, _ = evaluate_validation(model, val_loader, criterion, device)
        scheduler.step(val_loss)
        current_lr = float(optimizer_ft.param_groups[0]["lr"])

        history_rows.append(
            {
                "epoch": global_epoch,
                "stage": "fine_tuning",
                "train_loss": round(tr_loss, 6),
                "train_acc": round(tr_acc, 6),
                "val_loss": round(val_loss, 6),
                "val_acc": round(val_acc, 6),
                "lr": current_lr,
            }
        )

        if val_loss < best_val_loss - 1e-4:
            best_val_loss = val_loss
            best_val_acc = val_acc
            best_epoch = global_epoch
            no_improve_epochs = 0
            save_checkpoint(
                model,
                CHECKPOINT_PATH,
                class_to_idx=class_to_idx,
                epoch=global_epoch,
                val_accuracy=val_acc,
                val_loss=val_loss,
                extra_metadata={"dropout": hp.dropout, "stage": "fine_tuning"},
            )
        else:
            no_improve_epochs += 1
            if no_improve_epochs >= hp.early_stopping_patience:
                break

    history_df = pd.DataFrame(history_rows)
    history_df.to_csv(TRAINING_HISTORY_PATH, index=False)
    plot_training_curves(history_df, FIGURES_REPORTS_DIR / "training_curves.png")

    # Reload best validation checkpoint and calibrate rejection thresholds on validation data ONLY
    best_ckpt = torch.load(CHECKPOINT_PATH, map_location=device, weights_only=False)
    model.load_state_dict(best_ckpt["state_dict"])
    _, _, val_logits, val_labels = evaluate_validation(model, val_loader, criterion, device)

    rejection_cfg = calibrate_thresholds_on_validation(
        val_logits=val_logits,
        val_labels=val_labels,
        target_coverage=hp.target_val_coverage,
        temperature=hp.energy_temperature,
        gate_method="msp_and_energy",
    )
    rejection_cfg.save(REJECTION_CONFIG_PATH)

    # Overfitting / underfitting diagnostic summary
    final_row = history_df.iloc[-1]
    generalization_gap = float(final_row["train_acc"] - final_row["val_acc"])
    fit_diagnosis = (
        "Potential overfitting (train-val accuracy gap > 10%)"
        if generalization_gap > 0.10
        else "Underfitting warning (validation accuracy < 60%)"
        if best_val_acc < 0.60
        else "Well-regularized convergence"
    )

    elapsed_sec = round(time.time() - start_time, 2)
    with TRAINING_CONFIG_PATH.open("w", encoding="utf-8") as fh:
        json.dump(asdict(hp), fh, indent=2)

    metadata = {
        "model_name": "ResNet50",
        "pretrained_weights": "ResNet50_Weights.IMAGENET1K_V2",
        "status": "READY",
        "num_known_classes": num_classes,
        "best_epoch": best_epoch,
        "total_epochs_run": global_epoch,
        "best_val_accuracy": round(best_val_acc, 6),
        "best_val_loss": round(best_val_loss, 6),
        "generalization_gap": round(generalization_gap, 6),
        "fit_diagnosis": fit_diagnosis,
        "head_trainable_params": head_trainable,
        "finetune_trainable_params": ft_trainable,
        "total_params": total_params,
        "device_used": str(device),
        "training_duration_seconds": elapsed_sec,
        "rejection_config": asdict(rejection_cfg),
    }
    with MODEL_METADATA_PATH.open("w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)

    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and fine-tune MEDILEAF.AI ResNet50 classifier.")
    parser.add_argument("--epochs-head", type=int, default=5)
    parser.add_argument("--epochs-finetune", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--target-coverage", type=float, default=0.90)
    args = parser.parse_args()

    hp = TrainingHyperparameters(
        seed=args.seed,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        epochs_head=args.epochs_head,
        epochs_finetune=args.epochs_finetune,
        target_val_coverage=args.target_coverage,
    )
    summary = run_training(hp)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
