"""Image validation, deterministic preprocessing, and PyTorch Dataset utilities."""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageOps, UnidentifiedImageError
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from src.config import (
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD,
    MAX_UPLOAD_SIZE_BYTES,
    RESIZE_SHORTER_SIDE,
    SUPPORTED_EXTENSIONS,
)


@dataclass
class ImageValidationResult:
    is_valid: bool
    error_message: Optional[str] = None
    width: int = 0
    height: int = 0
    mode: str = ""
    file_size_bytes: int = 0
    image: Optional[Image.Image] = None


def validate_image_bytes(
    data: bytes,
    filename: str = "upload.jpg",
    allowed_extensions: Tuple[str, ...] = SUPPORTED_EXTENSIONS,
    max_size_bytes: int = MAX_UPLOAD_SIZE_BYTES,
    min_dim: int = 32,
) -> ImageValidationResult:
    """Validate uploaded image bytes for non-emptiness, extension, size, and decodability."""
    if not data or len(data) == 0:
        return ImageValidationResult(is_valid=False, error_message="Uploaded file is empty (0 bytes).")

    if len(data) > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        return ImageValidationResult(
            is_valid=False,
            error_message=f"File exceeds maximum allowed size of {max_mb:.1f} MB.",
            file_size_bytes=len(data),
        )

    ext = Path(filename).suffix.lower()
    if ext not in allowed_extensions:
        return ImageValidationResult(
            is_valid=False,
            error_message=f"Unsupported file format '{ext or 'unknown'}'. Supported: {', '.join(allowed_extensions)}.",
            file_size_bytes=len(data),
        )

    # First verify via OpenCV decoding as well as Pillow to catch truncated/corrupted payloads
    np_buf = np.frombuffer(data, dtype=np.uint8)
    cv_img = cv2.imdecode(np_buf, cv2.IMREAD_COLOR)
    if cv_img is None or cv_img.size == 0:
        return ImageValidationResult(
            is_valid=False,
            error_message="Image appears corrupted or unreadable by OpenCV decoder.",
            file_size_bytes=len(data),
        )

    try:
        with Image.open(io.BytesIO(data)) as pil_img:
            pil_img.verify()
        with Image.open(io.BytesIO(data)) as pil_img_loaded:
            pil_img_loaded.load()
            oriented = ImageOps.exif_transpose(pil_img_loaded)
            rgb_img = oriented.convert("RGB")
            w, h = rgb_img.size
            if w < min_dim or h < min_dim:
                return ImageValidationResult(
                    is_valid=False,
                    error_message=f"Image dimensions ({w}x{h}) are too small (minimum {min_dim}x{min_dim}px).",
                    width=w,
                    height=h,
                    mode=pil_img_loaded.mode,
                    file_size_bytes=len(data),
                )
            return ImageValidationResult(
                is_valid=True,
                width=w,
                height=h,
                mode=rgb_img.mode,
                file_size_bytes=len(data),
                image=rgb_img,
            )
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        return ImageValidationResult(
            is_valid=False,
            error_message=f"Corrupted or invalid image file: {exc}",
            file_size_bytes=len(data),
        )


def validate_image_file(
    filepath: str | Path,
    allowed_extensions: Tuple[str, ...] = SUPPORTED_EXTENSIONS,
    max_size_bytes: int = MAX_UPLOAD_SIZE_BYTES,
) -> ImageValidationResult:
    """Validate an image file on disk."""
    path = Path(filepath)
    if not path.exists() or not path.is_file():
        return ImageValidationResult(is_valid=False, error_message=f"File not found: {path}")
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        return ImageValidationResult(is_valid=False, error_message=f"Failed reading file: {exc}")
    return validate_image_bytes(
        raw_bytes,
        filename=path.name,
        allowed_extensions=allowed_extensions,
        max_size_bytes=max_size_bytes,
    )


def get_train_transforms(image_size: int = IMAGE_SIZE) -> transforms.Compose:
    """Training-only augmentation pipeline matching ResNet50 RGB expectations."""
    return transforms.Compose(
        [
            transforms.RandomResizedCrop(image_size, scale=(0.75, 1.0), ratio=(0.85, 1.15)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.2),
            transforms.RandomRotation(degrees=20),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.15, hue=0.03),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )


def get_eval_transforms(
    image_size: int = IMAGE_SIZE,
    resize_shorter_side: int = RESIZE_SHORTER_SIDE,
) -> transforms.Compose:
    """Deterministic validation, test, OOD, and Streamlit inference transforms.

    MUST remain identical across training evaluation, Colab notebook, and app inference.
    """
    return transforms.Compose(
        [
            transforms.Resize(resize_shorter_side),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )


class MedicinalLeafDataset(Dataset):
    """PyTorch Dataset backed by a split manifest CSV."""

    def __init__(
        self,
        manifest_df: pd.DataFrame,
        class_to_idx: Optional[Dict[str, int]] = None,
        transform: Optional[transforms.Compose] = None,
        is_ood: bool = False,
    ) -> None:
        self.df = manifest_df.reset_index(drop=True).copy()
        self.class_to_idx = class_to_idx or {}
        self.transform = transform or get_eval_transforms()
        self.is_ood = is_ood

        if "filepath" not in self.df.columns or "species" not in self.df.columns:
            raise ValueError("Manifest DataFrame must contain 'filepath' and 'species' columns.")

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, int, str, str]:
        row = self.df.iloc[index]
        filepath = str(row["filepath"])
        species = str(row["species"])

        with Image.open(filepath) as img:
            rgb_img = ImageOps.exif_transpose(img).convert("RGB")

        tensor = self.transform(rgb_img)
        if self.is_ood:
            label = -1
        else:
            if species not in self.class_to_idx:
                raise KeyError(f"Species '{species}' missing from class_to_idx mapping.")
            label = int(self.class_to_idx[species])

        return tensor, label, species, filepath


def create_dataloader(
    manifest_path: str | Path,
    class_to_idx: Optional[Dict[str, int]],
    transform: transforms.Compose,
    batch_size: int = 32,
    shuffle: bool = False,
    num_workers: int = 2,
    is_ood: bool = False,
) -> DataLoader:
    """Build a DataLoader from a manifest CSV."""
    df = pd.read_csv(manifest_path)
    dataset = MedicinalLeafDataset(
        manifest_df=df,
        class_to_idx=class_to_idx,
        transform=transform,
        is_ood=is_ood,
    )
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )
