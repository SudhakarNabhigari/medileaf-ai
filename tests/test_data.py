"""Tests for image validation, preprocessing consistency, and dataset splitting."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

try:
    from PIL import Image
    import torch
    from src.data import get_eval_transforms, get_train_transforms, validate_image_bytes, validate_image_file
    from scripts.prepare_dataset import prepare_species_splits
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


@unittest.skipUnless(DEPS_AVAILABLE, "Requires Pillow, PyTorch, Pandas, and Scikit-learn")
class TestDataAndPreprocessing(unittest.TestCase):
    def _make_jpeg_bytes(self, size=(256, 256), color=(34, 139, 34)) -> bytes:
        img = Image.new("RGB", size, color=color)
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        return buf.getvalue()

    def test_valid_jpeg_bytes(self) -> None:
        res = validate_image_bytes(self._make_jpeg_bytes(), filename="leaf.jpg")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.width, 256)
        self.assertEqual(res.height, 256)
        self.assertEqual(res.mode, "RGB")

    def test_empty_file_rejected(self) -> None:
        res = validate_image_bytes(b"", filename="empty.jpg")
        self.assertFalse(res.is_valid)
        self.assertIn("empty", (res.error_message or "").lower())

    def test_unsupported_extension_rejected(self) -> None:
        res = validate_image_bytes(b"not_an_image", filename="leaf.txt")
        self.assertFalse(res.is_valid)
        self.assertIn("unsupported", (res.error_message or "").lower())

    def test_corrupted_image_rejected(self) -> None:
        res = validate_image_bytes(b"\xff\xd8\xff\xe0corrupted_payload", filename="corrupt.jpg")
        self.assertFalse(res.is_valid)

    def test_missing_file_rejected(self) -> None:
        res = validate_image_file("/nonexistent/path/to/leaf.jpg")
        self.assertFalse(res.is_valid)

    def test_eval_transform_output_shape(self) -> None:
        img = Image.new("RGB", (320, 240), color=(40, 120, 40))
        t_eval = get_eval_transforms()
        tensor = t_eval(img)
        self.assertEqual(tuple(tensor.shape), (3, 224, 224))
        self.assertEqual(tensor.dtype, torch.float32)

        t_train = get_train_transforms()
        self.assertEqual(tuple(t_train(img).shape), (3, 224, 224))

    def test_species_split_has_zero_ood_leakage(self) -> None:
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            rows = []
            for sp in ["Species_A", "Species_B", "Species_C", "Species_D", "Species_OOD"]:
                for i in range(10):
                    rows.append(
                        {
                            "species": sp,
                            "filepath": f"{tmp}/{sp}_{i}.jpg",
                            "filename": f"{sp}_{i}.jpg",
                            "extension": ".jpg",
                            "size_bytes": 1000,
                            "width": 224,
                            "height": 224,
                            "mode": "RGB",
                            "sha256": f"hash_{sp}_{i}",
                            "is_valid": True,
                            "is_duplicate": False,
                            "issue": "ok",
                        }
                    )
            inv_csv = tmp_path / "inventory.csv"
            pd.DataFrame(rows).to_csv(inv_csv, index=False)

            cfg = prepare_species_splits(
                inventory_csv=inv_csv,
                ood_species=["Species_OOD"],
                seed=42,
            )
            self.assertTrue(cfg["leakage_checks_passed"])
            self.assertEqual(cfg["held_out_ood_species"], ["Species_OOD"])
            self.assertNotIn("Species_OOD", cfg["known_species"])


if __name__ == "__main__":
    unittest.main()
