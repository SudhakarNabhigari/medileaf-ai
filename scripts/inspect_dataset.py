"""Dataset inspection & quality verification script for MEDILEAF.AI.

Scans data/raw/ to inventory actual species folders, image counts, file sizes,
readability, dimensions, color modes, SHA-256 exact duplicates, and class imbalance.
Generates genuine reports under reports/dataset/ without fabricating any data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np
import pandas as pd
from PIL import Image, UnidentifiedImageError

from src.config import DATASET_REPORTS_DIR, RAW_DATA_DIR, SUPPORTED_EXTENSIONS, VERIFIED_DATASET_METADATA


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def discover_dataset_root(raw_dir: Path) -> Path:
    """Locate the directory whose direct subdirectories are species/class folders."""
    current = raw_dir
    for _ in range(3):
        subdirs = [p for p in current.iterdir() if p.is_dir() and not p.name.startswith(".")]
        files_in_subdirs = any(
            any(f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS for f in d.iterdir())
            for d in subdirs
        )
        if len(subdirs) >= 2 and files_in_subdirs:
            return current
        if len(subdirs) == 1:
            current = subdirs[0]
        else:
            break
    return raw_dir


def inspect_dataset(raw_dir: Path = RAW_DATA_DIR, reports_dir: Path = DATASET_REPORTS_DIR) -> Dict[str, object]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw dataset directory does not exist: {raw_dir}")

    dataset_root = discover_dataset_root(raw_dir)
    species_dirs = sorted(
        [d for d in dataset_root.iterdir() if d.is_dir() and not d.name.startswith(".")],
        key=lambda p: p.name.lower(),
    )

    if not species_dirs:
        raise RuntimeError(
            f"No species folders found under '{raw_dir}'. "
            "Extract the Mendeley Indian Medicinal Leaves dataset into data/raw/ first."
        )

    inventory_rows: List[Dict[str, object]] = []
    seen_hashes: Dict[str, str] = {}
    corrupted_files: List[str] = []
    zero_byte_files: List[str] = []
    unsupported_files: List[str] = []
    duplicate_pairs: List[Tuple[str, str]] = []
    modes_counter: Counter = Counter()

    for species_dir in species_dirs:
        species_name = species_dir.name
        for file_path in sorted(species_dir.rglob("*")):
            if not file_path.is_file():
                continue

            size_bytes = file_path.stat().st_size
            ext = file_path.suffix.lower()
            rel_path = str(file_path.as_posix())

            if size_bytes == 0:
                zero_byte_files.append(rel_path)
                inventory_rows.append(
                    {
                        "species": species_name,
                        "filepath": rel_path,
                        "filename": file_path.name,
                        "extension": ext,
                        "size_bytes": 0,
                        "width": 0,
                        "height": 0,
                        "mode": "",
                        "sha256": "",
                        "is_valid": False,
                        "is_duplicate": False,
                        "issue": "zero_byte",
                    }
                )
                continue

            if ext not in SUPPORTED_EXTENSIONS:
                unsupported_files.append(rel_path)
                inventory_rows.append(
                    {
                        "species": species_name,
                        "filepath": rel_path,
                        "filename": file_path.name,
                        "extension": ext,
                        "size_bytes": size_bytes,
                        "width": 0,
                        "height": 0,
                        "mode": "",
                        "sha256": "",
                        "is_valid": False,
                        "is_duplicate": False,
                        "issue": "unsupported_extension",
                    }
                )
                continue

            file_hash = compute_sha256(file_path)
            is_dup = file_hash in seen_hashes
            if is_dup:
                duplicate_pairs.append((rel_path, seen_hashes[file_hash]))
            else:
                seen_hashes[file_hash] = rel_path

            try:
                raw_bytes = file_path.read_bytes()
                cv_buf = np.frombuffer(raw_bytes, dtype=np.uint8)
                cv_img = cv2.imdecode(cv_buf, cv2.IMREAD_COLOR)
                if cv_img is None or cv_img.size == 0:
                    raise ValueError("Unreadable by OpenCV imdecode")

                with Image.open(file_path) as img:
                    img.verify()
                with Image.open(file_path) as img2:
                    w, h = img2.size
                    mode = img2.mode
                    modes_counter[mode] += 1
                inventory_rows.append(
                    {
                        "species": species_name,
                        "filepath": rel_path,
                        "filename": file_path.name,
                        "extension": ext,
                        "size_bytes": size_bytes,
                        "width": w,
                        "height": h,
                        "mode": mode,
                        "sha256": file_hash,
                        "is_valid": True,
                        "is_duplicate": is_dup,
                        "issue": "duplicate" if is_dup else "ok",
                    }
                )
            except (UnidentifiedImageError, OSError, ValueError):
                corrupted_files.append(rel_path)
                inventory_rows.append(
                    {
                        "species": species_name,
                        "filepath": rel_path,
                        "filename": file_path.name,
                        "extension": ext,
                        "size_bytes": size_bytes,
                        "width": 0,
                        "height": 0,
                        "mode": "",
                        "sha256": file_hash,
                        "is_valid": False,
                        "is_duplicate": is_dup,
                        "issue": "corrupted_unreadable",
                    }
                )

    if not inventory_rows:
        raise RuntimeError(f"No image files discovered under species folders in '{dataset_root}'.")

    inv_df = pd.DataFrame(inventory_rows)
    inv_df.to_csv(reports_dir / "dataset_inventory.csv", index=False)

    valid_df = inv_df[inv_df["is_valid"] == True]  # noqa: E712
    dist_df = (
        valid_df.groupby("species")
        .agg(
            valid_image_count=("filepath", "count"),
            mean_width=("width", "mean"),
            mean_height=("height", "mean"),
            duplicate_count=("is_duplicate", "sum"),
        )
        .reset_index()
        .sort_values("valid_image_count", ascending=False)
    )
    dist_df["mean_width"] = dist_df["mean_width"].round(1)
    dist_df["mean_height"] = dist_df["mean_height"].round(1)
    dist_df.to_csv(reports_dir / "class_distribution.csv", index=False)

    total_files = len(inv_df)
    total_valid = len(valid_df)
    total_species = int(dist_df["species"].nunique())
    min_count = int(dist_df["valid_image_count"].min()) if not dist_df.empty else 0
    max_count = int(dist_df["valid_image_count"].max()) if not dist_df.empty else 0
    imbalance_ratio = round(max_count / max(min_count, 1), 2)

    summary_payload = {
        **VERIFIED_DATASET_METADATA,
        "dataset_root": str(dataset_root.as_posix()),
        "total_species_folders": len(species_dirs),
        "valid_species_count": total_species,
        "total_files_scanned": total_files,
        "valid_image_count": total_valid,
        "corrupted_count": len(corrupted_files),
        "zero_byte_count": len(zero_byte_files),
        "unsupported_count": len(unsupported_files),
        "exact_duplicate_count": len(duplicate_pairs),
        "min_class_count": min_count,
        "max_class_count": max_count,
        "class_imbalance_ratio": imbalance_ratio,
        "color_modes": dict(modes_counter),
    }

    with (reports_dir / "dataset_metadata.json").open("w", encoding="utf-8") as fh:
        json.dump(summary_payload, fh, indent=2)

    # Markdown Reports
    summary_md = f"""# Dataset Summary Report

- **Dataset Name:** {VERIFIED_DATASET_METADATA['dataset_name']}
- **Source & Version:** {VERIFIED_DATASET_METADATA['source']} (Version {VERIFIED_DATASET_METADATA['version']})
- **DOI:** `{VERIFIED_DATASET_METADATA['doi']}`
- **Licence:** {VERIFIED_DATASET_METADATA['licence']}
- **Inspected Root:** `{dataset_root.as_posix()}`
- **Valid Species Count:** {total_species}
- **Valid Image Count:** {total_valid} (out of {total_files} scanned files)
- **Min / Max Images per Species:** {min_count} / {max_count} (Imbalance Ratio: {imbalance_ratio}x)
- **Poisonous Species Caution:** Folder labels reflect dataset directory names; botanical/toxicological classification must be verified explicitly before claiming poisonous-species coverage.
"""
    (reports_dir / "dataset_summary.md").write_text(summary_md, encoding="utf-8")

    quality_md = f"""# Dataset Quality Report

- **Corrupted / Unreadable Images:** {len(corrupted_files)}
- **Zero-Byte Files:** {len(zero_byte_files)}
- **Unsupported Extensions:** {len(unsupported_files)}
- **Exact SHA-256 Duplicates:** {len(duplicate_pairs)}
- **Image Modes Observed:** {dict(modes_counter)}

## Limitations Observed
1. Images are captured with varying natural backgrounds without strict laboratory lighting constraints.
2. Exact SHA-256 duplicates ({len(duplicate_pairs)}) must be deduplicated or kept within a single split to avoid data leakage.
3. Non-RGB images (if any) are converted to RGB during preprocessing.
"""
    (reports_dir / "dataset_quality_report.md").write_text(quality_md, encoding="utf-8")

    sample_lines = ["# Representative Sample Images Report\n", "| Species | Sample File | Dimensions | Mode |", "|---|---|---|---|"]
    for sp in dist_df["species"].head(15):
        row = valid_df[valid_df["species"] == sp].iloc[0]
        sample_lines.append(f"| {sp} | `{row['filename']}` | {row['width']}x{row['height']} | {row['mode']} |")
    (reports_dir / "sample_images_report.md").write_text("\n".join(sample_lines) + "\n", encoding="utf-8")

    return summary_payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect raw medicinal leaf dataset integrity.")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DATA_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DATASET_REPORTS_DIR)
    args = parser.parse_args()
    result = inspect_dataset(raw_dir=args.raw_dir, reports_dir=args.reports_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
