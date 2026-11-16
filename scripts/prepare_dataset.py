"""Reproducible species-wise splitting with strict held-out OOD isolation and duplicate leakage verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import (
    ARTIFACTS_DIR,
    CLASS_MAPPING_PATH,
    DATASET_REPORTS_DIR,
    KNOWN_TEST_MANIFEST_PATH,
    OOD_TEST_MANIFEST_PATH,
    PROCESSED_DATA_DIR,
    RANDOM_SEED,
    SPLIT_CONFIG_PATH,
    TRAIN_MANIFEST_PATH,
    VAL_MANIFEST_PATH,
)


def prepare_species_splits(
    inventory_csv: Path = DATASET_REPORTS_DIR / "dataset_inventory.csv",
    ood_species: Optional[List[str]] = None,
    ood_ratio: float = 0.20,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = RANDOM_SEED,
    deduplicate_by_hash: bool = True,
    min_samples_per_species: int = 4,
) -> Dict[str, object]:
    if not inventory_csv.exists():
        raise FileNotFoundError(
            f"Dataset inventory not found at '{inventory_csv}'. Run scripts/inspect_dataset.py first."
        )

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(inventory_csv)
    df = df[df["is_valid"] == True].copy()  # noqa: E712

    if deduplicate_by_hash and "sha256" in df.columns:
        df = df.drop_duplicates(subset=["sha256"], keep="first").reset_index(drop=True)

    species_counts = df["species"].value_counts()
    excluded_sparse_species = sorted(species_counts[species_counts < min_samples_per_species].index.tolist())
    if excluded_sparse_species:
        df = df[~df["species"].isin(excluded_sparse_species)].reset_index(drop=True)

    all_species = sorted(df["species"].unique().tolist())
    if len(all_species) < 4:
        raise ValueError(
            f"Need at least 4 species with >= {min_samples_per_species} images to build known + held-out OOD splits, found {len(all_species)}."
        )

    rng = np.random.default_rng(seed)
    if ood_species:
        held_out = sorted([s for s in ood_species if s in all_species])
        if not held_out:
            raise ValueError("None of the specified --ood-species exist in the eligible dataset inventory.")
    else:
        n_ood = max(1, int(round(len(all_species) * ood_ratio)))
        n_ood = min(n_ood, len(all_species) - 2)
        held_out = sorted(rng.choice(all_species, size=n_ood, replace=False).tolist())

    known_species = sorted([s for s in all_species if s not in set(held_out)])
    if len(known_species) < 2:
        raise ValueError("At least 2 known species must remain after holding out OOD species.")

    ood_df = df[df["species"].isin(held_out)].reset_index(drop=True)
    known_df = df[df["species"].isin(known_species)].reset_index(drop=True)

    # Stratified split on known species into Train / Validation / Known-Test
    train_val_df, known_test_df = train_test_split(
        known_df,
        test_size=test_ratio,
        stratify=known_df["species"],
        random_state=seed,
    )
    adjusted_val_ratio = val_ratio / (1.0 - test_ratio)
    train_df, val_df = train_test_split(
        train_val_df,
        test_size=adjusted_val_ratio,
        stratify=train_val_df["species"],
        random_state=seed,
    )

    # Strict Leakage Assertions
    assert set(train_df["species"]).isdisjoint(set(held_out)), "OOD species leaked into training!"
    assert set(val_df["species"]).isdisjoint(set(held_out)), "OOD species leaked into validation!"
    assert set(known_test_df["species"]).isdisjoint(set(held_out)), "OOD species leaked into known_test!"

    if "sha256" in df.columns:
        tr_hashes = set(train_df["sha256"])
        va_hashes = set(val_df["sha256"])
        kt_hashes = set(known_test_df["sha256"])
        oo_hashes = set(ood_df["sha256"])
        assert tr_hashes.isdisjoint(va_hashes), "Duplicate hash leakage between train and val!"
        assert tr_hashes.isdisjoint(kt_hashes), "Duplicate hash leakage between train and known_test!"
        assert tr_hashes.isdisjoint(oo_hashes), "Duplicate hash leakage between train and ood_test!"
        assert va_hashes.isdisjoint(oo_hashes), "Duplicate hash leakage between val and ood_test!"

    train_df.to_csv(TRAIN_MANIFEST_PATH, index=False)
    val_df.to_csv(VAL_MANIFEST_PATH, index=False)
    known_test_df.to_csv(KNOWN_TEST_MANIFEST_PATH, index=False)
    ood_df.to_csv(OOD_TEST_MANIFEST_PATH, index=False)

    class_to_idx = {species: idx for idx, species in enumerate(known_species)}
    idx_to_class = {str(idx): species for idx, species in enumerate(known_species)}
    mapping_payload = {
        "num_classes": len(known_species),
        "class_to_idx": class_to_idx,
        "idx_to_class": idx_to_class,
        "held_out_ood_species": held_out,
    }
    with CLASS_MAPPING_PATH.open("w", encoding="utf-8") as fh:
        json.dump(mapping_payload, fh, indent=2)

    split_config = {
        "seed": seed,
        "deduplicated_by_sha256": deduplicate_by_hash,
        "min_samples_per_species": min_samples_per_species,
        "excluded_sparse_species": excluded_sparse_species,
        "ood_selection_method": "explicit_list" if ood_species else f"random_species_ratio_{ood_ratio}",
        "known_species_count": len(known_species),
        "held_out_ood_species_count": len(held_out),
        "known_species": known_species,
        "held_out_ood_species": held_out,
        "counts": {
            "train": int(len(train_df)),
            "validation": int(len(val_df)),
            "known_test": int(len(known_test_df)),
            "ood_test": int(len(ood_df)),
        },
        "leakage_checks_passed": True,
    }
    with SPLIT_CONFIG_PATH.open("w", encoding="utf-8") as fh:
        json.dump(split_config, fh, indent=2)

    return split_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Create leakage-free known/OOD species dataset splits.")
    parser.add_argument("--inventory", type=Path, default=DATASET_REPORTS_DIR / "dataset_inventory.csv")
    parser.add_argument("--ood-ratio", type=float, default=0.20)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--test-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--min-samples-per-species", type=int, default=4)
    parser.add_argument("--ood-species", nargs="*", default=None)
    args = parser.parse_args()

    result = prepare_species_splits(
        inventory_csv=args.inventory,
        ood_species=args.ood_species,
        ood_ratio=args.ood_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
        min_samples_per_species=args.min_samples_per_species,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
