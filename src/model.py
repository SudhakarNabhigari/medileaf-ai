"""ResNet50 transfer-learning model definition and checkpoint utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

import torch
import torch.nn as nn
from torchvision import models
from torchvision.models import ResNet50_Weights


def build_resnet50_classifier(
    num_classes: int,
    pretrained: bool = True,
    dropout: float = 0.3,
) -> nn.Module:
    """Create a ResNet50 classifier with replaced fully-connected head."""
    if num_classes < 2:
        raise ValueError(f"num_classes must be >= 2 for multi-class classification, got {num_classes}.")

    weights = ResNet50_Weights.IMAGENET1K_V2 if pretrained else None
    model = models.resnet50(weights=weights)
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(p=dropout),
        nn.Linear(in_features, num_classes),
    )
    return model


def freeze_backbone(model: nn.Module) -> None:
    """Freeze all parameters except the classification head (model.fc)."""
    for name, param in model.named_parameters():
        param.requires_grad = name.startswith("fc.")


def unfreeze_layers(model: nn.Module, layer_prefixes: Iterable[str] = ("layer3", "layer4", "fc")) -> None:
    """Selectively unfreeze specified ResNet50 blocks for fine-tuning."""
    prefixes = tuple(layer_prefixes)
    for name, param in model.named_parameters():
        param.requires_grad = any(name.startswith(f"{prefix}.") for prefix in prefixes)


def count_trainable_parameters(model: nn.Module) -> Tuple[int, int]:
    """Return (trainable_params, total_params)."""
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return trainable, total


def save_checkpoint(
    model: nn.Module,
    checkpoint_path: str | Path,
    class_to_idx: Dict[str, int],
    epoch: int,
    val_accuracy: float,
    val_loss: float,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Persist model weights alongside exact class mapping and validation metrics."""
    path = Path(checkpoint_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    idx_to_class = {int(v): k for k, v in class_to_idx.items()}
    payload = {
        "architecture": "resnet50",
        "num_classes": len(class_to_idx),
        "class_to_idx": class_to_idx,
        "idx_to_class": idx_to_class,
        "epoch": int(epoch),
        "val_accuracy": float(val_accuracy),
        "val_loss": float(val_loss),
        "state_dict": model.state_dict(),
        "extra_metadata": extra_metadata or {},
    }
    torch.save(payload, path)


def load_checkpoint(
    checkpoint_path: str | Path,
    class_mapping_path: Optional[str | Path] = None,
    device: Optional[torch.device] = None,
) -> Tuple[nn.Module, Dict[int, str], Dict[str, Any]]:
    """Load ResNet50 checkpoint and verify consistency with class_mapping.json if provided."""
    ckpt_path = Path(checkpoint_path)
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Model checkpoint not found: {ckpt_path}")

    target_device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(ckpt_path, map_location=target_device, weights_only=False)

    if "state_dict" not in checkpoint or "num_classes" not in checkpoint:
        raise ValueError("Invalid checkpoint structure: missing 'state_dict' or 'num_classes'.")

    num_classes = int(checkpoint["num_classes"])
    class_to_idx = checkpoint.get("class_to_idx", {})

    if class_mapping_path is not None:
        map_path = Path(class_mapping_path)
        if not map_path.exists():
            raise FileNotFoundError(f"Class mapping file not found: {map_path}")
        with map_path.open("r", encoding="utf-8") as fh:
            mapping_data = json.load(fh)
        file_class_to_idx = mapping_data.get("class_to_idx", mapping_data)
        if len(file_class_to_idx) != num_classes:
            raise ValueError(
                f"Class mapping mismatch: checkpoint expects {num_classes} classes, "
                f"class_mapping.json has {len(file_class_to_idx)}."
            )
        if class_to_idx and file_class_to_idx != class_to_idx:
            raise ValueError("Class mapping index labels do not match checkpoint class_to_idx.")
        class_to_idx = file_class_to_idx

    if not class_to_idx:
        raise ValueError("No class_to_idx mapping found in checkpoint or class_mapping.json.")

    dropout = float(checkpoint.get("extra_metadata", {}).get("dropout", 0.3))
    model = build_resnet50_classifier(num_classes=num_classes, pretrained=False, dropout=dropout)
    model.load_state_dict(checkpoint["state_dict"])
    model.to(target_device)
    model.eval()

    idx_to_class = {int(idx): str(label) for label, idx in class_to_idx.items()}
    return model, idx_to_class, checkpoint
