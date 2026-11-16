"""End-to-end tests for MediLeafPredictor error handling and known vs UNCERTAIN inference."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

try:
    from PIL import Image
    import torch
    from src.inference import MediLeafPredictor
    from src.model import build_resnet50_classifier, save_checkpoint
    from src.reject import RejectionConfig
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


@unittest.skipUnless(DEPS_AVAILABLE, "Requires Pillow and PyTorch")
class TestInferencePipeline(unittest.TestCase):
    def _make_png_bytes(self) -> bytes:
        img = Image.new("RGB", (256, 256), color=(30, 130, 50))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def test_missing_checkpoint_reports_model_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            predictor = MediLeafPredictor(
                checkpoint_path=Path(tmp) / "missing.pth",
                class_mapping_path=Path(tmp) / "missing.json",
                rejection_config_path=Path(tmp) / "rej.json",
            )
            self.assertFalse(predictor.is_ready)
            res = predictor.predict_bytes(self._make_png_bytes(), filename="leaf.png")
            self.assertEqual(res.status, "MODEL_NOT_READY")
            self.assertFalse(res.accepted)

    def test_corrupted_upload_returns_invalid_image(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            predictor = MediLeafPredictor(
                checkpoint_path=Path(tmp) / "missing.pth",
                class_mapping_path=Path(tmp) / "missing.json",
                rejection_config_path=Path(tmp) / "rej.json",
            )
            res = predictor.predict_bytes(b"corrupt_bytes", filename="bad.jpg")
            self.assertEqual(res.status, "INVALID_IMAGE")
            self.assertFalse(res.accepted)

    def test_loaded_checkpoint_runs_real_forward_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            ckpt = tmp_dir / "best_model.pth"
            cmap = tmp_dir / "class_mapping.json"
            rcfg = tmp_dir / "rejection_config.json"

            class_to_idx = {"ClassA": 0, "ClassB": 1, "ClassC": 2}
            model = build_resnet50_classifier(num_classes=3, pretrained=False)
            save_checkpoint(model, ckpt, class_to_idx, epoch=1, val_accuracy=0.85, val_loss=0.4)
            cmap.write_text(json.dumps({"class_to_idx": class_to_idx}), encoding="utf-8")
            # Force strict threshold = 0.99 so untrained random head reliably triggers UNCERTAIN
            RejectionConfig(gate_method="msp", msp_threshold=0.99).save(rcfg)

            predictor = MediLeafPredictor(ckpt, cmap, rcfg, device=torch.device("cpu"))
            self.assertTrue(predictor.is_ready)

            res = predictor.predict_bytes(self._make_png_bytes(), filename="test_leaf.png")
            self.assertEqual(res.status, "UNCERTAIN")
            self.assertEqual(res.predicted_species, "UNCERTAIN")
            self.assertFalse(res.accepted)
            self.assertIsNotNone(res.confidence)


if __name__ == "__main__":
    unittest.main()
