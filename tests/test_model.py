"""Tests for ResNet50 model construction, layer freezing, and checkpoint integrity."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

try:
    import torch
    from src.model import (
        build_resnet50_classifier,
        count_trainable_parameters,
        freeze_backbone,
        load_checkpoint,
        save_checkpoint,
        unfreeze_layers,
    )
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


@unittest.skipUnless(DEPS_AVAILABLE, "Requires PyTorch and Torchvision")
class TestResNet50Model(unittest.TestCase):
    def test_head_output_dimensions_and_freeze_unfreeze(self) -> None:
        model = build_resnet50_classifier(num_classes=6, pretrained=False, dropout=0.3)
        x = torch.randn(2, 3, 224, 224)
        logits = model(x)
        self.assertEqual(tuple(logits.shape), (2, 6))

        freeze_backbone(model)
        tr_head, total = count_trainable_parameters(model)
        self.assertLess(tr_head, total)
        self.assertGreater(tr_head, 0)

        unfreeze_layers(model, ("layer4", "fc"))
        tr_ft, _ = count_trainable_parameters(model)
        self.assertGreater(tr_ft, tr_head)

    def test_invalid_num_classes_raises(self) -> None:
        with self.assertRaises(ValueError):
            build_resnet50_classifier(num_classes=1, pretrained=False)

    def test_checkpoint_save_and_mismatch_detection(self) -> None:
        model = build_resnet50_classifier(num_classes=3, pretrained=False)
        class_to_idx = {"A": 0, "B": 1, "C": 2}
        with tempfile.TemporaryDirectory() as tmp:
            ckpt = Path(tmp) / "best_model.pth"
            cmap = Path(tmp) / "class_mapping.json"
            save_checkpoint(model, ckpt, class_to_idx, epoch=1, val_accuracy=0.9, val_loss=0.3)
            cmap.write_text(json.dumps({"class_to_idx": class_to_idx}), encoding="utf-8")

            loaded_model, idx_to_class, _ = load_checkpoint(ckpt, cmap, device=torch.device("cpu"))
            self.assertEqual(len(idx_to_class), 3)
            self.assertEqual(idx_to_class[0], "A")

            # Mismatched class mapping must raise ValueError
            cmap.write_text(json.dumps({"class_to_idx": {"A": 0, "B": 1}}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_checkpoint(ckpt, cmap, device=torch.device("cpu"))


if __name__ == "__main__":
    unittest.main()
